---
name: faa-grounding-gate
description: >
  The citation-truth gate for ALL curriculum authoring in this repo. Every factual claim in an RKP
  manifest, quiz question, explanation, or lesson overview must trace to a named ACS or FAA source
  document that physically exists on disk (or in DB2) — never to model memory. Activates
  automatically inside rkp-manifest-creation and quiz-bank-generation, and whenever Daniel says
  "verify the citations", "ground this", or asks whether a fact is real.
---

# FAA Grounding Gate

> **The Golden Rule: never state an aviation fact you have not read in a source document.**
> If you cannot point to the document, the page, and the words — you do not know it. Flag it for
> Daniel instead. "Unverified" is a correct answer; a fabricated citation is not.

This repo authors the content a student pilot studies for a real checkride. A wrong reg number can
fail a checkride, cause a violation, and destroy trust in the product. Accuracy beats throughput
every single time — there is no deadline that justifies a guess.

---

## 1. The permitted sources (the ONLY things you may cite)

These files are **on disk in this repo**. Read them. Do not cite anything not on this list without
Daniel's explicit approval.

| Source | Path | Cite it for |
|---|---|---|
| **PPL ACS** | `docs/private_airplane_acs_6.pdf` | ACS Area/Task/element codes + the exact element wording |
| Instrument ACS · Commercial ACS | `docs/instrument_rating_airplane_acs_8.pdf` · `docs/commercial_airplane_acs_7.pdf` | Only for non-PPL work |
| **ACS Curriculum Key** | `pipeline/curriculum/1 ACS Curriculum Key.json` | element code → lesson-id mapping |
| **14 CFR Part 61** | `pipeline/library/new/14 CFR part 61 (2025).pdf` | certification, currency, privileges, endorsements |
| **14 CFR Part 91** | `pipeline/library/new/14 CFR part 91 (2025).pdf` | operating rules, equipment, weather minimums |
| **14 CFR Parts 67 / 68** | `pipeline/library/new/14 CFR Part 67 (2025).pdf` · `...Part 68 (2025).pdf` | medical standards · BasicMed |
| **AIM** | `pipeline/library/new/AIM 2025.pdf` | procedures, airspace, communications |
| **PHAK** | `pipeline/library/new/FAA-H-8083-25 (PHAK).pdf` | general aeronautical knowledge |
| **AFH** | `pipeline/library/new/FAA-H-8083-3 (AFH).pdf` | flight maneuvers, technique |
| **Weather (AWH)** · **Risk Mgmt (RMH)** | `pipeline/library/new/FAA-H-8083-28 (AWH).pdf` · `FAA-H-8083-2 (RMH).pdf` | weather theory · ADM / risk |
| **Advisory Circulars** | `pipeline/library/new/AC {60-22, 61-142, 61-98E, 68-1, 68-1A, 90-66C, 91-73B, 91-92}.pdf` | ADM, flight reviews, BasicMed, non-towered ops, etc. |
| **DB2 live store** | via `src/gcp/probe_bridge_hop.py` / the derived tag vocabulary | confirming a bridge-key token actually resolves |

### Not on disk = not citable
Common gaps that have bitten this project: the **AME Guide**, **FCC forms**, **FAA Chief Counsel
legal interpretations**, **FAA Orders (8900.x)**, and the Instrument Flying Handbook. Thirteen
existing lessons cite sources in this category — they survive on semantic fallback, not on a real
bridge hop. **If a claim needs one of these: stop and flag it for Daniel.** Do not paraphrase it
from memory, and do not silently swap in a different citation that happens to be on disk.

---

## 2. What must be grounded

Ground **every** one of these before it enters a manifest, a quiz, or an overview:

- **Any regulatory citation** — `14 CFR 61.56`, `AIM 3-2-1`, `AC 61-98E`. Read the actual section.
- **Any number that carries legal or safety weight** — hours, altitudes, visibilities, distances,
  speeds, calendar-month windows, medical durations, equipment lists.
- **Any "must / required / prohibited" statement** — these are regulatory claims even when no reg is
  named. Name the reg or soften the claim to what the source actually supports.
- **Any ACS element code or its wording** — copy from the ACS PDF, don't reconstruct from the code.
- **Any accident/enforcement statistic** used in a quiz explanation — real NTSB/FAA figures only.
- **Any bridge-key token** — must exist in the DB2 vocabulary (`bridge-key-verification` proves it).

Not required: pedagogical framing, analogies, encouragement, and genuinely common aeronautical
knowledge (the four forces of flight). If it mentions a rule, a number, or a requirement — ground it.

---

## 3. How to actually verify (the mechanic) — READ THIS BEFORE YOU RELY ON IT

