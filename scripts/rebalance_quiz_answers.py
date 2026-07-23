"""Re-letter quiz-bank answer keys to a uniform distribution (board story 6-3, phase R2).

Per bank of 8 questions the correct answers land on the exact multiset {A,A,B,B,C,C,D,D},
so the 48-bank corpus totals 96 per letter. Deterministic: each bank is seeded with its
lesson_id, so re-runs (any machine) produce byte-identical output.

Mechanics — pure position work, zero prose edits:
  * Option OBJECTS move between labels (text + hazardous_attitude travel together);
    the label sequence stays A->D.
  * Position-locked option texts ("... of the above") are PINNED at their original letter;
    a question whose pinned option is not the correct answer gets a target letter that
    avoids the pinned slot.
  * `correct_answer` is rewritten to the letter where the correct TEXT landed.
  * `explanation` / `sjt_rationale` / question `text` / ids / references are untouched
    (phase R3 owns prose).

Safety: before writing anything, every bank must round-trip (parse -> serialize) to the
exact original bytes, proving the writer is format-faithful; after permuting, per-bank and
corpus invariants are hard-asserted. Default run is a DRY RUN (prints the letter table);
pass --execute to write the files.
"""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
QUIZ_DIR = REPO_ROOT / "curriculum_components" / "quiz_banks"
LETTERS = ["A", "B", "C", "D"]
TARGET_MULTISET = ["A", "A", "B", "B", "C", "C", "D", "D"]
SEED_PREFIX = "6-3:"  # story tag; changing it would change every permutation

# Texts that carry positional meaning and must not move ("None of the above" only makes
# sense as the last option). Deliberately narrow: aviation prose is full of standalone
# letters ("Class B airspace"), so we match the phrase, never letters.
PIN_RE = re.compile(r"(?i)\b(?:all|none|both|neither) of the above\b")


def load_banks() -> list[tuple[Path, str, dict, str]]:
    """Returns (path, raw_text, parsed, tail) — `tail` preserves the per-file
    trailing-newline convention (14 banks end with CRLF, 34 end without)."""
    banks = []
    for path in sorted(QUIZ_DIR.glob("*_quiz.json")):
        raw = path.read_bytes().decode("utf-8")
        tail = "\r\n" if raw.endswith("\r\n") else ""
        banks.append((path, raw, json.loads(raw), tail))
    return banks


