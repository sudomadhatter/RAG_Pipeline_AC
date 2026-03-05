"""
Upload local documents to GCS and import them into V2 data stores.
Handles both curriculum (.md) and library (.pdf) documents.
"""
import os, json, time
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'c:\AGY-Projects\ingestion-Pipeline-AC\auth_keys\librarian-service-account.json'

from google.cloud import storage
from google.cloud import discoveryengine_v1 as discoveryengine
from pathlib import Path

PROJECT_ID = 'aviationchat'
LOCATION = 'global'
PROJECT_NUMBER = '856831340418'

# GCS Buckets
CURRICULUM_BUCKET = 'aviationchat-curriculum-cms'
LIBRARY_BUCKET = 'aviationchat-library'

# Local paths
PIPELINE_ROOT = Path(r'c:\AGY-Projects\ingestion-Pipeline-AC\pipeline')
CURRICULUM_NEW = PIPELINE_ROOT / 'curriculum' / 'new'
LIBRARY_NEW = PIPELINE_ROOT / 'library' / 'new'


def upload_curriculum_to_gcs():
    """Upload all .md files from curriculum/new/ to GCS."""
    client = storage.Client()
    bucket = client.bucket(CURRICULUM_BUCKET)
    
    md_files = list(CURRICULUM_NEW.glob('*.md'))
    print(f"Found {len(md_files)} curriculum files to upload")
    
    for f in md_files:
        blob_name = f'v2/{f.name}'
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(str(f))
        print(f"  Uploaded: gs://{CURRICULUM_BUCKET}/{blob_name} ({f.stat().st_size:,} bytes)")
    
    return len(md_files)


def upload_library_to_gcs():
    """Upload all PDFs from library/new/ to GCS."""
    client = storage.Client()
    bucket = client.bucket(LIBRARY_BUCKET)
    
    pdf_files = list(LIBRARY_NEW.glob('*.pdf'))
    print(f"Found {len(pdf_files)} library PDFs to upload")
    
    for f in pdf_files:
        blob_name = f'v2/{f.name}'
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(str(f))
        print(f"  Uploaded: gs://{LIBRARY_BUCKET}/{blob_name} ({f.stat().st_size:,} bytes)")
    
    return len(pdf_files)


def import_documents(data_store_id: str, gcs_uri: str):
    """Trigger a document import from GCS into a Vertex AI Search data store."""
    client = discoveryengine.DocumentServiceClient()
    
    parent = client.branch_path(
        project=PROJECT_ID,
        location=LOCATION,
        data_store=data_store_id,
        branch='default_branch',
    )
    
    request = discoveryengine.ImportDocumentsRequest(
        parent=parent,
        gcs_source=discoveryengine.GcsSource(
            input_uris=[gcs_uri],
            data_schema='content',
        ),
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.FULL,
    )
    
    print(f"Importing from {gcs_uri} into {data_store_id}...")
    operation = client.import_documents(request=request)
    print(f"  Operation started: {operation.operation.name}")
    print(f"  Waiting for completion (this may take several minutes for large PDFs)...")
    
    result = operation.result(timeout=1800)  # 30 min timeout for large PDFs
    print(f"  Import complete!")
    return result


if __name__ == '__main__':
    import sys
    
    target = sys.argv[1] if len(sys.argv) > 1 else 'all'
    
    if target in ('curriculum', 'all'):
        print("=" * 60)
        print("STEP 1: Uploading Curriculum .md files to GCS")
        print("=" * 60)
        n = upload_curriculum_to_gcs()
        print(f"\nUploaded {n} files.\n")
        
        print("=" * 60)
        print("STEP 2: Importing Curriculum into aviation-curriculum-v2")
        print("=" * 60)
        import_documents(
            'aviation-curriculum-v2',
            f'gs://{CURRICULUM_BUCKET}/v2/*',
        )
        print()
    
    if target in ('library', 'all'):
        print("=" * 60)
        print("STEP 3: Uploading Library PDFs to GCS")
        print("=" * 60)
        n = upload_library_to_gcs()
        print(f"\nUploaded {n} files.\n")
        
        print("=" * 60)
        print("STEP 4: Importing Library into aviation-library-v2")
        print("=" * 60)
        import_documents(
            'aviation-library-v2',
            f'gs://{LIBRARY_BUCKET}/v2/*',
        )
    
    print("\n=== ALL DONE ===")
