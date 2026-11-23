# Previous Project Report Analysis

**Source document:** `Details/revised_report_v5.pdf` — PES University, Dept. of CSE, "PrepAIred: A Reinforcement-based LLM-powered Interview Preparation System", UE23CS320B Capstone Project Phase-2, submitted by Sparsh Kumar, Naveen S Khadd, Manasa S A, Athreya Shashidhara, guide Dr Uma D, Jan–May 2026. 48 printed pages (56 physical), 8 chapters, 7 tables, 5 figures, 10 references.

This is the **real, officially-submitted Phase-2 report** (real names, real guide, real certificate) — materially different in status from the anonymous Springer-style draft analyzed separately in `Springer_Paper_Content_Analysis.md`. Most of its content is well-grounded in the actual codebase. A few sections contain numbers that do not trace to the project's own canonical truth document or to any file in the repository. These are flagged below so Task 2 (the Phase-3 report, which will build on this one) does not inherit them silently.

## 1. Structure (for reuse as the Phase-3 report's starting skeleton)

| Chapter | Pages | Content |
|---|---|---|
| 1 | 1 | Introduction |
| 2 | 2–4 | Literature Survey (6 papers + 1 comparison table) |
| 3 | 5–7 | System Architecture (5 logical layers, tech stack) |
| 4 | 8–24 | Methodology (evaluator, RL/Strategy agent, guardrails G1–G6, baseline phase, audio agent, feedback agent, coding evaluator, logger) |
| 5 | 25–35 | Implementation (orchestrator concurrency/DI/state/termination, evaluator pipeline, feedback agent, RL agent, FastAPI dispatch, React frontend, logger) |
| 6 | 36–44 | Results (evaluator calibration grid search ×2, CrossEncoder fine-tuning ×2, evaluator result table, ablation study) |
| 7 | 45–47 | Conclusion, Limitations, Future Work |
| 8 | 48 | References (10, mixed — adaptive testing/RL curriculum literature + PPO/SBERT/FAISS papers) |

Front matter (title, certificate, declaration, acknowledgement, abstract, TOC, list of tables, list of figures) occupies physical pages 1–8 and is **course-specific** (UE23CS320B, Phase-2, Jan–May 2026 term) — it must be regenerated for Phase-3 using the blank templates in `Details/Report initial Pages(Pg 1-10)/` (course code UE23CS441A, term "August – Dec, 2026"), not copied from this report.

## 2. Content verified as accurate against the current codebase

