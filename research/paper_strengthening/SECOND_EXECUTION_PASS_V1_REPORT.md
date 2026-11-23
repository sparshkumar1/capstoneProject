# Second Execution Pass V1 — Evaluator, LLM, Multimodal, End-to-End

Complementary execution pass, run directly after (and coordinated with, not duplicating) the PPO Formulation Investigation V1 pass in the same session. Scope: evaluator quality (highest priority), LLM feedback/follow-up hardening, multimodal audit, end-to-end reliability (session recovery), and regression verification.

## 0. Baseline inspection (before any change)

`git status` at the start of this pass showed exactly the file set left by the prior (PPO/prompt-injection/fault-tolerance) pass, still uncommitted, with no other process running. No frozen/protected artifact (`research/CANONICAL_SCIENTIFIC_TRUTH.md`, `research/papers/*`, `research/results/paper3/*`, `research/confirmatory/X3-A/*`, `rl/checkpoints/*`, `ablation/results/*`, `research/data/evaluator_benchmark/final_human_gold.csv`) was touched by either pass. This pass builds on, and does not revert, any of that prior work.

## 1. Evaluator (highest priority) — two real defects found and fixed

Read `services/evaluator/app.py` in full (concept detection, semantic score, cross-encoder verification and its calibration, bonus/mistake-penalty logic, mandatory cap, final composition) before changing anything, then probed it adversarially with real (non-mock) model inference.

**Defect 1 — misconceptions using correct terminology escaped penalty.** The mistake-penalty logic's reasoning-aware rule only fired when concept coverage was *also* low. An answer naming the right vocabulary but describing backwards/contradictory logic (reasoning_score in the evaluator's own documented "partial/weak reasoning" band, ~0.30–0.50) received neither the existing S2 dampening nor any penalty. Measured: a "hash-map lookups are O(n), slower than O(1) nested loops" claim (correct vocabulary, inverted and false complexity reasoning) scored 0.488 ("Average"). Fixed with a new, symmetric penalty tier (`services/evaluator/app.py::mistake_penalty`, +0.08) targeting exactly this quadrant; the same example now scores 0.408.

**Defect 2 — verbatim repetition inflated the reasoning score.** Restating an already-correct answer's sentences twice raised the cross-encoder reasoning_score from 0.375 to 0.494 with no new information — an input-length artifact, not a correctness signal. Fixed with `dedupe_repeated_sentences()`, applied only to the scoring path (the returned `candidate_answer`/`candidate_claims` fields stay verbatim, since they must reflect what the candidate actually said). Repetition now produces byte-identical scores at 1x/2x/3x.

