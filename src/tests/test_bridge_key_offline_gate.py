"""Offline gate over the built DB1 import manifest (pipeline/curriculum/curriculum.jsonl).

This is the test that would have caught the original silent-empty-keys bug: it asserts every
one of the 184 entries validates, has non-empty document-level doc_keys, and carries no residual
corruption. Run `python src/gcp/reimport_db1_keys.py` (dry run) first to produce the JSONL.
"""
import json
from pathlib import Path

import pytest

from utils.schema import CurriculumLessonSchema, is_document_level, normalize_key

JSONL = Path(__file__).resolve().parents[2] / "pipeline" / "curriculum" / "curriculum.jsonl"

pytestmark = pytest.mark.skipif(
    not JSONL.exists(),
    reason="curriculum.jsonl not built yet — run src/gcp/reimport_db1_keys.py first",
)


def _entries():
    return [json.loads(line) for line in JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_all_entries_validate():
    bad = []
    for e in _entries():
        try:
            CurriculumLessonSchema(id=e["id"], structData=e["structData"])
        except Exception as ex:  # noqa: BLE001
            bad.append((e.get("id"), str(ex)))
    assert not bad, f"{len(bad)} entries failed schema: {bad[:5]}"


def test_expected_count():
    assert len(_entries()) == 184


def test_no_empty_doc_keys():
    empty = [e["id"] for e in _entries() if not e["structData"]["doc_keys"]]
    assert not empty, f"{len(empty)} lessons with empty doc_keys: {empty}"


def test_no_residual_corruption():
    dirty = []
    for e in _entries():
        for k in e["structData"]["doc_keys"]:
            if k.startswith("*") or "[cite:" in k or normalize_key(k) != k:
                dirty.append((e["id"], k))
    assert not dirty, f"{len(dirty)} keys still corrupted: {dirty[:5]}"


def test_every_lesson_has_a_document_level_key():
    """Each lesson must carry at least one document-level doc_key (a real bridge candidate),
    even if some keys are finer-grained references."""
    missing = [e["id"] for e in _entries()
               if not any(is_document_level(k) for k in e["structData"]["doc_keys"])]
    assert not missing, f"{len(missing)} lessons have only sub-document keys: {missing}"
