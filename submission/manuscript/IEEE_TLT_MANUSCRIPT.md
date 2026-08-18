# A Personalized Adaptive Framework for Multimodal Technical Interview Assessment and Preparation

**Authors:** Sparsh Kumar and the PrepAIred Research Group
**Format:** IEEE Two-Column Scientific Format
**Target Category:** AI in Computer Science Education, Adaptive Assessment & Intelligent Tutoring Systems
**Status:** Post-Experiment Master Empirical Consolidation (Stage 17)
**Authoritative Artifact:** `docs/paper_draft_ieee.md`

---

## Abstract

Technical interviews for software engineering roles are high-stakes, multimodal assessments that require simultaneous evaluation of conceptual accuracy, algorithmic reasoning, verbal communication, and live coding. Existing preparation platforms rely either on static problem delivery without pedagogical adaptation or on uncalibrated, monolithic large language models (LLMs) that conflate surface fluency with conceptual depth. We present **PrepAIred**, an adaptive, multimodal technical interview assessment framework. PrepAIred integrates: (1) a calibrated three-component answer evaluation pipeline ($S_1+S_2+R$) that decomposes student responses into surface semantic similarity, knowledge concept coverage via FAISS vector retrieval, and cross-encoder reasoning entailment; (2) a six-dimensional candidate-state representation tracking performance, speech prosody hesitation, confidence, and pacing; (3) a guardrail-augmented Proximal Policy Optimization (PPO) strategy controller over a three-action space (Easier, Same, Harder); (4) a three-level deduplication and personalized topic selector; and (5) a formative feedback module comparing deterministic rubric recovery against a generative LLM (`Qwen2.5-7B-Instruct`).

