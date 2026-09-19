# Phase 3 execution report (2026-09-19)

Only experiments that passed their hard confirmatory gate were run. Every run wrote its manifest first, preserved raw data, hashed its outputs and refused to overwrite. No result was rerun after inspection; no parameter changed after data existed.

## Executed
| Experiment | Tag / commit | Environment | Outputs | Outcome |
|---|---|---|---|---|
| **X3-A** (confirmatory; frozen checkpoints, 40 grid personas x 20 eval seeds x 5 training seeds, 63 000 sessions incl. frozen stratum) | `prereg/X3-A/v1` -> `b00541f` | `LOCK-X3-2026-09-19` | `research/confirmatory/X3-A/results/` (`sessions.csv`, decision, tables, report, 2 manifests) | **Primary: Delta (PPO+G minus Constant-Same+G) = -0.0350, 95 % CI [-0.0818, +0.0021], classification EQUIVALENT (within +-0.12 MAE)**; not PPO-superior; **X3-B trigger not fired** |
| **X2-B**, old-benchmark exploratory arm (64 answers, 8 questions) | `prereg/X2-B/v2` (v1 aborted before any output, AMEND-001) | `LOCK-X2-2026-09-19` | `research/confirmatory/X2-B/results/` | Derived CE: rho 0.4825, AUROC 0.782. **Upstream CE: rho 0.145** (Delta rho 0.337 [0.042, 0.606]). **Length-only baseline: rho 0.4897, AUROC 0.886 - matches/exceeds the derived model** |
| **X1-D** (test report + latency, SUT build A) | `prereg/X1-D/v1`, `sut/X1/build-A` | SUT `.venv` (unlocked) | `research/confirmatory/X1-D/results/` | **226 tests: 225 passed, 1 failed** (the known `test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics`), 0 errors, 0 skipped; warm evaluator median 236.1 ms [221.4, 252.5], P95 615.4 ms, P99 803.8 ms (cold first request 3787 ms, asset load 1563 ms); SQLite single-writer median 12.7 ms, P95 17.1 ms |

## Not executed
| Item | Reason |
|---|---|
| X3-B | Trigger did not fire (X3-A Equivalent); would also need decision D-N2 |
| X1-A, X1-B, X1-C | Protocols/harnesses not constructed (no tag); Docker daemon was available at run time; see `SPRINT_DECISIONS_AND_BLOCKERS.md` D |
| X2-C and the X2-B arm on X2-C | Institutional/ethics and provenance gate not satisfied; no items authored, no raters contacted |

## Negative and null findings (preserved, none suppressed)
- PPO+G is **equivalent** to a constant "Same" action with the same shield on the 40-persona grid; the pre-registered result is not PPO-superior. PPO+G is **more volatile** than Constant-Same+G (volatility +0.149 [0.067, 0.254]; oscillation +0.251 [0.130, 0.386]).
- On the grid the shield did **not** improve Constant-Same tracking (MAE 1.104 with vs 1.000 without; difference +0.104 [-0.184, 0.388]): the frozen five-persona benefit is persona-set dependent.
- On the old benchmark a **length-only** baseline is as good as the derived CrossEncoder (and the composite), so the benchmark does not demonstrate that R adds evidence beyond surface features.
- The exploratory X2-A false-accept analysis (Phase 1) did not favour the composite over R-only; H3 of X2-C is at risk.
- The full test suite has one failing test (unchanged from the disclosed known failure); it was not fixed (defect policy).

## Defects and deviations
Process/harness only, no scientific effect, all logged and retained: X3-A dry-run mutant failures (2), two concurrent launches (`research/preregistration/X3-A/DEVIATIONS.md`, entry 2 corrects entry 1); X2-B manifest path defect handled by AMEND-001 (`research/preregistration/X2-B/DEVIATIONS.md`). The X2-B script text prints "Protocol prereg/X2-B/v1" in its report header; the manifest records v2 (the hashed script was not edited after tagging).

## Integrity
Frozen baseline 366/366; manifests 9/9 completed with unchanged inputs and outputs; T2 recomputation of headline numbers 13/13 PASS (`research/analysis/PHASE4_T2_VERIFICATION.md`, `PHASE4_INTEGRITY_REPORT.md`).
