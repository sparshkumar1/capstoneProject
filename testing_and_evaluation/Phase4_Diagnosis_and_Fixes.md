# Phase 4 — Diagnosis and Justified Fixes

Both fixes below were diagnosed from genuine findings in Phase 2/3 testing (not invented), applied with minimal, single-purpose changes, verified individually, and regression-tested against the full suite with zero new failures. Applied with explicit user approval (2026-11-12, in direct response to being shown both findings and asked whether to apply fixes).

## Fix 1 — `rl/guardrails.py`: G5 guardrail coverage gap

**Diagnosis:** `testing_and_evaluation/rl_evaluation/T-N02_ppo_checkpoint_sanity_check.py` found that the real, frozen PPO checkpoint proposes "Harder" for a below-average-scoring candidate (perf=0.35). `testing_and_evaluation/rl_evaluation/T-N03_guardrail_verification.py` then confirmed empirically (not just by reading the code) that none of the 5 documented guardrails (G1/G2/G4/G5/G6) intercept this: G4/G1 require `perf < 0.30`, G5 required `perf > 0.40` — leaving `perf ∈ [0.30, 0.40)` uncovered for the escalate-with-moderate-confidence case.

**Classification:** Genuine architectural/implementation gap in the guardrail coverage — not a dependency, environment, or configuration issue.

**Root cause:** G5's lower threshold (`0.40 < perf`) was set with a gap relative to G1/G4's upper threshold (`perf < 0.30`), leaving `[0.30, 0.40)` with no rule.

**Fix applied:** Widened G5's lower bound from `0.40 < perf < 0.65` to `0.30 <= perf < 0.65` in `rl/guardrails.py`. One-line condition change plus docstring/comment updates explaining the fix and its date. No other guardrail's condition, priority order, or returned action changed.

**Why this fix, not an alternative:** This is the minimal change that exactly closes the identified gap with no overlap or new gap: G4/G1 cover `[0, 0.30)`, G5 now covers `[0.30, 0.65)` contiguously, G2/G6 are unaffected (their conditions don't reference this boundary). Alternatives considered and rejected: (a) lowering G1's upper-only condition — doesn't apply, G1 is about difficulty band not perf band; (b) adding a brand-new G7 rule — would duplicate G5's existing "Same" action and rationale for no benefit; (c) changing G4's threshold — G4 is specifically about *stuck* (perf<0.30 AND hes>0.60), a different and more severe condition, widening it would blur its intent.

**Verification:**
1. `T-N03_guardrail_verification.py` rerun with 2 new boundary cases added (`perf=0.30` exact new boundary, `perf=0.299` just below, confirming it still correctly falls to G1) — **13/13 cases pass, 0 mismatches.**
2. Full regression suite rerun: `EVALUATOR_MOCK_MODE=1 pytest -q --continue-on-collection-errors` → **264 passed, 19 failed (identical set: 18 Docker-daemon-down + 1 pre-existing known issue), 15 skipped. Zero new failures, zero regressions.**

**Scope/impact statement (per `CLAUDE.md`'s "Major architecture/experiment changes" requirement):**
- **What:** one guardrail threshold widened (`rl/guardrails.py`), affecting live/future sessions only.
- **Why:** closes an empirically-demonstrated safety gap where a below-average candidate could have difficulty escalated unopposed.
- **Affected components:** `rl/env/interview_env.py`, `agents/orchestrator/interview_orchestrator.py`, and `research/scripts/run_paper3_study.py` all import this shared module (per its own docstring) and will see the new behavior if re-run from this point forward.
- **Reproducibility impact:** **Does not alter any already-generated frozen result file.** `research/results/paper3/*` and `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` describe results generated under the *previous* guardrail version and remain historically accurate records of that version — they are not regenerated or retroactively changed by this fix. If `research/scripts/run_paper3_study.py` is ever re-run in the future, it will now produce different (and more correct) guardrail-intervention counts than the frozen study; this must be disclosed as a version difference, not silently treated as reproducing the same frozen numbers. **Flagging this explicitly here so Task 2/3 report writing does not accidentally conflate pre-fix and post-fix guardrail behavior.**

## Fix 2 — `launch.py`: Unicode console-encoding crash

**Diagnosis:** `testing_and_evaluation/baseline_results/T-N01_smoke_test_finding.md` — a live `launch.py --backend-only` smoke test crashed with `UnicodeEncodeError` immediately after both services started successfully, because the startup banner prints a `→` (U+2192) character that the default Windows `cp1252` console encoding cannot represent.

**Classification:** Genuine implementation bug (unguarded Unicode output, platform-encoding-dependent) — not an environment/dependency issue; contrast with the `httpx`/`pytest`/Docker gaps found elsewhere in this session, all of which were missing infrastructure rather than code defects.

**Fix applied:** Added `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` (and the same for `stderr`) at module level in `launch.py`, immediately after the imports and before any `print()` executes, wrapped in `try/except` for safety on platforms/Python versions where `reconfigure()` isn't available. `errors="replace"` ensures that even a glyph the target console genuinely cannot render becomes a replacement character instead of crashing the process.

**Why this fix, not an alternative:** Considered replacing `→` with ASCII `->` throughout the banner instead — rejected because (a) it only fixes this one script's current prints, not any future Unicode usage anywhere else in the script, and (b) the `reconfigure()` approach is the same pattern already used successfully in this session's own test scripts (`T-N06`), so it's consistent and known-working.

**Verification:**
1. Reproduced the exact original crash in isolation (`PYTHONIOENCODING=cp1252`, printing the literal failing string) — confirmed identical `UnicodeEncodeError`.
2. Confirmed the same print succeeds cleanly with the fix applied, under the same forced `cp1252` condition.
3. Confirmed `launch.py` itself (with the fix in place) runs its module-level code (which now includes the `reconfigure()` call, executed at import time) without error under forced `cp1252`, via `launch.py --help` (exercises imports/module-level code, binds no ports).
4. Full regression suite rerun (same run as Fix 1's verification, both changes were live simultaneously): 264 passed, 19 failed (same set), 15 skipped. `launch.py` isn't exercised by the pytest suite, so this mainly confirms no import-time breakage.
5. **Not independently re-verified via a full fresh end-to-end run** (would show the "Press Ctrl-C to stop" line actually printing) because ports 5000/8000 are still occupied by orphaned processes from the *original* pre-fix smoke test, and forcibly stopping those processes was blocked by the sandbox permission classifier. The three checks above are sufficient to confirm correctness; a confirmatory full run can be done once those ports are free.

**Outstanding items for the user (not fixes — just cleanup):**
- Two orphaned localhost-only dev-server processes from the original smoke test are still running on ports 5000/8000. Stop them at your convenience (not urgent, not a security concern, not blocking anything): find PIDs via `netstat -ano | grep -E ":5000 |:8000 "` and `! taskkill /F /T /PID <pid>`.
- `services/evaluator/evaluation_results/` and `services/evaluator/evaluation_sessions/` were created as a side effect of the evaluator service handling real requests during API-contract testing (T-N04) and the smoke test (T-N01) — these are untracked, harmless session-persistence artifacts (JSON files), not code changes. Not committed or cleaned up in this pass; your call whether to `.gitignore` them or delete them.

## Net result of Phase 4

Two real, user-approved, minimal, verified fixes applied. Full regression baseline after both: **264 passed / 19 failed (fully attributed, zero unexplained) / 15 skipped**, identical to the pre-fix baseline — confirming both changes are safe and additive, not disruptive.
