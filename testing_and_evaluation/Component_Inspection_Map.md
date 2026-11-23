# Component Inspection Map

Ground-truth module inventory, built by direct filesystem inspection in this session (not from documentation), cross-checked against `CLAUDE.md` and `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`. This is the basis for every test-priority decision in `Test_Strategy.md`.

## Candidate journey (as actually wired, not as originally proposed)

`apps/backend/main.py` (thin FastAPI/WebSocket dispatcher, no domain logic) → `agents/orchestrator/interview_orchestrator.py` (session hub, `asyncio.Lock`-serialized, sole state writer) → per-turn fan-out to:
- `agents/audio/*` (if voice answer: transcription, prosody, confidence/hesitation)
- `services/evaluator/app.py` (verbal answers) **or** `agents/coding_executor/coding_executor.py` (code submissions, Dockerized sandbox)
- `agents/strategy/hybrid_orchestrator.py` (PPO policy wrapper) + `rl/guardrails.py` (post-inference overrides)
- `agents/orchestrator/feedback_agent.py` (+ `services/qwen/app.py` for LLM-generated hints/follow-ups/partial credit when triggered)
- `agents/question_selector/question_selector.py` (next question via FAISS)
- `agents/orchestrator/logger.py` (+ `services/storage/*`, SQLite `data/prepaired.db`)

## Module table

| Module | File(s) | Purpose | Inputs | Outputs | Dependencies | Status | Criticality | Existing test coverage |
|---|---|---|---|---|---|---|---|---|
| Orchestrator | `agents/orchestrator/interview_orchestrator.py` | Session state hub, baseline+RL+guardrail pipeline (`_adapt_difficulty`), follow-up injection | WebSocket events (voice_answer, code_submission, next_question, request_hint, skip_question, end_session) | Session state, reports | evaluator_fn, select_questions_fn (injected) | **Implemented** | Critical | `tests/unit/test_orchestrator.py`, `tests/unit/test_persistence_and_history.py`, `tests/unit/test_stage11_3..6_*.py`, `tests/integration/test_full_interview_lifecycle.py` |
| FeedbackAgent | `agents/orchestrator/feedback_agent.py` | 15-field structured feedback, misconception detection, trend tracking | Evaluated turn data | Feedback dict | Qwen (conditional) | **Implemented** | High | `tests/unit/test_qwen_followup_feedback.py`, `test_qwen_specific_feedback.py` |
| Logger | `agents/orchestrator/logger.py` | Turn/session persistence | Turn records | `turns.jsonl`, `summary.json` | `services/storage` | **Implemented** | Medium | `tests/unit/test_persistence_and_history.py` |
| Evaluator | `services/evaluator/app.py` | `score = 0.15·S1 + 0.35·S2_eff + 0.50·R` (+bonus/penalty, caps); `S2_eff = S2` if `R>0.30` else `0.6·S2` | Transcript, rubric | Score, breakdown, covered/missing concepts | SBERT, FAISS, CrossEncoder (`models/tuned_model2`) | **Implemented, verified against canonical truth and code** | Critical | `tests/unit/test_evaluator.py`, `test_evaluator_outage_and_sandbox_cleanup.py` |
| Coding Executor | `agents/coding_executor/coding_executor.py`, `sandbox_policy.py` | Docker C sandbox exec, test-case pass/fail, complexity/sanity analysis | Submitted code | Pass/fail, runtime, canonical score | Docker (`Dockerfile.sandbox`) | **Implemented** | High | `tests/unit/test_coding_executor.py`, `test_stage11_4_coding_verification.py`, `test_stage11_5_coding_adaptation.py` |
| Audio Analysis | `agents/audio/{transcriber,audio_features,nlp_analyzer,hesitation_scorer,confidence_scorer,rl_state_vector,tone_analyzer,audio_io,recorder,output_formatter,main}.py` | Whisper/faster-whisper STT, Librosa prosody, filler/hedge detection, confidence+hesitation scalars | Audio blob | `confidence_score`, `hesitation_score` ∈[0,1], transcript | OpenAI Whisper, Librosa | **Implemented**. No video/MediaPipe anywhere in repo. | High | `tests/unit/test_speech_pipeline.py`, `test_backend_audio_warmup.py` |
| Question Selector | `agents/question_selector/question_selector.py` | Nearest-difficulty match over 125-question bank (`data/questions/qns.json`) + FAISS | Target difficulty, topic | Next question | FAISS index | **Implemented**. `bloom_level` (L1–L6) is descriptive metadata only, not used in selection. | High | Covered indirectly via orchestrator/e2e tests; no dedicated unit test file found |
| Strategy/RL Agent | `agents/strategy/hybrid_orchestrator.py` | PPO inference wrapper: build 6-D state → VecNormalize → `model.predict(deterministic=True)` → map action → heuristic fallback if checkpoint missing | Score, session state | Action (Easier/Same/Harder per `CLAUDE.md`'s 3-action spec — **capstone report's 5-action Hint/Follow-up-as-RL-action claim needs direct code read to confirm or correct**, see open item below), new difficulty | `rl/checkpoints/seed_123/{ppo_final.zip,vecnormalize.pkl}` (frozen, real) | **Implemented** | Critical | `tests/unit/test_rl_env.py`, `test_paper3_blockers.py` |
| Guardrails | `rl/guardrails.py` | Post-inference deterministic override rules (G-series) | Raw PPO action, state | Possibly-overridden action | — | **Implemented, frozen** (do not modify without approval) | Critical — this is the component Paper 3 identified as doing essentially all of the measured improvement over Fixed, not PPO | Covered via `test_paper3_blockers.py`; no isolated guardrail unit-test file found as a dedicated module |
| RL Environment | `rl/env/interview_env.py` | Custom Gymnasium env for training/eval | — | — | Gymnasium, SB3 | **Implemented, frozen** | High (training/eval infra, not live-session path) | `tests/unit/test_rl_env.py` |
| Simulated Candidate | `rl/training/simulated_candidate.py` | Synthetic candidate response generator for RL training/eval | Persona params | Simulated scores/signals | — | **Implemented, simulation-only** | Medium | Indirect, via `test_rl_env.py`/`test_paper3_blockers.py` |
| Score Validator | `agents/validation/score_validator.py` | Post-hoc score correction rules (mandatory_cap, mistake_penalty, coding_failure_multiplier) | Raw score, rubric evidence | Corrected score | — | **Implemented** | High | `tests/unit/test_score_validator.py` |
| Timer | `agents/timing/timer.py` | Session/question timing, `time_norm` feature | — | Normalized time ∈[0,1] | — | **Implemented** | Medium | `tests/unit/test_timer_scoring.py` |
| Qwen service | `services/qwen/app.py` | Local Qwen2.5-1.5B-Instruct (GGUF, `models/gguf/`) microservice: hints, follow-ups, partial credit | Question+answer context | Generated text/score | GGUF model file | **Implemented, local, not Mistral** (per `CLAUDE.md`) | High | `tests/unit/test_real_qwen_inference.py`, `test_qwen_followup_feedback.py`, `test_qwen_specific_feedback.py` |
| Storage | `services/storage/{database,analytics,best_answer}.py` | SQLite persistence (`data/prepaired.db`), analytics queries, best-answer tracking | Session/turn records | Query results | SQLite | **Implemented** | High | `tests/unit/test_best_answer_authority.py`, `test_persistence_and_history.py` |
| Backend dispatcher | `apps/backend/main.py` | FastAPI/WebSocket event routing only, no domain logic | WS JSON events | Routed calls to orchestrator | — | **Implemented, thin by design** | Critical (single point of entry) | Exercised indirectly by integration tests |
| Frontend | `apps/web/src/*` (React+Vite) | Interview Room, Session Report views | WebSocket | UI | — | **Implemented** | High (user-facing) | `apps/web/src/__tests__/*.test.jsx` (4 files: best_answer_authority, layout, question_progress, ui_fixes) |
| Video/behavioral (MediaPipe) | — | — | — | — | — | **Not implemented, not present anywhere in repo** | N/A | N/A |
| Strategy+Coaching MAS / arbitration layer | — | — | — | — | — | **Not implemented** — see `reference_material_analysis/Springer_Paper_Content_Analysis.md` | N/A | N/A |