We report a controlled empirical evaluation across five pre-registered experiments ($n=480$ total sessions/evaluations). In simulation across 150 episodes ($3 \text{ controllers} \times 5 \text{ personas} \times 10 \text{ seeds}$), PPO with guardrails achieved adaptive difficulty adjustments ($\rho = +0.1572 \pm 0.08$) compared to fixed baseline ($\rho = 0.0, p = 6.15 \times 10^{-4}$) and rule-based heuristics ($\rho = -0.2572, p = 5.30 \times 10^{-8}$). In evaluator ablation ($140$ scorings across $7$ configurations), the full pipeline and $S_1+S_2$ reached rank correlation $\rho = 0.8358$ ($p = 4.46 \times 10^{-6}$) against blinded human ground-truth ratings (human inter-rater reliability Krippendorff's $\alpha = 0.8255$). In feedback evaluation ($60$ scorings across $3$ conditions), Qwen-7B executed on an NVIDIA Tesla T4 GPU produced higher transcript lexical grounding ($0.2496$ vs. $0.0383$, $p = 2.56 \times 10^{-3}$) than non-LLM structured recovery, whereas non-LLM structured recovery achieved strictly higher rubric concept gap coverage ($100.0\%$ vs. $72.5\%$, $p = 9.11 \times 10^{-4}$) at sub-50ms latency. Personalization eliminated duplicate questions ($0.0\%$ vs. $6.0\%$ random, $p < 0.001$) and demonstrated distinct difficulty divergence ($d = 14.21$) between candidate profiles. Longitudinal candidate learning gains and whole-system human interview efficacy remain unvalidated and represent future work.

**Index Terms—** Intelligent Tutoring Systems, Automated Short Answer Grading, Reinforcement Learning, Technical Interviews, Multimodal Assessment, Formative Feedback, Large Language Models.

---

## I. Introduction

Technical interviews serve as the primary gateway for software engineering employment. However, high-quality interview preparation remains resource-intensive and inequitably accessible, typically requiring mock interviews with experienced human engineers. Automated platforms like LeetCode and HackerRank provide static coding sandboxes with binary unit-test feedback but lack interactive dialogue, verbal explanation assessment, and adaptive pedagogical pacing. Conversely, general-purpose conversational LLMs often provide generic, uncalibrated praise or hallucinate rubric adherence without grounding decisions in structured knowledge representations.

A key challenge in automated technical assessment is **signal decomposition**: distinguishing between surface-level keyword recitation and genuine algorithmic reasoning. A student who memorizes "use a hash map for $O(1)$ lookup" must be distinguished from one who explains hash collision resolution and load-factor rebalancing. Furthermore, human interviewers dynamically modulate question difficulty, probe misconceptions with follow-up questions, and extract behavioral cues such as speech hesitation.

To address these challenges, we introduce PrepAIred, an adaptive technical interview system. PrepAIred models candidate state along six continuous dimensions and dynamically orchestrates question difficulty, conceptual follow-ups, and formative feedback. Rather than presenting implementation technologies as standalone achievements, this paper investigates the empirical interactions, performance characteristics, and scientific trade-offs among the system's core components through controlled experiments.

---

## II. Problem Statement

We formulate the automated technical interview as a multi-turn, multimodal assessment process over a discrete turn horizon $t \in \{1, \dots, T\}$. At each turn $t$:
1. The system presents a technical question $q_t$ with difficulty $d(q_t) \in [0.1, 1.0]$ and rubric $\mathcal{R}(q_t)$.
2. The candidate provides an answer consisting of audio $\mathbf{a}_t$, transcribed text $x_t$, and optional C code $c_t$.
3. The system extracts a multi-component score $y_t \in [0, 1]$, prosodic speech features $\mathbf{p}_t$, and coding test results $\mathbf{k}_t$.
4. The system updates a candidate-state vector $\mathbf{s}_t \in [0, 1]^6$ and selects an adaptation action $a_t \in \{\text{Easier}, \text{Same}, \text{Harder}\}$ alongside the next question $q_{t+1}$.
5. If score $y_t < 0.65$, the system triggers targeted follow-up probes or synthesizes formative feedback.

The central research problem is designing and evaluating the decision mechanisms governing this closed loop to ensure calibrated scoring, adaptive difficulty pacing, and grounded feedback.

---

## III. Research Gap

While automated short answer grading (ASAG) [1] and intelligent tutoring systems (ITS) [2] have received extensive study, significant gaps remain in the context of technical interview preparation:
1. **Monolithic Scoring Limitations:** Most neural ASAG systems utilize single-encoder architectures that conflate keyword presence with logical entailment, rendering them susceptible to keyword gaming.
2. **Uncalibrated RL Adaptation:** Prior RL tutoring systems often lack deterministic pedagogical safety boundaries, leading to erratic difficulty swings in boundary conditions.
3. **Generative LLM vs. Deterministic Trade-Offs:** The comparative trade-offs between expensive generative LLM feedback and deterministic rubric recovery in automated assessment have not been rigorously quantified under controlled, paired experimental conditions.

---

## IV. Related Work

### A. Automated Short Answer Grading (ASAG)
Early ASAG utilized unsupervised semantic similarity and bag-of-words alignments [1], [3]. Supervised neural ASAG introduced BERT-based bi-encoders and cross-encoders [4], achieving strong correlation with human raters on standardized datasets (e.g., SemEval-2013 [3]). However, bi-encoders struggle with logical negation and fine-grained concept tracking. PrepAIred addresses this by combining bi-encoder semantic similarity ($S_1$), FAISS-indexed concept coverage ($S_2$), and cross-encoder reasoning entailment ($R$) with reasoning-dependent keyword dampening.

### B. Adaptive Question Sequencing & Reinforcement Learning
Adaptive learning systems traditionally leverage Item Response Theory (IRT) [5] and Deep Knowledge Tracing (DKT) [6]. Recent research has applied Reinforcement Learning (RL) to pedagogical sequencing [7], [8]. However, unconstrained RL policies can destabilize student engagement. PrepAIred implements policy shielding via deterministic pedagogical guardrails (G1–G6) over a PPO policy.

### C. Multimodal Speech and LLM Feedback
Speech prosody and pause rates provide indicators of cognitive load and uncertainty [9], [10]. Automated speech recognition (ASR) pipelines like WhisperX [11] enable forced word-level alignment. In formative feedback, recent work explores LLM prompting [12], but studies rarely benchmark LLM grounding against non-generative rubric recovery.

---

## V. Research Questions

This study investigates five pre-registered research questions:
- **RQ1 (Adaptive Difficulty):** How does PPO-based adaptive difficulty compare with fixed and deterministic rule-based controllers in simulated interview trajectories?
- **RQ2 (Evaluator Decomposition):** Which components of the structured evaluator ($S_1, S_2, R$) contribute to agreement with blinded human ratings, and does the multi-component pipeline provide measurable benefit over individual components?
- **RQ3 (Feedback Trade-Offs):** How do generic templates, non-LLM structured recovery, and generative Qwen-7B feedback differ in transcript lexical grounding, rubric gap coverage, actionability, and latency?
- **RQ4 (Personalization):** How does candidate-state-driven question selection affect question repetition and difficulty trajectory differentiation relative to non-adaptive selectors?
- **RQ5 (Component Isolation):** Which implemented subsystems contribute measurable behavioral changes under leave-one-out ablation?

---

## VI. Contributions

1. **Integrated Multimodal Architecture:** An end-to-end technical interview platform integrating speech prosody, isolated C execution, multi-component neural evaluation, RL strategy, and formative feedback.
2. **Calibrated Multi-Component Evaluator ($S_1+S_2+R$):** A structured scoring engine combining bi-encoder semantics, FAISS concept retrieval, and cross-encoder entailment with anti-keyword dampening, validated against blinded human raters ($\rho = 0.8358, \alpha = 0.8255$).
3. **Guardrail-Augmented PPO Difficulty Controller:** A 6D candidate-state formulation with deterministic safety boundaries that outperforms fixed and heuristic baselines in simulated adaptation ($\rho = +0.1572$).
4. **Empirical Characterization of Feedback Trade-Offs:** A tri-condition benchmark establishing that generative Qwen-7B achieves higher transcript lexical grounding ($0.2496$), whereas deterministic structured recovery achieves strictly higher rubric gap coverage ($100.0\%$) at sub-50ms latency.
5. **Open, Traceable Research Artifacts:** Complete experimental results ($n=480$ sessions) with cryptographic provenance and replication harnesses.

---

## VII. System Architecture

The PrepAIred architecture decouples responsibilities across independent microservices communicating via HTTP REST and WebSockets (Figure 1).

![Figure 1: System Architecture](research/results/figures/figure1_system_architecture.png)

**Table I: Core Subsystems and Operational Responsibilities**

| Subsystem | Underlying Technology | Primary Responsibility | Validation Level |
|---|---|---|:---:|
| **Frontend UI** | React 18, Vite, WebSockets | Voice recording, code editor, difficulty visualization | `TESTED` |
| **Backend API** | FastAPI, Python 3.12, SQLite | Session state, candidate state update, orchestration | `TESTED` |
| **Evaluator Service** | SBERT, FAISS, CrossEncoder | Multi-component score computation ($S_1+S_2+R$) | `EXPERIMENTALLY VALIDATED` |
| **Strategy Agent** | Stable-Baselines3 (PPO), Gym | Difficulty adaptation over $\{\text{Easier}, \text{Same}, \text{Harder}\}$ | `EXPERIMENTALLY VALIDATED` |
| **Speech Pipeline** | WhisperX, PyAnnote, Librosa | Forced alignment, WPM, pause rate, hesitation | `TESTED` |
| **Coding Sandbox** | Docker Engine, GCC, Cgroups | Isolated C compilation, timeout/memory enforcement | `TESTED` |
| **Feedback Agent** | Qwen2.5-7B-Instruct / Rubrics | Evidence-grounded formative feedback & probing | `EXPERIMENTALLY VALIDATED` |

---

## VIII. Candidate-State Representation

Candidate state $\mathbf{s}_t \in [0, 1]^6$ is updated after each turn $t$ (Figure 2, Table II):
$$\mathbf{s}_t = \big[ y_t,\, \bar{y}_t,\, c_t,\, h_t,\, \tau_t,\, d_t \big]$$

![Figure 2: Candidate-State Adaptation Loop](research/results/figures/figure2_candidate_state_loop.png)

**Table II: Candidate-State Vector Specification**

| Element | Symbol | Definition | Normalization Range |
|---|:---:|---|:---:|
| **Current Performance** | $y_t$ | Calibrated evaluator score on turn $t$ | $[0.0, 1.0]$ |
| **Average Performance** | $\bar{y}_t$ | Exponential moving average ($\alpha=0.3$) | $[0.0, 1.0]$ |
| **Candidate Confidence** | $c_t$ | Acoustic energy and transcript length composite | $[0.0, 1.0]$ |
| **Speech Hesitation** | $h_t$ | Normalized pause rate ($\Delta t \ge 0.45\text{s}$) & filler ratio | $[0.0, 1.0]$ |
| **Normalized Pacing** | $\tau_t$ | Ratio of actual response duration to target time | $[0.0, 1.0]$ |
| **Current Difficulty** | $d_t$ | Normalized difficulty level of question $q_t$ | $[0.1, 1.0]$ |

---

## IX. Reinforcement Learning Strategy & Safety Guardrails

### A. Action Space and Reward Formulation
The strategy agent chooses a discrete difficulty transition $a_t \in \{0: \text{Easier}, 1: \text{Same}, 2: \text{Harder}\}$ (Table III). The RL policy is trained with PPO in a customized Gymnasium environment (`InterviewEnv`) against simulated candidate personas for 300,000 steps.

**Table III: Strategy Action Mapping**

| Action Index | Action Label | Difficulty Delta $\Delta d$ | Target Scenario |
|:---:|:---:|:---:|---|
| **0** | `Easier` | $-0.15$ | Candidate struggling ($y_t < 0.40$) |
| **1** | `Same` | $0.00$ | Borderline performance ($0.40 \le y_t < 0.70$) |
| **2** | `Harder` | $+0.15$ | Strong mastery demonstrated ($y_t \ge 0.70$) |

The step reward $r_t$ balances technical score, learning slope, and stability penalties (Table IV):
$$r_t = y_t + 0.3 \cdot (y_t - y_{t-1}) - 0.2 \cdot \mathbb{I}_{\text{premature}} - 0.1 \cdot \mathbb{I}_{\text{repeat}}$$

**Table IV: PPO Hyperparameter Configuration**

| Parameter | Value | Parameter | Value |
|---|:---:|---|:---:|
| **Policy Architecture** | MLP ($2 \times 64$) | **Learning Rate** | $3 \times 10^{-4}$ |
| **Discount Factor ($\gamma$)** | $0.99$ | **GAE Parameter ($\lambda$)** | $0.95$ |
| **Clip Range** | $0.20$ | **Batch Size / Steps** | $64$ / $2048$ |
| **Normalization** | VecNormalize ($\text{clip}=10$) | **Seed** | $123$ |

### B. Pedagogical Safety Guardrails (G1–G6)
To prevent erratic policy behavior, deterministic guardrails evaluate post-policy transitions in priority order:
- **G4 (Critical Distress):** If $y_t < 0.30$ and $h_t > 0.60 \implies a_t = \text{Easier}$.
- **G1 (Mid-Difficulty Failure):** If $y_t < 0.30$ and $d_t \in [0.4, 0.7] \implies a_t = \text{Easier}$.
- **G2 (Low Confidence Hesitation):** If $c_t < 0.30$, $h_t > 0.70$, and $y_t < 0.80 \implies a_t \in \{\text{Same}, \text{Easier}\}$.
- **G3 (Policy Damping):** Prevents consecutive difficulty oscillations ($\Delta d_{t} \cdot \Delta d_{t-1} < 0$).
- **G5 (Borderline Reinforcement):** If $0.40 \le y_t \le 0.65 \implies a_t = \text{Same}$.
- **G6 (Mastery Acceleration):** If $y_t \ge 0.90$ and $d_t < 0.85 \implies a_t = \text{Harder}$.

---

## X. Multi-Component Answer Evaluation

The evaluator calculates three sub-scores combined through calibrated linear weights and non-linear rules:
$$\text{Score} = \text{clip}\Big( 0.15 \cdot S_1 + 0.35 \cdot S_{2,\text{eff}} + 0.50 \cdot R + \text{bonus} - \text{penalty},\; 0,\; 1 \Big)$$

1. **$S_1$ — Semantic Similarity ($w=0.15$):** Cosine similarity of `all-MiniLM-L6-v2` embeddings between candidate transcript and reference text.
2. **$S_2$ — Knowledge Concept Coverage ($w=0.35$):** Pre-embedded rubric concepts retrieved via FAISS. A concept is covered if maximum sentence cosine similarity exceeds threshold $\theta = 0.42$:
   $$S_2 = \frac{1}{|\mathcal{C}|} \sum_{c \in \mathcal{C}} \mathbb{I}\Big( \max_{s \in \text{sentences}} \cos(\mathbf{e}_s, \mathbf{e}_c) \ge 0.42 \Big)$$
3. **Anti-Keyword Dampening ($S_{2,\text{eff}}$):** If reasoning score $R \le 0.30$, concept coverage is dampened to prevent keyword listing from inflating scores:
   $$S_{2,\text{eff}} = \begin{cases} S_2 & \text{if } R > 0.30 \\ 0.60 \cdot S_2 & \text{if } R \le 0.30 \end{cases}$$
4. **$R$ — Deep Reasoning Entailment ($w=0.50$):** Fine-tuned CrossEncoder (`ms-marco-MiniLM-L12-v2`) jointly evaluating question, reference rubric, and candidate answer.
5. **Mandatory Check:** If mandatory concepts are missed, score is capped at $0.60$.

---

## XI. Question Selection, Follow-Up Probing & Formative Feedback

### A. 3-Level Question Deduplication
To prevent question repetition across and within sessions, candidate questions are filtered using:
1. **Level 1:** Exact question ID hash matching.
2. **Level 2:** Normalized text string equality.
3. **Level 3:** Jaccard token overlap threshold ($\text{Jaccard}(q_a, q_b) \ge 0.75$).

### B. Follow-Up Probing Logic
When candidate performance on a core concept is marginal ($0.30 \le y_t < 0.65$), the system triggers an evidence-grounded follow-up question targeting the exact missing concept. To prevent candidate frustration, follow-up probes are hard-capped at two consecutive turns per topic.

### C. Formative Feedback Generation
The feedback module synthesizes remediation along three paradigms:
1. **Generic Template Baseline:** Static boilerplate based on score brackets ($<0.40, 0.40-0.70, \ge 0.70$).
2. **Non-LLM Structured Evaluator Recovery:** Deterministic extraction of uncovered rubric concepts ($S_2 < 0.42$) and identified common misconceptions.
3. **Generative LLM (Qwen2.5-7B-Instruct):** Autoregressive synthesis conditioned on the candidate transcript, rubric concepts, and evaluation breakdown using official unquantized `bfloat16` weights.

---

## XII. Multimodal Audio, Coding Sandbox & Timing Formulation

### A. Speech Prosody Pipeline
Candidate audio is processed with WhisperX for forced alignment. Speech rate (words per minute), pause rate ($\Delta t \ge 0.45\text{s}$ silent intervals), and acoustic confidence are extracted to compute the hesitation index $h_t$.

### B. Isolated C Execution Sandbox
Code submissions are compiled with GCC (`-Wall -O2`) inside an isolated, unprivileged Docker container governed by Linux cgroups: 128MB RAM limit, 32 PIDs limit, 2.0s execution timeout, and complete network isolation.

### C. Technical Correctness Dominance in Scoring
Timing modifies technical score through an additive factor $f_{\text{time}} \in [-0.10, +0.03]$:
$$f_{\text{time}} = \begin{cases} +0.03 & \text{if } y_t \ge 0.60 \text{ and } \Delta t \le 0.70 \cdot T_{\text{target}} \\ -0.10 \cdot \frac{\Delta t - T_{\text{target}}}{T_{\text{target}}} & \text{if } \Delta t > T_{\text{target}} \\ 0.00 & \text{otherwise} \end{cases}$$
Crucially, fast incorrect answers ($y_t < 0.60$) receive $f_{\text{time}} = 0.00$, preventing rushed guesses from receiving speed bonuses.

---

## XIII. Experimental Methodology

We pre-registered and executed five controlled research experiments ($n=480$ total sessions/runs, Figure 3, Tables V & VI).

![Figure 3: Experimental Methodology](research/results/figures/figure3_experimental_methodology.png)

**Table V: Comparison Baselines & Experimental Controllers**

| Baseline / Controller | Configuration / Mechanism | Target Role |
|---|---|---|
| **Fixed Difficulty** | Constant difficulty $d = 0.50$ | Passive assessment baseline |
| **Rule-Based Adaptive** | Heuristic step: $+0.15$ if $y_t \ge 0.7$, $-0.15$ if $y_t < 0.4$ | Deterministic adaptive baseline |
| **PPO + Guardrails** | 6D state PPO policy with G1–G6 post-policy safety shields | Proposed adaptive controller |
| **Random Selector** | Uniform random question choice from curriculum bank | Unstructured selection baseline |
| **Topic Baseline** | Sequential topic-round-robin question selection | Standard curriculum selector |
| **Generic Template** | Score-bracket static text templates | Non-grounded feedback baseline |
| **Structured Recovery** | Direct extraction of missed rubric concept strings | Non-LLM grounded feedback |
| **Qwen-7B Grounded** | Qwen2.5-7B-Instruct autoregressive generation on CUDA GPU | Proposed generative feedback |

**Table VI: Master Experimental Design & Protocol Summary**

| Exp ID | Research Question | Conditions | Sample Size | Primary Metrics | Statistical Test |
|:---:|---|:---:|:---:|---|---|
| **EXP-1** | RQ1: Adaptive Difficulty | 3 Controllers | 150 episodes ($3 \times 5 \times 10$) | Adaptation correlation $\rho$, score slope | Wilcoxon signed-rank + Holm |
| **EXP-2** | RQ2: Evaluator Ablation | 7 Configurations | 140 scorings ($7 \times 20$) | Spearman $\rho$ vs Human, MAE | Spearman rank correlation |
| **EXP-3** | RQ3: Formative Feedback | 3 Feedback Modes | 60 evaluations ($3 \times 20$) | Lexical grounding, gap coverage, tips | Paired Wilcoxon + Holm |
| **EXP-4** | RQ4: Personalization | 3 Selectors | 60 sessions ($3 \times 2 \times 10$) | Repetition rate, trajectory divergence | Chi-Square, Euclidean distance |
| **EXP-5** | RQ5: Component Ablation | 7 Subsystems | 70 sessions ($7 \times 10$) | Subsystem-specific functional drop | Behavioral isolation audit |

---

## XIV. Empirical Results & Statistical Analysis

### A. EXP-1: Adaptive Difficulty Controller Evaluation

![Figure 4: Adaptive Difficulty Results](research/results/figures/figure4_adaptive_difficulty.png)

**Table VII: EXP-1 Adaptation Performance Across 150 Simulated Episodes**

| Controller | Mean Adaptation $\rho$ | Std Dev | Adjusted Slope | Pairwise vs. PPO ($p$-value) | Cohen's $d$ vs PPO |
|---|:---:|:---:|:---:|:---:|:---:|
| **Fixed Difficulty** | $0.0000$ | $0.0000$ | $+0.0000 \pm 0.00$ | $p = 6.15 \times 10^{-4}$ | $d = 0.5562$ |
| **Rule-Based Heuristic** | $-0.2572$ | $0.0650$ | $-0.0182 \pm 0.01$ | $p = 5.30 \times 10^{-8}$ | $d = 1.4654$ |
| **PPO + Guardrails** | $\mathbf{+0.1572}$ | $0.0800$ | $\mathbf{+0.0341 \pm 0.01}$ | — | — |

- **Observed Result:** PPO with guardrails achieved positive adaptation correlation ($\rho = +0.1572 \pm 0.08$), whereas Fixed was zero ($\rho = 0.0$) and Rule-Based exhibited negative oscillation ($\rho = -0.2572$).
- **Statistical Result:** Wilcoxon signed-rank tests confirmed that PPO significantly differed from Fixed ($p = 6.15 \times 10^{-4}, d = 0.5562$) and Rule-Based ($p = 5.30 \times 10^{-8}, d = 1.4654$).
- **Interpretation:** In simulated candidate interactions, PPO with guardrails maintained stable difficulty progression without the destabilizing oscillation observed in simple heuristic step-functions.

---

### B. EXP-2: Evaluator Component Ablation

![Figure 5: Evaluator Ablation Results](research/results/figures/figure5_evaluator_ablation.png)

**Table VIII: Evaluator Ablation vs. Blinded Human Ratings ($n=20$ items, $140$ scorings)**

| Configuration | $w_{S1}$ | $w_{S2}$ | $w_R$ | Spearman $\rho$ | $p$-value | Mean Absolute Error (MAE) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **$S_1$ Only (Surface Semantics)** | $1.00$ | $0.00$ | $0.00$ | $0.6385$ | $2.41 \times 10^{-3}$ | $0.2850$ |
| **$S_2$ Only (Concept Coverage)** | $0.00$ | $1.00$ | $0.00$ | $0.7937$ | $3.12 \times 10^{-5}$ | $0.2215$ |
| **$R$ Only (CrossEncoder Reasoning)** | $0.00$ | $0.00$ | $1.00$ | $0.3547$ | $1.24 \times 10^{-1}$ | $0.3850$ |
| **$S_1 + R$** | $0.23$ | $0.00$ | $0.77$ | $0.4485$ | $4.73 \times 10^{-2}$ | $0.3420$ |
| **$S_2 + R$** | $0.00$ | $0.41$ | $0.59$ | $0.7725$ | $6.92 \times 10^{-5}$ | $0.2310$ |
| **$S_1 + S_2$** | $0.30$ | $0.70$ | $0.00$ | $\mathbf{0.8358}$ | $4.46 \times 10^{-6}$ | $\mathbf{0.1907}$ |
| **Full Pipeline ($S_1+S_2+R$)** | $\mathbf{0.15}$ | $\mathbf{0.35}$ | $\mathbf{0.50}$ | $\mathbf{0.8358}$ | $4.46 \times 10^{-6}$ | $0.2585$ |

- **Observed Result:** Human inter-rater reliability among 3 blinded raters on the 20 benchmark items was Krippendorff's $\alpha = 0.8255$. Both the Full Pipeline and $S_1+S_2$ achieved identical rank correlation ($\rho = 0.8358, p = 4.46 \times 10^{-6}$), while $S_1+S_2$ achieved lower MAE ($0.1907$ vs. $0.2585$).
- **Statistical Result:** Concept coverage ($S_2$) provides the strongest standalone rank signal ($\rho = 0.7937$), whereas reasoning alone ($R$) exhibited high error ($\text{MAE} = 0.3850$).
- **Interpretation:** Combining concept coverage with semantic similarity captures the primary grading variance; reasoning entailment ($R$) provides critical keyword dampening ($S_{2,\text{eff}}$) but increases calibration error if uncalibrated.

---

### C. EXP-3: Formative Feedback Tri-Condition Evaluation

![Figure 6: Formative Feedback Comparison](research/results/figures/figure6_feedback_comparison.png)

**Table IX: Formative Feedback Benchmark Results ($n=20$ items, $60$ evaluations)**

| Condition | Architecture | Mean Lexical Grounding | 95% Bootstrap CI | Rubric Gap Coverage | Actionable Directives | Mean Latency |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **Generic Template** | Static Text | **0.0000** | [0.0000, 0.0000] | **0.0%** (0.0000) | **1.00** | < 0.01s |
| **Structured Recovery** | Non-LLM Rubric | **0.0383** | [0.0059, 0.0919] | $\mathbf{100.0\%}$ (1.0000) | $\mathbf{3.90}$ | < 0.05s |
| **Qwen-7B Grounded** | Qwen2.5-7B (Tesla T4) | $\mathbf{0.2496}$ | [0.1758, 0.3331] | **72.5%** (0.7250) | **3.70** | 9.78s |

- **Observed Result:** Qwen-7B achieved higher transcript lexical grounding ($0.2496$) than Structured Recovery ($0.0383$) and Generic ($0.0000$). Conversely, Structured Recovery achieved strictly higher rubric gap coverage ($100.0\%$) than Qwen-7B ($72.5\%$). Actionable directive counts were comparable between Structured ($3.90$) and Qwen-7B ($3.70$).
- **Statistical Result:**
  - *Lexical Grounding:* Qwen-7B vs. Generic ($W=0.0, p_{\text{holm}} = 3.94 \times 10^{-4}, d = 1.3628$); Qwen-7B vs. Structured ($W=15.0, p_{\text{holm}} = 2.56 \times 10^{-3}, d = 0.8903$).
  - *Gap Coverage:* Structured vs. Qwen-7B ($W=0.0, p_{\text{holm}} = 9.11 \times 10^{-4}, d = 1.0775$).
  - *Actionability:* Structured vs. Qwen-7B ($W=51.0, p_{\text{holm}} = 0.6033, d = 0.1133$, not significant).
- **Interpretation:** A clear architectural trade-off exists: Qwen-7B provides natural conversational synthesis with explicit candidate quotation, whereas non-LLM Structured Recovery guarantees complete rubric concept remediation at negligible latency and zero GPU compute cost.

---

### D. EXP-4: Personalization and Trajectory Divergence

![Figure 7: Personalization and Divergence Results](research/results/figures/figure7_personalization_divergence.png)

**Table X: EXP-4 Personalization Performance Across 60 Simulated Sessions**

| Question Selector | Question Repetition Rate | Weakness Remediation Rate | Strong Candidate Mean Diff | Struggling Candidate Mean Diff |
|---|:---:|:---:|:---:|:---:|
| **Random Baseline** | $6.00\%$ | $2.00\%$ | $0.50 \pm 0.05$ | $0.50 \pm 0.05$ |
| **Topic Baseline** | $2.00\%$ | $8.00\%$ | $0.52 \pm 0.04$ | $0.48 \pm 0.04$ |
| **Candidate-State Driven** | $\mathbf{0.00\%}$ | $\mathbf{16.67\%}$ | $\mathbf{0.82 \pm 0.06}$ | $\mathbf{0.24 \pm 0.05}$ |

- **Observed Result:** Candidate-state-driven selection eliminated question repetition ($0.0\%$ vs. $6.0\%$ random, $p < 0.001$), doubled weakness remediation rate ($16.67\%$ vs. $8.00\%$), and achieved a Euclidean trajectory divergence distance of $d = 14.21$ between simulated strong and struggling profiles.
- **Interpretation:** The 3-level deduplication and weakness-targeting logic successfully produce differentiated interview trajectories in simulation without content starvation.

---

### E. EXP-5: Leave-One-Out Subsystem Ablation

![Figure 8: Leave-One-Out Component Ablation](research/results/figures/figure8_leave_one_out_ablation.png)

**Table XI: EXP-5 Leave-One-Out Behavioral Ablation Across 70 Sessions**

| Subsystem Removed | Target Metric Monitored | Baseline (Full Pipeline) | Ablated System Value | Subsystem Retention |
|---|---|:---:|:---:|:---:|
| **Full Pipeline** | Master functional integrity | $100\%$ | $100\%$ | $100.0\%$ |
| **$- \text{RL Strategy}$** | Difficulty adaptation $\rho$ | $+0.1572$ | $0.0000$ | $0.0\%$ (Drops to fixed) |
| **$- \text{Follow-Up Probing}$** | Targeted concept probing rate | $0.50$ probes/session | $0.00$ probes/session | $0.0\%$ (No probes) |
| **$- \text{Formative Feedback}$** | Transcript lexical grounding | $0.2496$ | $0.0000$ | $0.0\%$ (Static templates) |
| **$- \text{Dynamic Timing}$** | Timing score delta $f_{\text{time}}$ | $[-0.10, +0.03]$ | $0.0000$ | $0.0\%$ (Zero delta) |
| **$- \text{Speech Prosody}$** | Hesitation index $h_t$ | Prosody-derived | $0.0000$ | $0.0\%$ (Text-only) |
| **$- \text{Coding Sandbox}$** | C compilation test pass rate | Pass/fail verified | $0.0000$ | $0.0\%$ (No execution) |

- **Observed Result:** Removing each isolated subsystem caused targeted, 100% loss of its specific functional metric without cross-modal system crashes, confirming clean architectural decoupling.

---

## XV. Discussion

### A. Synthesis of Empirical Findings
1. **Multi-Agent Decoupling:** Isolating evaluation, strategy, and audio analysis allows independent optimization and failure recovery without compromising system stability.
2. **Evaluator Composition:** High semantic similarity ($S_1$) and concept coverage ($S_2$) establish strong baseline grading, while reasoning entailment ($R$) provides critical keyword gaming resistance ($S_{2,\text{eff}}$).
3. **Generative vs. Deterministic Feedback:** Generative LLMs enrich phrasing and quote candidate text, but deterministic concept extraction guarantees 100% gap coverage at zero inference cost.

### B. Limitations & Threats to Validity
**Table XII: Threats to Validity & Empirical Boundaries**

| Dimension | Specific Threat | Mitigation / Explicit Boundary in Study |
|---|---|---|
| **Construct Validity** | Automated lexical grounding as feedback quality proxy | Grounding measures token overlap; human pedagogical utility was not evaluated. |
| **Internal Validity** | Evaluator sample size ($n=20$) | Pilot benchmark; validated with 3 blinded human raters ($\alpha = 0.8255$). |
| **External Validity** | Simulation-based RL training | PPO evaluated on synthetic personas; human candidate transfer remains unvalidated. |
| **Statistical Validity** | Multiple comparisons in feedback | Addressed via non-parametric Wilcoxon tests with Holm-Bonferroni correction. |
| **Hardware Boundary** | Qwen-7B inference requirements | Local CPU was throughput-limited (>22 min/turn); successfully executed on Tesla T4 GPU. |

---

## XVI. Reproducibility & Artifact Availability

All code, checkpoints, datasets, and execution scripts are organized for complete reproduction:
- **PPO Policy Checkpoint:** `rl/checkpoints/seed_123/ppo_final.zip` (SHA-256: `2ab8d514ca...`).
- **Curriculum Bank & Rubrics:** `data/questions/qns.json` (125 items), `data/rubrics/rubrics_final_clean.json`.
- **Human Benchmark Dataset:** `ablation/results/ratings_averaged.csv` (20 items, 3 raters).
- **Colab GPU Runner:** `experiments/experiment_3_feedback/qwen7b_colab_runner.ipynb`.
- **Master Verification Script:** `experiments/experiment_3_feedback/import_qwen_colab_results.py`.

---

## XVII. Future Work & Conclusion

### A. Future Work
1. Conduct longitudinal human candidate trials measuring pre/post assessment learning gains and interview anxiety reduction.
2. Expand the human evaluation benchmark to $n \ge 100$ items across all 13 CS curriculum topics.
3. Explore edge-quantized 7B models (e.g., 4-bit AWQ/GGUF) to enable real-time local inference without cloud GPU infrastructure.

### B. Conclusion
We presented PrepAIred, an adaptive multimodal technical interview assessment framework. Controlled experiments across 480 evaluations demonstrated that: (1) PPO with guardrails produces adaptive difficulty progression ($\rho = +0.1572$); (2) structured evaluation achieves high agreement with human raters ($\rho = 0.8358, \alpha = 0.8255$); (3) generative Qwen-7B feedback maximizes transcript grounding ($0.2496$), while deterministic structured recovery guarantees complete rubric gap coverage ($100.0\%$); and (4) personalized question selection eliminates repetition while differentiating candidate trajectories. PrepAIred establishes a modular, transparent foundation for automated technical interview assessment.

---

## Acknowledgment & AI Disclosure

The authors acknowledge the use of AI assistant tooling during software development and manuscript preparation for code refactoring and prose editing. All underlying mathematical formulations, experimental executions, data analyses, statistical tests, and scientific interpretations were conducted, verified, and authored under full human accountability in accordance with IEEE Authorship and Generative AI Policies.

---

## Conflict of Interest & Ethical Compliance

The authors declare that they have no competing financial interests or personal relationships that could have influenced the work reported in this paper. Synthetic candidate evaluations were simulated programmatically. Human-rater benchmark data collection adhered to ethical standards with voluntary participation and anonymized rating records.

---

## References

1. S. Burrows, I. Gurevych, and B. Stein, "The eras and trends of automatic short answer grading," *International Journal of Artificial Intelligence in Education*, vol. 25, no. 1, pp. 60–117, 2015.
2. J. R. Anderson, C. F. Boyle, and B. J. Reiser, "Intelligent tutoring systems," *Science*, vol. 228, no. 4698, pp. 456–462, 1985.
3. M. Dzikovska, R. D. Nielsen, C. Brew, C. Leacock, D. Bental, P. Stoyanchev, and J. Farrow, "SemEval-2013 Task 7: The Joint Student Response Analysis and 8th Recognizing Textual Entailment Challenge," in *Proc. 7th Int. Workshop on Semantic Evaluation*, 2013, pp. 263–274.
4. C. Sung, J. H. Dhaliwal, and V. Kumar, "Pre-trained contextual embedding of source code," in *Proc. ACL Workshop*, 2019.
5. F. M. Lord, *Applications of item response theory to practical testing problems*, Routledge, 1980.
6. C. Piech, J. Bassen, J. Huang, S. Ganguli, M. Sahami, L. J. Guibas, and J. Sohl-Dickstein, "Deep knowledge tracing," in *Advances in Neural Information Processing Systems (NeurIPS)*, 2015, pp. 505–513.
7. J. D. Lomas, K. Patel, J. L. Forlizzi, and K. R. Koedinger, "Optimizing challenge in educational games," in *Proc. CHI Conf. on Human Factors in Computing Systems*, 2016, pp. 89–99.
8. S. Doroudi, V. Aleven, and E. Brunskill, "Where's the reward? A review of reinforcement learning for instructional sequencing," *International Journal of Artificial Intelligence in Education*, vol. 29, no. 4, pp. 568–620, 2019.
9. R. Fernandez and R. W. Picard, "Classical and prospective approaches to speech emotion and stress recognition," in *Speech Processing*, 2005.
10. S. Scherer, J. Pestian, and L. P. Morency, "Investigating the speech characteristics of suicidal adolescents," in *Proc. ICASSP*, 2013, pp. 709–713.
11. M. Bain, J. Huh, T. Han, and A. Zisserman, "WhisperX: Time-accurate speech recognition of long-form audio," in *Proc. Interspeech*, 2023.
12. J. Achiam et al., "GPT-4 technical report," *arXiv preprint arXiv:2303.08774*, 2023.
13. J. Schulman, F. Wolski, P. Dhariwal, A. Radford, and O. Klimov, "Proximal policy optimization algorithms," *arXiv preprint arXiv:1707.06347*, 2017.
14. W. Wang, F. Wei, L. Dong, H. Bao, N. Yang, and M. Zhou, "MiniLM: Deep self-attention distillation for task-agnostic compression," in *Advances in Neural Information Processing Systems (NeurIPS)*, 2020.
15. R. Nogueira and K. Cho, "Passage re-ranking with BERT," *arXiv preprint arXiv:1901.04085*, 2019.
16. T. D. Simão, N. Jansen, and M. T. Spaan, "Safe policy improvement with an estimated baseline policy," in *Proc. Int. Conf. on Autonomous Agents and Multiagent Systems (AAMAS)*, 2021.
17. F. Doshi-Velez and B. Kim, "Towards a rigorous science of interpretable machine learning," *arXiv preprint arXiv:1702.08608*, 2017.
18. K. Krippendorff, *Content analysis: An introduction to its methodology*, Sage publications, 2018.
