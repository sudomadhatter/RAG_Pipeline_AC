"""Single source of truth for DB2 `document_tags`.

Both the vocabulary deriver (`scripts/derive_db2_vocabulary.py`) and the DB2 importer
(`src/gcp/import_db2_docs.py`) call `extract_tags` so the tag a document is BORN with is
exactly the token the vocabulary expects. The DB1/RKP side matches these at family level
via `utils.schema.to_family`.
"""
import re
from typing import List


def extract_tags(filename: str) -> List[str]:
    """Derive document-tag tokens from a library PDF filename.

    Mirrors (and extends) the app-repo `scripts/patch_db2_metadata.py::extract_tags`. The
    extension is the ACS pattern (`FAA-S-ACS-6C`), which the original lacked — without it the
    Private Pilot ACS would import untagged.
    """
    tags: List[str] = []
    text = filename.replace(".pdf", "")

    ac_match = re.search(r"AC[_\s]?(\d+[A-Z]?-\d+[A-Z]?)", text)
    if ac_match:
        tags.append(f"AC {ac_match.group(1)}")

    acs_match = re.search(r"(FAA-S-ACS-\d+[A-Z]?)", text)
    if acs_match:
        tags.append(acs_match.group(1))

    faa_match = re.search(r"(FAA-[A-Z]-\d+(?:-\d+[A-Z]?)?)", text)
    if faa_match and faa_match.group(1) not in tags:
        tags.append(faa_match.group(1))

    cfr_match = re.search(r"14[\s_]*CFR[\s_]*part[\s_]*(\d+)", text, re.IGNORECASE)
    if cfr_match:
        tags.append(f"14 CFR {cfr_match.group(1)}")

    if "AIM" in text or "Aeronautical Information Manual" in text:
        tags.append("AIM")

    return tags