> ⚠️ **Verified on this machine 2026-07-22: the PDFs on disk are NOT machine-readable today.**
> The `Read` tool cannot render them (`pdftoppm`/poppler not installed) and **`pypdf` is not
> installed and is not in `requirements.txt`** (the AFH split described in the PRD was done
> ad-hoc). Do not claim you "read the PDF" — you currently cannot. Use the paths below.

**Path A — DB2 (the working machine path).** The FAA library is already ingested into DB2
(`aviation-library-v2`, 27 documents) and credentials exist at `auth_keys/`. Query it read-only
(`src/gcp/probe_bridge_hop.py`, or a scoped Vertex search) and quote the returned passage. This is
the primary grounding path for regulatory and handbook content.

**Path B — Daniel.** He is the CFI and holds the documents. Ask for the operative text. This is
not an escalation of last resort; it is the designed content gate. A short "I need the exact
wording of 61.56(a)" costs minutes. A fabricated citation costs a checkride.

**Path C — enable local extraction (one-time, needs approval).** Adding `pypdf` to
`requirements.txt` would unlock offline text extraction from the on-disk PDFs and make Path A's
fallback unnecessary. Dependency changes are ask-first (`constitution.md`) — **propose it to Daniel;
do not add it unilaterally.** Until then treat the PDFs as human-readable references, not sources
you can quote.

Then, whichever path you used:

1. **Quote first, write second.** Pull the operative sentence out of the source before composing
   teaching text. Write from the quote, never from recall of the quote.
2. **Check the version.** Cite the edition actually in the library (`AC 61-98E`) — but see the
   family-matching note in `bridge_key_guide.md`: DB2 tags carry edition variants so an older
   reference still hops. Never invent a version letter.
3. **Confirm the bridge key resolves.** Run `bridge-key-verification` after authoring — an
   unresolvable key is an authoring bug, not a runtime one.
4. **Record the trace.** In the session's `walkthrough.md`, list each non-obvious claim with the
   source and passage it came from, and name which path (A/B/C) produced it. That trace is what
   makes a batch reviewable by Daniel instead of taken on faith.

---

## 4. Citation format

✅ `14 CFR 61.56(a)` · `14 CFR 91.205(b)(4)` · `AIM 3-2-1` · `AC 61-98E` · `FAA-H-8083-25 (PHAK), Ch. 7`

❌ Vague — "the FARs say", "per regulations", "Part 91 requires" (which section?)
❌ Invented — `14 CFR 99.999`, `FAR 22.5` (wrong scheme entirely; it is `14 CFR`)
❌ Version-stripped — `AC 61-98` with no letter
❌ Paraphrase-instead-of-cite — "the flight review rule" → cite `14 CFR 61.56`

Field placement: `far_references` / `far_reference` hold **FAA regulations only**. Legal
interpretations, NTSB data, and handbook narrative belong in `explanation` prose.

---

## 5. Red flags — the four ways this goes wrong

1. **Suspiciously precise numbers.** Regulatory thresholds are round (50 hours, 3 SM, 24 calendar
   months). A decimal is almost always invented.
2. **Merged regulations.** Two real rules fused into one false claim (VFR minimums live in 91.155;
   the 10,000 ft speed threshold is 91.117 — different sections).
3. **Stale rule state.** Regulations change. Cite the 2025 documents on disk, not remembered
   older text.
4. **Dropped exceptions.** "All aircraft must have a transponder" is false — 91.215 is mostly
   exceptions. If the source has carve-outs, the teaching text must survive them.

---

## 6. When a claim will not ground

Do exactly this, in order: (1) stop writing that claim, (2) leave the field empty or the RKP
incomplete — **never** fill it with a plausible-sounding substitute, (3) surface it to Daniel with
what you needed, what you searched, and why it failed, (4) let him supply the source or the ruling.
He is the CFI and the citation gate; that is his half of the partnership, not a bottleneck to route
around.

---

## 7. Anti-patterns

| ❌ Don't | ✅ Do instead |
|---|---|
| Write a reg number from memory because it "looks right" | Open the CFR PDF and read the section |
| Swap in an on-disk citation because the real source is missing | Flag the gap to Daniel |
| Cite a handbook chapter you did not open | Read the pages, then cite |
| Invent an NTSB statistic to make an explanation land | Use a real figure or drop the appeal to data |
| Soften a fabrication with "generally" or "typically" | Ground it or cut it |
| Treat the ACS code as self-describing | Copy the element wording from the ACS PDF |
| Let an unresolvable bridge key ship "to fix later" | Fix it before the batch closes |

---

## 8. Related

`rkp-manifest-creation` and `quiz-bank-generation` both run inside this gate.
`bridge-key-verification` proves the DB1→DB2 hop. The hard stops that make this binding live in
`.agents/rules/constitution.project.md`.
