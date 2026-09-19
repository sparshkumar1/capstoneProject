# Phase 4 freeze report (2026-09-19)

## Freeze actions
- Result sets frozen by SHA-256 listing `research/analysis/RESULT_HASHES_phase3.txt` (25 files: X3-A, X2-B, X1-D result directories) and annotated tags `freeze/X3-A/v1`, `freeze/X2-B/v1`, `freeze/X1-D/v1` (each carries the listing hash). Earlier tags: `prereg/X3-A/v1`, `prereg/X2-B/v1` + `v2`, `prereg/X1-D/v1`, `sut/X1/build-A`, and the frozen Paper-3 tag `v1.0-paper3-complete`.
- Raw outputs preserved: `sessions.csv` (63 000 sessions, action strings), `scores.csv`, `latency_raw.csv`, `junit.xml`, `pytest_console.txt`, all manifests; aborted/failed attempt directories retained unmodified (`results_attempt1_*`, `dryrun_attempt*`).
- Environment records: `research/locks/LOCK-X3-2026-09-19.*` (hash-pinned), `LOCK-X2-2026-09-19.*` (hash-pinned), `replay-Lobs.*` (version-only, Phase 1); X1-D used the unlocked SUT `.venv` (versions in the manifest).

## Claim registry (`research/claims/CLAIM_REGISTRY.csv`): 43 -> 115 rows
Statuses: VALID 58, WITHDRAWN 28, HISTORICAL 5, DESIGN-ONLY 9, EXPLORATORY 15, PENDING-REGISTRATION 0. New in Phases 1-3: `P1S-C001..C041` (Paper-1 claim survival), `X2A-C001..C009`, `P3-C017..C024`, `X3A-C001..C007`, `X2B-C001..C004`, `X1D-C001..C003`; `P3-C007/8/9` promoted to VALID (replay); `P2-C012` HISTORICAL; `P1-C009` DESIGN-ONLY. Each new row carries claim -> artifact -> script -> commit -> config -> environment -> SHA-256 (`recompute_tier` T3 for new experiments, T2 for stored-data analyses).

## Verification
- T1: 100 rows with artifact hashes re-verified (0 mismatches).
- T2: independent recomputation (different code path) of X3-A primary difference, persona/session counts, X2-B Spearman (derived, upstream, length-only), X1-D latency medians and JUnit counts: 13/13 PASS (`research/analysis/PHASE4_T2_VERIFICATION.md`).
- Frozen baseline 366/366; key hashes unchanged; 9 manifests completed with unchanged inputs/outputs (`research/analysis/PHASE4_INTEGRITY_REPORT.md`).
- Not done: T3 full reruns of the new experiments from a clean checkout (the harnesses are deterministic and write-once; a second run would need a new results directory); a `verify_claims` checker (planned, needs approval); external preregistration (not requested).

## Failures and caveats recorded
X1-D: 1 failing test (known). X3-A: none scientific; process deviations only. X2-B: attempt 1 aborted before output (AMEND-001). Exploratory labels are enforced in the registry (`X2A-*`, `X2B-*` EXPLORATORY/VALID-as-sensitivity only; none confirmatory).

## Open after Phase 4
X1-A/B/C (not constructed), X2-C (human gate), X3-B (parked; only if D-N2 and a trigger), `CLAUDE.md`/docs pointer updates (D-F1), manuscript work (not started).
