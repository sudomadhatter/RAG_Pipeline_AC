"""
Create V2 Data Stores with Layout-Aware Chunking
Replaces the v1 stores that use basic digitalParsingConfig.
"""
import sys
from pathlib import Path

# Resolve GCP credentials the same way every other pipeline script does — via auth_keys/.env +
# service-account.json — instead of a machine-specific hardcoded path (credential-resolution rule).
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402 — importing config sets GOOGLE_APPLICATION_CREDENTIALS

from google.cloud import discoveryengine_v1 as discoveryengine
from google.protobuf.json_format import MessageToDict
import json, sys

PROJECT_ID = config.GCP_PROJECT_ID
LOCATION = config.CURRICULUM_LOCATION

def create_data_store(store_id: str, display_name: str, chunk_size: int):
    """Create a new data store with layout parsing and chunking enabled."""
    
    client = discoveryengine.DataStoreServiceClient()
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection"
    
    data_store = discoveryengine.DataStore(
        display_name=display_name,
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
        content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
        document_processing_config=discoveryengine.DocumentProcessingConfig(
            default_parsing_config=discoveryengine.DocumentProcessingConfig.ParsingConfig(
                layout_parsing_config=discoveryengine.DocumentProcessingConfig.ParsingConfig.LayoutParsingConfig()
            ),
            chunking_config=discoveryengine.DocumentProcessingConfig.ChunkingConfig(
                layout_based_chunking_config=discoveryengine.DocumentProcessingConfig.ChunkingConfig.LayoutBasedChunkingConfig(
                    chunk_size=chunk_size,
                    include_ancestor_headings=True,
                )
            ),
        ),
    )
    
    print(f"Creating data store '{store_id}' with layout parsing, chunk_size={chunk_size}...")
    
    operation = client.create_data_store(
        parent=parent,
        data_store=data_store,
        data_store_id=store_id,
    )
    
    print(f"Waiting for operation to complete...")
    result = operation.result(timeout=120)
    result_dict = MessageToDict(result._pb)
    print(f"Created: {json.dumps(result_dict, indent=2)}")
    return result


if __name__ == "__main__":
    # Step 1: Create curriculum v2 (500 token chunks for lesson content)
    try:
        create_data_store(
            store_id='aviation-curriculum-v2',
            display_name='Aviation Curriculum V2',
            chunk_size=500,
        )
    except Exception as e:
        if 'ALREADY_EXISTS' in str(e):
            print("aviation-curriculum-v2 already exists, skipping.")
        else:
            print(f"Error creating curriculum v2: {e}")
            sys.exit(1)
    
    print()
    
    # Step 2: Create library v2 (1024 token chunks for reference PDFs)
    try:
        create_data_store(
            store_id='aviation-library-v2',
            display_name='Aviation Library V2',
            chunk_size=1024,
        )
    except Exception as e:
        if 'ALREADY_EXISTS' in str(e):
            print("aviation-library-v2 already exists, skipping.")
        else:
            print(f"Error creating library v2: {e}")
            sys.exit(1)
    
    print("\nDone! Both v2 data stores created.")
