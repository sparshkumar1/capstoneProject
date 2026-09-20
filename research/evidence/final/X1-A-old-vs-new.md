# X1-A old vs new (fault-injection campaign, build A vs build B)

- **Old (v1):** `prereg/X1-A/v1` (`80ac6044…`), `freeze/X1-A/v1` (`68a0bf5e…`), build A = `release/app-repair/v1` (`980747ff…`), run 2026-09-20 11:24–11:32 UTC, harness sha256 `a074ee9d…`. Results in `results/x1a/`.
- **New (v2):** `prereg/X1-A/v2` (`77cf3a57…`), build B = `sut/X1/build-B` (`beb374f3…`), run 2026-09-20 15:00–15:08 UTC, harness sha256 `74be10f5…`. Results in `results/x1a_v2/`; run record `run_records/x1a_v2/RUN_RECORD.json`. Exit 0, 60 repetitions, 0 harness errors, no leftover containers afterwards.
- **Environment:** same machine, same Docker (29.7.2, WSL2 6.6.87.2), Python 3.12 `.venv` (project venv, pins violated as recorded in registry X-C004). Qwen dependency replaced by the same local stub on port 8001 in both runs.
- **Exact code changes (build A → B, `git diff release/app-repair/v1 sut/X1/build-B -- agents services`, 4 files, +83/−4):** `interview_orchestrator.py` — new `_fail_closed_evaluator_unavailable` called from `handle_voice_answer` when `_evaluate_verbal` returns `decision_source`/`status` = `evaluator_unavailable` (no score/answer appended, no difficulty adaptation, no attempt persisted, attempt count and timing values restored, timer restarted, `infrastructure_errors` entry, `next_action = retry_answer`); `coding_executor.py` — unique container names and `docker rm -f` on timeout; `feedback_agent.py` — `llm_status` passed through from the Qwen service; `services/qwen/app.py` — feedback token cap 256 → 512 (`QWEN_FEEDBACK_MAX_NEW_TOKENS`). Rationale: `research/evidence/final/DEFECT_DECISIONS_FLT03_FLT06.md`.
- **Harness change:** only tags, SUT tag, output path and two file names; every criterion and bound (including the 5.0 s Qwen-down SLA and the 33.0 s FLT-07b bound) is unchanged.

## Per-scenario comparison (5 repetitions each)
| Scenario | v1 (build A) criteria met | v2 (build B) criteria met | v1 failed criteria | v2 failed criteria | oracle valid v1/v2 | seconds v1 | seconds v2 | changed |
|---|---|---|---|---|---|---|---|---|
| FLT-01 | 5/5 | 5/5 | - | - | True/True | 4.84-4.90 | 4.87-4.91 | no |
| FLT-02 | 5/5 | 5/5 | - | - | True/True | 12.78-12.85 | 12.79-12.82 | no |
| FLT-03 | 0/5 | 5/5 | infrastructure_failure_flagged, no_zero_score_recorded_as_candidate_failure | - | True/True | 1.41-1.53 | 0.00-0.00 | yes |
| FLT-04[nan] | 5/5 | 5/5 | - | - | True/True | 0.49-0.55 | 0.51-0.59 | no |
| FLT-04[inf] | 5/5 | 5/5 | - | - | True/True | 0.51-0.55 | 0.51-0.53 | no |
| FLT-04[999.0] | 5/5 | 5/5 | - | - | True/True | 0.30-0.35 | 0.29-0.35 | no |
| FLT-04[-3.0] | 5/5 | 5/5 | - | - | True/True | 1.41-1.48 | 1.40-1.46 | no |
| FLT-05 | 5/5 | 5/5 | - | - | True/True | 0.00-0.00 | 0.00-0.00 | no |
| FLT-06 | 0/5 | 5/5 | no_orphan_container_3s_after_return | - | True/True | 10.54-11.12 | 10.86-11.22 | yes |
| FLT-10 | 5/5 | 5/5 | - | - | True/True | 1.15-1.18 | 1.11-1.21 | no |
| FLT-07a | 5/5 | 5/5 | - | - | True/True | 2.08-2.10 | 2.07-2.10 | no |
| FLT-07b | 4/5 | 5/5 | fails_near_busy_timeout | - | True/True | 32.58-33.09 | 32.61-32.66 | yes |

