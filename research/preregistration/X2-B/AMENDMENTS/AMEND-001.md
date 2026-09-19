# AMEND-001 (X2-B): v1 -> v2, 2026-09-19

**What.** (i) `x2b_run.py`: the upstream weights (external HF cache, outside the repository) are recorded as a manifest *model* entry with their SHA-256 instead of being added through `add_inputs` (which requires a repository-relative path); (ii) `x2b_config.json`: `protocol_tag` = `prereg/X2-B/v2`. `PROTOCOL.md` is unchanged (its SHA-256 is identical in both tags).
**Why.** The first launch under `prereg/X2-B/v1` aborted in the manifest step with `ValueError: ... is not in the subpath of ...` before any model was loaded or scored (`results_attempt1_ABORTED_manifest_external_path_error/` contains only a manifest stub). No upstream or baseline output, no metric and no result existed.
**Approval / timing.** Made by the executor under the sprint authorisation, **before any confirmatory data existed** (allowed by PREREGISTRATION_SPEC A.5). No hypothesis, endpoint, metric, gate, scorer, seed or inference rule changed.
**Effect.** New `protocol_manifest.json` and tag `prereg/X2-B/v2`.
