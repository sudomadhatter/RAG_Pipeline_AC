import json
import re
from pathlib import Path
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from utils.schema import CurriculumLessonSchema

def fallback_generator(markdown_path: Path):
    content = markdown_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    acs_pattern = re.compile(r'PA\.(?:I{1,3}|IV|V|VI{0,3}|IX|X{1,3}|XI{1,3})\.\w+\.\w+')
    
    # We will just parse each file in pipeline/curriculum/new/*.md that doesn't have a .json
    new_dir = Path(os.path.dirname(__file__)) / ".." / "pipeline" / "curriculum" / "new"
    
    for md_file in new_dir.glob("lesson_pa_ix*.md"):
        json_file = md_file.with_suffix('.json')
        if json_file.exists():
            continue
            
        print(f"Fallback generating for {md_file.name}")
        content = md_file.read_text(encoding='utf-8')
        
        # Extract title
        acs_match = acs_pattern.search(content)
        acs_code = acs_match.group(0) if acs_match else "UNKNOWN"
        
        title = "Extracted Title"
        title_match = re.search(r'PA\.[^:]*:\s*(.+?)(?:\*\*|$)', content)
        if title_match:
            title = title_match.group(1).strip()
            
        doc_id = 'lesson_' + acs_code.lower().replace('.', '_')
        
        # Extract bridge keys
        reg_keys = []
        doc_keys = []
        keywords = []
        
        bridge_section = re.search(r'Bridge Keys.*?(?=\Z)', content, re.DOTALL)
        if bridge_section:
            bridge_text = bridge_section.group(0)
            
            reg_match = re.search(r'\* \*\*Regs\*\*:\s*(.+?)(?:\n|$)', bridge_text)
            if reg_match:
                reg_keys = [r.strip().rstrip('.') for r in reg_match.group(1).split(',')]
            
            doc_match = re.search(r'\* \*\*Docs\*\*:\s*(.+?)(?:\n|$)', bridge_text)
            if doc_match:
                doc_keys = [d.strip().rstrip('.') for d in doc_match.group(1).split(',')]
                
            kw_match = re.search(r'\* \*\*Keywords\*\*:\s*(.+?)(?:\n|$)', bridge_text)
            if kw_match:
                keywords = [k.strip().rstrip('.') for k in kw_match.group(1).split(',')]

        data = {
            "id": doc_id,
            "structData": {
                "acs_code": acs_code,
                "title": title,
                "type": "lesson_chunk",
                "ancestral_context": "Private Pilot > Emergency Operations",
                "reg_keys": reg_keys,
                "doc_keys": doc_keys,
                "keywords": keywords
            }
        }
        
        try:
            # Validate to clean up N/A and chapter strings
            validated = CurriculumLessonSchema(**data)
            json_file.write_text(validated.model_dump_json(indent=2), encoding='utf-8')
            print(f"  -> Wrote {json_file.name}")
        except Exception as e:
            print(f"  -> Failed to validate {md_file.name}: {e}")

if __name__ == "__main__":
    fallback_generator(Path("curriculum_components/curriculum_modules/Area 9 Tasks B,C PPL.md"))
