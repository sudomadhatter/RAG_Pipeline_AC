import os
from pathlib import Path

# Base Paths (assuming running from c:\AGY-Projects\ingestion-Pipeline-AC)
PROJECT_ROOT = Path(os.getcwd())
PIPELINE_ROOT = PROJECT_ROOT / "pipeline"

# Set Google App Credentials
if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
    SA_PATH = PROJECT_ROOT / "auth_keys" / "service-account.json"
    if SA_PATH.exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(SA_PATH)
    else:
        print(f"Warning: Service Account key not found at {SA_PATH}")

# Curriculum Paths
CURRICULUM_ROOT = PIPELINE_ROOT / "curriculum"
CURRICULUM_NEW = CURRICULUM_ROOT / "new"
CURRICULUM_ACTIVE = CURRICULUM_ROOT / "active"
CURRICULUM_SUPERSEDED = CURRICULUM_ROOT / "superseded"
CURRICULUM_MANIFEST = CURRICULUM_ROOT / "manifest.json"

# Library Paths
LIBRARY_ROOT = PIPELINE_ROOT / "library"
LIBRARY_NEW = LIBRARY_ROOT / "new"
LIBRARY_ACTIVE = LIBRARY_ROOT / "active"
LIBRARY_SUPERSEDED = LIBRARY_ROOT / "superseded"
LIBRARY_MANIFEST = LIBRARY_ROOT / "manifest.json"

# GCP Settings
GCP_PROJECT_ID = "aviationchat"

# Curriculum GCP Targets
CURRICULUM_BUCKET = "aviationchat-curriculum-cms"
CURRICULUM_DATA_STORE_ID = "aviation-curriculum-v1"
CURRICULUM_LOCATION = "global"

# Library GCP Targets
LIBRARY_BUCKET = "aviationchat-library"
LIBRARY_DATA_STORE_ID = "aviation-library-v1"
LIBRARY_LOCATION = "global"

# Vertex AI Search Output Manifest Names
CURRICULUM_JSONL_FILE = "curriculum.jsonl"
LIBRARY_JSONL_FILE = "library_metadata.jsonl"
