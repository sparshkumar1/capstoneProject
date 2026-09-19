# Claim-by-Claim Forensic Audit Matrix

**Audited Git Commit:** `9cfd34f`  
**Standard:** Every claim classified as SUPPORTED, PARTIALLY SUPPORTED, OUTDATED, NOT SUPPORTED, or UNKNOWN based on code and empirical assets.

---

## 1. Current Resume Claims

| Claim Text | Status | Evidence Path | Code Function / Asset | Verdict & Honest Scientific Framing |
|---|---|---|---|---|
| **"Built an adaptive technical interview system using reinforcement learning (PPO) to adjust question difficulty from a 6D candidate state based on performance and speech features."** | **SUPPORTED** | `rl/env/interview_env.py:151`, `agents/strategy/hybrid_orchestrator.py:84` | `InterviewEnv`, `HybridOrchestrator.suggest` | State is 6D (`perf, avg_perf, conf, hes, progress, diff`). Action space is Discrete(3). Speech features modulate RL pacing; they do NOT alter the technical score. |
| **"Added persistent candidate history and multiple retries with SQLite, storing past answers, scores, best attempts, and learning gaps across sessions."** | **SUPPORTED** | `services/storage/database.py:46-130`, `agents/orchestrator/interview_orchestrator.py:420` | `save_attempt`, `get_or_create_candidate` | Normalized tables in WAL mode. Voluntary retries pause turn progression; compound key deterministically recalculates `is_best = 1`. Follow-ups are isolated. |
| **"Built a DSA answer evaluation pipeline using SBERT, FAISS, and CrossEncoder for semantic similarity, concept matching, and reasoning-based answer evaluation."** | **SUPPORTED** | `services/evaluator/app.py:270-320` | `evaluate()` | Multi-signal weighting: $0.15 S_1 + 0.35 S_{2,\text{eff}} + 0.50 R$. CrossEncoder reasoning dampening ($R \le 0.30$) penalizes keyword stuffing by 40%. |
| **"Uses deterministic code evaluation in an isolated Docker sandbox."** | **SUPPORTED** | `agents/coding_executor/coding_executor.py:192-360` | `DockerCSandbox.compile_and_execute` | Enforces `--net=none`, `--cap-drop=ALL`, `--user 1001:1001`, `--read-only`, tmpfs, $128$MB RAM, $32$ PIDs, 2.0s timeout. Exit signals mapped deterministically. |
| **"Added rule-based follow-ups and local Qwen LLM feedback, using evaluator results and candidate history to provide candidate-specific feedback."** | **SUPPORTED** | `agents/orchestrator/interview_orchestrator.py:1580`, `services/qwen/app.py:577` | `_decide_and_inject_followup`, `_validate_feedback_output` | Socratic follow-up triggers on score < 0.80 or missing gaps (max 2 consecutive). Qwen feedback is grounded in structured evaluator claims and validated against boilerplate fluff. |

---

## 2. Old Resume Claims

| Claim Text | Status | Evidence Path | Reality in Codebase | Safe Scientific Framing |
|---|---|---|---|---|
| **"Refined RL policy convergence over 204,800 training steps using an optimized 6D behavioral-performance state vector and a custom reward function to eliminate premature difficulty escalation."** | **PARTIALLY SUPPORTED / HISTORICAL ARTIFACT** | `rl/training/retrain_quick.py:32`, `rl/env/interview_env.py:331` | Current training uses 300,000 steps. 204,800 was an early batch multiple (100 rollouts x 2048). Reward is hybrid ($0.60 R_{\text{dec}} + 0.30 R_{\text{out}} + 0.10 R_{\text{shp}}$). | State that initial convergence experiments ran over 204,800 steps, while current retrain harnesses use 300,000 steps for value stability. "Eliminates premature difficulty escalation" applies to simulation trajectories with guardrails. |
| **"Engineered a hybrid evaluation engine for C-language DSA, combining deterministic code sandboxing with SBERT embeddings and FAISS concept indexing to eliminate LLM grading hallucinations."** | **PARTIALLY SUPPORTED (WORDING)** | `services/evaluator/app.py`, `agents/coding_executor/` | The architecture completely removes the LLM from the scoring pipeline. | Say: *"removes the LLM from the technical scoring path"* or *"eliminates reliance on free-form LLM grading."* |
| **"Executed comprehensive ablation and sensitivity analyses... validating the systems architecture for submission to IEEE Access."** | **PARTIALLY SUPPORTED / IN DRAFT** | `docs/paper_draft_ieee*.md`, `ablation/results/` | Ablations exist in `ablation/` and `experiments/`. IEEE Access manuscript exists as an internal draft, but has NOT been submitted or accepted. | State that manuscripts and ablation results are formatted and prepared for submission to peer-reviewed indexed venues. |
