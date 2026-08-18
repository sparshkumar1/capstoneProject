# PrepAIred — Authoritative Research Claims Evidence & Classification Matrix

**Document Version:** 3.0.0 (Stage 16 Post-Experiment Empirical Consolidation)
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform
**Purpose:** Single authoritative source of truth for scientific claims, evidence levels, and paper language control.

---

## 1. Scientific Classification Taxonomy

Every research claim across the PrepAIred repository and scientific paper drafts is classified into exactly one of five mutually exclusive empirical categories:

1. **`IMPLEMENTED`**: Functionality exists in the active codebase.
2. **`TESTED`**: Automated test suites (pytest/vitest) verify the behavior and code invariants.
3. **`EXPERIMENTALLY VALIDATED`**: Controlled research experiments with recorded empirical data artifacts confirm the claim.
4. **`HUMAN VALIDATED`**: Actual human participants/raters participated under a documented experimental protocol.
5. **`NOT YET VALIDATED`**: Hypothesized or implemented capability lacking sufficient empirical/human evidence.

---

## 2. Comprehensive Claim Evidence Matrix

| # | Claim | Evidence Artifact | Implementation Location | Test Suite | Experiments | Human Evidence | Status | Allowed Paper Wording | Prohibited / Overstated Wording | Required Future Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| **1** | **Evaluator Multi-Component Scoring ($S_1 + S_2 + R$)** | `research/results/raw/experiment_2_raw.json`, `summary.csv` | `services/evaluator/app.py` | `tests/unit/test_evaluator.py` (13 tests) | EXP-2 7-configuration ablation on 20 pilot answers ($\rho = 0.8358, p = 4.46 \times 10^{-6}$) | Evaluator compared against averaged ratings from 3 blinded human raters | **`EXPERIMENTALLY VALIDATED`** | "The evaluator combines semantic similarity, concept coverage, and reasoning entailment into a calibrated score that correlated with human ratings on a 20-sample pilot dataset (Spearman $\rho=0.8358, p=4.46 \times 10^{-6}$)." | "The evaluator is universally accurate and outperforms human grading systems." | Expansion of evaluation dataset to $n \ge 100$ items across all 13 CS curriculum topics. |
| **2** | **Evaluator Human Inter-Rater Reliability** | `ablation/results/ratings_averaged.csv`, `compute_krippendorff.py` | `ablation/` | `tests/unit/test_evaluator.py` | Krippendorff's $\alpha = 0.8255$ on 20 test answers (56 paired judgements) | 3 independent human raters graded 20 answers on a 0–10 scale | **`HUMAN VALIDATED`** | "Inter-rater reliability among the three human raters on the 20-sample pilot answer dataset was Krippendorff $\alpha=0.8255$." | "The complete PrepAIred interview system has been human validated." | Full interview platform evaluation with candidate participants against experienced human interviewers. |
| **3** | **Anti-Keyword Dampening ($S_{2,\text{eff}}$)** | `services/evaluator/app.py:363` | `services/evaluator/app.py` | `tests/unit/test_evaluator.py` | Verified score penalty when $R \le 0.30$ | — | **`TESTED`** | "Applies a reasoning-dependent dampening factor ($0.60 \times S_2$ when $R \le 0.30$) to prevent keyword listing from inflating scores." | "Eliminates all gaming and cheating strategies." | Adversarial candidate prompt-injection benchmark. |
| **4** | **PPO Difficulty Adaptation Policy** | `rl/checkpoints/seed_123/ppo_final.zip` | `agents/strategy/hybrid_orchestrator.py`, `rl/env/interview_env.py` | `tests/unit/test_rl_env.py` (15 tests), `test_stage11_5_coding_adaptation.py` (14 tests) | PPO convergence across 300,000 timesteps; policy rollout evaluations | — | **`TESTED`** | "A PPO policy over a 3-action space (Easier, Same, Harder) adapts difficulty based on a strict 6D state representation." | "PPO improves interview efficacy over expert human interviewers." | Controlled human cohort comparison (PPO vs Heuristic vs Fixed). |
| **5** | **RL Synthetic Adaptation Quality** | `research/results/raw/experiment_1_raw.json`, `summary.csv` | `agents/strategy/` | `tests/unit/test_rl_env.py` | EXP-1 comparison across 150 episodes (PPO vs Fixed $p = 6.15 \times 10^{-4}, d = 0.556$; PPO vs Rule $p = 5.30 \times 10^{-8}, d = 1.465$) | — | **`EXPERIMENTALLY VALIDATED`** | "In simulation against synthetic candidate models across 150 episodes, PPO with guardrails achieved adaptive difficulty adjustments ($\rho = 0.1572 \pm 0.08$) compared to fixed baseline." | "PPO produces superior learning gains in human students." | Session trajectory collection from real human student participants. |
| **6** | **Pedagogical Safety Guardrails (G1–G6)** | `agents/strategy/hybrid_orchestrator.py` | `agents/strategy/hybrid_orchestrator.py` | `tests/unit/test_rl_env.py`, `test_orchestrator.py` | Rule override activation rates recorded in pilot simulation logs | — | **`TESTED`** | "Applies six deterministic post-hoc guardrails to prevent erratic difficulty swings in boundary cases." | "Guarantees mathematically optimal pedagogical intervention." | Multi-expert pedagogical review of edge-case interventions. |
| **7** | **3-Level Question Deduplication** | `research/results/raw/experiment_4_raw.json`, `summary.csv` | `apps/backend/main.py` | `tests/unit/test_personalization_questions.py` (13 tests) | EXP-4 60-run evaluation (Personalized 0.0% repetition vs Random 6.0%, $p < 0.001$) | — | **`EXPERIMENTALLY VALIDATED`** | "3-level deduplication (exact ID, normalized string, Jaccard overlap $\ge 0.75$) eliminated duplicate questions ($0.0\%$ repetition vs $6.0\%$ random)." | "Completely eliminates semantic repetition across infinite sessions." | Cross-session semantic embedding similarity tracking. |
| **8** | **Adaptive Trajectory Divergence** | `research/results/raw/experiment_4_raw.json`, `summary.csv` | `apps/backend/main.py`, `agents/orchestrator/interview_orchestrator.py` | `test_e2e_personalization_trajectories.py` | EXP-4 60-run evaluation (Strong vs Weak Euclidean divergence = 14.21) | — | **`EXPERIMENTALLY VALIDATED`** | "Demonstrates distinct difficulty trajectories for simulated strong versus struggling candidates (Euclidean divergence $14.21$)." | "Personalization measurably improves candidate hiring outcomes." | Controlled pre/post assessment trial with human cohorts. |
| **9** | **Real Isolated Docker C Sandbox** | `Dockerfile.sandbox`, `agents/coding_executor/coding_executor.py` | `agents/coding_executor/` | `tests/unit/test_coding_executor.py` (20 tests), `test_stage11_4_coding_verification.py` (14 tests) | Docker cgroup memory limit (128MB), 32 PIDs, 2.0s timeout, segfault capture verified | — | **`TESTED`** | "Executes candidate C code in an unprivileged, isolated Docker container with strict CPU, memory, and timeout governance." | "Impenetrable enterprise-grade security environment." | Third-party container security penetration audit. |
| **10** | **Evidence-Grounded Follow-Up Probing** | `research/results/raw/experiment_5_raw.json`, `summary.csv` | `agents/orchestrator/` | `tests/unit/test_qwen_followup_feedback.py` (14 tests), `test_stage11_3_followup_and_evaluation.py` (14 tests) | EXP-5 ablation verified 0.5 follow-up interventions triggered per session on struggling concepts | — | **`EXPERIMENTALLY VALIDATED`** | "Triggers targeted follow-up questions on low-scoring concepts, capped at two consecutive probes per topic." | "LLM follow-up questions dramatically accelerate student comprehension." | Controlled learning gain assessment with human students. |
| **11** | **Formative Feedback Grounding & Actionability** | `research/results/raw/experiment_3_raw.json`, `research/results/raw/experiment_3_qwen_raw.json` | `agents/orchestrator/feedback_agent.py` | `tests/unit/test_qwen_followup_feedback.py` | EXP-3 20-sample benchmark: Qwen-7B achieved higher transcript lexical grounding ($0.2496$ vs $0.0383$, $p=2.56 \times 10^{-3}$), while non-LLM structured recovery achieved higher rubric gap coverage ($100.0\%$ vs $72.5\%$, $p=9.11 \times 10^{-4}$); both exceeded generic boilerplate ($p < 0.001$) | — | **`EXPERIMENTALLY VALIDATED`** | "Generative Qwen-7B feedback produced significantly higher transcript lexical grounding ($0.2496$ vs $0.0383$, $p=2.56 \times 10^{-3}$) than non-LLM structured recovery on the 20-sample pilot benchmark, whereas non-LLM structured recovery provided strictly higher rubric concept gap coverage ($100.0\%$ vs $72.5\%$, $p=9.11 \times 10^{-4}$)." | "Qwen feedback universally improves student learning gains and hiring success." | Longitudinal retention studies measuring pedagogical utility and candidate comprehension over repeated interview sessions. |
| **12** | **Speech Prosody & Hesitation Extraction** | `agents/audio/` | `agents/audio/` | `tests/unit/test_speech_pipeline.py` (15 tests) | WhisperX forced alignment, WPM calculation, pause detection ($\Delta t \ge 0.45\text{s}$) verified | — | **`TESTED`** | "Extracts speech-to-text transcripts, speaking rate (WPM), pause rate, and acoustic hesitation indicators using WhisperX forced alignment." | "Acoustic hesitation accurately measures psychological stress and anxiety." | Clinical psychometric correlation study with physiological stress markers. |
| **13** | **Technical Correctness Dominance in Scoring** | `docs/SCORING.md`, `agents/timing/timer.py` | `agents/timing/timer.py` | `tests/unit/test_timer_scoring.py` (18 tests) | Timing modifier $f_{\text{time}} \in [-0.10, +0.03]$; fast incorrect answers receive $f_{\text{time}} = 0.0$ | — | **`TESTED`** | "Modulates technical scores using an additive timing term $f_{\text{time}} \in [-0.10, +0.03]$, ensuring fast incorrect answers never receive speed bonuses." | "The timing formula represents the mathematically ideal candidate pacing model." | Empirical psychometric timing calibration with professional recruiters. |
| **14** | **Multi-Agent Architectural Separation** | `docs/ARCHITECTURE.md`, `docs/AGENTS.md` | `agents/`, `services/` | `tests/integration/test_multiagent_responsibility_and_failures.py` (5 tests) | Independent service failure isolation; evaluator, Qwen, strategy, timing decoupled | — | **`TESTED`** | "Decouples session orchestration, neural evaluation, RL strategy, audio analysis, and coding execution into independent services." | "Multi-agent architecture inherently achieves superior interview results." | System latency, throughput, and modularity benchmarking. |
| **15** | **Curated 125 Question & Rubric Curriculum** | `data/questions/qns.json`, `data/rubrics/rubrics_final_clean.json` | `data/` | `tests/unit/test_personalization_questions.py` | 125 questions across 13 topics with logic markers, Bloom's tags, and starter code verified | Curated and reviewed by experienced CS educators | **`TESTED`** | "Maintains 125 curated C and DSA technical interview questions with structured evaluation rubrics." | "Covers every possible technical interview concept." | Continuous curriculum expansion and external educator review. |
| **16** | **Whole-System Human Interview Efficacy** | — | — | — | — | — | **`NOT YET VALIDATED`** | "Longitudinal user studies evaluating end-to-end interview efficacy and learning outcomes remain future work." | "PrepAIred has been validated with human candidates to increase hiring rates." | Controlled double-blind randomized trial with real interview candidates. |

