"""Permanent gate for story 6-3: balanced answer keys + letter-free feedback prose.

Two standing rules from _docs/SOP_curriculum_operations.md §6, enforced forever:
  1. Every bank's correct answers form the exact multiset {A,A,B,B,C,C,D,D} — no
     positional meaning (the 2026-07-22 audit found 67% "B"; the app does not shuffle
     options at render, so a skew is directly visible to students).
  2. Student-facing feedback prose (`explanation`, `sjt_rationale`) never references an
     option by letter — letter-anchored prose silently lies the moment options move.

Scales with the corpus: new banks are picked up by the glob and must pass from day one.
"""
import json
import re
from collections import Counter
from pathlib import Path

import pytest

QUIZ_DIR = Path(__file__).resolve().parents[2] / "curriculum_components" / "quiz_banks"
BANKS = sorted(QUIZ_DIR.glob("*_quiz.json"))
TARGET_MULTISET = ["A", "A", "B", "B", "C", "C", "D", "D"]

# Option-letter references in prose. Deliberately context-anchored: bare letters are
# everywhere in aviation prose ("Class B airspace", "A&P", "W&B", "HAVE A PLAN"), so
# every pattern requires an option-reference cue word or a parenthetical capital.
LETTER_REF = re.compile(
    r"\b[Oo]ptions?\s+[A-D]\b"
    r"|\b[Cc]hoices?\s+[A-D]\b"
    r"|\b[Aa]nswers?\s+[A-D]\b"
    r"|\(([A-D])\)"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_bytes().decode("utf-8"))


def test_corpus_present():
    assert BANKS, f"no quiz banks found under {QUIZ_DIR}"


@pytest.mark.parametrize("path", BANKS, ids=[p.stem for p in BANKS])
def test_bank_has_two_correct_answers_per_letter(path):
    bank = _load(path)
    assert len(bank["questions"]) == 8, f"{bank['lesson_id']}: {len(bank['questions'])} questions"
    letters = sorted(q["correct_answer"] for q in bank["questions"])
    assert letters == TARGET_MULTISET, (
        f"{bank['lesson_id']}: answer key {Counter(letters)} — every bank must be "
        f"exactly 2 per letter (SOP §6)"
    )


def test_corpus_distribution_is_uniform():
    counts = Counter(
        q["correct_answer"] for path in BANKS for q in _load(path)["questions"]
    )
    expected = {letter: 2 * len(BANKS) for letter in "ABCD"}
    assert dict(sorted(counts.items())) == expected


@pytest.mark.parametrize("path", BANKS, ids=[p.stem for p in BANKS])
def test_feedback_prose_is_letter_free(path):
    bank = _load(path)
    offenders = []
    for q in bank["questions"]:
        for field in ("explanation", "sjt_rationale"):
            text = q.get(field)
            if not text:
                continue
            hits = [m.group(0) for m in LETTER_REF.finditer(text)]
            if hits:
                offenders.append(f"{q['id']}.{field}: {hits[:4]}")
    assert not offenders, (
        "letter-anchored feedback prose (rewrite to reference option CONTENT — SOP §6):\n"
        + "\n".join(offenders)
    )
