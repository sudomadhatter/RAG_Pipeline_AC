import os
import json
import argparse
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

def generate_curriculum_metadata(markdown_path: Path) -> Path:
    """
    Uses Gemini structured output to read a raw Markdown lesson plan
    and strictly output a validated CurriculumLessonSchema JSON dict.
    """
    if not markdown_path.exists():
        raise FileNotFoundError(f"Source file not found: {markdown_path}")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in auth_keys/.env")

    client = genai.Client(api_key=api_key)

    print(f"Reading {markdown_path.name}...")
    content = markdown_path.read_text(encoding='utf-8')

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

    print("Requesting metadata generation from Gemini...")
    
    # We use Flash for speed, but Pro if it's super complex. We'll stick to 2.5 Flash.
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CurriculumLessonSchema,
        ),
    )

    # Response is guaranteed to match the Pydantic schema as a parsed JSON str
    metadata_json = response.text
    
    # Let's ensure it actually loads cleanly
    parsed_dict = json.loads(metadata_json)
    
    # Validate against the hardened schema (will fail on empty doc_keys)
    validated = CurriculumLessonSchema(**parsed_dict)
    
    # Post-generation warnings for chapter-level keys
    for key in validated.structData.doc_keys:
        if '(' in key or 'Ch ' in key:
            print(f"  [WARN] Chapter-level key detected: '{key}' — normalize to document level")
    
    if not validated.structData.doc_keys:
        raise ValueError(f"doc_keys is EMPTY after validation — this lesson will break the DB1→DB2 hop")
    
    print(f"  doc_keys: {validated.structData.doc_keys}")
    print(f"  reg_keys: {validated.structData.reg_keys}")
    
    # Write it back out alongside the .md file
    out_path = markdown_path.with_suffix('.json')
    out_path.write_text(json.dumps(parsed_dict, indent=2), encoding='utf-8')
    print(f"Generated JSON sidecar: {out_path.name}")
    
    return out_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Metadata Generator (Phase 0)")
    parser.add_argument("file", help="Path to the .md curriculum file")
    
    args = parser.parse_args()
    file_path = Path(args.file)
    
    try:
        generate_curriculum_metadata(file_path)
    except Exception as e:
        print(f"Failed to generate metadata: {e}")
