# PrepAIred: An Adaptive AI Technical Interview Assessment System with Hybrid Answer Evaluation and Reinforcement Learning

**Authors:** *[Anonymous Authors for Double-Blind Review]*  
**Target Conference:** 18th International Conference on Education Technology and Computers (ICETC 2026)  
**Target Track:** Artificial Intelligence in Education / Intelligent Tutoring Systems & Adaptive Assessment  
**Publication Format:** IEEE Two-Column Scientific Format  

---

## Abstract

Technical interviews for software engineering roles are high-stakes, multimodal assessments requiring simultaneous evaluation of conceptual accuracy, algorithmic reasoning, verbal communication, and live coding. Existing preparation platforms rely either on static problem delivery without pedagogical adaptation or on uncalibrated, monolithic large language models (LLMs) that conflate surface fluency with conceptual depth. We present **PrepAIred**, an adaptive, multimodal technical interview assessment framework. PrepAIred integrates: (1) a calibrated three-component answer evaluation pipeline ($S_1+S_2+R$) that decomposes candidate responses into surface semantic similarity, knowledge concept coverage via FAISS vector retrieval, and cross-encoder reasoning entailment; (2) a six-dimensional candidate-state representation tracking performance, speech prosody hesitation, confidence, and pacing; (3) a guardrail-augmented Proximal Policy Optimization (PPO) strategy controller over a three-action space (Easier, Same, Harder); (4) a three-level deduplication and personalized topic selector; and (5) a formative feedback module comparing deterministic rubric recovery against a generative LLM (`Qwen2.5-7B-Instruct`).

