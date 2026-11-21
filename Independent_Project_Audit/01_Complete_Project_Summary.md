# 01 — Complete Project Summary: PrepAIred

*Independent audit document. Produced 2026-11-13 from read-only inspection of the repository at `D:\Capstone_29_AUG\capstoneProject` (branch `workspace/human-eval-clean-push`, HEAD `9d5c528`). Tags: **VERIFIED FACT**, **OBSERVATION**, **INTERPRETATION**, **RECOMMENDATION**, **UNKNOWN**, carried over from the six underlying research passes in `Independent_Project_Audit/_research/`.*

---

## 3.1 Project Overview

**Name:** PrepAIred.
**Problem statement:** multimodal technical-interview preparation, with an adaptive-difficulty controller intended to keep question difficulty matched to a candidate's demonstrated skill in real time.
**Core functionality (VERIFIED FACT, implemented and running end-to-end):** a candidate logs in, starts a timed interview session (verbal or C-coding questions), answers by voice or code; the system transcribes/evaluates the answer, generates narrative feedback, decides the next question's difficulty, and produces a session report. An admin dashboard exists for session-level inspection.

**Main technical contribution, as actually evidenced (not as originally envisioned):** a composite, non-LLM answer-evaluation pipeline (SBERT + FAISS-rubric + a locally fine-tuned CrossEncoder) feeding a difficulty controller that combines a deterministic, priority-ordered **guardrail safety layer** with an optional **PPO policy**, deployed inside a Docker-sandboxed coding-evaluation path and a FastAPI/React application.

**Current completion status:** the *application* is substantially complete and functionally real (FastAPI backend with 19 routes including a live WebSocket interview loop; a non-trivial React SPA with a Monaco code editor, admin dashboard, and voice recorder; a hardened Docker C sandbox; SQLite persistence). The *research evidence* behind two of the three headline AI claims (the PPO difficulty controller's value-add, and the evaluator's correlation with human judgment) is, by the project's **own** internal audit, either explicitly withdrawn (PPO) or openly scoped as weak/exploratory (evaluator correlation ρ=0.3812). This is the central fact an external reviewer must hold in mind throughout this document: **the engineering is more mature than the research claims it was built to support.**

**Intended users:** the candidate (student/job-seeker practicing technical interviews) and an instructor/admin role (dashboard).

**Scope, as actually implemented:** C-language technical interviews (verbal + coding questions), audio-based confidence/hesitation measurement, no video/behavioral analysis (confirmed absent, §3.2/§3.4), simulation-only RL training (no real-user RL data).

---

## 3.2 Technology Stack

Only technologies independently confirmed in the running implementation are listed (source: `Independent_Project_Audit/_research/01_architecture_and_modules.md` §8, cross-checked against `requirements/*.txt`).

