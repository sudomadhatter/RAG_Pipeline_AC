"""
Split task-level .md files into per-ACS-element files,
generate structured metadata JSON for each, upload to GCS,
and create a JSONL manifest for Vertex AI Search import.

This replicates the v1 schema (per-element structData with acs_code,
reg_keys, doc_keys, etc.) on top of the v2 layout-aware chunking.
"""
import os, json, re, sys
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'c:\AGY-Projects\ingestion-Pipeline-AC\auth_keys\librarian-service-account.json'

from google.cloud import storage
from google.cloud import discoveryengine_v1 as discoveryengine
from pathlib import Path

PROJECT_ID = 'aviationchat'
LOCATION = 'global'
CURRICULUM_BUCKET = 'aviationchat-curriculum-cms'

PIPELINE_ROOT = Path(r'c:\AGY-Projects\ingestion-Pipeline-AC\pipeline')
CURRICULUM_NEW = PIPELINE_ROOT / 'curriculum' / 'new'
OUTPUT_DIR = PIPELINE_ROOT / 'curriculum' / '_v2_split'


def split_task_file(filepath: Path) -> list[dict]:
    """
    Split a task-level .md file into individual ACS elements.
    Handles TWO heading formats:
      - Tasks A&B: ### **PA.I.A.K1: Title**
      - Tasks C-F:  **PA.I.C.K1: Title** (bold text after ## --- breaks)
    Returns list of dicts: {id, acs_code, title, content, bridge_keys}
    """
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Find all lines that contain an ACS code pattern like PA.I.X.K1
    acs_pattern = re.compile(r'PA\.(?:I{1,3}|IV|V|VI{0,3}|IX|X{1,3}|XI{1,3})\.\w+\.\w+')
    element_starts = []
    
    for i, line in enumerate(lines):
        # Match lines like: ### **PA.I.A.K1: ...  OR  **PA.I.C.K1: ...
        if acs_pattern.search(line):
            # Make sure it's a heading/title line, not a reference in body text
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('**PA.'):
                element_starts.append(i)
    
    elements = []
    for idx, start_line in enumerate(element_starts):
        # Content runs from this element start to the next, or end of file
        end_line = element_starts[idx + 1] if idx + 1 < len(element_starts) else len(lines)
        
        # Walk backwards from end to skip any ## --- or blank preamble of next section
        while end_line > start_line and lines[end_line - 1].strip() in ('', '## ---', '### ---', '---'):
            end_line -= 1
        
        heading_line = lines[start_line]
        section_lines = lines[start_line:end_line]
        section_content = '\n'.join(section_lines)
        
        # Extract ACS code
        acs_match = acs_pattern.search(heading_line)
        acs_code = acs_match.group(0) if acs_match else 'UNKNOWN'
        
        # Extract title (text after the ACS code and colon)
        title_match = re.search(r'PA\.(?:I{1,3}|IV|V|VI{0,3}|IX|X{1,3}|XI{1,3})\.\w+\.\w+[^:]*:\s*(.+?)(?:\*\*|$)', heading_line)
        title = title_match.group(1).strip().rstrip('*').strip() if title_match else heading_line.strip().strip('#').strip('*').strip()
        
        # Generate document ID
        doc_id = 'lesson_' + acs_code.lower().replace('.', '_')
        
        # Extract bridge keys from "Bridge Keys" section
        reg_keys = []
        doc_keys = []
        keywords = []
        
        bridge_section = re.search(r'Bridge Keys.*?(?=\n##|\n\*\*PA\.|\Z)', section_content, re.DOTALL)
        if bridge_section:
            bridge_text = bridge_section.group(0)
            
            reg_match = re.search(r'Regs?:\s*(.+?)(?:\n|$)', bridge_text)
            if reg_match:
                reg_keys = [r.strip().rstrip('.') for r in reg_match.group(1).split(',')]
            
            doc_match = re.search(r'Docs?:\s*(.+?)(?:\n|$)', bridge_text)
            if doc_match:
                doc_keys = [d.strip().rstrip('.') for d in doc_match.group(1).split(',')]
            
            kw_match = re.search(r'Keywords?:\s*(.+?)(?:\n|$)', bridge_text)
            if kw_match:
                keywords = [k.strip().rstrip('.') for k in kw_match.group(1).split(',')]
        
        # Determine element type
        element_suffix = acs_code.split('.')[-1]
        if element_suffix.startswith('K'):
            element_type = 'knowledge'
        elif element_suffix.startswith('R'):
            element_type = 'risk_management'
        elif element_suffix.startswith('S'):
            element_type = 'skill'
        else:
            element_type = 'lesson_chunk'
        
        elements.append({
            'id': doc_id,
            'acs_code': acs_code,
            'title': title,
            'type': 'lesson_chunk',
            'element_type': element_type,
            'content': section_content.strip(),
            'reg_keys': reg_keys,
            'doc_keys': doc_keys,
            'keywords': keywords,
        })
    
    return elements


