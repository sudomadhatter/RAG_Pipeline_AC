import os
from pathlib import Path
from google.cloud import storage
from google.api_core.exceptions import GoogleAPIError

def upload_to_gcs(
    local_path: Path, 
    bucket_name: str, 
    destination_blob_name: str, 
    project_id: str
) -> str:
    """
    Uploads a local file to a Google Cloud Storage bucket.
    Returns the GS URI (e.g., gs://bucket/path/file.txt).
    """
    try:
        client = storage.Client(project=project_id)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        
        blob.upload_from_filename(str(local_path))
        print(f" Uploaded {local_path.name} to gs://{bucket_name}/{destination_blob_name}")
        
        return f"gs://{bucket_name}/{destination_blob_name}"
    
    except GoogleAPIError as e:
        print(f" GCP Upload Failed for {local_path.name}: {e}")
        raise e
    except Exception as e:
        print(f" Unexpected Error during upload for {local_path.name}: {e}")
        raise e
