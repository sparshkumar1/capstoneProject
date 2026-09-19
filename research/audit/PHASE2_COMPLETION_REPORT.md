# Phase 2 completion report (2026-09-19)

**Status: PARTIAL by design.** Protocols were finalized, hashed and tagged only for experiments whose construction was complete and whose gates could be satisfied. Nothing was tagged or run where a scientific fork, an external gate or unfinished construction remained.

| Experiment | Protocol final? | Tag | Environment lock | Mutation/positive controls (dry run) | Hard gate |
|---|---|---|---|---|---|
| **X3-A** | Yes | `prereg/X3-A/v1` (commit `b00541f`) | `LOCK-X3-2026-09-19` (hash-pinned, `uv --generate-hashes`, verified at run start) | G-HARNESS: new session loop == frozen loop on 5 frozen personas (9 fields x 25 sessions x 5 conditions), shield copy == frozen shield on 200 000 states, 3 mutants detected. Two earlier attempts failed because the chosen heuristic mutants were behaviourally invisible on the fixture (recorded in `DRYRUN_LOG.md`; no criterion relaxed) | 15/15 (`HARD_GATE_CHECK.md`) |
| **X3-B** | No (conditional) | - | - | - | Parked: trigger not fired; would additionally need decision D-N2 |
| **X2-B (old-benchmark exploratory arm)** | Yes (confirmatory X2-C arm explicitly excluded) | `prereg/X2-B/v1`, amended `prereg/X2-B/v2` (AMEND-001, before any data) | `LOCK-X2-2026-09-19` (hash-pinned) | G-MODEL-HASH, G-METRIC-CONTROLS, G-DERIVED-REPRO (derived output reproduces stored R within 0.002); statistics and both models self-tested on synthetic text before tagging | Passed for the exploratory arm |
| **X2-C** | No | - | - | - | **Blocked**: institutional/ethics gate and provenance records not satisfied; D-X2-TAU/rho_min open; no item authoring or rater contact was done |
| **X1-D** | Yes (test report + latency only) | `prereg/X1-D/v1`, SUT `sut/X1/build-A` | none (SUT `.venv`, unlocked by design; versions recorded) | not applicable (no oracle) | Passed for the scoped design |
| **X1-A / X1-B / X1-C** | **No** | - | - | Not constructed | **Not run**: construction incomplete (see `SPRINT_DECISIONS_AND_BLOCKERS.md` section D); needs enumeration table, injectors/mutants, prompt set, discriminating attack programs and oracles |

## What Phase 2 produced
- Tags: `prereg/X3-A/v1`, `prereg/X2-B/v1`, `prereg/X2-B/v2`, `prereg/X1-D/v1`, `sut/X1/build-A`. Each tag message carries the SHA-256 of `PROTOCOL.md` and `protocol_manifest.json`; every runner verifies the tag, ancestry, all dependency hashes and (where applicable) the lock before producing output.
- Run-manifest helper extended to `research/confirmatory/` and `research/preregistration/` (write-once outputs).
- Environment locks with wheel hashes for the two locked families; the earlier `replay-Lobs` record remains a Phase-1 (version-only) record.
- Decisions recorded, not taken: D-N2, D-X2-TAU, D-F1, D-HUMAN, D-X3B-OP.
- No external submission of any preregistration; no external communication.

## Deviations
X3-A: two dry-run mutant failures; a process-management error (two concurrent launches) corrected in `research/preregistration/X3-A/DEVIATIONS.md` (no scientific effect). X2-B: manifest-path defect before any output, handled by AMEND-001 and tag v2. All attempt directories are retained.

## Gate to Phase 3
Executed only what passed its hard gate: X3-A, X2-B (exploratory arm), X1-D. Not executed: X3-B (trigger), X2-C (human gate), X1-A/B/C (not constructed).
