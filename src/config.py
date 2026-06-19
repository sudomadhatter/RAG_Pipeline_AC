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

# Curriculum filesystem layout — the DB1 source store under pipeline/curriculum/.
#   elements/        — split-lesson .md (DB1 content); one .md per live DB1 doc
#   sidecars/        — locally-authored *.json metadata sidecars (Area IX; the rest of the
#                      lessons carry their metadata in the live store + the built manifest)
#   new/             — authoring inbox: generate_metadata.py / fallback_generator2.py write here
#   curriculum.jsonl — GENERATED DB1 import manifest (rebuilt by src/gcp/reimport_db1_keys.py)
CURRICULUM_ROOT = PIPELINE_ROOT / "curriculum"
CURRICULUM_NEW = CURRICULUM_ROOT / "new"
CURRICULUM_ELEMENTS = CURRICULUM_ROOT / "elements"
CURRICULUM_SIDECARS = CURRICULUM_ROOT / "sidecars"
CURRICULUM_JSONL_FILE = "curriculum.jsonl"
CURRICULUM_JSONL = CURRICULUM_ROOT / CURRICULUM_JSONL_FILE

# Authored-asset layout under curriculum_components/ — the human/CFI-authored source assets the
# ingestion scripts read FROM (distinct from the DB1 source store above). Centralized here so a
# path only ever changes in one place, mirroring the CURRICULUM_* constants.
#   curriculum_modules/ — CFI master modules (.md), split into curriculum/elements/
#   rkp_manifests/      — RKP manifest JSON  → Firestore rkp_manifests (upload_manifests.py)
#   quiz_banks/         — quiz bank JSON     → Firestore quiz_banks   (ingest_quiz_banks.py)
#   faa_docs/           — FAA source PDFs    → DB2                    (import_db2_docs.py)
#   lesson_podcasts/    — authored podcast .md (not currently ingested by any script)
COMPONENTS_ROOT = PROJECT_ROOT / "curriculum_components"
MODULES_DIR = COMPONENTS_ROOT / "curriculum_modules"
RKP_MANIFESTS_DIR = COMPONENTS_ROOT / "rkp_manifests"
QUIZ_BANKS_DIR = COMPONENTS_ROOT / "quiz_banks"
FAA_DOCS_DIR = COMPONENTS_ROOT / "faa_docs"
PODCASTS_DIR = COMPONENTS_ROOT / "lesson_podcasts"

# GCP Settings
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "aviationchat")

# Curriculum (DB1) GCP targets — datastore ID/location come from .env (single source of truth),
# defaulting to the live store names verified against the GCP project (aviation-*-v2).
CURRICULUM_BUCKET = "aviationchat-curriculum-cms"
CURRICULUM_DATA_STORE_ID = os.getenv("VERTEX_SEARCH_DB1_ID", "aviation-curriculum-v2")
CURRICULUM_LOCATION = os.getenv("VERTEX_SEARCH_LOCATION", "global")

# Library (DB2) GCP targets — the FAA PDF store, built by src/gcp/import_db2_docs.py.
LIBRARY_BUCKET = "aviationchat-library"
LIBRARY_DATA_STORE_ID = os.getenv("VERTEX_SEARCH_DB2_ID", "aviation-library-v2")
LIBRARY_LOCATION = os.getenv("VERTEX_SEARCH_LOCATION", "global")