- Five-layer architecture (Candidate / Input Analysis / Orchestration / Evaluation / Strategy-Feedback), orchestrator-as-sole-state-writer design, `asyncio.Lock` concurrency model, dependency-injection pattern for the evaluator/question-selector, idempotent `end()` — all consistent with `agents/orchestrator/interview_orchestrator.py` as described in `CLAUDE.md`.
- Evaluator weighting **0.15·S1 + 0.35·S2 + 0.50·R** (Table 4.1, §4.1.5) — matches `services/evaluator/app.py:377-383` and `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §A exactly.
- Six-dimensional RL state vector — consistent with `CLAUDE.md` and `research/audit/rl_state_definition.md`. Guardrails G1–G6 trigger-condition table — structurally plausible, not line-by-line re-verified against `rl/guardrails.py` in this pass.
- **Confirmed wrong (checked directly against code in Phase 2, `testing_and_evaluation/Component_Inspection_Map.md`)**: Table 4.3's 5-action RL space (Easier/Same/Harder/Hint/Follow-up). `agents/strategy/hybrid_orchestrator.py:46-47,278-281` hard-codes `Discrete(3)` = {Easier, Same, Harder} and explicitly rejects any checkpoint with a different action space. Hint/Follow-up are not PPO-selected actions. Matches `CLAUDE.md`, contradicts this report. Add to §3 below as a fifth confirmed discrepancy.
- Technology stack table (FastAPI/uvicorn, SB3 PPO, SBERT all-MiniLM-L6-v2, FAISS, CrossEncoder ms-marco-MiniLM-L-12-v2, Whisper, Librosa) — consistent with `CLAUDE.md`.
- Fifteen-field feedback schema, misconception dictionary via substring matching, trend tracking (±0.08 threshold) — plausible implementation detail, not independently re-verified line-by-line in this pass but internally consistent and architecturally sound.

## 3. Content that does NOT trace to any stored artifact — do not repeat without verification

### 3.1 PPO training scale (Abstract, Ch.1, Ch.4.2.4, Ch.7.1)
Report states: PPO trained **"over 500,000 simulated steps"**, three seeds **(42, 123, 777)**, production policy = seed 123.
`CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §D.1 (the project's sole authority on verified metrics) states the frozen Paper-3 study used **24,576 timesteps per training seed**, seeds **42/123/456/789/999**, and explicitly lists **"300,000 PPO steps"** as a withdrawn/superseded figure in other documents (§H). "500,000 steps" is not listed anywhere in canonical truth, frozen results, or any file found by search in this session. The seed set (42,123,777) also does not match the frozen study's seed set. **Do not carry "500,000 steps" or seeds (42,123,777) into the Phase-3 report or IEEE paper without first locating a stored artifact that supports them** — if none exists, use the canonical 24,576-steps/5-seed figures instead, or mark the discrepancy explicitly as unresolved.

### 3.2 Evaluator fallback chain module paths (§5.2, §5.2.3)
Report describes a "four-level fallback chain": `qwen_integration/evaluate_upgraded.py` → `Evaluator_final/Evaluator/evaluate.py` → legacy rule-based → word-count heuristic, with a Qwen partial-credit trigger at `S1 > 0.40 AND S2 < 0.60`.
Neither `qwen_integration/` nor `Evaluator_final/` exists anywhere in the repository or in git history (`git log --all` for these paths returns nothing). The actual special-case rule in `services/evaluator/app.py:377` is `effective_S2 = S2 if R > 0.30 else S2*0.60` — a different condition on different variables (R-gated S2 dampening, not an S1/S2-gated Qwen partial-credit call). **This section's module names and the specific partial-credit trigger condition should not be reused in Task 2 without a source-code citation**; the real fallback behavior (if any beyond the single `app.py` path) needs to be verified in Task 1.

### 3.3 Chapter 6.6 "Ablation Study: Difficulty Adaptation Conditions"
Reports a 4-condition ablation (PPO+Guardrails / PPO Only / Heuristic Only / Fixed Difficulty) over "400 total evaluated question-answer turns," with an "adaptation Spearman ρ" between score at turn *t* and difficulty at *t+1* (ρ=0.580, p=3.14×10⁻¹⁰ for the full system; 0.342; 0.104; N/A for the four conditions respectively) and session-mean scores 0.620/0.568/0.540/0.500.
**None of these specific figures appear in `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §D.2**, which instead documents a *different* frozen Paper-3 ablation using **Tracking MAE and volatility** as the metrics (Fixed 1.200 MAE; Heuristic 0.473; PPO+guardrails five-seed mean 0.677 MAE), not an adaptation-correlation metric with p-values. The methodology style (cluster-style p-values, condition hierarchy, "guardrail contribution" framing) closely resembles the XA/XC experiments in the separate, independently-confirmed-fictional Strategy/Coaching paper (see `Springer_Paper_Content_Analysis.md`) rather than anything in this project's own Paper-3 artifacts. **This entire section's numbers should be treated as unverified pending a Task-1 check for a stored artifact; if none is found, do not reuse them in Task 2/3.**

### 3.4 Chapter 6.1–6.4 (evaluator calibration grid search, CrossEncoder fine-tuning experiments)
These describe grid-search calibration (Experiments 1 & 2, MSE 0.05046 → 0.04835) and CrossEncoder fine-tuning (300→600 instances, Spearman 0.61→0.79) run on "Kaggle infrastructure using an NVIDIA Tesla T4 GPU." No corresponding stored config/result file was located in this pass (not exhaustively searched — Task 1 should check `research/results/`, `ablation/results/`, and any Kaggle-notebook exports before reuse). The CrossEncoder provenance description here ("partially fine-tuned... layers 4–5, pooler, classifier head trainable") is **directionally consistent** with `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §B's "partially fine-tuned derivative... layers 4–5, pooler and classifier head changed" — this part appears genuinely grounded, unlike §3.1–3.3 above. The specific MSE/Spearman numbers and the multi-source (Claude/Gemini/Perplexity/ChatGPT/DeepSeek) 600-instance dataset composition still need a stored-artifact citation before reuse.

### 3.5 RL action-space size (§4.2.2, Table 4.3)
Report claims a 5-action RL space (Easier/Same/Harder/Hint/Follow-up) selectable by the PPO policy. Code (`agents/strategy/hybrid_orchestrator.py:46-47,278-281`) confirms `Discrete(3)` = {Easier, Same, Harder} only; the checkpoint loader rejects any other action-space shape. **Do not reuse the 5-action framing in Task 2**; use `Discrete(3)` and describe Hint/Follow-up as guardrail/FeedbackAgent-triggered, not RL-selected.

### 3.7 Evaluator microservice framework (Table 3.1: "Evaluator microservice | FastAPI (port 5000)")
**Checked directly against code (Phase 2):** `services/evaluator/app.py:582` is `app = Flask(__name__) if FLASK_AVAILABLE else Flask()` — it is a **Flask** application with `@app.route(...)` handlers (`/health`, `/api/evaluator/set-question`, `/api/evaluator/evaluate-answer`, `/api/evaluator/last-result`, `/api/evaluator/current-question`), not FastAPI. By contrast, `services/qwen/app.py:314` genuinely is `FastAPI(title="PrepAIred Qwen Service", ...)` with real `@app.post`/`@app.get` routes — the Qwen service's framework claim is correct. **Do not describe the evaluator as FastAPI in Task 2/3**; it is Flask. This affects which test-client pattern Task 1 testing must use for each service (Flask's `test_client()` for the evaluator, `fastapi.testclient.TestClient` for Qwen and the backend).

