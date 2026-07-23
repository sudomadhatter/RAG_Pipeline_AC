# _docs/instruction_docs/ — INDEX  (the authoring guides)

The six how-to guides. The **skills** (`.claude/skills/`) are the operational version of these —
a skill loads the guide's rules and enforces the grounding gate; the guide is the reference text.

| Guide | Paired skill |
|---|---|
| `rkp_creation_guide.md` | `rkp-manifest-creation` |
| `quiz_authoring_guide.md` | `quiz-bank-generation` |
| `bridge_key_guide.md` | `bridge-key-verification` |
| `flashcard_creation_guide.md` | (script-owned: `generate_knowledge_formatted.py`) |
| `curriculum_lifecycle.md` | — end-to-end stage walkthrough |
| `get_back_on_track.md` | — recovery when a batch goes wrong |

All authoring is bound by `faa-grounding-gate`: claims trace to ACS/FAA sources only, never model memory.
