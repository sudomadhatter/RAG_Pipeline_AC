# src/tests/ — INDEX  (the offline gate)

`python -m pytest src/tests/ -q` — 33 tests, **no cloud access and no credentials required**. Schema
validation + bridge-key structural checks. This is one half of the definition-of-done for any
curriculum story (the other half is the live `probe_bridge_hop.py` proof).

A test that needs a live key or a real store is in the wrong tier — mock at the boundary
(`unittest.mock`).
