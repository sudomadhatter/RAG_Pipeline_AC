import os
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.operation import Operation

def import_documents_to_vertex(
    project_id: str,
    location: str,
    data_store_id: str,
    gcs_uri: str
) -> Operation:
    """
    Triggers a Discovery Engine (Vertex AI Search) import documents job.
    
    Args:
        project_id: GCP Project ID
        location: e.g., 'global'
        data_store_id: The Target DB Collection (e.g., 'aviation-curriculum-v1')
        gcs_uri: A Google Cloud Storage URI to the input JSONL file (e.g., 'gs://bucket/path/data.jsonl')
        
    Returns:
        The LRO (Long Running Operation) object to await for completion.
    """
    client = discoveryengine.DocumentServiceClient()

    # The full resource name of the search data store branch.
    # We default to the 'default_branch' (0) which is what normal data stores use.
    parent = client.branch_path(
        project=project_id,
        location=location,
        data_store=data_store_id,
        branch="default_branch",
    )

    request = discoveryengine.ImportDocumentsRequest(
        parent=parent,
        gcs_source=discoveryengine.GcsSource(
            input_uris=[gcs_uri],
            data_schema="custom"  # Denotes unstructured with custom structData metadata
        ),
        # Treat duplicate IDs as updates (overwrite the old document)
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL
    )

    print(f"Triggering Vertex AI Search Import to {data_store_id}...")
    try:
        operation = client.import_documents(request=request)
        print("Waiting for Vertex AI Search import to complete. This may take several minutes...")
        
        # Block until completion
        response = operation.result()
        print(f" Import Successful! Metadata: {operation.metadata}")
        return response
    except Exception as e:
        print(f" Vertex AI Import Failed: {e}")
        raise e
