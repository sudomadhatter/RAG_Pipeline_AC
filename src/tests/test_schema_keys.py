"""Unit tests for the bridge-key normalizer + matcher (utils.schema).

These verify the rules we CONTROL: corruption is stripped, real references are kept, garbage is
dropped, and family-matching connects curriculum editions to library editions. They do not call
the live stores.
"""
import pytest

from utils.schema import (
    normalize_key, is_garbage, is_document_level, to_family, coverage,
    CurriculumStructData,
)


@pytest.mark.parametrize("raw,expected", [
    ("** AC 61-98D (Currency & Flight Review)", "AC 61-98D"),
    ("FAA-H-8083-25C (PHAK)", "FAA-H-8083-25C"),
    ("AC 90-109A [cite: 1453]", "AC 90-109A"),
    ("14 CFR 91.103.", "14 CFR 91.103"),
    ("Chart Supplement U.S.", "Chart Supplement U.S."),   # initialism period preserved
    ("FAA P-8740-36", "FAA P-8740-36"),                    # non-DB2 reference kept verbatim
])
def test_normalize_strips_corruption_keeps_reference(raw, expected):
    assert normalize_key(raw) == expected


@pytest.mark.parametrize("raw", ["Ch 8", "Ch 9)", "Chapter 17", "N/A", "  ", "**"])
def test_garbage_detected(raw):
    assert is_garbage(normalize_key(raw))


@pytest.mark.parametrize("raw", ["AC 61-98D", "FAA-H-8083-25C", "AIM"])
def test_real_references_not_garbage(raw):
    assert not is_garbage(normalize_key(raw))


@pytest.mark.parametrize("raw,doc_level", [
    ("FAA-H-8083-25C", True),
    ("AC 61-98D", True),
    ("AIM", True),
    ("FAA-H-8083-3C Chapter 18", False),   # inline chapter -> sub-document
    ("AIM 8-1-5", False),                  # AIM section -> sub-document
    ("FAA-H-8083-25C (PHAK Ch 6)", True),  # closed annotation normalizes away -> document token
])
def test_document_level_filter(raw, doc_level):
    assert is_document_level(raw) is doc_level


@pytest.mark.parametrize("curriculum,library", [
    ("FAA-H-8083-25C", "FAA-H-8083-25"),   # edition-letter difference
    ("AC 61-98D", "AC 61-98E"),            # D vs E
    ("FAA-H-8083-2A", "FAA-H-8083-2"),
    ("14 CFR 61.56", "14 CFR 61"),         # section vs part
])
def test_family_match_across_editions(curriculum, library):
    assert to_family(curriculum) == to_family(library)


def test_coverage_splits_covered_and_reference_only():
    covered, ref = coverage(["FAA-H-8083-25C", "FCC Form 605"])
    assert "FAA-H-8083-25C" in covered      # PHAK family is in live DB2
    assert "FCC Form 605" in ref            # not in the library — kept as a reference


def test_structdata_cleans_on_construction():
    sd = CurriculumStructData(
        acs_code="PA.I.A.K1", title="t", type="lesson_chunk", ancestral_context="x",
        reg_keys=["** 14 CFR 61.56"], doc_keys=["** FAA-H-8083-25C (PHAK)", "Ch 8"],
        keywords=["** WINGS"],
    )
    assert sd.reg_keys == ["14 CFR 61.56"]
    assert sd.doc_keys == ["FAA-H-8083-25C"]      # corruption stripped, garmented "Ch 8" dropped
    assert sd.keywords == ["WINGS"]


def test_structdata_rejects_empty_doc_keys():
    with pytest.raises(Exception):
        CurriculumStructData(
            acs_code="x", title="t", type="lesson_chunk", ancestral_context="x",
            reg_keys=[], doc_keys=["N/A"], keywords=[],   # cleans to empty -> min_length=1 fails
        )