| Technology | Actual usage | Component | Implementation status | Verification source |
|---|---|---|---|---|
| WhisperX (+ faster-whisper backend) | Speech-to-text | `agents/audio/transcriber.py:46,167-168` | **Fully implemented**, with an automatic energy-based fallback (no transcript) if unavailable | VERIFIED FACT |
| pyannote.audio | Voice-activity segmentation | `agents/audio/transcriber.py:47-53` | Implemented, with a compatibility shim for a version-drifted API | VERIFIED FACT |
| praat-parselmouth | Prosodic feature extraction | `agents/audio/audio_features.py` | Implemented (not line-audited in depth) | OBSERVATION |
| MediaPipe / OpenCV (video) | — | — | **Absent — zero matches repo-wide** | VERIFIED FACT |
| SentenceTransformers — SBERT `all-MiniLM-L6-v2` | Semantic similarity (S1) | `services/evaluator/app.py:43` | Fully implemented, genuinely off-the-shelf | VERIFIED FACT |
| SentenceTransformers — CrossEncoder, local checkpoint `tuned_model2` | Reasoning score (R) | `services/evaluator/app.py:47` | Fully implemented; **partially fine-tuned derivative, incomplete provenance** (16.28% of weights differ from upstream `cross-encoder/ms-marco-MiniLM-L-6-v2`; training data/author unrecoverable) | VERIFIED FACT (code+hash) / OBSERVATION (fine-tune extent, from prior in-repo forensic tensor-diff) |
| FAISS (faiss-cpu) | Precomputed rubric-vector retrieval for scoring | `services/evaluator/app.py:37-67` | Fully implemented | VERIFIED FACT |
| Flask | Evaluator HTTP microservice | `services/evaluator/app.py:561-938` | Implemented but **likely dead/legacy at runtime** — the backend calls `evaluate()` as a direct Python import, not over HTTP | INTERPRETATION |
| Qwen (local GGUF, CPU) | Narrative feedback / hints / follow-up questions | `services/qwen/app.py:248-270` | Fully implemented; **never touches scoring** (confirmed: zero Qwen references in `services/evaluator/app.py`, score computed before any Qwen call) | VERIFIED FACT |
| Mistral | — | — | **Not present anywhere in the codebase** | VERIFIED FACT |
| Docker (C sandbox) | Untrusted code execution | `agents/coding_executor/coding_executor.py:130-460` | Fully implemented, hardened (`--net=none`, `--cap-drop=ALL`, non-root, read-only+tmpfs, resource limits); fails closed if Docker unreachable | VERIFIED FACT |
| SQLite (`data/prepaired.db`) | Persistence | `services/storage/database.py` | Fully implemented for writes; **admin dashboard reads from an in-memory dict, not this store** (see §3.3) | VERIFIED FACT + INTERPRETATION |
| FastAPI | Backend application server | `apps/backend/main.py` | Fully implemented, 19 routes incl. 1 WebSocket | VERIFIED FACT |
| React 18 + Vite | Frontend SPA | `apps/web/` | Fully implemented, non-trivial (live interview room, admin dashboard, Monaco editor, voice recorder) | VERIFIED FACT |
| Stable-Baselines3 PPO | Difficulty-adaptation policy | `rl/env/interview_env.py`, `rl/training/` | Fully implemented and trained (5 seeds); **its measurable contribution over a trivial constant action, under the safety shield, is not statistically distinguishable from zero on the project's own confirmatory test** (see §3.5, §3.7) | VERIFIED FACT (training) + VERIFIED FACT (the project's own confirmatory null result, `X3A-C001`) |
| Guardrails (deterministic safety shield) | Post-hoc override of any proposed difficulty action | `rl/guardrails.py`, `agents/orchestrator/interview_orchestrator.py:1529-1573` | Fully implemented; **does essentially all of the measurable adaptive work** per the project's own audit-replay finding | VERIFIED FACT |
| `EVALUATOR_MOCK_MODE` env var | Documented as the standard "fast/mock" test flag | CI, docker-compose, test docstrings | **Vestigial — set everywhere, read nowhere.** The real evaluator always loads real SBERT/FAISS/CrossEncoder models regardless of this flag | VERIFIED FACT (no consumer found anywhere) |

---

## 3.3 Architecture

**Request flow (candidate perspective, VERIFIED FACT, traced end-to-end):**
1. Login (`POST /api/login`) → session creation (`POST /api/sessions`) constructs an `InterviewOrchestrator` instance held in a process-global `SESSIONS[sid]` dict (`apps/backend/main.py`).
2. The live interview runs over a WebSocket (`/ws/interview/{session_id}`). Verbal answers go through `handle_voice_answer`; coding answers through `handle_code_submission` (`agents/orchestrator/interview_orchestrator.py`).
3. Each answer is scored by `_run_integrated_evaluator` → direct in-process call into `services/evaluator/app.py::evaluate()` (SBERT+FAISS+CrossEncoder composite) or, for code, by the Docker sandbox (`agents/coding_executor/`).
4. The orchestrator then runs a **two-phase** difficulty pipeline: a deterministic baseline warm-up (first 2-3 questions) followed by a guardrail-wrapped RL/heuristic phase (`_adapt_difficulty`). The RL policy (via `agents/strategy/hybrid_orchestrator.py`) is best-effort; if unavailable, a documented non-RL heuristic takes over. **Guardrails are applied unconditionally regardless of which source proposed the action.**
5. Narrative feedback, hints, and follow-up questions are generated by a local Qwen microservice, strictly downstream of the already-computed score — Qwen never adjusts `final_score`.
6. On completion, a session report is built from in-memory state and persisted to SQLite (`services/storage/database.py`).

