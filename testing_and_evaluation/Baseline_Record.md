# Baseline Record — Phase 2/3

## Provenance

- **Git commit:** `9d5c528b3596d0d80c6bb8d606547f64c036b081`
- **Branch:** `workspace/human-eval-clean-push`
- **Date of this baseline:** 2026-11-12
- **Working tree at time of baseline:** clean except `Details/` (untracked, user-supplied reference material) and `reference_material_analysis/`, `testing_and_evaluation/` (this session's new output)

## Environment (measured directly, not assumed from `CLAUDE.md`)

| Item | `CLAUDE.md` states | Actually measured in `.venv` | Note |
|---|---|---|---|
| Python | 3.12 | **3.11.9** | Mismatch — recorded as fact, not corrected |
| numpy | pin `<2.0.0` | 1.26.4 | **Within pin** |
| torch | pin `<2.7.0` | 2.6.0 | **Within pin** |
| accelerate | pin `<1.0.0` | 0.34.2 | **Within pin** |
| stable-baselines3 | — | 2.8.0 | — |
| gymnasium | — | 0.29.1 | — |
| sentence-transformers | — | 2.7.0 | — |
| faiss-cpu | — | 1.15.0 | — |
| transformers | — | 4.57.6 | — |
| fastapi | — | 0.141.1 | — |
| pytest / pytest-asyncio | listed in `requirements/dev.txt` (pinned, not installed) | **not installed** | Blocked this session's `pip install` — see below |

**Finding:** `docs/PROJECT_STATE.md`'s "ENVIRONMENT RECONCILIATION ISSUE" (numpy 2.5.2, torch 2.11.0, accelerate 1.13.0, all violating pins) **no longer reflects the actual `.venv`** — the currently installed versions are all within their stated pins. This is good news but is **not** something I have edited `docs/PROJECT_STATE.md` to reflect (per `CLAUDE.md`: "do not resolve the listed open decisions unasked" — flagging here instead, for the user to decide whether to update that doc).

## OS
`MINGW64_NT-10.0-26300` (Windows 11 Pro, Git Bash / MSYS environment).

## What ran in this baseline pass (no `pytest` required — read-only, direct Python execution)

### T-N02 — Frozen PPO checkpoint inference sanity check
Script: `testing_and_evaluation/rl_evaluation/T-N02_ppo_checkpoint_sanity_check.py`. Loads the real, frozen `rl/checkpoints/seed_123/{ppo_final.zip,vecnormalize.pkl}` via the actual production wrapper `agents.strategy.hybrid_orchestrator.HybridOrchestrator`, calls the real `.suggest()` on 10 constructed candidate states.

**Result: PASS.** `ready=True is_compatible=True` — checkpoint loaded and validated correctly (Discrete(3), Box(6,)). All 10 scenarios (strong/weak/boundary/nervous-expert/floor/ceiling/declining/improving) returned a valid action ∈ {Easier, Same, Harder} and a difficulty staying within [1,5]; floor and ceiling clamping confirmed correct. All 10 used the real PPO policy (`source=ppo`), none fell back to heuristic. Full log: `testing_and_evaluation/logs/T-N02_output.log`.

**Notable individual result** (not a failure, a behavioral observation): for `score=0.35` (below-average, below the evaluator's 0.65 mandatory-cap threshold), the raw policy proposed **Harder**, not Easier/Same. This was flagged for follow-up in T-N03.

### T-N03 — Guardrail rule verification
Script: `testing_and_evaluation/rl_evaluation/T-N03_guardrail_verification.py`. Calls the real, frozen `rl.guardrails.apply_canonical_guardrails()` directly on 11 constructed states, including each documented G-rule's boundary and the T-N02 observation above.

**Result: PASS (0 mismatches)** — all 5 guardrails (G1, G2, G4, G5, G6) and the infrastructure-failure override fire exactly where the code's own docstring says they should; boundary cases (perf=0.29 vs 0.30, difficulty in/out of the mid-band) behave correctly at the documented edges. Full log: `testing_and_evaluation/logs/T-N03_output.log`.

**Genuine finding, empirically confirmed (not asserted):** none of the five documented guardrails (G1/G2/G4/G5/G6) cover the open interval **perf ∈ (0.30, 0.40)** when the underlying policy proposes escalation (Harder) and confidence/hesitation are moderate (not extreme enough to trigger G2). A candidate scoring 0.35 — below-average by the evaluator's own mandatory-cap threshold (0.65) — can have their difficulty increased with no guardrail intervention. This is a real, reproducible gap in the current guardrail coverage, not a report-derived or invented number. **Recommended for inclusion in the Testing & Evaluation report's reliability findings and in Phase 4 (diagnosis) as a candidate for a justified fix (e.g., extending G1's band or adding a new rule) — not fixed in this pass, since `CLAUDE.md` requires explicit approval before changing guardrail logic.**

## Full automated test suite — FINAL baseline (user installed `pytest`/`pytest-asyncio` then `httpx`)

**Result: 264 passed, 19 failed, 15 skipped, 0 collection errors (93.3% of 283 executable tests).** Full breakdown and root-cause attribution: `testing_and_evaluation/baseline_results/Full_Suite_Baseline_Results.md`.

**Every one of the 19 remaining failures is fully explained** — 18 by the Docker daemon not running on this machine (client v29.7.2 installed, daemon unreachable — confirmed via `docker ps`), and exactly 1 by the pre-existing, already-documented known failure (`test_stage11_5_coding_adaptation.py::test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics`, obs[4] 0.0 vs expected 0.22 — reproduced identically, not touched per `CLAUDE.md`). **Zero new/unexplained defects found across the entire suite.**

**Remaining optional gap:** start Docker Desktop (the daemon, not just the client) if the 18 sandboxed-code-execution tests should run too. Not required for Task 1 to proceed — this gap is documented and attributed, not silently ignored.

## T-F01 — Frontend tests (`apps/web/src/__tests__/*.test.jsx`)

Ran via `npm run test:ci` (`vitest run`, v2.1.9) in `apps/web/` — no blocked dependency, `node_modules` already present.

**Result: PASS — 4/4 test files, 28/28 tests passed.** Duration ~14–20s. Covers: theme toggle (`layout.test.jsx`), best-answer authority reflecting backend state including a "no eligible best → no best-answer UI" regression case (`best_answer_authority.test.jsx`), primary-question-vs-follow-up progress numbering (`question_progress.test.jsx`), and 17 Stage-11.8 UI-fix regressions including an explicit-error-state-on-API-failure check and a check that raw numerical scores/percentages are hidden from the qualitative feedback card (`ui_fixes.test.jsx`). Full log: `testing_and_evaluation/logs/T-F01_frontend_vitest_output.log`.