def process_all_tasks():
    """Split all task files, upload per-element .md files, build JSONL."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    md_files = sorted(CURRICULUM_NEW.glob('Area *.md'))
    print(f"Found {len(md_files)} task files to split\n")
    
    all_elements = []
    gcs_client = storage.Client()
    bucket = gcs_client.bucket(CURRICULUM_BUCKET)
    
    for filepath in md_files:
        print(f"--- Splitting: {filepath.name} ---")
        elements = split_task_file(filepath)
        print(f"  Found {len(elements)} ACS elements")
        
        for elem in elements:
            # Write individual .md file
            elem_file = OUTPUT_DIR / f"{elem['id']}.md"
            elem_file.write_text(elem['content'], encoding='utf-8')
            
            # Upload to GCS 
            blob_name = f"v2/elements/{elem['id']}.md"
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(str(elem_file))
            
            gcs_uri = f"gs://{CURRICULUM_BUCKET}/{blob_name}"
            
            # Determine ancestral context from the file name
            task_match = re.search(r'Area \d+ Task (\w+)', filepath.name)
            task_letter = task_match.group(1) if task_match else '?'
            area_match = re.search(r'Area (\d+)', filepath.name)
            area_num = area_match.group(1) if area_match else '?'
            ancestral = f"Private Pilot > Area {area_num} > Task {task_letter}"
            
            # Build JSONL entry (same schema as v1)
            jsonl_entry = {
                'id': elem['id'],
                'structData': {
                    'acs_code': elem['acs_code'],
                    'title': elem['title'],
                    'type': elem['type'],
                    'ancestral_context': ancestral,
                    'reg_keys': elem['reg_keys'],
                    'doc_keys': elem['doc_keys'],
                    'keywords': elem['keywords'],
                },
                'content': {
                    'mimeType': 'text/plain',
                    'uri': gcs_uri,
                },
            }
            all_elements.append(jsonl_entry)
            
            print(f"    {elem['id']} ({elem['acs_code']}) -> {len(elem['reg_keys'])} regs, {len(elem['doc_keys'])} docs")
    
    # Write JSONL manifest
    jsonl_path = OUTPUT_DIR / 'curriculum_v2_import.jsonl'
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for entry in all_elements:
            f.write(json.dumps(entry) + '\n')
    
    print(f"\nGenerated JSONL manifest: {jsonl_path} ({len(all_elements)} documents)")
    
    # Upload JSONL to GCS
    jsonl_blob = bucket.blob('v2/curriculum_v2_import.jsonl')
    jsonl_blob.upload_from_filename(str(jsonl_path))
    print(f"Uploaded manifest to gs://{CURRICULUM_BUCKET}/v2/curriculum_v2_import.jsonl")
    
    return len(all_elements)


def reimport_curriculum():
    """Trigger a FULL re-import using the JSONL manifest."""
    client = discoveryengine.DocumentServiceClient()
    parent = client.branch_path(
        project=PROJECT_ID, location=LOCATION,
        data_store='aviation-curriculum-v2', branch='default_branch',
    )
    
    request = discoveryengine.ImportDocumentsRequest(
        parent=parent,
        gcs_source=discoveryengine.GcsSource(
            input_uris=[f'gs://{CURRICULUM_BUCKET}/v2/curriculum_v2_import.jsonl'],
            data_schema='document',
        ),
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.FULL,
    )
    
    print("Re-importing curriculum with structured metadata...")
    operation = client.import_documents(request=request)
    print(f"  Operation: {operation.operation.name}")
    print(f"  Waiting for completion...")
    result = operation.result(timeout=600)
    print(f"  Import complete!")
    return result


def reimport_library():
    """Re-import library PDFs with structured metadata (category, title, etc.)."""
    client = discoveryengine.DocumentServiceClient()
    gcs_client = storage.Client()
    bucket = gcs_client.bucket('aviationchat-library')
    
    library_new = PIPELINE_ROOT / 'library' / 'new'
    pdf_files = sorted(library_new.glob('*.pdf'))
    
    entries = []
    for pdf in pdf_files:
        fname = pdf.name
        # Determine category and subfolder
        if fname.startswith('14 CFR') or fname.startswith('49 CFR'):
            category = 'regulation'
            subfolder = 'regulations'
        elif fname.startswith('AC '):
            category = 'advisory_circular'
            subfolder = 'advisory_circulars'
        else:
            category = 'handbook'
            subfolder = 'handbooks'
        
        # Build ID
        doc_id = re.sub(r'[^a-z0-9]+', '_', fname.lower().replace('.pdf', '')).strip('_')
        title = fname.replace('.pdf', '')
        
        entry = {
            'id': doc_id,
            'structData': {
                'title': title,
                'filename': fname,
                'category': category,
                'subfolder': subfolder,
            },
            'content': {
                'mimeType': 'application/pdf',
                'uri': f'gs://aviationchat-library/v2/{fname}',
            },
        }
        entries.append(entry)
        print(f"  {doc_id} -> {category}")
    
    # Write JSONL
    jsonl_path = OUTPUT_DIR / 'library_v2_import.jsonl'
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for e in entries:
            f.write(json.dumps(e) + '\n')
    
    # Upload JSONL
    jsonl_blob = bucket.blob('v2/library_v2_import.jsonl')
    jsonl_blob.upload_from_filename(str(jsonl_path))
    print(f"Uploaded manifest to gs://aviationchat-library/v2/library_v2_import.jsonl")
    
    # Import
    parent = client.branch_path(
        project=PROJECT_ID, location=LOCATION,
        data_store='aviation-library-v2', branch='default_branch',
    )
    request = discoveryengine.ImportDocumentsRequest(
        parent=parent,
        gcs_source=discoveryengine.GcsSource(
            input_uris=['gs://aviationchat-library/v2/library_v2_import.jsonl'],
            data_schema='document',
        ),
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.FULL,
    )
    
    print("Re-importing library with structured metadata...")
    operation = client.import_documents(request=request)
    print(f"  Waiting for completion...")
    result = operation.result(timeout=1800)
    print(f"  Library import complete!")
    return result


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'all'
    
    if target in ('curriculum', 'all'):
        print("=" * 60)
        print("CURRICULUM: Split + Metadata + Re-import")
        print("=" * 60)
        n = process_all_tasks()
        print(f"\nProcessed {n} ACS elements. Now re-importing...\n")
        reimport_curriculum()
        print()
    
    if target in ('library', 'all'):
        print("=" * 60)
        print("LIBRARY: Metadata JSONL + Re-import")
        print("=" * 60)
        reimport_library()
    
    print("\n=== DONE ===")