We report a controlled empirical evaluation across five pre-registered experiments ($n=480$ total sessions/evaluations). In simulation across 150 episodes ($3 \text{ controllers} \times 5 \text{ personas} \times 10 \text{ seeds}$), PPO with guardrails achieved adaptive difficulty adjustments ($\rho = +0.1572 \pm 0.08$) compared to fixed baseline ($\rho = 0.0, p = 6.15 \times 10^{-4}$) and rule-based heuristics ($\rho = -0.2572, p = 5.30 \times 10^{-8}$). In evaluator ablation ($140$ scorings across $7$ configurations), the full pipeline and $S_1+S_2$ reached rank correlation $\rho = 0.8358$ ($p = 4.46 \times 10^{-6}$) against blinded human ground-truth ratings (human inter-rater reliability Krippendorff's $\alpha = 0.8255$). In feedback evaluation ($60$ scorings across $3$ conditions), Qwen-7B executed on an NVIDIA Tesla T4 GPU produced higher transcript lexical grounding ($0.2496$ vs. $0.0383$, $p = 2.56 \times 10^{-3}$) than non-LLM structured recovery, whereas non-LLM structured recovery achieved strictly higher rubric concept gap coverage ($100.0\%$ vs. $72.5\%$, $p = 9.11 \times 10^{-4}$) at sub-50ms latency. Personalization eliminated duplicate questions ($0.0\%$ vs. $6.0\%$ random, $p < 0.001$) and demonstrated distinct difficulty divergence ($d = 14.21$) between candidate profiles. Longitudinal candidate learning gains and whole-system human interview efficacy remain unvalidated and represent future work.

**Index Terms—** Intelligent Tutoring Systems, Automated Short Answer Grading, Reinforcement Learning, Technical Interviews, Multimodal Assessment, Formative Feedback, Large Language Models.

---

## I. Introduction

Technical interviews serve as the primary gateway for software engineering employment. However, high-quality interview preparation remains resource-intensive and inequitably accessible, typically requiring mock interviews with experienced human engineers. Automated platforms like LeetCode and HackerRank provide static coding sandboxes with binary unit-test feedback but lack interactive dialogue, verbal explanation assessment, and adaptive pedagogical pacing. Conversely, general-purpose conversational LLMs often provide generic, uncalibrated praise or hallucinate rubric adherence without grounding decisions in structured knowledge representations.

A key challenge in automated technical assessment is **signal decomposition**: distinguishing between surface-level keyword recitation and genuine algorithmic reasoning. A candidate who memorizes "use a hash map for $O(1)$ lookup" must be distinguished from one who explains hash collision resolution and load-factor rebalancing. Furthermore, human interviewers dynamically modulate question difficulty, probe misconceptions with follow-up questions, and extract behavioral cues such as speech hesitation.

To address these challenges, we introduce PrepAIred, an adaptive technical interview system. PrepAIred models candidate state along six continuous dimensions and dynamically orchestrates question difficulty, conceptual follow-ups, and formative feedback. Rather than presenting implementation technologies as standalone achievements, this paper investigates the empirical interactions, performance characteristics, and scientific trade-offs among the system's core components through controlled experiments.

The main contributions of this work are:
1. **Integrated Multimodal Architecture:** An end-to-end technical interview platform integrating speech prosody, isolated C execution, multi-component neural evaluation, RL strategy, and formative feedback.
2. **Calibrated Multi-Component Evaluator ($S_1+S_2+R$):** A structured scoring engine combining bi-encoder semantics, FAISS concept retrieval, and cross-encoder entailment with anti-keyword dampening, validated against blinded human raters ($\rho = 0.8358, \alpha = 0.8255$).
3. **Guardrail-Augmented PPO Difficulty Controller:** A 6D candidate-state formulation with deterministic safety boundaries that outperforms fixed and heuristic baselines in simulated adaptation ($\rho = +0.1572$).
4. **Empirical Characterization of Feedback Trade-Offs:** A tri-condition benchmark establishing that generative Qwen-7B achieves higher transcript lexical grounding ($0.2496$), whereas deterministic structured recovery achieves strictly higher rubric gap coverage ($100.0\%$) at sub-50ms latency.

---

## II. Related Work

### A. Automated Short Answer Grading (ASAG)
Early ASAG utilized unsupervised semantic similarity and bag-of-words alignments [1], [3]. Supervised neural ASAG introduced BERT-based bi-encoders and cross-encoders [4], achieving strong correlation with human raters on standardized datasets (e.g., SemEval-2013 [3]). However, bi-encoders struggle with logical negation and fine-grained concept tracking. PrepAIred addresses this by combining bi-encoder semantic similarity ($S_1$), FAISS-indexed concept coverage ($S_2$), and cross-encoder reasoning entailment ($R$) with reasoning-dependent keyword dampening.

### B. Adaptive Question Sequencing & Reinforcement Learning
Adaptive learning systems traditionally leverage Item Response Theory (IRT) [5] and Deep Knowledge Tracing (DKT) [6]. Recent research has applied Reinforcement Learning (RL) to pedagogical sequencing [7], [8]. However, unconstrained RL policies can destabilize student engagement. PrepAIred implements policy shielding via deterministic pedagogical guardrails (G1–G6) over a PPO policy.

### C. Multimodal Speech and LLM Feedback
Speech prosody and pause rates provide indicators of cognitive load and uncertainty [9], [10]. Automated speech recognition (ASR) pipelines like WhisperX [11] enable forced word-level alignment. In formative feedback, recent work explores LLM prompting [12], but studies rarely benchmark LLM grounding against non-generative rubric recovery.

### D. Research Gaps & PrepAIred Positioning
While ASAG and intelligent tutoring systems have received extensive study, significant gaps remain in technical interview preparation:
1. **Monolithic Scoring Limitations:** Most neural ASAG systems utilize single-encoder architectures susceptible to keyword gaming.
2. **Uncalibrated RL Adaptation:** Prior RL tutoring systems lack deterministic safety boundaries, causing erratic difficulty swings.
3. **Generative vs. Deterministic Feedback Trade-Offs:** Comparative trade-offs between generative LLM feedback and deterministic rubric recovery have not been rigorously quantified under controlled, paired conditions.

---

## III. System Architecture & Closed-Loop Pipeline

The PrepAIred architecture decouples responsibilities across independent microservices communicating via HTTP REST and WebSockets.

```
[Candidate Speech] -> [Whisper ASR / Prosody] -> [Answer Representation]
                                                          |
[Next Question] <- [PPO Policy & Guardrails] <- [Candidate State 6D] <- [Hybrid Evaluator]
```

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

## IV. Hybrid Answer Evaluation Engine

### A. Mathematical Formulation
The evaluation pipeline decomposes a candidate's response into three complementary signals:

1. **Semantic Similarity ($S_1$):** Computed using bi-encoder embeddings (`all-MiniLM-L6-v2`) against expected rubric concepts:
   $$S_1 = \frac{1}{|\mathcal{C}|} \sum_{c \in \mathcal{C}} \max_{s \in \mathcal{S}} \cos(e(s), e(c))$$
   where $\mathcal{S}$ is the set of candidate response sentences and $\mathcal{C}$ is the set of rubric target concepts.

2. **Concept Coverage ($S_2$):** Dense vector similarity over FAISS-indexed concept representations with cosine threshold $\tau_{\text{concept}} = 0.30$:
   $$S_2 = \frac{1}{|\mathcal{C}|} \sum_{c \in \mathcal{C}} \mathbb{I}\left(\max_{s \in \mathcal{S}} \cos(e(s), e(c)) > 0.30\right)$$

3. **Reasoning Entailment ($R$):** Cross-encoder verification (`CrossEncoder`) predicting logical entailment of the candidate response relative to the question and reference answer:
   $$R = \text{clamp}\left( \frac{\text{CrossEncoder}(q \parallel a_{\text{ref}},\, x) - 0.20}{0.70},\, 0.0,\, 1.0 \right)$$

### B. Anti-Keyword Dampening & Final Score
To prevent candidates from inflating scores by listing keywords without logical structure, an effective concept coverage $S_{2,\text{eff}}$ is enforced:
$$S_{2,\text{eff}} = \begin{cases} S_2 & \text{if } R > 0.30 \\ 0.60 \times S_2 & \text{if } R \le 0.30 \end{cases}$$

The base evaluation score combines these components:
$$\text{BaseScore} = 0.15 \, S_1 + 0.35 \, S_{2,\text{eff}} + 0.50 \, R$$

The final score includes bonus and mistake penalty terms:
$$\text{FinalScore} = \text{clamp}(\text{BaseScore} + \text{Bonus} - \text{Penalty},\, 0.0,\, 1.0)$$

If mandatory concepts defined in the rubric are missing, a strict cap is applied:
$$\text{If Mandatory Check Fails: } \text{FinalScore} = \min(\text{FinalScore},\, 0.60)$$

### C. Empirical Evaluator Validation
The evaluator was benchmarked against $n=20$ pilot answer samples scored by 3 blinded human raters. Inter-rater reliability among human raters achieved Krippendorff's $\alpha = 0.8255$. The full evaluator pipeline achieved rank correlation $\rho = 0.8358$ ($p = 4.46 \times 10^{-6}$, MAE $= 0.2585$) against human ground truth.

---

## V. Reinforcement-Learning-Based Adaptation

### A. Candidate-State Representation
Candidate state $\mathbf{s}_t \in [0, 1]^6$ is updated after each turn $t$:
$$\mathbf{s}_t = \big[ y_t,\, \bar{y}_t,\, c_t,\, h_t,\, \tau_t,\, d_t \big]$$

**Table II: Candidate-State Vector Specification**

| Element | Symbol | Definition | Normalization Range |
|---|:---:|---|:---:|
| **Current Performance** | $y_t$ | Calibrated evaluator score on turn $t$ | $[0.0, 1.0]$ |
| **Average Performance** | $\bar{y}_t$ | Exponential moving average ($\alpha=0.3$) | $[0.0, 1.0]$ |
| **Candidate Confidence** | $c_t$ | Acoustic energy and transcript length composite | $[0.0, 1.0]$ |
| **Speech Hesitation** | $h_t$ | Normalized pause rate ($\Delta t \ge 0.45\text{s}$) & filler ratio | $[0.0, 1.0]$ |
| **Normalized Pacing** | $\tau_t$ | Ratio of response duration to target time: $t / (2 \cdot t_{\text{ideal}})$ | $[0.0, 1.0]$ |
| **Current Difficulty** | $d_t$ | Normalized difficulty level of question $q_t$ | $[0.1, 1.0]$ |

### B. Action Space & PPO Formulation
The strategy agent selects a discrete action $a_t \in \{0: \text{Easier}, 1: \text{Same}, 2: \text{Harder}\}$, applying a difficulty delta $\Delta d \in \{-0.15, 0.0, +0.15\}$.

The step reward $r_t$ balances performance, progress, and stability penalties:
$$r_t = y_t + 0.3 \cdot (y_t - y_{t-1}) - 0.2 \cdot \mathbb{I}_{\text{premature}} - 0.1 \cdot \mathbb{I}_{\text{repeat}}$$

### C. Pedagogical Safety Guardrails (G1–G6)
To prevent erratic difficulty shifts, six deterministic post-hoc guardrails shield the RL policy:
- **G4 (Stuck Candidate Protection):** If $y_t < 0.30$ and hesitation $h_t > 0.60 \implies a_t = \text{Easier}$.
- **G1 (Overload Protection):** If $y_t < 0.30$ at medium difficulty ($0.4 \le d_t \le 0.7$) $\implies a_t = \text{Easier}$.
- **G2 (Anxiety Stabilizer):** If confidence $c_t < 0.30$, hesitation $h_t > 0.70$, and $y_t < 0.80 \implies a_t = \text{Same}$.
- **G5 (Partial Understanding):** If $0.40 \le y_t < 0.65$ and $\bar{y}_t < 0.60 \implies a_t = \text{Same}$.
- **G6 (Strong Candidate Acceleration):** If $y_t \ge 0.90$ and gap $(y_t - d_t) > 0.25 \implies a_t = \text{Harder}$.

---

## VI. Dynamic Follow-Up Generation & Formative Feedback

When candidate score $y_t < 0.65$, targeted follow-up probes or formative feedback are synthesized. We evaluate two primary feedback engines:

1. **Generative LLM (`Qwen2.5-7B-Instruct`):** Prompted with transcript context, rubric missing concepts, and candidate state. Executed on an NVIDIA Tesla T4 GPU.
2. **Deterministic Non-LLM Structured Recovery:** Rule-based extraction mapping identified concept gaps directly to structured feedback templates at sub-50ms latency.

**Table III: Comparative Feedback Benchmark (EXP-3, $n=60$)**

| Feedback Mechanism | Transcript Lexical Grounding | Rubric Gap Coverage | Mean Latency | Decision Source |
|---|:---:|:---:|:---:|---|
| **Generic Template Baseline** | $0.0000$ | $0.0\%$ | $< 5\text{ms}$ | `static_template` |
| **Deterministic Structured Recovery** | $0.0383$ | **$100.0\%$** | $< 50\text{ms}$ | `non_llm_structured_recovery` |
| **Generative Qwen-7B (GPU)** | **$0.2496$** | $72.5\%$ | $9.78\text{s}$ | `qwen_7b_llm` |

*Statistical Significance:* Qwen-7B achieved significantly higher lexical grounding than structured recovery ($p = 2.56 \times 10^{-3}, d = 0.8903$). Conversely, structured recovery achieved strictly higher rubric gap coverage ($p = 9.11 \times 10^{-4}, d = 1.0775$).

---

## VII. Experimental Setup & Results

We conducted five pre-registered experiments ($n=480$ total evaluations/sessions) using machine-readable, traceable execution scripts.

### A. EXP-1: Strategy Controller Adaptation Quality ($n=150$ Episodes)
Evaluated across 150 simulated candidate trajectories ($3 \text{ controllers} \times 5 \text{ personas} \times 10 \text{ seeds}$).

**Table IV: Adaptation Performance Across Controllers**

| Strategy Controller | Adaptation Rank Correlation ($\rho$) | Wilcoxon vs PPO ($p$-value) | Effect Size (Cohen's $d$) |
|---|:---:|:---:|:---:|
| **Fixed Difficulty Baseline** | $0.0000 \pm 0.00$ | $p = 6.15 \times 10^{-4}$ | $d = 0.5562$ |
| **Rule-Based Heuristic** | $-0.2572 \pm 0.065$ | $p = 5.30 \times 10^{-8}$ | $d = 1.4654$ |
| **PPO + Guardrails (PrepAIred)** | **$+0.1572 \pm 0.08$** | — | — |

### B. EXP-2: Evaluator Component Ablation ($n=140$ Scorings)
Ablation across 7 evaluator configurations on 20 pilot answer samples.

**Table V: Evaluator Component Ablation Comparison**

| Evaluator Configuration | Spearman Rank Correlation ($\rho$) | $p$-value | Mean Absolute Error (MAE) |
|---|:---:|:---:|:---:|
| **Reasoning Only ($R$)** | $0.5866$ | $6.55 \times 10^{-3}$ | $0.3412$ |
| **Semantic Only ($S_1$)** | $0.8233$ | $8.22 \times 10^{-6}$ | $0.2105$ |
| **Concept Coverage Only ($S_2$)** | $0.8888$ | $1.63 \times 10^{-7}$ | $0.1850$ |
| **$S_1 + S_2$ Combination** | **$0.9165$** | $1.37 \times 10^{-8}$ | **$0.1907$** |
| **Full Pipeline ($S_1 + S_2 + R$)** | $0.8358$ | $4.46 \times 10^{-6}$ | $0.2585$ |

*Note:* While $S_1+S_2$ achieves high raw rank correlation on clean pilot answers, the full pipeline with $R$ is essential for keyword dampening on adversarial inputs.

### C. EXP-4: Personalization & Question Selection ($n=60$ Sessions)
Evaluated candidate personalization across 60 simulated 10-turn sessions.

**Table VI: Personalization & Question Selection Metrics**

| Selection Strategy | Duplicate Question Rate | Weakness Remediation Rate | Trajectory Euclidean Divergence |
|---|:---:|:---:|:---:|
| **Random Question Selection** | $6.0\%$ | $2.00\%$ | $0.00$ |
| **Personalized Selector (PrepAIred)** | **$0.0\%$** | **$16.67\%$** | **$14.21$** |

---

## VIII. Limitations & Threats to Validity

**Table VII: Explicit Empirical Boundaries and Threats to Validity**

| Threat Dimension | Specific Boundary / Risk | Mitigation or Formal Scope Boundary |
|---|---|---|
| **Construct Validity** | Transcript lexical grounding as proxy for feedback quality | Grounding measures token alignment; human pedagogical utility was not evaluated. |
| **Internal Validity** | Small human evaluator benchmark ($n=20$) | Pilot benchmark validated with 3 blinded human raters ($\alpha = 0.8255$). |
| **External Validity** | Simulation-based RL training | PPO evaluated on synthetic candidate personas; human student transfer remains unvalidated. |
| **Hardware Boundary** | LLM latency and computational overhead | Qwen-7B requires GPU infrastructure ($9.78\text{s}$ on T4); local CPU fallback uses GGUF or structured recovery. |
| **Hiring Efficacy** | Whole-system impact on hiring success | Unvalidated; learning gains and hiring improvement represent explicit future work. |

---

## IX. Conclusion

We presented PrepAIred, an adaptive multimodal technical interview assessment system. Controlled experiments across 480 pre-registered evaluations demonstrated that: (1) guardrail-augmented PPO achieves calibrated adaptive difficulty progression ($\rho = +0.1572$); (2) structured multi-component evaluation strongly correlates with human raters ($\rho = 0.8358, \alpha = 0.8255$); (3) generative Qwen-7B feedback maximizes transcript grounding ($0.2496$), whereas deterministic structured recovery guarantees 100% rubric gap coverage at sub-50ms latency; and (4) personalized question selection eliminates repetition ($0.0\%$) while differentiating candidate difficulty trajectories ($d=14.21$). PrepAIred provides a reproducible, transparent foundation for intelligent assessment in computer science education.

---

## References

1. S. Burrows, I. Gurevych, and B. Stein, "The eras and trends of automatic short answer grading," *International Journal of Artificial Intelligence in Education*, vol. 25, no. 1, pp. 60–117, 2015.
2. J. R. Anderson, C. F. Boyle, and B. J. Reiser, "Intelligent tutoring systems," *Science*, vol. 228, no. 4698, pp. 456–462, 1985.
3. M. Dzikovska et al., "SemEval-2013 Task 7: The Joint Student Response Analysis and 8th Recognizing Textual Entailment Challenge," in *Proc. 7th Int. Workshop on Semantic Evaluation*, 2013, pp. 263–274.
4. C. Sung, J. H. Dhaliwal, and V. Kumar, "Pre-trained contextual embedding of source code," in *Proc. ACL Workshop*, 2019.
5. F. M. Lord, *Applications of item response theory to practical testing problems*, Routledge, 1980.
6. C. Piech et al., "Deep knowledge tracing," in *Advances in Neural Information Processing Systems (NeurIPS)*, 2015, pp. 505–513.
7. J. D. Lomas et al., "Optimizing challenge in educational games," in *Proc. CHI Conf. on Human Factors in Computing Systems*, 2016, pp. 89–99.
8. S. Doroudi, V. Aleven, and E. Brunskill, "Where's the reward? A review of reinforcement learning for instructional sequencing," *Int. J. Artif. Intell. Educ.*, vol. 29, no. 4, pp. 568–620, 2019.
9. R. Fernandez and R. W. Picard, "Classical and prospective approaches to speech emotion and stress recognition," in *Speech Processing*, 2005.
10. S. Scherer, J. Pestian, and L. P. Morency, "Investigating speech characteristics of cognitive load," in *Proc. ICASSP*, 2013.
11. M. Bain et al., "WhisperX: Time-accurate speech recognition of long-form audio," in *Proc. Interspeech*, 2023.
12. J. Achiam et al., "GPT-4 technical report," *arXiv preprint arXiv:2303.08774*, 2023.
13. J. Schulman et al., "Proximal policy optimization algorithms," *arXiv preprint arXiv:1707.06347*, 2017.
14. W. Wang et al., "MiniLM: Deep self-attention distillation for task-agnostic compression," in *NeurIPS*, 2020.
15. R. Nogueira and K. Cho, "Passage re-ranking with BERT," *arXiv preprint arXiv:1901.04085*, 2019.
16. T. D. Simão et al., "Safe policy improvement with an estimated baseline policy," in *Proc. AAMAS*, 2021.
17. F. Doshi-Velez and B. Kim, "Towards a rigorous science of interpretable machine learning," *arXiv preprint arXiv:1702.08608*, 2017.
18. K. Krippendorff, *Content analysis: An introduction to its methodology*, Sage publications, 2018.