### 3.6 Question retrieval mechanism (Fig. 3.1, Fig. 4.2, §3.2.5 — "QnSelector Agent retrieves the next question from the Faiss VectorStore")
**Checked directly against code (Phase 2):** `agents/question_selector/question_selector.py` has **zero FAISS or embedding dependency** (confirmed by inspecting every import — only `json`, `os`, `random`, `collections.defaultdict`). The real selection logic is purely rule-based: `nearest_difficulty()` (closest float match against the question bank's discrete difficulty values), `get_valid_topics()`/`select_topic()` (least-recently-asked topic rotation with a per-topic session cap and no-immediate-repeat rule), `select_question_from_topic()` (random choice among not-yet-asked questions in the matched topic+difficulty bucket). **There is no semantic retrieval anywhere in question selection.** The FAISS index that does exist in the repo (`logic_vectors.faiss`, `logic_metadata.pkl`) is used exclusively by the **evaluator** (`services/evaluator/app.py`) for S2 concept-coverage scoring of candidate *answers* against rubric concept groups — not for selecting *questions*. **Do not describe question selection as FAISS/vector-retrieval-based in Task 2/3**; describe it accurately as difficulty-nearest-match + topic-rotation. This is the sixth confirmed discrepancy between this report and the actual codebase.

## 4. Literature survey (Ch.2) reuse assessment

Six cited works (Wu et al. 2026, Karjus et al. 2026, Mendonça et al. 2025, Wang et al. 2025 "AutoSCORE", Microsoft Research 2026 "Argos", Lishitz et al. 2025, Zhu et al. 2025 "MultiAgentBench", Auctores Online 2025) plus a comparison table (Table 2.1). These are the **same literature-positioning narrative style** as the separately-analyzed Springer paper's Related Work section, but applied here to real claimed system capabilities (adaptive difficulty, structured feedback, multimodal signals) rather than the fictional MAS layer. Citations were not independently verified against Zotero/live sources in this pass — flag as `[CITATION TO VERIFY]` per `CLAUDE.md`'s rule before reuse in Task 2/3, since several of these (2026-dated papers, "Argos" from Microsoft Research) are unusual enough to warrant a direct check.

## 5. Recommended handling for Task 2

- **Reuse directly**: Chapters 1, 3, 5 (architecture/implementation prose), the technology stack table, the fifteen-field feedback schema, the guardrail rule table (after independently re-confirming action-space size against code), Chapter 7's honest limitations list (synthetic evaluation only, static question bank, substring-based misconception detection, partial baseline resolution, 2/15 fields live in UI) — these limitations are themselves valuable, truthful content.
- **Verify before reuse**: §3.1–3.4 above (PPO step count, evaluator fallback module paths, the Ch.6.6 ablation numbers, the Ch.6.1–6.4 calibration/fine-tuning numbers) and the six literature citations.
- **Do not reuse unmodified**: any sentence that states these unverified numbers as established fact without a `[stored artifact path]` citation.