---

## 3. Strict Paper Language Enforcement Rules

To prevent overclaiming in scientific manuscripts and documentation:

1. **Prohibited Unanchored Terms:** Words such as *improves*, *outperforms*, *superior*, *effective*, *accurate*, *better*, *state-of-the-art*, and *human validated* must never be used in a whole-system context without citing the specific validated subsystem (e.g. Evaluator on $n=20$).
2. **Evaluator Human Validation vs. Whole System:** Distinguish carefully between evaluator correlation with human ratings ($\rho=0.8358, p=4.46 \times 10^{-6}$) and inter-rater reliability among human raters ($\alpha=0.8255$). The whole platform is **not** human validated.
3. **RL Simulation Distinction:** Any discussion of PPO difficulty adaptation quality must explicitly specify that it was measured on *simulated candidate trajectories across 150 episodes*, not in human hiring trials.
4. **Personalization Scope:** Trajectory divergence between candidate ability profiles is *demonstrated in simulation and integration testing ($d=14.21$)*, but *learning gain efficacy* remains a hypothesis for future longitudinal study.
5. **Attribution Integrity:** Non-LLM structured recovery must never be described as LLM-generated output.

---

## 4. Summary of Claims by Permitted Status Label

Exact row count validation across the 16 claim rows:

| Permitted Status Label | Claim Rows Matching Status | Count |
|---|---|---|
| **`IMPLEMENTED`** | — | **0** |
| **`TESTED`** | Rows 3, 4, 6, 9, 12, 13, 14, 15 | **8** |
| **`EXPERIMENTALLY VALIDATED`** | Rows 1, 5, 7, 8, 10, 11 | **6** |
| **`HUMAN VALIDATED`** | Row 2 | **1** |
| **`NOT YET VALIDATED`** | Row 16 | **1** |
| **Total** | **All 16 Rows ($0 + 8 + 6 + 1 + 1$)** | **16** |

---

## 5. Master Output Artifacts Registry

All experimental data is machine-readable and stored under:

- **Raw Results:** [`research/results/raw/`](research/results/raw/)
- **Processed Analysis:** [`research/results/processed/`](research/results/processed/)
- **Result Tables:** [`research/results/tables/`](research/results/tables/)
- **Markdown Summaries:** [`research/results/summaries/`](research/results/summaries/)
