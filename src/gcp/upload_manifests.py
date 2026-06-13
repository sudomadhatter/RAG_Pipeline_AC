import os
import json
import traceback
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

# Paths
PROJECT_ROOT = Path(r"c:\AGY-Projects\ingestion-Pipeline-AC")
SA_PATH = PROJECT_ROOT / "auth_keys" / "librarian-service-account.json"
RKP_MANIFESTS_DIR = PROJECT_ROOT / "specialist_curriculum" / "rkp_manifests"

# Ensure environment variable is set
if SA_PATH.exists():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(SA_PATH)
else:
    print(f"Error: Librarian Service Account key not found at {SA_PATH}")
    exit(1)

def main():
    print("Initializing Firebase Admin SDK...")
    cred = credentials.Certificate(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    
    # Initialize the app (protect against dual-init if run interactively)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {"projectId": "aviationchat"})
        
    print("Connecting to Firestore database: 'aviationchat-database'")
    # Crucial: target the correct database per the architecture pattern
    db = firestore.client(database_id="aviationchat-database")
    
    collection_ref = db.collection("rkp_manifests")
    
    json_files = list(RKP_MANIFESTS_DIR.glob("*_rkp.json"))
    total_files = len(json_files)
    success_count = 0
    fail_count = 0
    
    print(f"\nFound {total_files} RKP manifest files. Starting upload...\n")
    
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
                
            # Write to Firestore. Using set() will create or overwrite the existing document
            collection_ref.document(doc_id).set(data)
            print(f"  [OK] Uploaded {doc_id} from {file_path.name}")
            success_count += 1
            
        except Exception as e:
            print(f"  [FAIL] Error processing {file_path.name}: {e}")
            fail_count += 1
            
    print("\n--- Upload Complete ---")
    print(f"Total Found: {total_files}")
    print(f"Successful:  {success_count}")
    print(f"Failed:      {fail_count}")
    print("-----------------------\n")
    
if __name__ == "__main__":
    main()
