# curriculum_components/scripts/ — INDEX

Authoring-side utilities (distinct from the repo-level `scripts/` and the gated `src/gcp/` tools):

- `fallback_generator*.py` — parse a master module into split lessons + sidecars
- `generate_knowledge_formatted.py` — Gemini pass that fills the flashcard field
  (`knowledge_formatted`) in each RKP manifest; the ONLY writer of that field
