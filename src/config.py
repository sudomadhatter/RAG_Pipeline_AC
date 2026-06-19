import os
from pathlib import Path
from dotenv import load_dotenv

# Repo root resolved from THIS file — never depends on the current working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PIPELINE_ROOT = PROJECT_ROOT / "pipeline"

# Load the real .env (datastore IDs + credentials) here, so config is self-contained
# regardless of which script imports it first. Does not override vars already in the environment.
load_dotenv(dotenv_path=PROJECT_ROOT / "auth_keys" / ".env")

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
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "aviationchat")

# Curriculum GCP Targets — datastore ID/location come from .env (single source of truth),
# defaulting to the live store names verified against the GCP project (aviation-*-v2).
CURRICULUM_BUCKET = "aviationchat-curriculum-cms"
CURRICULUM_DATA_STORE_ID = os.getenv("VERTEX_SEARCH_DB1_ID", "aviation-curriculum-v2")
CURRICULUM_LOCATION = os.getenv("VERTEX_SEARCH_LOCATION", "global")

# Library GCP Targets
LIBRARY_BUCKET = "aviationchat-library"
LIBRARY_DATA_STORE_ID = os.getenv("VERTEX_SEARCH_DB2_ID", "aviation-library-v2")
LIBRARY_LOCATION = os.getenv("VERTEX_SEARCH_LOCATION", "global")

# Vertex AI Search Output Manifest Names
CURRICULUM_JSONL_FILE = "curriculum.jsonl"
LIBRARY_JSONL_FILE = "library_metadata.jsonl"
