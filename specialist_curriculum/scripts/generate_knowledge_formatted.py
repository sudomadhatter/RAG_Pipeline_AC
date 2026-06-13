"""
Generate knowledge_formatted — Pedagogically Optimized Markdown for Flashcard UI

Reads RKP manifest JSON, sends each knowledge point to Gemini Pro
to reformat plain text into exam-ready study Markdown (bullet points,
bold key terms, sub-headings per sub-topic). The original 'knowledge'
field is NEVER modified — only 'knowledge_formatted' is written.

SAFETY: Default processes ONLY PPL_PA_I_A_01_rkp.json.
Pass --all to process all 34 files. Pass --write to save to disk.

Usage:
    python generate_knowledge_formatted.py              # single file, dry run
    python generate_knowledge_formatted.py --write      # single file, save
    python generate_knowledge_formatted.py --all --write  # all 34 files, save
"""

import json
import sys
import os
import time
from pathlib import Path

try:
    from google import genai
except ImportError:
    print("ERROR: google-genai not installed. Run: pip install google-genai")
    sys.exit(1)

# ── Configuration ──
MANIFESTS_DIR = Path(__file__).parent.parent / "rkp_manifests"
MODEL_ID = "gemini-2.5-pro"

SYSTEM_PROMPT = """You are an expert FAA Private Pilot examiner and aviation ground school instructor. Your job is to reformat a raw knowledge paragraph from a Private Pilot License (PPL) curriculum into a clean, exam-ready study card for a student pilot.

## YOUR MISSION
Rewrite the given knowledge text as a concise, well-structured Markdown study card that a student can flip over on a flashcard and instantly verify against their recalled answer. It must be test-focused, precise, and pedagogically sound.

## STRICT RULES

### Structure
1. Use bullet points (- ) as the primary format — ONE testable fact per bullet
2. Use sub-headings (### ) ONLY when the text covers 3 or more clearly distinct sub-topics (e.g., "Third-Class Medical" vs "BasicMed" vs "Restrictions")
3. Keep sub-headings extremely short (2-4 words max): ### Third-Class, ### BasicMed, ### Restrictions
4. Do NOT nest bullets more than one level deep — keep it flat and scannable

### Content Rules
5. **Bold** every key term, regulation number, specific limit, and number on first use (e.g., **14 CFR 61.57**, **3 takeoffs and landings**, **90 days**, **BasicMed**)
6. Every specific number, duration, limit, or threshold MUST appear as a standalone bullet or be clearly bolded in its bullet
7. FAR references MUST be bolded every time they appear (e.g., **14 CFR 61.113**)
8. PRESERVE ALL factual content — do NOT add, remove, hallucinate, or rephrase facts
9. Do NOT copy the phrasing "the student must" or "the pilot must" — state the rule directly

### Length & Completeness
10. Output must be COMPLETE — never truncate mid-sentence or mid-list
11. Aim for 6-12 bullets for a normal RKP, or 3-5 bullets per sub-section if using headings
12. Maximum output: 400 words. If content exceeds this, distill the most testable facts

### Output Format
13. Output ONLY the formatted Markdown — no code fences, no preamble, no "Here is..." commentary
14. Do NOT add an introduction line, a summary line, or any conversational text

## QUALITY BENCHMARK
A well-formatted card looks like this:

Input: "A private pilot must hold a valid pilot certificate, a current medical or BasicMed, and a government-issued photo ID. To carry passengers, pilots need 3 takeoffs and landings within 90 days in the same category, class, and type (full stop at night). A flight review is required every 24 calendar months."

Output:
### Documents Required
- **Valid pilot certificate**
- **Current medical certificate** or **BasicMed** qualification
- **Government-issued photo ID**

### Passenger Currency (14 CFR 61.57)
- **3 takeoffs and landings** within the preceding **90 days**
- Must be in the **same category, class, and type** of aircraft
- At night: landings must be **full stop** (no touch-and-goes)

### Flight Review
- Required every **24 calendar months** (**14 CFR 61.56**)
"""


def format_knowledge(client: genai.Client, knowledge_text: str, title: str, why: str) -> str:
    """Send a single knowledge point to Gemini for Markdown formatting."""
    prompt = f"""RKP Title: {title}
Why This Matters: {why}

Raw Knowledge Text:
{knowledge_text}

Reformat this into a study-optimized Markdown flashcard back following the system instructions exactly. Be complete — do not truncate."""

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.05,
            max_output_tokens=2048,
        ),
    )
    return response.text.strip()


def process_manifest(client: genai.Client, filepath: Path, dry_run: bool = True) -> dict:
    """Process a single RKP manifest file."""
    print(f"\n{'='*60}")
    print(f"Processing: {filepath.name}")
    print(f"{'='*60}")

    with open(filepath, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # ── Auto-Hydrate Media Files ──
    import re
    match = re.match(r'^(PPL_PA_[IVXLCDM]+_[A-Z]+)', manifest.get("lesson_id", ""))
    if match:
        task_prefix = match.group(1)
        manifest["audio_file"] = f"{task_prefix}_audio.m4a"
        manifest["video_file"] = f"{task_prefix}_video.mp4"
        print(f"  [Media] {manifest['audio_file']} / {manifest['video_file']}")

    for i, rkp in enumerate(manifest["required_knowledge_points"]):
        title = rkp["title"]
        why = rkp.get("why", "")
        knowledge = rkp["knowledge"]

        print(f"\n  -- RKP {rkp['id']}: {title} --")
        print(f"  Source ({len(knowledge)} chars): {knowledge[:80]}...")

        formatted = format_knowledge(client, knowledge, title, why)
        rkp["knowledge_formatted"] = formatted

        # Validate — warn if output looks truncated
        last_char = formatted.rstrip()[-1] if formatted.strip() else ""
        if last_char not in [".", ")", "]", "*", "_", "k", "s", "d", "e", "t", "n", "g", "y", "l", "r"]:
            print(f"  [WARN] Output may be truncated (ends: ...{formatted[-30:]!r})")

        print(f"  Formatted ({len(formatted)} chars):")
        for line in formatted.split("\n")[:8]:  # Preview first 8 lines
            print(f"    {line}")
        if len(formatted.split("\n")) > 8:
            print(f"    ... ({len(formatted.split(chr(10)))-8} more lines)")

        # Rate limiting — be gentle with the API
        if i < len(manifest["required_knowledge_points"]) - 1:
            time.sleep(0.75)

    if not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f"\n  [SAVED] {filepath.name}")
    else:
        print(f"\n  [DRY RUN] Review output above — no file written.")

    return manifest


def main():
    # Load .env from auth_keys directory
    env_path = Path(__file__).parent.parent.parent / "auth_keys" / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())

    # Check for API key
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    run_all = "--all" in sys.argv
    write = "--write" in sys.argv

    if run_all:
        files = sorted(MANIFESTS_DIR.glob("*_rkp.json"))
        print(f"Processing ALL {len(files)} manifest files with {MODEL_ID}")
    else:
        target = MANIFESTS_DIR / "PPL_PA_I_A_01_rkp.json"
        if not target.exists():
            print(f"ERROR: {target} not found")
            sys.exit(1)
        files = [target]
        print(f"Processing SINGLE file: {target.name}")

    if not write:
        print("DRY RUN mode — pass --write to save changes")

    for filepath in files:
        process_manifest(client, filepath, dry_run=not write)
        if len(files) > 1:
            time.sleep(1.5)  # Extra rate limiting between files

    print(f"\n{'='*60}")
    print(f"Done! Processed {len(files)} file(s).")
    if not write:
        print("   Re-run with --write to save changes to disk.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