def jdump(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def serialize_bank(bank: dict) -> str:
    """Emit the house format exactly: CRLF, 2-space indent, one-line option objects,
    no trailing newline."""
    lines = ["{"]
    lines.append(f'  "lesson_id": {jdump(bank["lesson_id"])},')
    lines.append(f'  "title": {jdump(bank["title"])},')
    lines.append('  "questions": [')
    questions = bank["questions"]
    for qi, q in enumerate(questions):
        lines.append("    {")
        keys = list(q.keys())
        for ki, key in enumerate(keys):
            comma = "," if ki < len(keys) - 1 else ""
            if key == "options":
                lines.append('      "options": [')
                opts = q["options"]
                for oi, opt in enumerate(opts):
                    inner = ", ".join(f"{jdump(k)}: {jdump(v)}" for k, v in opt.items())
                    lines.append(
                        "        {" + inner + "}" + ("," if oi < len(opts) - 1 else "")
                    )
                lines.append("      ]" + comma)
            else:
                lines.append(f"      {jdump(key)}: {jdump(q[key])}{comma}")
        lines.append("    }" + ("," if qi < len(questions) - 1 else ""))
    lines.append("  ]")
    lines.append("}")
    return "\r\n".join(lines)


def find_pins(question: dict) -> list[str]:
    return [o["label"] for o in question["options"] if PIN_RE.search(o["text"])]


def assign_targets(bank: dict, rng: random.Random) -> list[str]:
    """One target letter per question; multiset {A,A,B,B,C,C,D,D}; pinned-correct
    questions keep their letter, pinned-incorrect questions avoid the pinned slot."""
    questions = bank["questions"]
    if len(questions) != len(TARGET_MULTISET):
        raise SystemExit(
            f"{bank['lesson_id']}: {len(questions)} questions, expected {len(TARGET_MULTISET)}"
        )
    targets: list[str | None] = [None] * len(questions)
    pool = list(TARGET_MULTISET)
    forbidden: dict[int, set[str]] = {}

    for i, q in enumerate(questions):
        pins = find_pins(q)
        if not pins:
            continue
        if q["correct_answer"] in pins:
            targets[i] = q["correct_answer"]  # pinned AND correct: letter frozen
            pool.remove(q["correct_answer"])
        else:
            forbidden[i] = set(pins)  # correct text may not land on a pinned slot

    open_idx = [i for i in range(len(questions)) if targets[i] is None]
    for attempt in range(10_000):
        rng.shuffle(pool)
        trial = dict(zip(open_idx, pool))
        if all(trial[i] not in forbidden.get(i, ()) for i in open_idx):
            for i in open_idx:
                targets[i] = trial[i]
            return targets  # type: ignore[return-value]
    raise SystemExit(f"{bank['lesson_id']}: no valid target assignment found")


def permute_question(q: dict, target: str, rng: random.Random) -> None:
    old_by_label = {o["label"]: o for o in q["options"]}
    if set(old_by_label) != set(LETTERS):
        raise SystemExit(f"{q['id']}: labels are {sorted(old_by_label)}, expected A-D")
    correct_obj = old_by_label[q["correct_answer"]]
    placed: dict[str, dict] = {}
    for label in find_pins(q):
        placed[label] = old_by_label[label]
    if correct_obj in placed.values():
        if placed.get(target) is not correct_obj:
            raise SystemExit(f"{q['id']}: pinned correct option vs target {target}")
    else:
        if target in placed:
            raise SystemExit(f"{q['id']}: target {target} collides with a pinned option")
        placed[target] = correct_obj
    movable = [o for o in q["options"] if o not in placed.values()]
    rng.shuffle(movable)
    free_labels = [l for l in LETTERS if l not in placed]
    for label, obj in zip(free_labels, movable):
        placed[label] = obj
    q["options"] = [
        {"label": label, **{k: v for k, v in placed[label].items() if k != "label"}}
        for label in LETTERS
    ]
    q["correct_answer"] = target


def verify_bank(original: dict, rebalanced: dict) -> None:
    counts = Counter(q["correct_answer"] for q in rebalanced["questions"])
    if sorted(counts.elements()) != TARGET_MULTISET:
        raise SystemExit(f"{rebalanced['lesson_id']}: letter histogram {dict(counts)}")
    for oq, nq in zip(original["questions"], rebalanced["questions"]):
        old_correct_text = next(
            o["text"] for o in oq["options"] if o["label"] == oq["correct_answer"]
        )
        new_correct_text = next(
            o["text"] for o in nq["options"] if o["label"] == nq["correct_answer"]
        )
        if old_correct_text != new_correct_text:
            raise SystemExit(f"{nq['id']}: correct TEXT changed — abort")
        strip = lambda opts: sorted(  # noqa: E731
            json.dumps({k: v for k, v in o.items() if k != "label"}, sort_keys=True)
            for o in opts
        )
        if strip(oq["options"]) != strip(nq["options"]):
            raise SystemExit(f"{nq['id']}: option payloads changed — abort")
        for label in find_pins(oq):
            pinned_text = next(o["text"] for o in oq["options"] if o["label"] == label)
            now_there = next(o["text"] for o in nq["options"] if o["label"] == label)
            if pinned_text != now_there:
                raise SystemExit(f"{nq['id']}: pinned option moved off {label} — abort")
        for key in oq:
            if key in ("options", "correct_answer"):
                continue
            if oq[key] != nq[key]:
                raise SystemExit(f"{nq['id']}: field {key!r} changed — abort")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--execute", action="store_true", help="write files (default: dry run)")
    args = parser.parse_args()

    banks = load_banks()
    if len(banks) != 48:
        raise SystemExit(f"expected 48 banks, found {len(banks)}")

    format_failures = [
        p.name for p, raw, data, tail in banks if serialize_bank(data) + tail != raw
    ]
    if format_failures:
        raise SystemExit(
            "serializer is not format-faithful for: " + ", ".join(format_failures)
        )
    print(f"[format] 48/48 banks round-trip byte-identical — writer is faithful\n")

    before = Counter()
    after = Counter()
    moved = stayed = 0
    for path, _raw, bank, tail in banks:
        original = json.loads(json.dumps(bank))
        rng = random.Random(SEED_PREFIX + bank["lesson_id"])
        targets = assign_targets(bank, rng)
        row = []
        for q, target in zip(bank["questions"], targets):
            before[q["correct_answer"]] += 1
            row.append(f"{q['id'].rsplit('_', 1)[1]} {q['correct_answer']}->{target}")
            if q["correct_answer"] == target:
                stayed += 1
            else:
                moved += 1
            permute_question(q, target, rng)
            after[q["correct_answer"]] += 1
        verify_bank(original, bank)
        pins = [
            f"{q['id'].rsplit('_', 1)[1]}:{','.join(find_pins(q))}"
            for q in bank["questions"]
            if find_pins(q)
        ]
        pin_note = f"  [pinned {' '.join(pins)}]" if pins else ""
        print(f"{bank['lesson_id']}:  {'  '.join(row)}{pin_note}")
        if args.execute:
            path.write_bytes((serialize_bank(bank) + tail).encode("utf-8"))

    print(f"\n[before] {dict(sorted(before.items()))}")
    print(f"[after]  {dict(sorted(after.items()))}")
    print(f"[moved]  {moved} question keys re-lettered, {stayed} already on target")
    if sorted(after.elements()) != sorted(TARGET_MULTISET * 48):
        raise SystemExit("corpus histogram is not 96/96/96/96 — abort")
    print("[verify] every bank exactly 2 per letter · corpus 96/96/96/96 · texts intact")
    print("MODE: " + ("EXECUTED — files rewritten" if args.execute else "dry run, nothing written"))


if __name__ == "__main__":
    main()
