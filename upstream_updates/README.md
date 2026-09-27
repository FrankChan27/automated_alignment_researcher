# upstream_updates (DOWNSTREAM-LOCAL)

Machine-readable records of detected upstream changes for the FrankChan27 fork.

Each manifest is named `<YYYY-MM-DD>-<newsha12>.json` and written by
`downstream/scripts/write_update_manifest.py` (usually via `monitor_once.sh`).

Manifests are intentionally **committable** on `upstream-sync/*` branches so
reviewers can see classification, impact flags, and recommended action alongside
the Draft PR. They do **not** update `downstream/UPSTREAM_PIN.json`.
