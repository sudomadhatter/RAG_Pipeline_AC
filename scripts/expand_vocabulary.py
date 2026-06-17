import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure we can import our pipeline config
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
import config

try:
    from google.cloud import discoveryengine_v1 as discoveryengine
except ImportError:
    print("google-cloud-discoveryengine package not found. Install it with: pip install google-cloud-discoveryengine")
    sys.exit(1)

# Load env file for credentials
env_path = Path(__file__).parent.parent / "auth_keys" / ".env"
load_dotenv(dotenv_path=env_path)

def query_live_db2_tags():
    project_id = config.GCP_PROJECT_ID
    location = config.LIBRARY_LOCATION
    data_store_id = config.LIBRARY_DATA_STORE_ID
    
    # We must use credentials from the environment, using the standard pattern
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        cred_path = str(Path(__file__).parent.parent / "auth_keys" / "librarian-service-account.json")
        if Path(cred_path).exists():
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
        else:
            print(f"Warning: Could not find credentials at {cred_path}")
            
    print(f"Querying Discovery Engine: projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{data_store_id}")
    
    try:
        client = discoveryengine.DocumentServiceClient()
        parent = client.branch_path(
            project=project_id,
            location=location,
            data_store=data_store_id,
            branch="default_branch"
        )
        
        request = discoveryengine.ListDocumentsRequest(parent=parent, page_size=1000)
        
        all_tags = set()
        doc_count = 0
        
        for doc in client.list_documents(request=request):
            doc_count += 1
            if hasattr(doc, 'struct_data') and doc.struct_data:
                tags = doc.struct_data.get('document_tags', [])
                if hasattr(tags, 'list_value'):
                    # Depending on how the struct_data is represented 
                    for tag in tags.list_value.values:
                        all_tags.add(tag.string_value)
                elif isinstance(tags, list):
                    for tag in tags:
                        all_tags.add(tag)

        print(f"Scanned {doc_count} documents in DB2.")
        print(f"Found {len(all_tags)} unique document tags:")
        for tag in sorted(list(all_tags)):
            print(f"  '{tag}',")
            
        return all_tags

    except Exception as e:
        print(f"Error querying Discovery Engine: {e}")
        return set()

if __name__ == "__main__":
    query_live_db2_tags()