**Key architectural findings not otherwise obvious from a directory listing:**
- **Fail-closed design, confirmed in two places independently:** if the evaluator is unavailable, the orchestrator does **not** fabricate a score — it rolls back the attempt and asks the candidate to retry (`interview_orchestrator.py:542-587`). If the Docker daemon is unreachable, the coding sandbox refuses to execute untrusted code rather than falling back to native execution (`coding_executor.py:166-186`). This is a genuinely evidence-respecting design choice, consistent with the project's stated "never invent results" principle, and it is implemented in code, not just asserted in documentation.
- **The admin dashboard does not read from the persisted database.** `/api/admin/*` routes iterate the process-local `SESSIONS` dict, not the SQLite `sessions`/`question_attempts` tables that `services/storage/database.py` actually writes to. This means the admin view only reflects sessions created since the backend process last restarted — a partial-wiring gap between "data is saved" and "the admin UI reads the saved data."
- **The evaluator's Flask HTTP API is likely dead weight at runtime.** `launch.py` starts it as a standalone process on port 5000, but `apps/backend/main.py` never calls it over HTTP — it imports `evaluate()`/`get_rubric()` directly as Python functions. The Flask server appears to be a legacy integration surface kept alive by the launcher but not actually exercised by the production request path.

---

## 3.4 Module-by-Module Implementation

*(Condensed; full line-level citations in `_research/01_architecture_and_modules.md`.)*

