import os
import json
import re
from pathlib import Path
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from utils.schema import CurriculumLessonSchema
import config

def split_and_generate_regex(markdown_path: Path):
    content = markdown_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    acs_pattern = re.compile(r'PA\.(?:I{1,3}|IV|V|VI{0,3}|IX|X{1,3}|XI{1,3})\.\w+\.\w+')
    element_starts = []
    
    for i, line in enumerate(lines):
        if acs_pattern.search(line):
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('**PA.'):
                element_starts.append(i)
                
    out_dir = config.CURRICULUM_NEW
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for idx, start_line in enumerate(element_starts):
        end_line = element_starts[idx + 1] if idx + 1 < len(element_starts) else len(lines)
        
        while end_line > start_line and lines[end_line - 1].strip() in ('', '## ---', '### ---', '---'):
            end_line -= 1
            
        heading_line = lines[start_line]
        section_lines = lines[start_line:end_line]
        section_content = '\n'.join(section_lines)
        
        acs_match = acs_pattern.search(heading_line)
        acs_code = acs_match.group(0) if acs_match else 'UNKNOWN'
        
        title_match = re.search(r'PA\.[^:]*:\s*(.+?)(?:\*\*|$)', heading_line)
        title = title_match.group(1).strip() if title_match else "Extracted Title"
        
        doc_id = 'lesson_' + acs_code.lower().replace('.', '_')
        
        # Write .md
        md_file = out_dir / f"{doc_id}.md"
        md_file.write_text(section_content.strip(), encoding='utf-8')
        
        # Extract bridge keys
        reg_keys = []
        doc_keys = []
        keywords = []
        
        bridge_section = re.search(r'Bridge Keys.*?(?=\Z)', section_content, re.DOTALL)
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
        
        json_file = out_dir / f"{doc_id}.json"
        try:
            validated = CurriculumLessonSchema(**data)
            json_file.write_text(validated.model_dump_json(indent=2), encoding='utf-8')
            print(f"Generated {md_file.name} and {json_file.name}")
        except Exception as e:
            print(f"Failed to validate {doc_id}: {e}")

if __name__ == "__main__":
    split_and_generate_regex(Path("curriculum_components/curriculum_modules/Area 9 Tasks B,C PPL.md"))
