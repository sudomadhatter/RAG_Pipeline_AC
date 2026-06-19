# new/ — authoring inbox

Drop freshly-extracted lesson sidecars here. `src/utils/generate_metadata.py` and
`scripts/fallback_generator2.py` write to this folder (`config.CURRICULUM_NEW`).

When a lesson is finished, promote it: the `.md` content moves to `../elements/` and the `.json`
metadata sidecar moves to `../sidecars/`. This folder is normally empty — it exists only as the
landing zone for in-progress authoring.