**Regression check against real evidence, not re-tuning.** Both fixes were justified before being checked against any benchmark. Afterward, all 64 cases in the existing human-gold evaluator benchmark were re-scored with the fixed evaluator (`research/paper_strengthening/scripts/evaluator_v2_recalibration_check.py`, same question-clustered bootstrap methodology, seed, and B=2000 as the existing `reanalyze_evaluator_ablation.py`): Spearman ρ moved from **0.3812 to 0.3787** (both well inside each other's CI), with only 6/64 cases changing score at all (mean |Δ|=0.0075, max=0.08). This is a **null result on this metric**, reported honestly rather than as an improvement — the two fixes target failure modes this small, 8-question benchmark does not specifically probe.

**Not done:** re-weighting the composite toward R-only/S1+R, despite Table X (prior pass) already showing they correlate higher on this benchmark. CLAUDE.md already frames the full composite as intentionally "safety-hardened" against a benchmark this size; re-tuning weights to chase an 8-question correlation number is exactly what this task's instructions forbid ("do not introduce arbitrary weights... merely to improve a small test set"), so no such change was made.

**D1 benchmark:** re-inspected. Unchanged from the prior pass's finding — the statistical design (V14 protocol, 122-question eligible bank, 67 confirmatory) is finalized, but the actual answer-text content (93 answers across quality tiers) was never authored. No new generation artifact exists. Authoring ~93 technical answers single-handedly, with no independent calibration, risks exactly the construction-validity problems the 14-version protocol history worked to avoid. Documented as blocked, not attempted, per the task's own explicit fallback instruction.

Tests: `tests/unit/test_evaluator.py`, 11→16 tests, all passing with the real (non-mock) SBERT/FAISS/CrossEncoder models.

## 2. LLM feedback and follow-up — one contradiction-check gap closed, malformed-output recovery verified

**Feedback validator gap.** `_validate_feedback_output` checked LLM feedback against evaluator `missing_concepts` for contradiction (rejecting feedback that claims a missing concept was covered) but had no equivalent check against `incorrect_claims` — a misconception the evaluator flagged could be echoed back to the candidate as correct without being rejected. Fixed with a symmetric check (exact match, substring overlap, and narrative-phrase forms), mirroring the existing pattern exactly. 3 new tests.

**Malformed-output recovery.** `_extract_json_from_llm` was previously untested by name. Confirmed directly: it returns `None` (never raises) on empty strings, non-JSON prose, and truncated JSON. A new endpoint-level test patches `ModelRegistry` to simulate a loaded model returning unparseable garbage and confirms `POST /api/qwen/followup` still returns a well-formed 200 response via the deterministic fallback. No defect found — this closes a testing gap, not a behavioral one.

**Prompt-injection and follow-up validation** (from the prior pass, not repeated here): `_sanitize_for_prompt` and `_validate_followup_output` remain in place and pass their full test suite alongside this pass's additions.

Tests: `tests/unit/test_qwen_followup_feedback.py`, 42→44 tests, all passing (44/44 confirmed after this pass's additions).

## 3. Multimodal — no video exists; fusion already correctly separated; audio fix verified end-to-end

- **Video:** a repository-wide search for `mediapipe`/`video_engagement`/`facial`/`landmark` returns zero matches. This project's own architecture note ("No video/MediaPipe") is confirmed still accurate. There is nothing implemented to audit for robustness.
- **Fusion:** traced how audio-derived confidence/hesitation signals reach the rest of the system. They feed only the RL observation vector (used by the guardrail/PPO controller), never `services/evaluator/app.py`'s technical-correctness computation, which is fully code-isolated from any communication signal (the evaluator's own comment already states diagnostic metrics are "NEVER added as positive bonus to technical score"). The user's stated concern — an unreliable communication signal overwhelming technical correctness — does not apply to the current architecture. Verified, not fixed; no defect found.
- **Audio consistency:** confirmed the prior pass's WPM/WPS fix is exercised on the real production call path (`apps/backend/main.py`'s `transcribe_and_align` → `score_hesitation` call, not just an isolated unit test).

## 4. End-to-end reliability — session recovery implemented, not merely documented as absent

The prior pass identified, but did not fix, a genuine gap: `SESSIONS` (`apps/backend/main.py`) is an in-memory-only dict of live `InterviewOrchestrator` instances; a backend process restart loses every in-progress session, and `save_session()` only ever persisted coarse metadata (mode, topics, status), never enough to resume.

