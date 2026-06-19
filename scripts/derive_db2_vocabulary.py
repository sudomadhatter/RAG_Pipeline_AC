"""
Derive the DB2 tag vocabulary from the LIVE aviation-library-v2 store.

The vocabulary is NOT hand-authored — it is the exact set of tokens that the app's
`patch_db2_metadata.py` would write as `document_tags`, computed from each DB2 document's
filename. Run this after any DB2 change and paste the output into `src/utils/schema.py`.

Read-only. Requires GOOGLE_APPLICATION_CREDENTIALS (or auth_keys/service-account.json).
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
import config  # noqa: E402  (sets GOOGLE_APPLICATION_CREDENTIALS, datastore IDs)
from utils.db2_tags import extract_tags  # noqa: E402  (single source of truth for tags)

try:
    from google.cloud import discoveryengine_v1 as discoveryengine
    from google.protobuf.json_format import MessageToDict
except ImportError:
    print("google-cloud-discoveryengine not installed.")
    sys.exit(1)


def derive() -> set[str]:
    client = discoveryengine.DocumentServiceClient()
    parent = client.branch_path(
        project=config.GCP_PROJECT_ID,
        location=config.LIBRARY_LOCATION,
        data_store=config.LIBRARY_DATA_STORE_ID,
        branch="default_branch",
    )
    vocab: set[str] = set()
    doc_count = 0
    untagged: list[str] = []
    for doc in client.list_documents(request=discoveryengine.ListDocumentsRequest(parent=parent, page_size=1000)):
        doc_count += 1
        sd = MessageToDict(doc._pb.struct_data) if doc._pb.struct_data else {}
        filename = sd.get("filename") or sd.get("title") or ""
        tags = extract_tags(filename)
        if tags:
            vocab.update(tags)
        else:
            untagged.append(filename)

    print(f"Scanned {doc_count} documents in {config.LIBRARY_DATA_STORE_ID}.")
    print(f"Derived {len(vocab)} vocabulary tokens:")
    for t in sorted(vocab):
        print(f"    '{t}',")
    if untagged:
        print(f"\nWARNING: {len(untagged)} documents produced NO tag (filename pattern unmatched):")
        for f in untagged:
            print(f"    {f!r}")
    return vocab


if __name__ == "__main__":
    derive()