## Resolved item: RL action-space size

**Checked directly in this session** (`agents/strategy/hybrid_orchestrator.py:8-47,278-281`): the PPO policy's action space is confirmed `Discrete(3)` = {0: Easier, 1: Same, 2: Harder} — `ACTION_MAP`/`ACTION_NAME_TO_IDX` are hard-coded to exactly these three, and the checkpoint-loader explicitly rejects any checkpoint whose `action_space` is not `Discrete(3)`. This matches `CLAUDE.md` exactly. `revised_report_v5.pdf` Table 4.3's claim of a 5-action RL space including Hint/Follow-up **does not match the code** — this is a fifth confirmed discrepancy in that report (added to `reference_material_analysis/Previous_Project_Report_Analysis.md` §3). Hint/Follow-up, where they occur, are triggered by the guardrail layer and FeedbackAgent, not by the PPO policy's own action selection.

## Test infrastructure present

- `tests/unit/` — 21 files; `tests/integration/` — 4 files (25 Python test files total).
- `apps/web/src/__tests__/` — 4 frontend test files (Vitest, based on `apps/web/src/test/setup.js`).
- **No `conftest.py`** anywhere in `tests/`.
- 21/25 Python test files use `pytest`-specific features (fixtures/marks) — not runnable under plain `unittest`.
- **`pytest` and `pytest-asyncio` are listed in `requirements/dev.txt` but are not installed in `.venv`** (confirmed via `python -m pip list` and `python -m pytest --version` → `No module named pytest`). This blocks the documented baseline command (`EVALUATOR_MOCK_MODE=1 .venv/Scripts/python.exe -m pytest -q`) until installed — see the blocker note in the Phase 2 chat summary.
- Only one audio fixture exists repo-wide: `tests/test_candidate_hash_table_answer.wav`. No reference-transcript dataset exists for WER/CER measurement — speech-transcription accuracy testing is infeasible without new, verified reference data (do not fabricate this).
- Human evaluation benchmark: `research/data/evaluator_benchmark/{benchmark_cases.json, benchmark_dataset.csv, final_human_gold.csv}` — 64 constructed answers to 8 questions, 3 raters (frozen, per `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §C.1). Usable for answer-evaluation correlation testing; already analyzed, not to be re-labeled as new.
- Question bank: `data/questions/qns.json` (125 questions) + `data/rubrics/rubrics_final_clean.json` (125 matching rubrics). Usable for retrieval/coverage testing.
- RL checkpoint: `rl/checkpoints/seed_123/{ppo_final.zip, vecnormalize.pkl, retrain_log.csv}` — the real, frozen, deployed policy. Usable for policy-behavior inspection (inference only — no retraining).
- Docker: `Dockerfile.{backend,evaluator,frontend,qwen,sandbox}` + `docker-compose.yml` all present — usable for compatibility/deployment smoke checks.