**Implemented this pass:**
- `InterviewOrchestrator.snapshot_state()` / `.restore_from_snapshot()` — captures/restores `self._state` plus the two mutable attributes not inside it (`self._question_queue`, `self._current_q_index`; the queue matters because follow-up questions get inserted into it directly, diverging from `self._state["questions"]`).
- A new `session_snapshots` SQLite table and `save_session_snapshot()` / `load_session_snapshot()` (`services/storage/database.py`), additive to the existing schema.
- Backend glue: `_snapshot_session()` (called after every state-mutating WebSocket message: start, voice_answer, code_submission, next_question, retry, skip_question) and `_try_restore_session()` (attempted when a reconnecting client's session_id is no longer in `SESSIONS`, before falling back to the existing "Session not found" error).

**Explicitly bounded, disclosed scope — not claimed as full fidelity.** Not restored: `_active_question_attempts` (in-progress retry state for the current question), `_attempt_counts`, `_timer_snapshot`, `_pre_attempt_state`, `_rl_adapted_turns`. A resumed session's current question resumes as freshly asked, not mid-attempt. This is a genuine, working capability for the main failure mode (a crash/restart between turns), not a complete state-machine restore.

**Tests (`tests/unit/test_session_recovery.py`, 9 new, all passing):** SQLite save/load round-trip (including overwrite-on-update and missing-session behavior); orchestrator-level round-trip, including a follow-up-injected queue (the one case that diverges from the plain question list) and a malformed-snapshot rejection test; and — the most direct test of the actual failure mode — a backend-glue round-trip that snapshots a real orchestrator, then calls `_try_restore_session` as if `SESSIONS` had just been cleared by a restart, against a temp database via `monkeypatch`.

**Not done:** a live-WebSocket-level integration test (connect, disconnect, reconnect, verify continuation) — the repository had no existing WebSocket TestClient test pattern for this endpoint to build on, and `apps/backend/main.py` has heavy import-time dependencies (evaluator models, Qwen, coding sandbox) that make a full live-server test a larger, separate undertaking than this pass's time allowed. The DB, orchestrator, and backend-glue layers are each tested directly and pass; the live-WebSocket layer is the one remaining, disclosed gap.

Other end-to-end items re-examined (not newly changed): "malformed-but-200 evaluator JSON" (prior pass: framing correction, no HTTP boundary exists), zero-word audio (prior pass: confirmed robust end-to-end).

## 5. Integrated regression verification

- `tests/unit/test_evaluator.py`: 16/16 passed (real models).
- `tests/unit/test_qwen_followup_feedback.py`: 44/44 passed.
- `tests/unit/test_session_recovery.py`: 9/9 passed (new file).
- `tests/unit/test_persistence_and_history.py` + `tests/unit/test_orchestrator.py`: 34/34 passed (checked for regressions from the `database.py`/`interview_orchestrator.py` changes).
- Full repository suite (`pytest -q`, `EVALUATOR_MOCK_MODE=1`): **328 passed, 1 failed, 510.6s.** The one failure is `test_stage11_5_coding_adaptation.py::test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics` — the same pre-existing, already-documented failure noted in CLAUDE.md's own gotchas (an RL-observation `time_norm` issue unrelated to speech/confidence scoring, confirmed by direct reading of the test in the prior pass). No new failure was introduced by this pass.

No PPO/reward/state/action code was touched. No frozen/confirmatory/held-out file was modified. No file from the concurrently-running PPO pass was edited.

## 6. What remains blocked, and why

- **D1 benchmark**: blocked on content-authoring construction validity (unchanged from the prior pass's assessment).
- **PDF generation**: still not feasible in this environment (no pandoc/wkhtmltopdf/weasyprint), and the project defers IEEE formatting until a venue is chosen.
- **Live-WebSocket session-recovery test**: the mechanism is implemented and tested at every layer below the live socket; a full connect/disconnect/reconnect integration test through a running server is the one remaining test gap for this feature.
- **Evaluator re-weighting toward R-only/S1+R**: deliberately not attempted — already-known, already-documented tradeoff (CLAUDE.md's "safety-hardened" framing), not re-litigated here without new evidence to justify overriding that decision.
- **CrossEncoder logical-robustness limitation**: one adversarial probe (a fluent but logically nonsensical answer using correct terminology, describing a mechanism that always returns the same index) scored 0.696 reasoning_score / 0.6944 final ("Good") — the cross-encoder itself, not the composition weights, appears to weight lexical/structural plausibility over deep logical entailment in at least this case. This is disclosed as a genuine limitation of the underlying model (whose training provenance is itself incomplete, per CLAUDE.md), not something fixable by reweighting or a cheap heuristic within this pass's scope.

## Files changed this pass

Modified: `services/evaluator/app.py`, `services/qwen/app.py`, `services/storage/database.py`, `agents/orchestrator/interview_orchestrator.py`, `apps/backend/main.py`, `tests/unit/test_evaluator.py`, `tests/unit/test_qwen_followup_feedback.py`, `research/paper_strengthening/FINAL_MANUSCRIPT_EVIDENCE_V2.md`, `research/paper_strengthening/CLAIM_LEDGER_SYSTEM_PAPER_V1.md`.

New: `tests/unit/test_session_recovery.py`, `research/paper_strengthening/scripts/evaluator_v2_recalibration_check.py`, `research/paper_strengthening/results/evaluator_v2_recalibration_check.json`, this report.

No commit, tag, push, or submission was made.
