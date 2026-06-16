import os
import sys
import json
import traceback
from pathlib import Path

# Fix Windows console encoding for Unicode characters
sys.stdout.reconfigure(encoding='utf-8')

import firebase_admin
from firebase_admin import credentials, firestore

# Paths — updated to match current workspace
PROJECT_ROOT = Path(r"c:\Users\dlohn\.gemini\antigravity\scratch\Ingestion_pipeline_AvCh")
SA_PATH = PROJECT_ROOT / "auth_keys" / "service-account.json"
QUIZ_BANKS_DIR = PROJECT_ROOT / "specialist_curriculum" / "quiz_banks"

# Ensure environment variable is set
if SA_PATH.exists():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(SA_PATH)
else:
    print(f"Error: Service Account key not found at {SA_PATH}")
    exit(1)

def validate_quiz(data: dict, filename: str) -> list[str]:
    """Validate quiz bank structure. Returns list of errors."""
    errors = []
    lesson_id = data.get("lesson_id", "UNKNOWN")
    questions = data.get("questions", [])

    if len(questions) != 8:
        errors.append(f"{lesson_id}: Expected 8 questions, got {len(questions)}")

    # Count perspectives
    perspective_counts = {}
    for q in questions:
        qid = q.get("id", "?")
        perspective = q.get("perspective", "MISSING")
        perspective_counts[perspective] = perspective_counts.get(perspective, 0) + 1

        if not q.get("tested_rkp_id"):
            errors.append(f"{qid}: missing tested_rkp_id")
        if q.get("far_reference") is None:
            errors.append(f"{qid}: far_reference is null (must be a string)")
        if not q.get("text"):
            errors.append(f"{qid}: missing question text")

        # SJT-specific checks
        if q.get("question_type") == "sjt":
            if q.get("correct_answer") != "D":
                errors.append(f"{qid}: SJT correct_answer must be 'D', got '{q.get('correct_answer')}'")
            if not q.get("sjt_rationale"):
                errors.append(f"{qid}: SJT missing sjt_rationale")
            # Check hazardous_attitude on incorrect options
            for opt in q.get("options", []):
                if opt.get("label") != "D" and not opt.get("hazardous_attitude"):
                    errors.append(f"{qid}: SJT option {opt.get('label', '?')} missing hazardous_attitude")

    # Check perspective distribution
    expected = {"legal": 2, "safety": 2, "application": 2, "risk_management": 2}
    for perspective, expected_count in expected.items():
        actual = perspective_counts.get(perspective, 0)
        if actual != expected_count:
            errors.append(f"{lesson_id}: Expected {expected_count} '{perspective}' questions, got {actual}")

    return errors


def main():
    print("Initializing Firebase Admin SDK...")
    cred = credentials.Certificate(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    
    # Initialize the app (protect against dual-init if run interactively)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {"projectId": "aviationchat"})
        
    print("Connecting to Firestore database: 'aviationchat-database'")
    # Crucial: target the correct database per the architecture pattern
    db = firestore.client(database_id="aviationchat-database")
    
    collection_ref = db.collection("quiz_banks")
    
    json_files = list(QUIZ_BANKS_DIR.glob("*_quiz.json"))
    total_files = len(json_files)
    success_count = 0
    fail_count = 0
    skipped_count = 0
    
    print(f"\nFound {total_files} quiz bank files. Starting upload...\n")
    
    for file_path in sorted(json_files):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Use lesson_id as the document ID
            doc_id = data.get("lesson_id")
            if not doc_id:
                print(f"  [ERROR] {file_path.name} missing 'lesson_id'")
                fail_count += 1
                continue
                
            # Validate quiz structure before upload
            validation_errors = validate_quiz(data, file_path.name)
            if validation_errors:
                print(f"  [REJECT] {file_path.name} failed validation:")
                for err in validation_errors:
                    print(f"           → {err}")
                skipped_count += 1
                continue
                
            # Write to Firestore. Using set() will create or overwrite the existing document
            collection_ref.document(doc_id).set(data)
            print(f"  [OK] Uploaded {doc_id} from {file_path.name}")
            success_count += 1
            
        except Exception as e:
            print(f"  [FAIL] Error processing {file_path.name}: {e}")
            fail_count += 1
            
    print("\n--- Upload Complete ---")
    print(f"Total Found:  {total_files}")
    print(f"Successful:   {success_count}")
    print(f"Rejected:     {skipped_count}")
    print(f"Failed:       {fail_count}")
    print("-----------------------\n")
    
if __name__ == "__main__":
    main()
