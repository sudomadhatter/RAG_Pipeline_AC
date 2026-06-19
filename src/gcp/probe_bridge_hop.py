"""Prove the DB1->DB2 bridge end to end, the way the app does it.

For each RKP manifest, take its document-level bridge_keys, build the SAME strict filter the app
uses (`document_tags: ANY(...)`), search DB2, and assert >=1 hit. This is a live READ (safe to run
anytime) but only returns hits AFTER `import_db2_docs.py --execute` has applied document_tags — so
run it as the post-import proof. Before that, every lesson returns 0 (the honest "bridge dead" state).
"""
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402
from utils.schema import to_document_level, is_garbage, normalize_key  # noqa: E402

from google.cloud import discoveryengine_v1 as discoveryengine  # noqa: E402

MANIFESTS = config.RKP_MANIFESTS_DIR


def serving_config(client):
    return (f"projects/{config.GCP_PROJECT_ID}/locations/{config.LIBRARY_LOCATION}"
            f"/collections/default_collection/dataStores/{config.LIBRARY_DATA_STORE_ID}"
            f"/servingConfigs/default_search")


def manifest_keys(data) -> list[str]:
    keys = []
    for r in data.get("required_knowledge_points", []):
        for k in (r.get("bridge_keys") or []):
            nk = normalize_key(k)
            if not is_garbage(nk):
                dl = to_document_level(nk)
                if dl not in keys:
                    keys.append(dl)
    return keys


def main(limit=None):
    client = discoveryengine.SearchServiceClient()
    sc = serving_config(client)
    files = sorted(MANIFESTS.glob("*_rkp.json"))
    if limit:
        files = files[:limit]

    hit_lessons = 0
    zero = []
    for fp in files:
        data = json.loads(fp.read_text(encoding="utf-8"))
        lesson = data.get("lesson_id", fp.stem)
        keys = manifest_keys(data)
        if not keys:
            zero.append((lesson, "no bridge_keys"))
            continue
        quoted = ", ".join(f'"{k}"' for k in keys)
        req = discoveryengine.SearchRequest(
            serving_config=sc, query=data.get("title", lesson),
            filter=f"document_tags: ANY({quoted})", page_size=5,
        )
        try:
            resp = client.search(req)
            n = sum(1 for _ in resp.results)
        except Exception as e:  # noqa: BLE001
            zero.append((lesson, f"error: {e}"))
            continue
        if n >= 1:
            hit_lessons += 1
            print(f"  [HIT {n}] {lesson:18s} keys={keys}")
        else:
            zero.append((lesson, f"0 hits for {keys}"))

    print(f"\n{hit_lessons}/{len(files)} lessons returned >=1 DB2 bridge hit.")
    if zero:
        print(f"{len(zero)} with no hit:")
        for lesson, why in zero:
            print(f"    {lesson}: {why}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Live DB1->DB2 bridge round-trip probe (read-only).")
    ap.add_argument("--limit", type=int, default=None, help="probe only the first N manifests")
    main(ap.parse_args().limit)
