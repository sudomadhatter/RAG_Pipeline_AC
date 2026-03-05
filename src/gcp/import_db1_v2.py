"""
Split all 8 lesson .md files into per-ACS-element documents,
extract structured Bridge Key metadata, upload to GCS, and
import into aviation-curriculum-v2 with FULL reconciliation.

All files use: ## PA.I.X.K1: Title
Bridge Keys format:
  ### 4. Bridge Keys (Metadata)
  * **Regs:** ...
  * **Docs:** ...
  * **Keywords:** ...
"""
import os, json, re
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'c:\AGY-Projects\ingestion-Pipeline-AC\auth_keys\librarian-service-account.json'

from pathlib import Path
from google.cloud import storage, discoveryengine_v1 as discoveryengine

PROJECT_ID     = 'aviationchat'
LOCATION       = 'global'
CURRICULUM_BUCKET = 'aviationchat-curriculum-cms'
BASE           = Path(r'c:\AGY-Projects\ingestion-Pipeline-AC\pipeline\curriculum\new')
SPLIT_DIR      = Path(r'c:\AGY-Projects\ingestion-Pipeline-AC\pipeline\curriculum\_v2_split')
SPLIT_DIR.mkdir(parents=True, exist_ok=True)

ACS_HEADING    = re.compile(r'^## (PA\.I\.\w+\.\w+): (.+)$', re.MULTILINE)


def parse_bridge_keys(text: str) -> dict:
    """Extract reg_keys, doc_keys, keywords from the Bridge Keys section."""
    reg_keys, doc_keys, keywords = [], [], []
    m = re.search(r'Bridge Keys.*?(?=\n## |\Z)', text, re.DOTALL | re.IGNORECASE)
    if not m:
        return dict(reg_keys=reg_keys, doc_keys=doc_keys, keywords=keywords)
    bridge = m.group(0)
    for line in bridge.split('\n'):
        line = line.strip().lstrip('*').strip()
        if line.lower().startswith('regs:') or line.lower().startswith('**regs'):
            raw = re.sub(r'\*\*Regs[^:]*:\*\*\s*', '', line, flags=re.IGNORECASE).strip()
            reg_keys = [r.strip().rstrip('.') for r in raw.split(',') if r.strip()]
        elif line.lower().startswith('docs:') or line.lower().startswith('**docs'):
            raw = re.sub(r'\*\*Docs[^:]*:\*\*\s*', '', line, flags=re.IGNORECASE).strip()
            doc_keys = [d.strip().rstrip('.') for d in raw.split(',') if d.strip()]
        elif line.lower().startswith('keywords:') or line.lower().startswith('**keywords'):
            raw = re.sub(r'\*\*Keywords[^:]*:\*\*\s*', '', line, flags=re.IGNORECASE).strip()
            keywords = [k.strip().rstrip('.') for k in raw.split(',') if k.strip()]
    return dict(reg_keys=reg_keys, doc_keys=doc_keys, keywords=keywords)


def split_file(filepath: Path) -> list[dict]:
    content = filepath.read_text(encoding='utf-8')
    # Split at every ## PA.I. heading
    segments = re.split(r'(?=^## PA\.I\.)', content, flags=re.MULTILINE)
    elements = []
    for seg in segments:
        seg = seg.strip()
        m = re.match(r'^## (PA\.I\.\w+\.\w+): (.+)', seg)
        if not m:
            continue
        acs_code = m.group(1)
        title    = m.group(2).strip()
        doc_id   = 'lesson_' + acs_code.lower().replace('.', '_')
        # Determine type
        suffix = acs_code.split('.')[-1]
        if suffix.startswith('K'):   elem_type = 'knowledge'
        elif suffix.startswith('R'): elem_type = 'risk_management'
        elif suffix.startswith('S'): elem_type = 'skill'
        else:                        elem_type = 'lesson_chunk'
        bridge = parse_bridge_keys(seg)
        elements.append(dict(
            id=doc_id, acs_code=acs_code, title=title,
            element_type=elem_type, content=seg, **bridge,
        ))
    return elements


def main():
    gcs_client = storage.Client()
    bucket     = gcs_client.bucket(CURRICULUM_BUCKET)
    all_entries = []
    total_elements = 0

    for filepath in sorted(BASE.glob('Area *.md')):
        print(f'\n--- {filepath.name} ---')
        elements = split_file(filepath)
        print(f'  {len(elements)} elements extracted')
        total_elements += len(elements)

        for elem in elements:
            # Write local split file
            local = SPLIT_DIR / f"{elem['id']}.md"
            local.write_text(elem['content'], encoding='utf-8')
            # Upload to GCS
            blob_name = f"v2/elements/{elem['id']}.md"
            bucket.blob(blob_name).upload_from_filename(str(local))
            gcs_uri = f'gs://{CURRICULUM_BUCKET}/{blob_name}'
            # Build JSONL entry
            all_entries.append({
                'id': elem['id'],
                'structData': {
                    'acs_code':     elem['acs_code'],
                    'title':        elem['title'],
                    'element_type': elem['element_type'],
                    'reg_keys':     elem['reg_keys'],
                    'doc_keys':     elem['doc_keys'],
                    'keywords':     elem['keywords'],
                },
                'content': {'mimeType': 'text/plain', 'uri': gcs_uri},
            })
            print(f"    {elem['id']} | regs:{len(elem['reg_keys'])} docs:{len(elem['doc_keys'])} kw:{len(elem['keywords'])}")

    # Write + upload JSONL manifest
    jsonl_path = SPLIT_DIR / 'curriculum_v2_import.jsonl'
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for entry in all_entries:
            f.write(json.dumps(entry) + '\n')
    bucket.blob('v2/curriculum_v2_import.jsonl').upload_from_filename(str(jsonl_path))
    print(f'\nManifest: {len(all_entries)} documents -> gs://{CURRICULUM_BUCKET}/v2/curriculum_v2_import.jsonl')

    # FULL import into aviation-curriculum-v2
    doc_client = discoveryengine.DocumentServiceClient()
    parent = doc_client.branch_path(
        project=PROJECT_ID, location=LOCATION,
        data_store='aviation-curriculum-v2', branch='default_branch',
    )
    req = discoveryengine.ImportDocumentsRequest(
        parent=parent,
        gcs_source=discoveryengine.GcsSource(
            input_uris=[f'gs://{CURRICULUM_BUCKET}/v2/curriculum_v2_import.jsonl'],
            data_schema='document',
        ),
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.FULL,
    )
    print('\nImporting into aviation-curriculum-v2 (FULL reconciliation)...')
    op = doc_client.import_documents(req)
    print(f'  Operation: {op.operation.name}')
    op.result(timeout=600)
    print('  Import complete!')

    # Final verification
    docs = list(doc_client.list_documents(parent=parent))
    print(f'\nDB1 now has {len(docs)} documents (expected {total_elements})')
    print('\n=== DONE ===')


if __name__ == '__main__':
    main()
