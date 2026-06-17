import os
import json
import sys
from pathlib import Path

# Ensure we can import our pipeline schema
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from utils.schema import CurriculumLessonSchema, DB2_VOCABULARY
import config

def audit_and_clean_sidecars():
    print(f"Auditing JSON sidecars against hardened DB2_VOCABULARY...")
    print(f"Vocabulary size: {len(DB2_VOCABULARY)}")
    
    # We check both new and active
    target_dirs = [config.CURRICULUM_NEW, config.CURRICULUM_ACTIVE]
    
    total_files = 0
    fixed_files = 0
    error_files = 0
    
    for d in target_dirs:
        if not d.exists():
            continue
            
        for json_file in d.glob('*.json'):
            total_files += 1
            content = json_file.read_text(encoding='utf-8')
            try:
                data = json.loads(content)
                needs_save = False
                
                doc_keys = data.get('structData', {}).get('doc_keys', [])
                valid_keys = []
                
                # Manual validation and cleaning before passing to the strict Pydantic model
                for key in doc_keys:
                    original_key = key
                    key = key.strip()
                    
                    if key.upper() == 'N/A' or not key:
                        needs_save = True
                        print(f"  [{json_file.name}] Stripping N/A or empty key")
                        continue
                        
                    # Fix chapter-level annotations (e.g. "FAA-H-8083-25C (PHAK Ch 6)")
                    if '(' in key:
                        key = key.split('(')[0].strip()
                        needs_save = True
                        print(f"  [{json_file.name}] Stripped chapter annotation: '{original_key}' -> '{key}'")
                        
                    if ' Chapter ' in key or ' Ch ' in key:
                        key = key.split(' Chapter ')[0].split(' Ch ')[0].strip()
                        needs_save = True
                        print(f"  [{json_file.name}] Stripped chapter string: '{original_key}' -> '{key}'")
                        
                    # Handle specific Area 9 misses we know about
                    if key == 'AC 120-111' or key == 'AC 120-80' or key == 'FAA-S-ACS-6C' or key == 'FAA Safety Briefing "Startle Response"' or key == 'FAA-H-8083-2A':
                        pass # These were added to DB2_VOCABULARY
                    elif key not in DB2_VOCABULARY:
                        print(f"  [ERROR] [{json_file.name}] Unknown key: '{key}'. MUST FIX MANUALLY.")
                        error_files += 1
                        
                    if key in DB2_VOCABULARY:
                        valid_keys.append(key)
                
                if needs_save:
                    # Update and try schema validation
                    data['structData']['doc_keys'] = valid_keys
                    CurriculumLessonSchema(**data) # Will raise if invalid (like empty doc_keys)
                    
                    json_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
                    fixed_files += 1
                    print(f"  [{json_file.name}] Saved fixes.")
                else:
                    # Just validate
                    CurriculumLessonSchema(**data)
                    
            except Exception as e:
                print(f"  [FATAL] [{json_file.name}] Failed: {e}")
                error_files += 1
                
    print(f"\nAudit complete.")
    print(f"  Total files checked: {total_files}")
    print(f"  Files fixed & saved: {fixed_files}")
    print(f"  Files with errors: {error_files}")
    
    if error_files > 0:
        sys.exit(1)

if __name__ == "__main__":
    audit_and_clean_sidecars()
