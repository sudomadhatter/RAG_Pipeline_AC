import os
import json
import argparse
import re
from pathlib import Path
from dotenv import load_dotenv

# We need to make sure we can import our pipeline schema
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.schema import CurriculumLessonSchema

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("google-genai package not found. Install it with: pip install google-genai")
    sys.exit(1)

# Load env file specifically from the known structure
env_path = Path(__file__).parent.parent.parent / "auth_keys" / ".env"
load_dotenv(dotenv_path=env_path)

def split_task_file(content: str, filename: str = "Area X Task Y.md") -> list[dict]:
    """
    Split a task-level .md file into individual ACS elements.
    Returns list of dicts: {id, acs_code, title, element_type, content}
    """
    lines = content.split('\n')
    
    # Find all lines that contain an ACS code pattern like PA.I.X.K1
    acs_pattern = re.compile(r'PA\.(?:I{1,3}|IV|V|VI{0,3}|IX|X{1,3}|XI{1,3})\.\w+\.\w+')
    element_starts = []
    
    for i, line in enumerate(lines):
        if acs_pattern.search(line):
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('**PA.'):
                element_starts.append(i)
    
    elements = []
    for idx, start_line in enumerate(element_starts):
        end_line = element_starts[idx + 1] if idx + 1 < len(element_starts) else len(lines)
        
        while end_line > start_line and lines[end_line - 1].strip() in ('', '## ---', '### ---', '---'):
            end_line -= 1
        
        heading_line = lines[start_line]
        section_lines = lines[start_line:end_line]
        section_content = '\n'.join(section_lines)
        
        acs_match = acs_pattern.search(heading_line)
        acs_code = acs_match.group(0) if acs_match else 'UNKNOWN'
        
        title_match = re.search(r'PA\.(?:I{1,3}|IV|V|VI{0,3}|IX|X{1,3}|XI{1,3})\.\w+\.\w+[^:]*:\s*(.+?)(?:\*\*|$)', heading_line)
        title = title_match.group(1).strip().rstrip('*').strip() if title_match else heading_line.strip().strip('#').strip('*').strip()
        
        doc_id = 'lesson_' + acs_code.lower().replace('.', '_')
        
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
            'element_type': element_type,
            'content': section_content.strip(),
        })
    
    return elements

def generate_curriculum_metadata(content: str, offline: bool = False, existing_sidecar: dict = None) -> dict:
    """
    Uses Gemini structured output to read a raw Markdown lesson plan chunk
    and strictly output a validated CurriculumLessonSchema JSON dict.
    Returns the raw parsed dict.
    """
    if offline:
        if not existing_sidecar:
            raise ValueError("Offline mode requires an existing JSON sidecar, but none was found.")
        print("  [Offline] Reusing existing JSON sidecar (validated).")
        # Validate even the reused sidecar — a stale/bad one must fail HERE, not slip to DB1.
        CurriculumLessonSchema(**existing_sidecar)
        return existing_sidecar

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in auth_keys/.env")

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an expert aviation curriculum developer. I am providing you with the text of an FAA Airman Certification Standards (ACS) lesson plan.

    Your task is to analyze this lesson plan and extract the required metadata to generate a valid JSON object matching the requested schema.
    
    Guidelines:
    - id: A unique lowercase slug like "lesson_pa_i_a_k1" derived from the ACS code.
    - acs_code: The exact FAA ACS code (e.g., "PA.I.A.K1"). Look for this in the text or derive from context.
    - title: A concise 1-sentence title or short phrase summarizing the lesson intent.
    - type: Always "lesson_chunk".
    - ancestral_context: The hierarchical path in the ACS, e.g., "Private Pilot > Preflight Preparation > Pilot Qualifications".
    - reg_keys: A list of 14 CFR regulations relevant to this task (e.g., ["14 CFR part 61", "14 CFR part 91"]).
    - doc_keys: A list of FAA handbooks/ACs at DOCUMENT level only (e.g., ["FAA-H-8083-25C", "AC 61-98D", "AIM"]).
      IMPORTANT: Use document-level identifiers ONLY. Do NOT include chapter or section
      (e.g., "FAA-H-8083-25C" not "FAA-H-8083-25C (PHAK Ch 6)"). These keys must match
      the Vertex AI Search document_tags vocabulary exactly. doc_keys must NOT be empty.
    - keywords: 3 to 6 critical keyword terms.

    Here is the lesson text:
    -----------------------------------
    {content}
    -----------------------------------
    """

    print("  Requesting metadata generation from Gemini (temperature=0.0)...")
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CurriculumLessonSchema,
            temperature=0.0,
        ),
    )

    parsed_dict = json.loads(response.text)
    
    # Validate against the hardened schema (will fail on empty doc_keys or off-vocab)
    validated = CurriculumLessonSchema(**parsed_dict)
    
    print(f"  doc_keys: {validated.structData.doc_keys}")
    print(f"  reg_keys: {validated.structData.reg_keys}")
    
    return parsed_dict

def process_master_module(markdown_path: Path, offline: bool = False):
    import config
    
    if not markdown_path.exists():
        raise FileNotFoundError(f"Source file not found: {markdown_path}")
        
    print(f"Reading master module: {markdown_path.name}")
    content = markdown_path.read_text(encoding='utf-8')
    elements = split_task_file(content, markdown_path.name)
    print(f"Split into {len(elements)} chunks.")
    
    out_dir = config.CURRICULUM_NEW
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for i, elem in enumerate(elements):
        print(f"Processing chunk {i+1}/{len(elements)}: {elem['id']}")
        
        md_out_path = out_dir / f"{elem['id']}.md"
        json_out_path = out_dir / f"{elem['id']}.json"
        
        existing_sidecar = None
        if json_out_path.exists():
            try:
                existing_sidecar = json.loads(json_out_path.read_text(encoding='utf-8'))
            except Exception:
                pass
                
        parsed_dict = generate_curriculum_metadata(
            content=elem['content'],
            offline=offline,
            existing_sidecar=existing_sidecar
        )
        
        md_out_path.write_text(elem['content'], encoding='utf-8')
        json_out_path.write_text(json.dumps(parsed_dict, indent=2), encoding='utf-8')
        print(f"  Wrote {md_out_path.name} and {json_out_path.name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Metadata Generator & Module Splitter")
    parser.add_argument("file", help="Path to the master .md curriculum module")
    parser.add_argument("--offline", action="store_true", help="Reuse existing JSON sidecars instead of calling the LLM (deterministic re-runs; fails if a sidecar is missing)")

    args = parser.parse_args()
    file_path = Path(args.file)

    try:
        process_master_module(file_path, offline=args.offline)
    except Exception as e:
        print(f"Failed to process module: {e}")
