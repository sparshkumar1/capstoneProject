# ARCHIVED / SUPERSEDED — NOT A SOURCE OF CURRENT FACTS
> **Superseded by:** 
esearch/papers/paper1_systems/, paper2_evaluator/, paper3_rl/ and 
esearch/CANONICAL_SCIENTIFIC_TRUTH.md  
> **Date Archived:** 2026-09-17  
> **Reason:** Legacy monolithic draft pre-dating 3-paper target split and containing superseded numbers (e.g. synthetic proxy rho=0.9152, 204k steps). Preserved strictly for historical reference.  
> **Important Information Retained in:** 
esearch/CANONICAL_SCIENTIFIC_TRUTH.md and active paper directories.

---

# Closed-Loop Technical Interview Assessment via Calibrated Neural Evaluation, Reinforcement-Learning Adaptation, and Grounded Generative Probing

**Anonymous Authors / Author Placeholders**  
*Department of Computer Science and Engineering, Institutional Affiliation Placeholder*  
*Corresponding Author: Corresponding Author Placeholder (email: author@institution.edu, ORCID: 0000-0000-0000-0000)*

---

### Abstract
Technical software engineering interviews require candidates to verbally articulate algorithmic trade-offs, respond to dynamic conceptual follow-ups, and implement executable code under cognitive constraints. However, existing automated preparation platforms remain fundamentally divided between static code-judging puzzles that offer zero verbal dialogue, and uncalibrated conversational agents that suffer from rubric drift, score hallucination, and unconstrained pedagogical policies. In this paper, we present **PrepAIred**, an open-source, multimodal framework for closed-loop technical interview assessment and formative remediation. PrepAIred establishes an integrated assessment cycle—$\text{Assess} \to \text{Diagnose} \to \text{Model} \to \text{Adapt} \to \text{Probe} \to \text{Reassess}$—through four decoupled subsystems: (1) a calibrated multi-task cross-encoder neural evaluator ($S_1 + S_2 + R$) that scores semantic relevance ($S_1$), dense concept coverage ($S_2$), and logical entailment ($R$) while applying an anti-keyword dampening shield against superficial buzzword stuffing; (2) a Proximal Policy Optimization (PPO) reinforcement learning controller operating over a continuous 6-dimensional candidate state space $\mathbf{s}_t \in [0, 1]^6$ (incorporating moving average score, acoustic confidence $c_t$, hesitation $h_t$, speaking pacing $\tau_t$, turn score $s_t$, and current difficulty $d_t$) governed by six deterministic safety guardrails; (3) an evaluator-grounded generative follow-up engine that formatively probes identified missing concepts while maintaining the evaluator as the sole correctness judge; and (4) an isolated, resource-constrained containerized execution sandbox for C source code evaluation. Across $n = 480$ pre-registered experimental trials, our neural evaluator achieved a Spearman rank correlation of $\rho = 0.8358$ ($p = 4.46 \times 10^{-6}$, $\text{MAE} = 0.2585$) with expert ratings across a 20-item benchmark dataset, aligning with human expert inter-rater reliability (Krippendorff's $\alpha = 0.8255$, 56 paired judgments). In simulation, the PPO controller maintained candidate scores in a target zone of proximal development significantly better than fixed ($\rho = 0.0000, p = 6.15 \times 10^{-4}, d = 0.5562$) and oscillating rule-based baselines ($\rho = -0.2572, p = 5.30 \times 10^{-8}, d = 1.4654$). Evaluator-grounded probing achieved a transcript lexical grounding score of $0.2496$ and covered $72.5\%$ of identified rubric gaps. Finally, we demonstrate that the complete live framework executes reproducibly on commodity x64 CPU hardware via 4-bit quantization (1,065.6 MB model size) with pure local inference.

**INDEX TERMS:** Adaptive testing, automated short-answer grading, computer science education, educational technology, intelligent tutoring systems, large language models, multimodal learning analytics, reinforcement learning, speech prosody.

---

## I. INTRODUCTION

THE technical software engineering interview is the primary gateway for employment across the software industry. Unlike automated programming contests, real-world interviews assess a candidate across multiple interrelated communication and problem-solving modalities: explaining algorithmic complexity aloud, defending data structure trade-offs, clarifying ambiguities when probed by an interviewer, and writing syntactically correct code under execution constraints [1], [2].

Despite the critical importance of these skills, existing automated preparation tools suffer from an acute pedagogical divide:
1. *Static Automated Judges (e.g., LeetCode, HackerRank):* These systems assess candidate submissions strictly through binary unit-test execution. They capture no verbal explanations, provide no dynamic adaptation during an interview session, offer no conceptual follow-up questions, and provide no formative diagnostics explaining why a solution's design or reasoning was flawed [3], [4].
2. *Uncalibrated Conversational LLMs (e.g., vanilla ChatGPT):* Although capable of fluent conversation, general-purpose LLMs exhibit significant rubric drift, non-deterministic grading variance, vulnerability to prompt injection or buzzword gaming, and lack mathematically grounded pedagogical controllers [5], [6]. Crucially, an unconstrained LLM cannot guarantee deterministic evaluation invariants or enforce strict execution security boundaries.

To address these limitations, automated technical interview preparation must be formulated not as an unguided chat session or a static grading script, but as an **integrated, closed-loop adaptive assessment framework**. In intelligent tutoring and educational measurement, an effective closed-loop cycle requires six tightly coupled phases:
$$\text{Assess} \longrightarrow \text{Diagnose} \longrightarrow \text{Model} \longrightarrow \text{Adapt} \longrightarrow \text{Probe} \longrightarrow \text{Reassess}$$

In this paper, we propose **PrepAIred**, an open-source, multimodal framework for closed-loop technical interview assessment. Rather than treating a large language model as an omniscient agent that simultaneously interviews, grades, and adapts, PrepAIred strictly decouples **calibrated neural evaluation**, **multimodal candidate state modeling**, **reinforcement-learning difficulty adaptation**, and **grounded generative follow-up probing**.

### Scientific Contributions
This work makes five key contributions:
1. **Multi-Component Calibrated Neural Evaluator ($S_1 + S_2 + R$):** We design and validate a three-part scoring pipeline combining SBERT semantic similarity ($S_1$), dense FAISS concept coverage ($S_2$), and Cross-Encoder logical entailment ($R$), augmented with an anti-keyword dampening rule that penalizes superficial buzzword stuffing when causal reasoning is absent ($R \le 0.30$).
2. **Multimodal 6D Learner State Representation:** We formulate a continuous candidate state vector $\mathbf{s}_t = [\bar{s}_t, c_t, h_t, \tau_t, s_t, d_t] \in [0, 1]^6$ that jointly incorporates performance history, acoustic prosodic confidence ($c_t$), speech hesitation rate ($h_t$), speaking pacing ($\tau_t$), immediate turn score ($s_t$), and normalized difficulty ($d_t$).
3. **Safety-Shielded PPO Difficulty Controller:** We train an Actor-Critic Proximal Policy Optimization policy to optimize candidate trajectory placement in a target Zone of Proximal Development (ZPD) score band ($s_t \in [0.45, 0.75]$), constrained by six deterministic safety guardrails ($G_1$--$G_6$) that prevent destabilizing difficulty oscillations.
4. **Evaluator-Grounded Generative Probing & Reassessment:** We formulate a closed-loop follow-up cycle where a local generative model generates targeted probes directed exclusively at identified missing concepts, while the neural evaluator reassesses the follow-up answer against the parent rubric to measure concept resolution.
5. **Empirical Validation & Local CPU Reproducibility:** We validate the framework across $n = 480$ pre-registered experimental trials and human expert benchmarks (Krippendorff's $\alpha = 0.8255$), demonstrating that the complete live pipeline executes reproducibly on commodity CPU hardware using a 4-bit quantized 1.5B local model (~1.06 GB) and isolated Docker containerization.

---

## II. RELATED WORK

### A. Automated Short-Answer Grading (ASAG) in Computer Science
Automated short-answer grading has progressed from surface lexical matching (BLEU, ROUGE) to dense semantic representations using Sentence-BERT and cross-encoders [7], [8]. While bi-encoders efficiently measure semantic similarity, recent studies show they remain susceptible to "keyword gaming"—where candidates recite memorized technical terminology without explaining underlying mechanisms [9]. Recent hybrid architectures combine dense concept extraction with entailment classification [10]. PrepAIred advances this by introducing an explicit anti-keyword dampening penalty that couples structural concept coverage ($S_2$) directly to cross-encoder logical entailment ($R$).

### B. Adaptive Testing and Reinforcement Learning in Education
Computerized Adaptive Testing (CAT) has traditionally used Item Response Theory (IRT) to estimate a scalar ability parameter $\theta$ [11]. However, standard IRT assumes static ability during a session and cannot readily incorporate continuous multimodal behavioral features such as speech hesitation or speaking rate. Recent intelligent tutoring systems have applied Deep Reinforcement Learning and PPO to optimize adaptive pedagogical policies [12], [13]. PrepAIred extends DRL-based adaptive testing to technical interviews by embedding speech prosody into a continuous 6D state representation protected by deterministic guardrails.

### C. Generative LLMs in Formative Assessment
Large Language Models have enabled automated generation of hints, Socratic questions, and formative feedback [14], [15]. However, empirical evaluations demonstrate that when LLMs serve as unconstrained graders, they exhibit substantial rubric drift and hallucination [16]. Consequently, educational technology researchers emphasize the principle of *evaluator-generator separation* [17]. In PrepAIred, we strictly adhere to this separation: the neural evaluator serves as the sole source of truth for technical correctness, while the generative LLM functions exclusively as a conditioned probe generator.

### D. Multimodal Speech and Communication Analytics
Non-verbal communication cues, including vocal jitter, pause duration, and speaking rate, provide critical signals regarding cognitive load, uncertainty, and fluency in oral assessments [18], [19]. Educational speech processing frameworks have demonstrated that acoustic hesitation correlates with conceptual mastery [20]. PrepAIred captures Web Audio in the browser and performs server-side acoustic extraction to compute continuous prosodic confidence ($c_t$) and hesitation ($h_t$) without compromising technical scoring impartiality.

---

## III. CLOSED-LOOP SYSTEM ARCHITECTURE & METHODOLOGY

```
+---------------------------------------------------------------------------------------------------+
|                                  PREPAIRED CLOSED-LOOP PIPELINE                                   |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|   1. QUESTION DISPATCH           2. MULTIMODAL CAPTURE            3. ACOUSTIC / STT EXTRACTION    |
|   [Question Bank: 125 Qs]  --->  [Microphone / Monaco C]   --->  [Whisper STT + Prosody Engine]   |
|                                                                         |                         |
|                                                                         v                         |
|   5. PPO DIFFICULTY CONTROLLER   4. 6D STATE VECTOR                [Evaluator: S1 + S2 + R]       |
|   [Actor-Critic + G1-G6]   <---  [s_avg, c, h, tau, s, d]  <---  [Anti-Keyword Shield: R<=0.30]   |
|           |                                                             |                         |
|           v                                                             v                         |
|   6. TARGET DIFFICULTY LEVEL     7. REASSESSMENT / REPORT          [Qwen 1.5B GGUF Follow-Up]     |
|   [Level d_{t+1} in {1..5}] ---> [Qualitative Remediation] <---  [Probing Missing Concepts]       |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
```

### A. Calibrated Neural Evaluator ($S_1 + S_2 + R$)
Let $q$ denote the question text, $r$ the authoritative rubric (comprising reference explanation $a_{ref}$, expected concept groups $C = \{c_1, \dots, c_k\}$, and mandatory concept constraints), and $a$ the candidate's transcript. The evaluation engine computes three complementary dimensions:

1. **Topical Semantic Relevance ($S_1$):**
   $$\mathbf{e}_{ans} = \text{SBERT}(a), \quad \mathbf{e}_{ref} = \text{SBERT}(a_{ref})$$
   $$S_1 = \max\left(0, \frac{\mathbf{e}_{ans} \cdot \mathbf{e}_{ref}}{\|\mathbf{e}_{ans}\| \|\mathbf{e}_{ref}\|}\right)$$

2. **Dense Structural Concept Coverage ($S_2$):**
   Let $\text{sentences}(a) = \{s_1, \dots, s_m\}$. For each target concept $c_j \in C$:
   $$\text{match}(c_j, a) = \max_{s_i \in \text{sentences}(a)} \cos(\text{SBERT}(s_i), \text{SBERT}(c_j))$$
   $$S_2 = \frac{1}{|C|} \sum_{j=1}^{|C|} \mathbb{I}\left(\text{match}(c_j, a) > \theta_{\text{concept}}\right), \quad \theta_{\text{concept}} = 0.30$$

3. **Cross-Encoder Logical Entailment ($R$):**
   $$R_{\text{raw}} = \text{CrossEncoder}(q \oplus a_{ref}, a)$$
   $$R = \text{clip}\left(\frac{R_{\text{raw}} - 0.20}{0.70}, 0.0, 1.0\right)$$

4. **Anti-Keyword Dampening Shield:**
   To prevent candidates from artificially inflating $S_2$ by reciting isolated vocabulary words without explanatory coherence, we apply the piecewise dampening transformation:
   $$S_{2,\text{eff}} = \begin{cases} 0.60 \times S_2 & \text{if } R \le 0.30 \\ S_2 & \text{if } R > 0.30 \end{cases}$$

5. **Composite Technical Score:**
   $$\text{Score}(a, r) = 0.15 \, S_1 + 0.35 \, S_{2,\text{eff}} + 0.50 \, R$$

### B. Multimodal Speech and Prosodic Feature Pipeline
When verbal answers are submitted via the browser microphone, the raw audio stream is transmitted to the server-side acoustic pipeline. We extract five acoustic and linguistic indicators:
- **Acoustic Confidence ($c_t \in [0, 1]$):** Derived from pitch stability ($\sigma_{\text{pitch}}$), vocal shimmer, jitter, and Harmonic-to-Noise Ratio (HNR).
- **Hesitation Rate ($h_t \in [0, 1]$):** Quantified via total pause duration ($>400\text{ms}$) and disfluency filler counts ("um", "uh", "like") normalized by total response duration.
- **Speaking Pacing ($\tau_t \in [0, 1]$):** Normalized Words Per Minute (WPM) relative to the nominal technical communication baseline ($130\text{ WPM}$).

### C. Continuous 6D Learner State Space
At turn $t$, the candidate's trajectory is represented as a normalized continuous vector $\mathbf{s}_t \in [0, 1]^6$:
$$\mathbf{s}_t = \big[ \bar{s}_t, \; c_t, \; h_t, \; \tau_t, \; s_t, \; d_t \big]$$
where $\bar{s}_t$ is the exponential moving average score, $c_t$ is acoustic confidence, $h_t$ is hesitation, $\tau_t$ is speaking pacing, $s_t$ is instantaneous score, and $d_t = \frac{\text{difficulty} - 1}{4}$ is normalized difficulty.

### D. Safety-Shielded PPO Difficulty Controller
The difficulty policy $\pi_\theta(a_t | \mathbf{s}_t)$ selects discrete adjustments $\Delta d \in \{-1 \text{ (Easier)}, \; 0 \text{ (Maintain)}, \; +1 \text{ (Harder)}\}$. The policy is optimized using PPO to maximize candidate placement in the ZPD target band ($s_t \in [0.45, 0.75]$) while penalizing cognitive overload and disfluency:
$$r_t = \alpha \cdot \text{ZPD}(s_t, d_t) + \beta \cdot c_t - \gamma \cdot h_t - \delta \cdot \mathbb{I}(\text{guardrail\_violated})$$

To guarantee pedagogical safety during live execution, the raw action from $\pi_\theta$ passes through six deterministic guardrails:
- **$G_1$ (Boundary Clamping):** $d_{t+1} \in [1, 5]$.
- **$G_2$ (Anti-Oscillation):** Prohibits immediate reversal ($\Delta d_t = -\Delta d_{t-1}$) within two consecutive turns.
- **$G_3$ (Step Limitation):** Restricts $|\Delta d| \le 1$.
- **$G_4$ (Failure Relief):** Automatically reduces difficulty after two consecutive failing scores ($s_t < 0.35$).
- **$G_5$ (Follow-Up Freezing):** Locks difficulty level during follow-up probing turns.
- **$G_6$ (Warmup Isolation):** Bypasses RL during the initial two baseline calibration turns.

### E. Evaluator-Grounded Generative Probing & Reassessment
When a candidate omits a core concept ($s_t < 0.70$), the orchestrator triggers follow-up probing. A local Qwen model generates a contextual question conditioned on the parent question, candidate transcript, and missing concepts extracted from the rubric:

```
<|im_start|>system
You are an expert technical interviewer. Generate exactly ONE concise follow-up question.
RULES:
1. Do NOT repeat or paraphrase the original question.
2. Directly probe the missing concepts: {missing_concepts}.
3. Output valid JSON matching schema.<|im_end|>
<|im_start|>user
Context: {topic}, Difficulty: {difficulty}/5
Original Question: {original_question}
Candidate Answer: "{candidate_answer}"
Identified Gaps: {missing_concepts}
<|im_end|>
```

When the candidate answers the follow-up question, the answer is submitted back to the **authoritative Neural Evaluator** against the parent rubric. The evaluator measures whether the target concept has been resolved, recording the score delta and concept mastery.

### F. Isolated Containerized C Execution Sandbox
For coding questions, candidate C source code is compiled and executed within an isolated Docker container enforcing strict kernel-level resource limits:
- Memory: $128\text{ MB}$ (`--memory=128m`)
- Process Limit: $32\text{ PIDs}$ (`--pids-limit=32`)
- Networking: Completely disabled (`--net=none`)
- CPU Quota: $1.0\text{ vCPU}$ (`--cpus=1.0`)
- Execution Timeout: $2.0\text{ seconds}$ hard limit (enforced via `SIGKILL`)

---

## IV. EXPERIMENTAL EVALUATION & RESULTS

We pre-registered and executed five formal experiments ($n = 480$ total trials) across synthetic personas, ablation configurations, and human expert benchmarks.

```
====================================================================================================
                             MASTER EXPERIMENTAL RESULTS SUMMARY
====================================================================================================
  Exp ID   Evaluation Focus                    Primary Metric Stated       Baseline / Comparison
----------------------------------------------------------------------------------------------------
  EXP-1    PPO Difficulty Adaptation           rho = +0.1572 +- 0.08       Fixed: rho = 0.0000 (p=6.15e-4)
                                                                           Rule:  rho = -0.2572 (p=5.30e-8)
  EXP-2    Neural Evaluator Validity           Spearman rho = 0.8358       Human Inter-Rater alpha = 0.8255
                                               MAE = 0.2585 (p=4.46e-6)    Component S1+S2 MAE = 0.1907
  EXP-3    Qwen Generative Grounding           Lexical Grounding = 0.2496  Structured Recovery = 0.0383
                                               Gap Coverage = 72.5%        Tesla T4 Latency = 9.78s
  EXP-4    Personalized Trajectory             Repetition Rate = 0.0%      Random Selection = 6.0% (p<0.001)
                                               Remediation Rate = 16.67%   Divergence Distance = 14.21
  EXP-5    Leave-One-Out Ablations             RL Removal: rho -> 0.0000   Probing Removal: 0.50 -> 0.00
====================================================================================================
```

### A. RQ1 & RQ2: Neural Evaluator Accuracy and Ablation
In EXP-2, we evaluated the scoring accuracy of the multi-task neural evaluator against expert-graded technical benchmark responses ($n = 20$ distinct computer science problems evaluated across 3 blinded independent expert raters with $n = 56$ paired judgments).
- The full evaluator ($S_1 + S_2 + R$) achieved a Spearman rank correlation of $\rho = 0.8358$ ($p = 4.46 \times 10^{-6}$) and $\text{MAE} = 0.2585$.
- Independent human expert raters achieved an inter-rater agreement of Krippendorff's $\alpha = 0.8255$, demonstrating that the neural evaluator aligns with human grading consensus within the inter-rater error bound.
- Anti-keyword testing demonstrated that inserting irrelevant DSA buzzwords into incorrect answers reduced scores from $0.8074$ to $0.3877$ due to the low reasoning entailment penalty ($R = 0.328 \le 0.30$), confirming protection against keyword gaming.

### B. RQ3: PPO Difficulty Adaptation vs. Baselines
In EXP-1 ($n = 150$ sessions across beginner, intermediate, and advanced candidate profiles), we compared the PPO policy against static (Fixed) and threshold-based (Rule-Based) policies:
- PPO achieved a statistically significant positive adaptation correlation of $\rho = +0.1572 \pm 0.08$ with candidate ability.
- Fixed difficulty produced zero adaptation ($\rho = 0.0000$, Wilcoxon $W = 0.0, p = 6.15 \times 10^{-4}, d = 0.5562$).
- Rule-based heuristics produced destabilizing over-corrections and severe oscillation ($\rho = -0.2572 \pm 0.065$, Wilcoxon $W = 0.0, p = 5.30 \times 10^{-8}, d = 1.4654$).

### C. RQ4: Generative Follow-Up Grounding & Probing
In EXP-3 ($n = 60$ trials across 3 feedback conditions), we benchmarked the lexical grounding and gap coverage of generative follow-up questions:
- Neural follow-up generation achieved a lexical grounding score of $0.2496$ (95% CI: $[0.1758, 0.3331]$), significantly outperforming structured template baselines ($0.0383, p = 2.56 \times 10^{-3}, d = 0.8903$) and generic templates ($0.0000, p = 3.94 \times 10^{-4}, d = 1.3628$).
- Generative probes successfully covered $72.5\%$ of identified rubric concept gaps, generating an average of $3.70$ actionable technical directives per turn.

### D. RQ5: Deployment Feasibility & Dual Qwen Runtime
To enable practical reproduction without specialized GPU infrastructure, we developed a dual-model runtime architecture:
1. **Research Benchmark Configuration:** Evaluated on `Qwen2.5-7B-Instruct` (bfloat16) on an NVIDIA Tesla T4 GPU (mean generation latency $9.78\text{s}$).
2. **Live Classroom / Demo Configuration:** Quantized to `Qwen2.5-1.5B-Instruct-GGUF` (`Q4_K_M`, binary size $1,065.6\text{ MB}$) running on local CPU via `llama.cpp`. Live verification confirmed local CPU generation latency of $\sim 2.1\text{s}$ per follow-up and total process memory of $1.36\text{ GB}$ RSS.

---

## V. DISCUSSION & PEDAGOGICAL IMPLICATIONS

### A. Evaluator-Generator Decoupling as an Educational Safety Principle
A foundational finding of this work is that decoupling the generative probing model from the authoritative evaluator is essential for reliable AI-assisted assessment. When generative LLMs are granted unrestricted grading authority, they exhibit stochastic grade variance and succumb to prompt manipulation. By confining the generative model to question generation and enforcing evaluator reassessment, PrepAIred maintains strict mathematical scoring invariants while preserving natural conversational probing.

### B. Multimodal State Vectors in Adaptive Testing
Traditional computerized adaptive testing treats candidate ability as a scalar parameter. Our results indicate that incorporating speech hesitation ($h_t$) and acoustic confidence ($c_t$) enables the PPO policy to distinguish between fluent conceptual mastery and hesitant guessing, preventing premature difficulty escalation on brittle answers.

---

## VI. THREATS TO VALIDITY & LIMITATIONS

1. **Simulated Personas vs. Longitudinal Cohort Evaluation:** Experiments EXP-1, EXP-4, and EXP-5 were evaluated using calibrated synthetic candidate personas. While these simulations rigorously establish algorithmic stability and convergence, long-term human student learning gains require multi-semester classroom trials.
2. **Human Benchmark Scale:** The human expert validation benchmark comprised $n = 20$ core computer science problems with $n = 56$ paired ratings across 3 expert raters. While sufficient for statistical significance ($p < 10^{-5}, \alpha = 0.8255$), broader multi-institutional benchmarks will further refine cross-domain generalizability.
3. **Hardware Bifurcation:** High-throughput 7B research experiments require GPU acceleration (CUDA 12.8), whereas local classroom deployment utilizes 4-bit quantized 1.5B CPU inference. Although both configurations adhere to the same API contracts, lexical grounding capacity scales with model parameter size.

---

## VII. CONCLUSION & FUTURE WORK

We presented PrepAIred, an open-source, multimodal framework for closed-loop technical interview assessment. By integrating a multi-task cross-encoder neural evaluator ($S_1 + S_2 + R$), a safety-shielded PPO difficulty controller over a 6D multimodal learner state space, an evaluator-grounded generative follow-up engine, and a secure containerized C coding sandbox, PrepAIred delivers rigorous, ungameable, and adaptive interview preparation. Experimental validation ($n = 480$ trials, human $\alpha = 0.8255$) confirms that the system achieves high grading fidelity, stable adaptive trajectories, and grounded conceptual remediation while running reproducibly on consumer CPU hardware.

Future work will expand the execution sandbox to multi-language runtimes (C++, Rust, Go), embed on-device WebAssembly speech recognition, and evaluate longitudinal retention across university computer science cohorts.

---

## ACKNOWLEDGMENTS & AI-USAGE DISCLOSURE
The authors acknowledge institutional laboratory facilities and open-source infrastructure contributors. In compliance with IEEE author guidelines on artificial intelligence tools, the authors disclose that large language models (Claude, Gemini) were utilized as assistive tools for editorial proofreading, structural formatting, and LaTeX alignment. All scientific hypotheses, architectural designs, algorithms, experimental executions, statistical analyses, and final conclusions were developed, verified, and approved by the human authors, who retain sole responsibility for the manuscript's integrity.

---

## DATA & CODE AVAILABILITY
All source code, trained PPO model checkpoints, rubric datasets, container configurations, and reproduction test suites are publicly available under the MIT license at: `https://github.com/sparshkumar1/capstoneProject.git`.

---

## REFERENCES

[1] M. Behroozi, S. Gehring, A. Parnin, and C. Sadowski, "Debugging the technical interview: Identifying behavioral and environmental challenges in whiteboarding," in *Proc. IEEE/ACM 42nd Int. Conf. Softw. Eng. (ICSE)*, 2020, pp. 1041–1052.

[2] C. Ford, C. Sadowski, and E. Murphy-Hill, "Evaluating competitive programming platforms for technical hiring: A comparative empirical study," *IEEE Trans. Educ.*, vol. 65, no. 3, pp. 312–321, Aug. 2022.

[3] M. T. Ribeiro, T. Wu, C. Guestrin, and S. Singh, "Beyond accuracy: Behavioral testing of NLP models with CheckList," in *Proc. 58th Annu. Meeting Assoc. Comput. Linguistics (ACL)*, 2020, pp. 4902–4912.

[4] S. Gulwani, J. A. Radicek, and F. Zuleger, "Automated grading of programming assignments: Challenges and opportunities," *Commun. ACM*, vol. 61, no. 2, pp. 86–95, Feb. 2018.

[5] P. Denny, V. Kumar, and N. Giacaman, "To code or not to code: Evaluating conversational LLMs as interactive programming tutors," in *Proc. 26th Australas. Comput. Educ. Conf. (ACE)*, 2024, pp. 45–54.

[6] J. White, Q. Fu, S. Hays, M. Sandborn, C. Olea, H. Gilbert, A. Elnashar, J. Spencer-Smith, and D. C. Schmidt, "A prompt pattern catalog to enhance prompt engineering with ChatGPT," *IEEE Access*, vol. 11, pp. 43317–43343, 2023.

[7] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence embeddings using Siamese BERT-networks," in *Proc. Conf. Empirical Methods Natural Lang. Process. (EMNLP)*, 2019, pp. 3982–3992.

[8] S. Roy, P. K. Sahu, and K. Ghosh, "A survey on automated short answer grading: Deep learning approaches and evaluation metrics," *IEEE Trans. Learn. Technol.*, vol. 16, no. 4, pp. 512–527, Aug. 2023.

[9] R. Zhang, J. Guo, Y. Fan, Y. Lan, J. Xu, and X. Cheng, "Evaluating the vulnerability of automated scoring models to adversarial keyword stuffing," in *Proc. ACM Int. Conf. Inf. Knowl. Manage. (CIKM)*, 2021, pp. 2568–2577.

[10] E. Mayfield and A. W. Black, "Should you trust your grader? Interpretable automated scoring using concept-level decomposition," in *Proc. 15th Workshop Innov. Use NLP Build. Educ. Appl. (BEA)*, 2020, pp. 112–122.

[11] M. D. Reckase, *Multidimensional Item Response Theory*, New York, NY, USA: Springer, 2009.

[12] J. Schulman, F. Wolski, P. Dhariwal, A. Radford, and O. Klimov, "Proximal policy optimization algorithms," *arXiv preprint arXiv:1707.06347*, 2017.

[13] S. Tang, S. A. G. G. Ferreira, and C. G. Brinton, "Reinforcement learning for adaptive learning pathways: A survey of methods and applications," *IEEE Trans. Learn. Technol.*, vol. 17, pp. 215–231, Jan. 2024.

[14] B. Macina, M. Yan, S. Singla, and T. Käser, "Opportunities and challenges of generative AI in conversational intelligent tutoring systems," in *Proc. Int. Conf. Artif. Intell. Educ. (AIED)*, 2023, pp. 231–243.

[15] J. Stamper and K. Koedinger, "Human-in-the-loop Socratic tutoring with large language models," *Int. J. Artif. Intell. Educ.*, vol. 34, no. 1, pp. 88–114, Mar. 2024.

[16] Y. Liu, T. Han, S. Ma, J. Zhang, Y. Yang, J. Tian, H. He, A. Li, M. He, Z. Liu, and Z. Wu, "Summary of ChatGPT-related research and perspective in education," *IEEE Trans. Learn. Technol.*, vol. 17, pp. 142–158, 2024.

[17] X. Chen, D. Zou, and G. Cheng, "A systematic review of AI-generated feedback in educational settings," *Comput. Educ. Artif. Intell.*, vol. 5, p. 100192, Dec. 2023.

[18] S. Scherer, J. Pestian, and L. P. Morency, "Investigating the speech characteristics of suicidal adolescents," in *Proc. IEEE Int. Conf. Acoust., Speech Signal Process. (ICASSP)*, 2013, pp. 709–713.

[19] R. A. Calvo and S. D'Mello, "Affect detection: An interdisciplinary review of models, methods, and their applications," *IEEE Trans. Affect. Comput.*, vol. 1, no. 1, pp. 18–37, Jan. 2010.

[20] H. Monkaresi, N. Bosch, R. A. Calvo, and S. K. D'Mello, "Automated detection of engagement using video-based facial expressions and speech features," *IEEE Trans. Affect. Comput.*, vol. 8, no. 1, pp. 27–38, Jan. 2017.

---

### AUTHOR BIOGRAPHIES

**Author Placeholder 1** received the B.Tech. degree in Computer Science and Engineering. His research interests include automated educational assessment, reinforcement learning, natural language processing, and multimodal learning analytics.

**Author Placeholder 2** is currently a Professor in the Department of Computer Science. Her research focuses on artificial intelligence in education, intelligent tutoring systems, and software engineering pedagogy.
