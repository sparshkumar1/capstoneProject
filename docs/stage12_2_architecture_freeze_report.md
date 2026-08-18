# STAGE 12.2 — FINAL PRE-RESEARCH ARCHITECTURE & FALLBACK VERIFICATION REPORT

**Status:** Complete & Fully Verified
**Date:** 2026-08-16
**Final Verdict:** `FINAL PRE-RESEARCH FREEZE: PASS`

---

## 1. Qwen Fallback Exact Behavior

When the Qwen microservice or local Ollama backend is unavailable:
1. **Follow-Up Generation:**
   - The system executes `_synthesize_structured_followup` grounded strictly in Stage 1 Evaluator evidence (the candidate's identified missing concepts or misconceptions).
   - It outputs a targeted probe question explicitly tagged with `decision_source = "non_llm_structured_recovery"` and `llm_status = "llm_unavailable"`.
   - The follow-up question is injected into the session queue without making false claims of LLM generation.
2. **Feedback Generation:**
   - `FeedbackAgent` executes deterministic rubric-grounded feedback using the candidate's exact transcript, covered concepts, missing concepts, word count, and evaluator score breakdown.
   - It outputs structured feedback explicitly tagged with `decision_source = "non_llm_structured_recovery"` and `llm_status = "llm_unavailable"`.
   - Evaluator scores ($S_1, S_2, R$) are preserved verbatim without alteration.
3. **Candidate State:**
   - Updates candidate session state (`scores`, `concepts_missed`, `concepts_mastered`, `communication_indicators`) solely from genuine evaluator and acoustic measurements. No fake metrics are written to candidate state.

---

## 2. Qwen Attribution Verification

| Mode | Microservice / LLM State | `decision_source` | `llm_status` | Claim of LLM Generation |
|---|---|---|---|---|
| **Live Follow-Up** | Qwen-1.5B loaded & inferred | `"qwen_1.5b_llm"` | `"available"` | Genuine LLM generation |
| **Live Feedback** | Qwen-7B loaded & inferred | `"qwen_7b_llm"` | `"available"` | Genuine LLM generation |
| **Offline Structured Recovery** | Model unloaded / offline / unreachable | `"non_llm_structured_recovery"` | `"llm_unavailable"` | **No LLM claim** (explicit deterministic recovery) |
| **Feedback Agent Offline** | Port 8001 unreachable | `"non_llm_structured_recovery"` / `"evaluator_structured"` | `"llm_unavailable"` | **No LLM claim** (evaluator evidence preserved) |

*Invariant Verified:* `decision_source` NEVER begins with `qwen_*_llm` when Qwen was unavailable.

---

## 3. Authoritative Question Selector

- **Authoritative Production Path:** [`apps.backend.main.select_questions`](apps/backend/main.py)
- **Callers in Production:**
  1. `InterviewOrchestrator.__init__` (initial session question queue generation)
  2. `InterviewOrchestrator._rebuild_remaining_questions` (dynamic queue rebuilding upon PPO difficulty adjustments)
- **Capabilities:**
  - Level 1 Deduplication: Exact question ID filtering (`seen_ids`)
  - Level 2 Deduplication: Normalized text filtering (`seen_texts`)
  - Level 3 Deduplication: Jaccard lexical token overlap filter ($\ge 0.75$) against entire session history
  - Alternating format buckets (`verbal`, `code`)
  - Remediation boost for candidate weaknesses / advancement probe for strengths
  - Guaranteed Easy constraint ($\le 2$) on Question 1.

---

## 4. Baseline Question Selector Classification

- **Path:** [`agents/question_selector/question_selector.py`](agents/question_selector/question_selector.py)
- **Classification:** **`BASELINE / RESEARCH`**
- **Role:** Preserved early baseline implementation (topic-count limiting + nearest-difficulty matching) used for experimental baseline comparison against the adaptive production selector.
- **Runtime Isolation:** Never invoked by `InterviewOrchestrator` or `apps/backend/main.py` in the production call graph.

---

## 5. RL Attribution Matrix

| Session Phase | Scenario | `decision_source` | `rl_status` | `raw_rl_action` | `guardrail_applied` |
|---|---|---|---|---|---|
| **Warmup** | Baseline questions 1–3 | `"baseline_warmup"` | `"baseline_warmup"` | `None` | `None` |
| **Adaptive RL** | PPO policy active & valid | `"ppo"` | `"available"` | `"Easier"` / `"Same"` / `"Harder"` | `None` |
| **Guardrail** | Safety override triggered | `"guardrail_gX"` | `"available"` | Original PPO action | `"guardrail_gX"` |
| **RL Unavailable** | Checkpoint missing / error | `"non_rl_heuristic_recovery"` | `"rl_unavailable"` | `None` | `None` |

*Invariant Verified:* Heuristic recovery is NEVER labeled as PPO.

---

## 6. Exact 6D RL Observation Space

The observation space is strictly 6-dimensional, bounded in $[0.0, 1.0]$:

$$\mathbf{s} = \begin{bmatrix}
\text{performance} & [0.0, 1.0] \\
\text{average\_performance} & [0.0, 1.0] \\
\text{confidence} & [0.0, 1.0] \\
\text{hesitation} & [0.0, 1.0] \\
\text{time\_norm} & [0.0, 1.0] \\
\text{difficulty} & [0.0, 1.0]
\end{bmatrix} \in \mathbb{R}^6$$

- `performance`: Latest question evaluation score.
- `average_performance`: Rolling average of last 5 question scores.
- `confidence`: Acoustic/lexical confidence score from speech pipeline.
- `hesitation`: Acoustic pause/filler rate ($1.0 - \text{conf}$).
- `time_norm`: Normalized response latency ($\text{clip}(t_{\text{elapsed}} / t_{\text{allowed}}, 0, 1)$).
- `difficulty`: Normalized current difficulty level ($\text{diff} / 5.0$).

*Separation Guarantee:* Coding sandbox execution time (`execution_time_ms`) is tracked strictly in candidate state and is **never** injected into `time_norm` or the 6D observation vector.

---

## 7. Exact RL Action Space

$$\mathcal{A} = \text{Discrete}(3) = \{0: \text{Easier},\ 1: \text{Same},\ 2: \text{Harder}\}$$

---

## 8. Timer & Scoring Formula

Authoritative formula implemented in [`agents/timing/timer.py`](agents/timing/timer.py) and specified in [`docs/SCORING.md`](docs/SCORING.md):

$$S_{\text{final}} = \text{clip}\Big( S_{\text{tech}} + f_{\text{time}}(\tau, S_{\text{tech}}),\ 0.0,\ 1.0 \Big)$$

$$f_{\text{time}}(\tau, S_{\text{tech}}) = \begin{cases}
+ \min(\delta_{\text{fast}},\ \delta_{\text{fast}} \cdot S_{\text{tech}}) & \text{if } \tau \le \theta_{\text{fast}} \text{ and } S_{\text{tech}} \ge \theta_{\text{score}} \\
0.0 & \text{if } \theta_{\text{fast}} < \tau \le 1.00 \\
- \delta_{\text{overrun}} \cdot \min(1.0,\ \tau - 1.0) & \text{if } \tau > 1.00
\end{cases}$$

- $\delta_{\text{fast}} = 0.03$ ($+3\%$)
- $\delta_{\text{overrun}} = 0.10$ ($-10\%$)
- $\theta_{\text{fast}} = 0.50$
- $\theta_{\text{score}} = 0.70$
- Range: $f_{\text{time}} \in [-0.10, +0.03]$
- Invariant: $S_{\text{tech}} < 0.70 \implies f_{\text{time}} \le 0.0$ (Fast Wrong answers never receive a speed bonus).

---

## 9. Production vs Research Boundary

| Category | Directory / Files | Description |
|---|---|---|
| **PRODUCTION** | `apps/backend/`, `apps/web/`, `agents/orchestrator/`, `agents/strategy/`, `agents/timing/`, `services/evaluator/`, `services/coding/`, `services/transcription/` | Real application runtime, evaluator engine, Docker sandbox, WhisperX STT, PPO inference, UI frontend |
| **RESEARCH** | `rl/checkpoints/`, `rl/env/`, `rl/training/`, `rl/candidate_simulator/` | Gymnasium RL simulation environment, PPO training pipeline, checkpoint weights, normalization statistics |
| **BASELINE** | `agents/question_selector/question_selector.py` | Heuristic topic-balancing question selector baseline |
| **EXPERIMENT** | `ablation/` (`ablation_evaluator.py`, `significance_statistics.py`, `compute_krippendorff.py`, `results/`) | Benchmark scripts, inter-rater reliability analysis, evaluation matrices |
| **INFRASTRUCTURE RECOVERY** | `services/qwen/app.py:_synthesize_structured_*`, `agents/orchestrator/feedback_agent.py:_justification` | Deterministic rubric-grounded recovery paths when microservices are unavailable |
| **DOCUMENTATION** | `docs/` (`SCORING.md`, `DOCKER.md`, `paper_draft_ieee.md`, `DATASET_CARD.md`, `MODEL_CARD.md`) | Authoritative architecture specs and research drafts |

---

## 10. Research Artifacts Preserved

| Artifact | Path | SHA-256 Checksum | Invariant Status |
|---|---|---|---|
| **PPO Policy Checkpoint** | `rl/checkpoints/seed_123/ppo_final.zip` | `2ab8d514ca748abd0ac650d4a0b1676093530b21a16b1586c764b6db8ac54575` | **Intact** |
| **VecNormalize Statistics** | `rl/checkpoints/seed_123/vecnormalize.pkl` | `1481ca2c11cb1c2f9ae055c5350fc168359900daea2da3897a6b63f4dfc29df2` | **Intact** |
| **Gym RL Environment** | `rl/env/interview_env.py` | `f6ab20a6770f923b115154afa0337fa7173b950390c9fc0a2be298be2eef1245` | **Intact** |
| **Question Bank & Rubrics** | `data/questions/qns.json` | `2007ff39ff694b16fa364d44dd83b448c823901a7858c427ca495a4dcb26d2aa` | **Intact** |
| **Research Paper Manuscript** | `docs/paper_draft_ieee.md` | `e3c7be8b012d7c16f726291e30603c2d27b30f38ad0ece2737b525d22efab44b` | **Intact** |

---

## 11. Unsupported Paper Claims Analysis

| Paper Claim | Section in Draft | Empirical Classification | Remediation / Note |
|---|---|---|---|
| Three-component evaluator calibration ($S_1 + S_2 + R$) | Sec IV | **`EXPERIMENTALLY VALIDATED`** | Verified via 7 ablation configurations on 20 samples with 3 human raters ($\rho=0.9152, \alpha=0.8255$). |
| Guardrail-augmented PPO difficulty adaptation | Sec V | **`IMPLEMENTED & TESTED`** | Verified via automated integration tests and real session execution. |
| RL Ablation on synthetic candidate simulations | Sec VI-B | **`EXPERIMENTALLY VALIDATED`** | Validated on simulated interview trajectories; marked as pilot in paper. |
| Candidate longitudinal learning improvement | Sec VII-C | **`NOT YET VALIDATED`** | Explicitly declared as future work / limitation in Section VII-C.3. |
| Human interview efficacy comparison | Sec VII-C | **`NOT YET VALIDATED`** | Declared as future longitudinal trial. |
| Automatic follow-up gap probing | Sec IV | **`IMPLEMENTED & TESTED`** | Validated with explicit attribution and rubric-grounded gap probing. |
| Docker C sandbox security and test verification | Sec III | **`IMPLEMENTED & TESTED`** | Validated with 20 unit tests and live container testing. |

---

## 12–16. Testing Summary & Issues

- **Total Backend Tests Collected:** 178
- **Total Backend Tests Executed & Passed:** **177 passed (100%)**
- **Total Backend Tests Skipped:** 1 (`test_real_qwen_inference.py` marked for live GPU)
- **Total Backend Tests Failed:** **0**
- **Total Frontend Vitest Tests Passed:** **7/7 passed (100%)**
- **Remaining Issues:** **0**

---

# FINAL PRE-RESEARCH FREEZE: PASS