FLT-03 v1 first-repetition fault observation: {"seconds": 1.533, "decision_source": "qwen_feedback_stub", "fb_grade": "F", "fb_status": null, "state_scores": [0.0], "infra_errors": []}
FLT-03 v2 first-repetition fault observation: {"seconds": 0.002, "decision_source": "evaluator_unavailable", "fb_grade": "Unscored", "fb_status": "evaluator_unavailable", "state_scores": [], "infra_errors": [{"question_id": "x1a_q1", "type": "evaluator_unavailable", "error": "Authoritative verbal evaluation service is unavailable. No score fabricated."}]}
FLT-06 v1 first-repetition fault observation: {"status": "compilation_error", "seconds": 10.74, "leftover_containers_after_3s": ["223dafffc749"], "next_submission_status": "accepted"}
FLT-06 v2 first-repetition fault observation: {"status": "compilation_error", "seconds": 11.217, "leftover_containers_after_3s": [], "next_submission_status": "accepted"}

## What changed
- **FLT-03 (evaluator outage): 0/5 → 5/5.** Build A recorded the outage as a candidate score of 0.0, grade "F", with no infrastructure flag; build B returns `status = decision_source = evaluator_unavailable`, grade "Unscored", records nothing in `scores`, and logs an `infrastructure_errors` entry. The campaign oracle inspects in-memory session state only; that no attempt is persisted is verified by a unit test (`test_evaluator_outage_persists_no_attempt`), not by this campaign.
- **FLT-06 (compiler outlives the timeout): 0/5 → 5/5.** Timeout still fires at 10.9–11.2 s; no container remains 3 s after return in any repetition (build A: a container remained in 5/5).
- **FLT-07b (SQLite lock held 34 s): 4/5 → 5/5 — this is NOT a repair.** Nothing in the database path changed between builds. Build A's miss was one repetition at 33.09 s against the registered 33.0 s bound; build B's five repetitions were 32.61–32.66 s. The difference is run-to-run timing variation around a bound that sits within ~0.4 s of the measured behaviour (`X1_METHOD_AUDIT.md` §2); the bound was deliberately not changed. The result should be read as "behaviour correct in both runs; timing bound marginal".
- **FLT-01 (Qwen down):** still passes with a margin of about 0.1 s to the registered 5.0 s SLA (4.87–4.91 s in v2; 4.84–4.90 s in v1); on a slower or busier machine this criterion could flip.
- All other scenarios (FLT-02, FLT-04 ×4, FLT-05, FLT-07a, FLT-10): unchanged, 5/5, oracles valid in both runs.

## Did any scientific claim change?
Yes, in the direction of the defects being closed for the tested scenarios: on build B every executed scenario met its criteria, so the registered condition for the word "fault-tolerant" in protocol §5 (every executed scenario passes with a valid oracle) is **technically met for the executed classes**. **The word is still not recommended** and remains unsupported for the paper: FLT-08 (WebSocket) and FLT-09 (audio) were never executed; FLT-05 injects "Docker CLI not found", not an unresponsive daemon; FLT-04's oracle accepts NaN/Inf/−3 silently becoming 0.0 (unrepaired; not an outage, but the same silent-zero pattern); FLT-07b's pass is timing-marginal; the oracles are perturbation controls, not mutant builds; the build-B pass was obtained after the defects were seen and repaired by the same agent, so it is a regression check of two specific fixes, not an independent test. Supportable wording: **"failure-aware"** — an evaluator outage or a compiler hang is detected, flagged and not recorded as a candidate result, for the enumerated request-path scenarios, on this build and machine.
**Remaining application limitations (not repaired):** NaN/Inf/out-of-range evaluator scores are clamped to a number without an infrastructure flag; empty or failed-STT transcripts remain an explicit flagged zero-score turn by design; the Qwen client timeout (6.0 s) remains shorter than real generation time on this CPU (13–21 s) and the UI abandons an evaluation after 20 s.