| Module | Purpose | Status | Key limitation found |
|---|---|---|---|
| `agents/orchestrator/interview_orchestrator.py` (2,299 lines) | Per-session runtime controller: question queue, follow-ups, scoring dispatch, difficulty adaptation, reporting | Fully implemented, degrade-gracefully pattern (every sub-agent import is `try/except`-guarded) | Nearly every cross-module call is wrapped in broad `except Exception: pass` — resilient, but a silently-broken dependency would not surface as an error without a log |
| `agents/audio/` (transcriber, prosody, confidence, hesitation, state-vector) | STT + prosodic confidence/hesitation signal extraction for the RL state vector | Fully implemented (WhisperX), with a genuine energy-based fallback mode if WhisperX fails | No video/behavioral component exists (confirmed absent, not merely unimplemented-by-omission — this was a deliberate scope decision per `docs/PROJECT_STATE.md`'s unresolved-decisions list) |
| `services/evaluator/app.py` (939 lines) | Composite answer scoring: `0.15·S1 + 0.35·S2_eff + 0.50·R` | Fully implemented, formula verified exactly against the project's documented spec | Stale header comment inside the file itself cites different "best tuned params" than the code actually uses — an internal documentation/code mismatch, independent of any external claim |
| `agents/coding_executor/` | Hardened Docker sandbox for C code | Fully implemented, fails closed | Re-compiles inside each per-test-case container in addition to an up-front compile-only check — a minor efficiency cost, not a correctness bug |
| `apps/backend` (FastAPI, 19 routes) | Session orchestration, API surface, WebSocket interview loop | Fully implemented | Admin endpoints read from an in-memory dict, not SQLite (see §3.3) |
| `apps/web` (React 18 + Vite) | Candidate-facing SPA, admin dashboard | Fully implemented, non-trivial | Exact backend-route-to-frontend-call mapping not exhaustively cross-checked in this audit (`apps/web/src/api.js` content not fully enumerated) |
| `rl/env/interview_env.py` + `rl/guardrails.py` + `rl/training/simulated_candidate.py` | PPO difficulty-controller training environment and post-hoc safety shield | Fully implemented, Gym-compliant, 5-seed multi-seed training genuinely performed | See §3.5 — the learned policy's measurable value over the guardrail layer alone is not established by the project's own confirmatory test |
| `services/storage/database.py` | SQLite persistence (`candidates`, `sessions`, `question_attempts`) | Fully implemented, WAL mode, foreign keys on | No standalone schema/migration file — `init_db()` is the sole schema definition |

---

## 3.5 Algorithms and AI Components

### Answer evaluation (`services/evaluator/app.py`)
```
S1 = mean over rubric targets of max cosine similarity (candidate sentence embeddings, SBERT) vs. rubric "semantic" vectors
S2 = fraction of rubric "concept" groups whose best-matching sentence similarity > 0.30  (FAISS-retrieved rubric vectors)
R  = clamp01( (CrossEncoder.predict(reference, candidate) − 0.20) / 0.70 )
S2_eff = S2            if R > 0.30
       = S2 × 0.60     otherwise   (anti keyword-stuffing dampener)
final_score = clamp01( 0.15·S1 + 0.35·S2_eff + 0.50·R ) + bonus − penalty, capped at 0.60 if a mandatory concept is missing
```
**VERIFIED FACT** (`services/evaluator/app.py:136-405`), exact match to the project's documented formula. The R-rescaling affine transform (`(raw-0.20)/0.70`) is an uncited, hand-set heuristic — no calibration script or data backs the three breakpoints it encodes (**OBSERVATION/INTERPRETATION**).

The CrossEncoder (`models/tuned_model2`, weight-file hash independently re-verified against the project's own canonical-truth document) is confirmed by a prior in-repo forensic tensor-diff to be **83.7% bit-identical** to the public `cross-encoder/ms-marco-MiniLM-L-6-v2` checkpoint, with **16.28%** of parameters (encoder layers 4–5, pooler, classifier) differing in a pattern consistent with a low-learning-rate fine-tune. A second, now-deleted checkpoint with different weights and a different validation Spearman existed, with no documented rationale for which one was kept. The fine-tuning data, procedure, and author are **not recoverable** from the repository or its git history. **This is "partially fine-tuned, incomplete provenance," not "off-the-shelf" — confirmed, not merely asserted.**

Qwen (local GGUF model) has **no role in scoring**: zero references to Qwen exist in `services/evaluator/app.py`; the backend computes `final_score` before any Qwen call exists in the call chain; `services/qwen/app.py` even regex-rejects any numeric "Score:"-looking text the LLM tries to generate, as an explicit score-leakage guard.

### RL difficulty controller (`rl/env/interview_env.py`, `rl/guardrails.py`)
- **State:** 6-D Box `[perf, avg_perf, confidence, hesitation, progress(t/T), difficulty/5]`, all in `[0,1]`. **Action:** Discrete(3) {Easier, Same, Harder}. **VERIFIED FACT**, matches the documented spec exactly.
- **Reward (hybrid, default):** `0.60·decision_component + 0.30·outcome_component + 0.10·shaping_component + stability_penalty + critical_consistency_bonus`, where `decision_component = +1/−1` for agreeing/disagreeing with a **hand-coded rule oracle** (`oracle_action_from_obs`, a 7-rule if/elif ladder). **Up to ~90% of the reward's structure is anchored to imitating that oracle**, not to an independently measured training-time outcome.
- **Training:** genuinely 5 seeds (42/123/456/789/999), 24,576 timesteps each, matching the project's stated multi-seed policy. Action distribution shifts, consistently across all 5 seeds, from near-uniform at the start of training to "Same"-dominant (≈50%) by the end.
- **Guardrails** (`rl/guardrails.py`): a deterministic, priority-ordered post-hoc safety shield (6 rules), active during **both** training and inference, applied *before* the reward is computed — meaning the policy is rewarded/penalized on the action actually taken *after* guardrail override, not its raw proposal.
- **The central, independently-corroborated finding:** on the project's own primary evaluation metric (persona-target tracking MAE), a rule-based **Heuristic** baseline (0.473) beats **every** PPO variant, including PPO+Guardrails (0.673–0.687). A trivial **constant-"Same" policy plus the same guardrails** reproduces the PPO+Guardrails MAE almost exactly. The project's own confirmatory, pre-registered test (`X3A-C001`, 40-persona held-out grid) reports a 95% CI of **[−0.0818, 0.0021]** for PPO's contribution beyond a constant action under the shield — classified by the project itself as **"no detectable PPO contribution beyond the shield in these checkpoints in this simulator,"** and explicitly states PPO is *more* volatile than the constant action under the same shield. This audit's own independent read of the raw-policy coordinate-sensitivity sweep corroborates this from a different angle: the trained policy's output is "Same" across the **entire range** of performance, confidence, hesitation, and progress when swept individually — only current difficulty (and the extreme low end of rolling average) moves it.
- **Conclusion (INTERPRETATION, synthesizing the above):** the guardrail layer, not the learned PPO policy, accounts for essentially all of the measurable adaptive behavior in the deployed system. This is the single most important scientific finding in the entire project, and it is the project's **own** finding — not something this audit is the first to notice.

### Question retrieval / Docker sandbox
Question selection is **rule-based** (difficulty/topic/type matching with anti-repeat logic), **not** FAISS-based — FAISS is used only by the evaluator for rubric-concept retrieval, a correction the project itself made and this audit confirmed. The Docker C sandbox is genuinely hardened (10 independent container-isolation flags, confirmed present in code) and fails closed when Docker is unreachable.

---

## 3.6 Data and Datasets

- **Question/rubric bank:** `data/questions/qns.json`, `data/rubrics/rubrics_final_clean.json` — curated JSON, not a database table.
- **RL training data:** entirely **simulated** (`rl/training/simulated_candidate.py`, a sigmoid performance model). No real-user interaction data is used for RL training or evaluation anywhere in the repository. **The project is explicit about this scope limitation and this audit found no contradiction of it.**
- **Human evaluator-benchmark data:** `research/data/evaluator_benchmark/final_human_gold.csv` — 64 rows, 3 raters per case, columns for each rater's score plus an adjudicated gold label. **This file contains no question text, no candidate-answer text, and no model-predicted score** — it is the human-judgment half of the correlation study only; the model's predictions for these same 64 cases live in a separate, not-independently-re-verified-in-this-pass result file. File hash independently recomputed and matched against the project's own canonical-truth manifest.
- **Train/evaluation separation:** the same CrossEncoder checkpoint is used both to score candidates **live in production** and to produce the human-correlation benchmark number — methodologically correct (you must validate the deployed scorer, not a proxy) but it also means the CrossEncoder's provenance gap is a single point of uncertainty affecting both production scoring and the validation study equally, not confined to one side.
- **A separate, unflattering, project-disclosed finding:** a trivial length-only baseline (word count) matches or slightly exceeds the derived CrossEncoder's correlation with the human gold labels on this benchmark (0.4897 vs 0.4825) — registered by the project's own claim registry, not suppressed.

---

## 3.7 Current Project Status

| Feature | Planned | Implemented | Tested | Verified (independent, this audit) | Remaining work |
|---|---|---|---|---|---|
| Voice-based interview (STT + prosody) | Yes | Yes | Yes (unit+integration) | Yes — confirmed real WhisperX pipeline, real fallback path | Length-bias / WER accuracy evaluation not done |
| C-code sandboxed execution | Yes | Yes | Yes | Yes — confirmed hardened, fail-closed | None material found |
| Composite answer evaluator | Yes | Yes | Partially (narrow unit tests + one correlation study) | Yes (code) / Partially (quality) | Length-bias probe, CrossEncoder provenance recovery, larger confirmatory human study (X2-C) |
| Qwen narrative feedback/hints/follow-ups | Yes | Yes | Not quantitatively | Yes (role confirmed: never scores) | No quality metric exists for Qwen's generated text at all |
| Guardrailed PPO difficulty controller | Yes ("RL improves adaptation") | Yes (trained, deployed) | Yes (sanity-checked, baseline-compared) | Yes — and the project's own confirmatory test finds **no detectable PPO value over the guardrail alone** | Reframe claims; investigate reward/evaluation-metric mismatch; resolve deployed-vs-evaluated checkpoint hash mismatch |
| Admin dashboard | Yes | Yes (UI) | Partially | Partially — reads stale in-memory state, not the DB | Wire admin reads to SQLite |
| IEEE paper | Yes (one paper) | **Two independent, non-reconciled paper tracks exist** (`paper/manuscripts/paper1-3` venue-targeted work vs. `final_deliverables/03_Research_Paper` guardrail-bug paper) | N/A | Confirmed both exist | Consolidate into one submission plan |
| Root `README.md` / `docs/PROJECT_STATE.md` currency | Yes | No | N/A | Confirmed **stale**: test-count badge (178 vs. a direct recount of 298), and headline human-validation figure (ρ=0.6975, the project's own documented superseded pilot, presented as current while the newer, completed, lower-correlation study is described as "pending") | Update immediately — lowest-cost, highest-visibility fix available |
