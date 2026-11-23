> **V10 — generic IEEE-style review manuscript.** No conference has been selected for this version; it does
> not claim compliance with any particular venue's template, page limit, indexing, or disclosure policy.
> Venue-specific formatting and disclosure checks are performed once a venue is chosen.

---

# PrepAIred: A Reinforcement-Learning-Adapted, Evidence-Gated Technical Interview Preparation System

Dr. Uma D · Sparsh Kumar · Naveen S Khadd · Athreya Shashidhara · Manasa S A
Dept. of Computer Science and Engineering, PES University, Bengaluru, India

## Abstract

Technical interview practice platforms require evaluating technical reasoning and verbal communication under realistic conditions. However, automated systems typically collapse delivery into technical scoring or rely on unconstrained Large Language Models (LLMs) vulnerable to prompt drift, hallucinated criteria, and verbosity bias. We present PrepAIred, an interview-preparation architecture that decouples scoring from dialogue generation. PrepAIred combines a multi-tier technical evaluator (semantic similarity, rubric concept coverage, fine-tuned CrossEncoder reasoning), an independent acoustic confidence model, a continuous-state Proximal Policy Optimization (PPO) difficulty controller, and deterministic evidence gating that restricts the LLM to grounded follow-ups. We evaluate technical scoring against an exploratory human-reference benchmark of $n = 64$ constructed answers across eight computer science questions, reporting exact deployed scoring formulas and code-verified implementations. The CrossEncoder reasoning signal correlates with human judgment (Spearman $\rho = 0.4832$, 95% CI $[0.250, 0.676]$), and the deployed composite achieves $\rho = 0.3812$. However, a length-confound analysis reveals the CrossEncoder is strongly associated with answer length ($\rho = 0.6594$, 95% CI $[0.457, 0.831]$); controlling for length, its partial correlation drops to $0.2434$ (95% CI $[-0.008, 0.507]$). Because this confidence interval spans zero, an independent reasoning contribution beyond answer length is not statistically established on this benchmark. Furthermore, we make no claims of candidate learning gains, and take no position on whether PPO outperforms simpler guardrailed policies.

*Index Terms* — Adaptive Systems, Natural Language Processing, Reinforcement Learning, Large Language
Models, Technical Interview Evaluation.

## I. Introduction

Technical interviews in computer science, data structures, algorithms, and system design require
candidates to simultaneously demonstrate domain knowledge, analytical problem-solving, structured
logic, and fluent communication. Mock interview practice is a standard part of interview preparation,
but scalable practice platforms face a fundamental trade-off. Human mock interviews provide
high-quality, contextual feedback but are costly, non-scalable, and subject to evaluator variability.
Automated preparation systems traditionally rely on static question repositories with pre-scripted
test cases, failing to adapt dynamically when a candidate shows partial conceptual understanding,
misunderstands a core requirement, or demonstrates strong technical correctness alongside hesitant
verbal delivery.

The recent emergence of general-purpose Large Language Models (LLMs) has enabled conversational
interview agents capable of generating dynamic questions and natural-language feedback. Despite their
fluency, unconstrained LLM interviewers introduce operational risks in educational assessment:
grading inconsistency, prompt drift, hallucinated rubric criteria, and a tendency to reward polished
phrasing over technical correctness — unconstrained prompts can let a candidate achieve a favorable
evaluation through keyword repetition even when the underlying reasoning is flawed. Standalone LLMs
also lack principled difficulty adaptation, relying on subjective prompt interpretation rather than a
structured, evidence-driven policy.

PrepAIred addresses these problems with a decoupled architecture that separates rigorous quantitative
technical and speech assessment from qualitative natural-language generation, and strips the LLM of
scoring authority entirely. This paper documents the system as it is actually implemented, and reports
— favorably and unfavorably — what the project's evidence base does and does not support.

**Contributions**, scoped to what the evidence in this paper actually establishes:

1. A fully specified, code-verified system architecture for live, multi-turn, spoken technical-interview
   practice that structurally separates deterministic, multi-signal scoring from LLM-generated dialogue:
   the LLM is confined to phrasing grounded follow-ups and feedback under evidence-based triggers it does
   not control, and difficulty is adapted from a continuous six-dimensional state that treats
   speech-derived confidence as a first-class, non-penalizing signal rather than folding it into the
   technical score. A focused literature comparison (§II) finds this specific combination — applied to a
   live spoken interaction with a human candidate, with an RL-based continuous-state difficulty controller
   — was not present in the closest comparable systems identified; this is reported as an architectural
   and implementation-verification contribution, not a claim of demonstrated superiority over an
   LLM-judge baseline, which this paper does not test.
2. A precisely specified, code-verified multi-tier technical evaluator combining semantic similarity,
   rubric-based concept coverage, and a fine-tuned CrossEncoder reasoning signal, with every published
   weight and threshold matching the deployed implementation exactly (§IV).
3. A precisely specified, code-verified independent acoustic/temporal communication-confidence model,
   decoupled from technical scoring with one disclosed, narrow exception (§V).
4. A deterministic, evidence-gated follow-up and feedback mechanism, described here exactly as
   implemented (§VII).
5. A rigorous, honest characterization of the CrossEncoder scoring signal's actual evidentiary status,
   including a length-confound analysis showing its correlation with human judgment is substantially
   explained by answer length, with a length-independent contribution not established on the current
   benchmark (§X.B) — reported as a disclosed limitation, not implied validation.
6. A per-signal association analysis of the three evaluator signals' own stored scores against the
   same human-reference benchmark (not a component ablation — no signal was removed from the deployed
   composite and recomputed), reporting each signal's own correlation with human judgment separately:
   the CrossEncoder signal's is confidently non-zero, the semantic-similarity signal's is not, and the
   concept-coverage signal's is boundary-ambiguous across two independently frozen bootstrap analyses
   (§X.B, Table V) — evidence not previously reported for this system, computed from already-frozen
   data rather than a new experiment; and a follow-up paired, question-aware bootstrap contrast between
   the signals (§X.B, Table VI) showing none of the four tested pairwise gaps, including the deployed
   composite versus the CrossEncoder alone, is statistically distinguished from zero at this sample
   size — also computed from the same already-frozen data, exploratory and not preregistered.
7. Software-verification evidence (automated test suites, including a newly fixed
   evaluator-reliability defect) establishing implementation correctness — explicitly not a claim of
   pedagogical effectiveness, candidate learning gain, or evaluator accuracy (§X.A).

We do **not** claim that PPO measurably improves difficulty tracking beyond a simple guardrailed
constant policy: no evidence currently eligible for citation in this paper establishes that
contribution either way (§VI).

## II. Related Work

Automated short-answer scoring and technical assessment have evolved from early surface-level
keyword matching to modern transformer-based semantic representations. Sentence-BERT demonstrated
that Siamese transformer networks can produce semantically meaningful sentence embeddings for fast
similarity comparisons [1]. However, semantic similarity alone remains vulnerable to false positives
when candidate responses contain relevant terminology without correct logical structure. CrossEncoder
models trained on passage-ranking datasets such as MS MARCO provide finer-grained pairwise entailment
verification [2]. Prior automated assessment research has focused primarily on static answer grading;
PrepAIred integrates a CrossEncoder-based reasoning score into a broader adaptive interview system
that connects quantitative scoring directly to downstream question selection and grounded follow-up
generation.

Speech analysis and communication modeling in professional interviews have established that
non-verbal prosodic features correlate with perceived confidence and interview readiness. Classical
acoustic toolkits such as Praat enable extraction of physical voice parameters including jitter,
shimmer, and Harmonics-to-Noise Ratio (HNR) [3]. Subsequent interview-prediction systems combined
language representations with acoustic parameters to predict human ratings [4], and automated
interview-video frameworks applied multimodal regression to evaluate candidate delivery [5]. Existing
speech-enabled interview tools frequently fold acoustic metrics into a single overall performance
score, which can penalize technically proficient but vocally hesitant candidates. PrepAIred instead
maintains speech confidence as an independent, non-penalizing state dimension that informs difficulty
selection without degrading technical correctness scores.

Reinforcement Learning (RL) and Intelligent Tutoring Systems (ITS) have long addressed adaptive
pedagogical sequencing. Early cognitive tutors modeled student skill acquisition using Bayesian
Knowledge Tracing [6] and rule-based cognitive architectures [7]. Curriculum reinforcement learning
formulates educational path optimization as a Markov Decision Process, using policy-gradient
algorithms such as Proximal Policy Optimization (PPO) to balance challenge and capability [8], and
automated-curriculum methods generalize this idea to broader RL settings [9], [10]. Adaptive testing
frameworks grounded in item response theory similarly aim to optimize test length and difficulty
[11]. Where traditional RL tutoring adjusts content across structured, static lessons, PrepAIred
applies PPO difficulty adaptation within a multi-turn, speech-interactive technical interview
environment governed by a continuous six-dimensional observation state — with the caveat, disclosed
in §VI and §XII of this paper, that no evidence eligible for this paper establishes that this
adaptation improves on a simpler guardrailed policy.

LLMs in educational assessment offer flexible narrative feedback but are documented to suffer from
unconstrained generation and hallucination risk [12]. In technical-interview simulation specifically,
unconstrained LLM interviewers can drift from rubric definitions or fail to enforce consistent
difficulty escalation. PrepAIred addresses this by stripping the LLM of scoring authority entirely,
using a locally served Qwen2.5 model (§III) exclusively as a grounded natural-language generator
operating strictly under deterministic, evidence-driven state-machine triggers, with model outputs
constrained by the Qwen technical report's own documented instruction-following behavior [13].

Multimodal interview-simulation frameworks have recently been extended toward broader career-guidance
problems: Ascend AI provides a multimodal architecture unifying psychometric candidate profiling,
predictive career-path modeling, personalized learning-roadmap generation, and interview simulation
[14]. PrepAIred differs in scope: rather than end-to-end career guidance, it focuses specifically on
single-session adaptive technical-interview assessment and difficulty optimization, combining
question-specific hybrid answer evaluation, an independent acoustic communication-confidence model,
PPO difficulty adaptation over a continuous six-dimensional state, and evidence-gated deterministic
follow-up selection.

Closer to PrepAIred's own setting, Gomez et al. report a formative qualitative study (n = 20) of an
AI-driven mock technical-interview tool with whiteboarding tasks and real-time feedback, finding
participants described the experience as realistic and reported increased confidence, alongside
challenges with conversational flow and timing [15]. That system does not report a reinforcement-learning
difficulty controller or a deterministic scoring component decoupled from the dialogue model; confidence
there is a self-reported qualitative outcome rather than a modeled, acoustic system state feeding a
difficulty policy, which is the role it plays in PrepAIred (§V, §VI). A more direct validation of this
paper's evidence-gating principle, in a different setting, comes from work compiling a rubric into a
locked, executable specification and enforcing evidence-anchored, structured LLM-judge scoring for
essay- and summarization-style text evaluation, improving alignment with human scores and stability under
rubric-phrasing variation [16]. That result is independent evidence that evidence-anchored scoring can
measurably improve over unconstrained LLM judgment in the domain it was tested in; PrepAIred applies a
structurally similar separation of scoring authority from the dialogue model to a live, multi-turn,
spoken interaction with a human candidate rather than static text evaluation, and reports its own
evaluator-correlation evidence (§X.B) rather than importing that result. A third related direction lets
one LLM play the interviewer role to dynamically evaluate another LLM across multi-turn
question/feedback/follow-up exchanges, with no human candidate, no reinforcement learning, and no
deterministic non-LLM scoring component — the interviewer LLM is simultaneously the questioner and the
judge [17]. PrepAIred targets human candidates and removes scoring authority from the LLM entirely rather
than assigning more of it. A focused search for a system combining all of PrepAIred's elements — a
code-verified, deterministic multi-signal scorer decoupled from an LLM dialogue role; a live, spoken,
multi-turn interaction with a human candidate; an independent acoustic confidence signal; and an
RL-based continuous-state difficulty controller — did not find one; this is reported as the outcome of a
focused comparison against the closest identified systems, not as a claim that no such system exists.

**Table I** synthesizes this comparison.

*TABLE I — Comparative Analysis of Related Literature and PrepAIred*

| Research Theme | Representative Works | Typical Scope / Limitations | PrepAIred Approach |
|---|---|---|---|
| Automated Answer Assessment | Reimers & Gurevych [1], Bajaj et al. [2] | Static scoring, not embedded in an interactive questioning loop | Combines SBERT, rubric coverage, and CrossEncoder into an adaptive loop |
| Speech & Communication | Boersma [3], Naim et al. [4], Chen et al. [5] | Typically combine speech metrics into a single overall performance score | Separates speech confidence as an independent RL state dimension |
| Adaptive Tutoring & RL | Anderson et al. [7], Schulman et al. [8], Graves et al. [9] | Curriculum/tutoring RL commonly applied to static or structured tasks, not live multi-turn interviews | Applies PPO over a 6D state targeting technical interviews (tracking benefit not established here, §VI) |
| LLMs in Assessment | Ji et al. [12], Qwen Team [13] | Documented hallucination/inconsistency risk under unconstrained generation | Restricts the LLM to grounded follow-ups, gated deterministically |
| Multimodal Career Frameworks | Ascend AI [14] | Addresses end-to-end career guidance and learning-roadmap generation, not interview-answer evaluation | Focuses specifically on technical answer evaluation and 6D PPO adaptation |
| AI Mock Interview Tools | Gomez et al. [15] | n = 20 qualitative study; confidence is self-reported, not a modeled system state; no RL, no decoupled deterministic scorer | Models confidence as a computed acoustic/temporal signal feeding a difficulty controller |
| Evidence-Anchored LLM Judging | Hong et al. (RULERS) [16] | Validates rubric-locked, evidence-anchored scoring for static essay/summarization text evaluation; no interactive dialogue, no RL | Applies a structurally similar evidence-gating principle to a live, spoken, multi-turn human interview |
| LLM-as-Interviewer Evaluation | Kim et al. [17] | LLM interviews another LLM; no human candidate; the interviewer LLM is also the judge | Targets human candidates; removes scoring authority from the LLM entirely |

## III. System Architecture

PrepAIred is built on a decoupled microservice architecture: a React 18 single-page application, a
FastAPI/WebSocket session gateway, an asynchronous orchestration engine, a PyTorch technical
evaluation service, an audio feature-processing module, a Stable-Baselines3 PPO difficulty
controller, and a **local GGUF-quantized LLM runtime (llama.cpp, Qwen2.5-1.5B-Instruct, Q4_K_M)**. The
LLM-serving module's startup routine (`services/qwen/app.py`) loads only Qwen2.5-1.5B-Instruct, first
via GGUF/llama.cpp and, only if that fails and a research-GPU environment flag is explicitly set, via
a PyTorch Transformers fallback of the same 1.5B model; it does not call any remote or Ollama-hosted
service, and does not load a 7B model under any startup path in the current source — a "Qwen 7B"
attribution label exists in the module's response schema for a research configuration, but no code
path registers a 7B model, so that label is unreachable in the tested configuration. This section
describes the deployed and tested configuration: Qwen2.5-1.5B-Instruct only.

The end-to-end session lifecycle (Fig. 1) is: session-length selection (5, 15, or 30 primary
questions); a deterministic Easy-pool baseline phase for the first two questions; parallel
technical/speech evaluation per turn; a deterministic follow-up decision layer (§VII); PPO-driven
difficulty adaptation from the third question onward; and a final feedback view with all numeric
scores suppressed from the candidate.

*TABLE II — PrepAIred Architectural Component Specification*

| Component | Method / Library | Operational Role |
|---|---|---|
| Web Frontend | React 18 SPA + Web Speech API | User interaction, audio capture, score-suppressed UI |
| API Gateway | FastAPI + WebSockets | Real-time session routing and state orchestration |
| Hybrid Evaluator | SentenceTransformers + FAISS + CrossEncoder | Deterministic technical answer scoring |
| Confidence Engine | Praat-derived acoustic features + timing analysis | Speech delivery and vocal confidence modeling |
| RL Strategy | Stable-Baselines3 PPO | Continuous-state difficulty adaptation |
| LLM Engine | Qwen2.5-1.5B-Instruct via local GGUF (llama.cpp) | Grounded follow-up question and feedback generation |
| Question Bank | Structured JSON / FAISS indices | Rubrics, concept vectors, and question pools |

*Fig. 1.* End-to-end operational workflow of PrepAIred. The candidate configures session parameters, establishing a two-question Easy-pool
baseline phase. Text transcripts and speech audio undergo parallel evaluation to yield technical
correctness ($S_1$, $S_2$, $R$) and communication confidence ($C_{final}$) scores. Deterministic
evidence logic (§VII) determines whether to initiate a grounded follow-up probe (up to two bounded
attempts) or proceed directly through the 6D PPO state-adaptation loop (§VI) until the selected
primary-question count is reached. *(This diagram describes control flow, cross-checked against the
orchestrator code; it is not a data figure and is not regenerated from a results file.)*

## IV. Hybrid Technical Answer Evaluation

The technical evaluation engine computes a score $S_{final} \in [0.0, 1.0]$ by comparing candidate
transcript $T_c$ against a canonical question rubric $R_q$, containing semantic reference statements
$R_q^{semantic}$, required concepts $R_q^{concept}$, misconception vectors $M_q$, advanced-insight
vectors $B_q$, and mandatory-concept flags.

**A. Semantic similarity ($S_1$).** $T_c$ is segmented into sentences $\{s_1,\dots,s_n\}$; each
sentence and each reference statement $t_j \in R_q^{semantic}$ are embedded with `all-MiniLM-L6-v2`
(384-dimensional). $S_1$ is the mean, over reference statements, of the maximum cosine similarity to
any candidate sentence:
$$S_1 = \frac{1}{|R_q^{semantic}|}\sum_{j=1}^{|R_q^{semantic}|} \max_{1\le i\le n}\cos(e_i, v_j).$$

**B. Concept coverage ($S_2$) and dampening.** For each required concept $c_k \in R_q^{concept}$,
presence is an indicator at cosine-similarity threshold $\tau_{concept}=0.30$:
$$S_2 = \frac{1}{|R_q^{concept}|}\sum_{k=1}^{|R_q^{concept}|} \mathbb{1}\!\left(\max_{1\le i\le n}\cos(e_i,c_k) > 0.30\right).$$
To resist keyword stuffing (terms present without connecting logic), effective coverage is dampened
when reasoning score $R$ is at or below a floor of 0.30:
$$S_2^{effective} = \begin{cases} S_2, & R>0.30 \\ 0.60\cdot S_2, & R\le 0.30. \end{cases}$$

**C. CrossEncoder reasoning score ($R$).** $T_c$ and the reference answer $A_q$ are jointly
scored by `cross-encoder/ms-marco-MiniLM-L-6-v2`; the raw logit $r_{raw}$ is linearly rescaled and
clamped:
$$R = \mathrm{clamp}\!\left(\frac{r_{raw}-0.20}{0.70},\,0.0,\,1.0\right).$$

**D. Bonus, mistake penalty, and mandatory concepts.** Mistake penalty accumulates matched
misconception-vector hits (threshold 0.55, increment 0.07, capped at 0.30):
$$P_{mistake} = \min\!\left(0.30,\ \sum_{m\in M_q} 0.07\cdot\mathbb{1}(\max_i\cos(e_i,m)>0.55) + P_{reasoning}\right),$$
bonus credit accumulates matched advanced-insight hits (threshold 0.50, increment 0.03):
$$S_{bonus} = \sum_{b\in B_q} 0.03\cdot\mathbb{1}(\max_i\cos(e_i,b)>0.50).$$
The base score aggregates the three weighted signals, then bonus/penalty are applied and clamped:
$$S_{base} = 0.15\,S_1 + 0.35\,S_2^{effective} + 0.50\,R,\qquad S_{final}=\mathrm{clamp}(S_{base}+S_{bonus}-P_{mistake},\,0.0,\,1.0).$$
If mandatory concepts are required and any is missing, the score is hard-capped: $\text{Mandatory
Pass}=\text{False} \implies S_{final}=\min(0.60, S_{final})$.

*TABLE III — Hybrid Technical Evaluator Parameter Configurations* (every value below was
re-verified against `services/evaluator/app.py` and matches exactly)

| Parameter | Value | Description |
|---|---|---|
| Semantic weight ($S_1$) | 0.15 | Weight on SBERT similarity |
| Concept weight ($S_2$) | 0.35 | Weight on structural concept coverage |
| Reasoning weight ($R$) | 0.50 | Weight on CrossEncoder reasoning |
| Concept threshold ($\tau_{concept}$) | 0.30 | Cosine cutoff for concept match |
| Reasoning floor | 0.30 | CrossEncoder threshold triggering dampening |
| Dampening factor | 0.60 | Concept-coverage multiplier when $R\le0.30$ |
| Bonus increment / threshold | 0.03 / 0.50 | Credit per matched insight / match cutoff |
| Mistake increment / threshold | 0.07 / 0.55 | Penalty per matched mistake / match cutoff |
| Penalty cap | 0.30 | Maximum accumulated mistake penalty |
| Mandatory cap | 0.60 | Maximum score if mandatory concepts missed |

Every formula and constant above was independently verified against the deployed code
(`services/evaluator/app.py`) and matches exactly.

## V. Communication Confidence Model

Candidate vocal delivery is modeled independently of technical correctness, so that hesitation or
delivery nervousness does not alter technical scores while still letting the RL policy adapt to
candidate confidence state.

**A. Prosodic voice quality ($V_Q$).** From pitch jitter $j$, shimmer $s$, Harmonics-to-Noise Ratio
$h$, and pitch-variance $C_{pitch\_var}$:
$$C_{jitter}=\mathrm{clamp}(1-j/0.03,0,1),\quad C_{shimmer}=\mathrm{clamp}(1-s/0.12,0,1),\quad C_{HNR}=\mathrm{clamp}(h/28.0,0,1),$$
$$V_Q = 0.32\,C_{jitter}+0.30\,C_{shimmer}+0.28\,C_{HNR}+0.10\,C_{pitch\_var}.$$

**B. Fluency, rate, rhythm.** Fluency penalizes excess pause time ($t_{pause}/t_{speech}$, scaling
1.7); rate fluency rewards words-per-minute in $[2.1,4.3]$ (center 3.2) and decays outside that band;
rhythm penalizes more than 7 detected pauses (scale 12) — formulas verified against
`agents/audio/confidence_scorer.py`.

**C. Composite confidence ($C_{final}$).**
$$C_{final} = 0.28\,V_Q + 0.27\,L + 0.22\,F_{fluency} + 0.13\,F_{rate} + 0.10\,F_{rhythm},$$
with $L$ a linguistic-confidence signal from ASR output; if ASR confidence $A_{conf}<0.45$, the model
shifts weight toward the acoustic signal: $C_{final} = 0.75\,C_{final} + 0.25\,V_Q$. Numerical
confidence values are never shown to the candidate.

**A narrow qualification to independence.** Vocal hesitation does not alter technical scores through
the acoustic channel — $C_{final}$ has no parameter in the technical evaluator. Independence is not
unconditional, however: the technical evaluator applies a small, capped penalty (0.03) when the
candidate's **transcript text** contains a lexical hedging word (e.g. "maybe," "not sure," "umm")
**and** the answer's content is independently weak (concept coverage < 0.50 and reasoning < 0.40).
This is a text-level signal, not the acoustic model, and only ever applies alongside already-weak
content.

## VI. Reinforcement Learning for Adaptive Difficulty

PrepAIred formulates difficulty selection as a Markov Decision Process solved with PPO. The state
space, action space, and transition rules below were independently confirmed against the project's
canonical specification.

*TABLE IV — Continuous Six-Dimensional RL State Space*

| Index | Variable | Range | Definition |
|---|---|---|---|
| 0 | Performance ($P_t$) | [0,1] | Current-turn technical score $S_{final}$ |
| 1 | AvgPerformance ($\bar P_t$) | [0,1] | Rolling mean of technical scores |
| 2 | Confidence ($C_t$) | [0,1] | Composite speech confidence $C_{final}$ |
| 3 | Hesitation ($H_t$) | [0,1] | $1-F_{fluency}$ |
| 4 | TimeNorm ($T_t$) | [0,1] | Elapsed session time / budget |
| 5 | Difficulty ($D_t$) | [0,1] | Current difficulty tier / 5 |

The agent selects a discrete action $a_t\in\{0,1,2\}$ (Easier / Same / Harder), moving difficulty tier
$D_t\in\{1,\dots,5\}$ by $\mp1$ or 0, bounded to that range.

**Reward formulation.** The frozen PPO checkpoints evaluated in this paper were trained against the
project's canonical training configuration: a weighted reward combining decision alignment with a
hand-coded rule oracle (weight 0.60), an outcome-delta term (0.30), a multimodal shaping term (0.10),
and a stability penalty (−0.10). The project's own training records describe this reward as "largely
imitation of a rule oracle" rather than target-tracking against a fixed performance setpoint.

**On PPO's own effectiveness, this paper takes no position, because no evidence eligible for citation
here establishes one.** The frozen PPO checkpoints were trained against a single default simulated
candidate persona, with no persona sampler in the training scripts, and the training candidate's
noise generator is unseeded, so no claim that these checkpoints generalize across candidate personas,
or that the training seeds alone would reproduce them, is supported. Beyond that, this paper does not
assert that PPO improves difficulty tracking over simpler alternatives, because it has no evidence of
its own, and no evidence yet eligible for citation, that would support such a claim in either
direction. A separate, not-yet-public companion manuscript is the dedicated subject of PPO
effectiveness for this system; under this project's citation-timing policy, its findings are not used
here, even as uncited narrative summary.

## VII. Deterministic Follow-Up and Feedback

PrepAIred decouples the decision to initiate a follow-up probe from natural-language generation:
follow-up probing is governed by deterministic evaluator evidence, not unconstrained LLM judgment.

**Trigger logic** (derived directly from `agents/orchestrator/interview_orchestrator.py` and
`services/evaluator/app.py`):

- A follow-up is **skipped** only when the technical score is $\ge0.85$ **and** there is no missing
  concept, no detected misconception, and no other identified gap.
- Otherwise, a follow-up is **triggered** whenever there is a missing concept, a detected
  misconception, a technical score below 0.80, or any other identified gap — including a failed
  mandatory-concept check or reasoning below 0.50, evaluated in that priority order.
- At most two follow-up attempts are permitted per question.

This mechanism is coarser than the project's originally-designed five-condition trigger table (which
included a separate high-score "Depth Probe" intended to surface edge cases); the deployed code
implements only the two-condition-class rule above, and does the **opposite** of a high-score probe —
a high, clean score exits the follow-up loop rather than triggering one (see §XII). The
deterministic, non-LLM-judged gating principle itself — evidence decides whether to probe, not LLM
discretion — is what this paper reports as implemented and verified; the more elaborate
five-condition design is not, since the code does not implement it.

When a trigger fires, the locally served Qwen2.5-1.5B-Instruct model generates a targeted follow-up
prompt, grounded with the original question, the candidate's response, missing concepts, and
identified misconceptions. If a gap persists after Follow-up #1, Follow-up #2 is generated with
accumulated history; if unresolved after two attempts, the sub-loop terminates, qualitative feedback
is generated, and the primary interview workflow resumes. The candidate's own transcript is displayed for
reference, followed by six qualitative feedback sections (What You Got Right; Concepts, combining covered
and missing concepts in one view; Incorrect or Incomplete; How to Improve; Delivery & Communication; AI
Summary), plus a conditional Retry/Best-Answer Status section shown only when a prior comparable attempt
exists; all quantitative scores ($S_{final}$, $S_1$, $S_2$, $R$, $C_{final}$) are strictly suppressed from
this view, including an explicit stripping pass that removes any numeric score pattern the
narrative-generation step might otherwise leak. This section structure and the score-suppression behavior
were confirmed directly against the frontend feedback-rendering component
(`apps/web/src/FeedbackCard.jsx`), correcting an earlier, less precise description of the feedback view
(which had listed a different section breakdown not matching this component).

## VIII. Question Selection and Session Control

Candidates select a primary session length of 5, 15, or 30 questions. The question-selection engine
manages retrieval across Easy ($D\in\{1,2\}$), Medium ($D=3$), and Hard ($D\in\{4,5\}$) pools.
Questions 1 and 2 form a deterministic baseline phase, sampled independently from the Easy pool
subject to an intra-session non-repetition constraint; PPO-driven adaptive selection activates from
Question 3 onward. Follow-up questions are subordinate probes and do not increment the primary
question counter (`primary_question_index` in `agents/orchestrator/interview_orchestrator.py` counts
primary questions only, explicitly carrying the parent primary question's index for any follow-up); the
session terminates when the primary count reaches the candidate-selected session length
(`num_questions`, defaulting to 15 if unset, governs the primary-question budget the session runs
against).

## IX. Hyperparameter Selection

The evaluator's thresholds and weights (Table III) reflect the authors' design choices. No tuning
log, development-set result, or sweep record documenting a systematic empirical tuning process was
found in the project's records, so this paper does not claim that a recorded tuning study established
these specific values, even though the constants themselves are verified correct against the deployed
code (§IV).

## X. Experimental Methodology and Verification

### A. Implementation verification and source snapshot

This paper describes a specific version-controlled development snapshot, including the evaluator-reliability fix described below. The fix was covered by 16 targeted regression tests across its dedicated test files (`tests/unit/test_score_validator.py` and `tests/unit/test_evaluator_infrastructure_failure_flag.py`); all 16 passed on the documented working tree. The cases cover non-finite evaluator scores, missing (`None`) scores, non-numeric values, invalid objects, a contradictory upstream success status paired with invalid scores, and preservation of a genuine finite zero score. This is implementation-correctness evidence only: it does not establish evaluator validity, candidate learning, or improved interview outcomes. The fix was present in the reviewed working tree and had not yet been merged into the project's main integration branch at the recorded snapshot; exact revision details are retained in the project engineering record.

### B. CrossEncoder reasoning model

Throughout this subsection, the **human-reference score** for each of the 64 constructed answers is the
mean of three recorded ratings for 54 of the 64 answers, and an adjudicated score for the remaining 10
(the 8 keyword-stuffed cases and 2 partial-answer cases, where the three ratings diverged); it is not a
uniform three-rater consensus across all 64 items, and it is described here as an exploratory benchmark,
not an expert panel or independent adjudication — rater identity, qualifications, independence/blinding
beyond the rating sheet content, consent, and any institutional ethics determination are not documented in
the project's records (§XIII). The frozen source file's own internal label for the adjudicated subset is a
file identifier, not a methodological claim, and is not reused as a description here. The three raters'
inter-rater reliability on this benchmark is high (ICC(2,1) = 0.953, independently re-derived via a
second, differently structured implementation, an exact match to the frozen figure) but this figure should
not be read as evidence of fine-grained rater discrimination: a one-way ANOVA of each rater's raw score
against the benchmark's 10 author-assigned construction categories finds 98–99% of the variance
(η² = 0.9815, 0.9881, and 0.9849 for the three raters individually; 0.9891 for the gold score) in every
rater's score, and in the gold score itself, is explained by which category the item belongs to,
with the average disagreement between raters on the same item (SD ≈ 0.068) roughly 5–6× smaller than the
spread between different items' category-driven means (SD ≈ 0.361). The high reliability substantially
reflects a benchmark built from clearly separated quality categories (a correct concise answer is easy for
any rater to distinguish from a keyword-stuffed one), not necessarily fine-grained agreement on more
ambiguous within-category quality differences.

The frozen, comparable result is the R-only (CrossEncoder-only) Spearman correlation against the
project's human-reference benchmark: **ρ = 0.4832**, case-bootstrap 95% CI [0.250, 0.676], n = 64
constructed answers across 8 questions — exploratory/initial evidence, not a general validity claim.
The deployed evaluator is a **composite** of three signals (§IV), whose combined score has a
separately measured, more thoroughly characterized correlation with the human-reference benchmark:
Spearman ρ = 0.3812, case-bootstrap 95% CI [0.158, 0.577], same 64 items — numerically lower than the
CrossEncoder-alone figure. A paired bootstrap contrast of this specific gap, reported below, finds it is
not statistically distinguished from sampling noise at this sample size, so we describe the composite as
numerically, not confirmedly, lower than R alone; the composite's design — discounting $S_2$ when $R$ is
low — remains a structural robustness rationale rather than an independently validated correlation
trade-off (§XI).

**Per-signal association analysis.** The project's frozen scoring dataset for this benchmark stores each
raw evaluator signal's own score alongside the deployed composite, letting this paper report each signal's
own correlation with human judgment on the identical 64 items. This is **not a component ablation**: no
signal was removed from the deployed composite and the composite recomputed without it; these are simply
the already-stored, already-scored $S_1$, $S_2^{effective}$, and $R$ values, each independently correlated
against the human-reference gold. It is also not a new experiment: the underlying scores and their
two-level cluster-bootstrap confidence intervals were already frozen under the project's internal
preregistration gates, dated 2026-09-19. Every value below was independently reproduced twice — once by
recomputing the point-estimate Spearman correlations directly from the stored scores, and once by
re-executing the exact documented two-level bootstrap
(`numpy.random.default_rng(42)`, B = 10,000, resample 8 questions with replacement then resample each
drawn question's 8 answers with replacement, so the resampling unit is the question, respecting the
8-question clustering) — both reproductions match the frozen result exactly.

*TABLE V — Per-Signal Association with Human Judgment (two-level cluster bootstrap, B = 10,000, same
64 items / 8 questions as §X.B)*

| Signal | Spearman ρ | 95% CI |
|---|---|---|
| $S_1$ alone (SBERT semantic similarity) | 0.2070 | [−0.0231, 0.5027] |
| $S_2^{effective}$ alone (concept coverage, post-dampening) | 0.3006 | [−0.0057, 0.6523] |
| $R$ alone (CrossEncoder) | 0.4832 | [0.2453, 0.6956] |
| Deployed composite (0.15·$S_1$+0.35·$S_2^{effective}$+0.50·$R$) | 0.3812 | [0.1529, 0.6473] |

The composite row is the same 0.3812 point estimate reported earlier in this subsection, not a new or
separate measurement; its confidence interval here differs slightly from the [0.153, 0.649] two-level-
cluster interval reported below (§X.B, "Composite-score robustness") because that figure comes from a
second, independently-implemented frozen bootstrap (same nominal method and seed, a different underlying
scoring pipeline) — both are legitimate, frozen results for the identical point estimate, and neither is
more "correct" than the other.

This second frozen bootstrap also matters for $S_2^{effective}$ specifically: the second pipeline's
independently computed two-level CI for $S_2^{effective}$ is [0.0031, 0.6543] — excluding zero — while
the first, shown above, is [−0.0057, 0.6523] — including zero. The two point estimates agree (0.3006 in
both), but whether $S_2$'s CI excludes zero depends on which of two equally-frozen, equally-legitimate
bootstrap runs is consulted; the true interval is evidently very close to this boundary. We therefore do
**not** claim $S_2^{effective}$'s marginal correlation is confidently non-zero, but we also do not claim
it is confidently zero-or-indistinguishable-from-zero — the data at this sample size cannot settle it
either way, and it would be a similar overreach to pick whichever of the two frozen analyses gives the
cleaner-sounding answer.

$S_1$'s CI excludes a confidently non-zero reading under both frozen analyses ([−0.023, 0.503] and
[−0.023, 0.501]), and $R$'s CI excludes zero under both ([0.245, 0.696] and [0.246, 0.698]). **This is a
set of four separate per-signal statements, each compared only against zero — it is not by itself a
between-signal significance test.**

**Paired between-signal contrast.** An exploratory secondary analysis computes the actual paired,
question-aware contrast that a marginal, per-signal comparison alone cannot provide. It reuses the same
already-frozen,
already-seen scoring data (no new model run, no new data) and the same two-level cluster bootstrap
method and seed as the original per-signal analysis, but resamples both signals in a pair from the
*same* bootstrap draw in every replicate, so the comparison is paired rather than two independent CIs.
Method fixed in advance in a dated protocol note written before computing any result. All four confidence
intervals were independently re-derived a second time via a differently-structured implementation
(separate data-loading and statistics libraries, a separately-written resampling loop) against the same
source data; all four reproduce exactly, confirming the pairing (the same resample applied to both
signals each replicate) is implemented correctly and not merely internally consistent. This remains an
**exploratory,
inconclusive paired comparison of already-seen, already-frozen data** — not a preregistered confirmatory
test, and its results below are not read as evidence that the signals are statistically equivalent.

*TABLE VI — Paired Signal Contrasts (two-level cluster bootstrap, B = 10,000, seed 42, same draw for
both signals per replicate; exploratory, not preregistered)*

| Contrast | Point difference (ρ) | 95% CI | Excludes zero? |
|---|---|---|---|
| $R$ − $S_1$ | +0.2761 | [−0.0747, 0.5745] | No |
| $R$ − $S_2^{effective}$ | +0.1826 | [−0.1632, 0.5353] | No |
| $S_1$ − $S_2^{effective}$ | −0.0936 | [−0.2938, 0.1654] | No |
| Composite − $R$ alone | −0.1020 | [−0.2853, 0.1171] | No |

**None of the four paired contrasts excludes zero.** Despite $R$'s marginal correlation (0.4832) being
more than double $S_1$'s (0.2070), the paired bootstrap does not distinguish $R$ from $S_1$ or from
$S_2^{effective}$ at this sample size (n = 64 cases, 8 question clusters); nor does it distinguish $S_1$
from $S_2^{effective}$; nor does it distinguish the deployed composite from $R$ alone, despite the
composite's numerically lower point estimate. This does not mean the signals are equivalent — a CI that
includes zero at n = 64/8 is underpowered evidence either way, not evidence of no difference — but it
does mean the earlier text's caution was correct, and is now a tested rather than merely a withheld
claim. We therefore continue to explicitly not claim $R$ is uniquely or significantly better than $S_1$
or $S_2$, and now additionally do not claim the deployed composite is a statistically confirmed
correlation trade-off relative to $R$ alone — only that its point estimate is numerically lower. We do
not conclude $S_1$ or $S_2$ are non-functional in the deployed system — they serve structural roles
(keyword-stuffing resistance via dampening, mandatory-concept gating) that a bare correlation with an
overall human quality rating does not capture. This is a current-cycle, non-P2 result and must not be
confused with the project's separate, paused, N=20-pilot seven-way evaluator ablation, which used a
different, superseded, single-rater human-reference set, genuinely recomputed the composite under
several signal-combination weightings (a real ablation grid), and stays excluded from this paper (§XII).

$R$'s own marginal association (both frozen analyses agree it excludes zero) must be read together
with, not instead of, the length-confound analysis immediately below: that analysis finds $R$'s
correlation with human judgment is substantially explained by its own association with answer length,
and the length-controlled partial correlation's 95% CI includes zero. We do not describe $R$ as
validated "reasoning verification" on the strength of this section's marginal correlation — a
non-zero marginal association is not the same claim as an established, length-independent reasoning
contribution, and the latter is the one this paper does not make.

**Composite-score robustness to resampling** (about the full composite score, not the CrossEncoder
component alone). A two-level (question-then-case) cluster bootstrap, B = 10,000, widens the interval
to [0.153, 0.649], reflecting the coarser 8-question effective sample; leave-one-question-out
correlations stay in a narrow band (0.352–0.434); leave-one-rater-out correlations are similarly
stable (0.355–0.382).

**CrossEncoder component vs. simple lexical baselines.** A preregistered exploratory analysis arm
(tag `prereg/X2-B/v2`) compared the CrossEncoder's own correlation against a trivial word-count-only
baseline, using the **raw, unmapped CrossEncoder logit** (ρ = 0.4825) rather than the deployed,
clamped-and-rescaled $R$ signal reported above (ρ = 0.4832): **ρ = 0.4897, 95% CI [0.219, 0.708]** —
matching or exceeding the CrossEncoder's own correlation. BM25 (ρ = 0.3812), TF-IDF (ρ = 0.245), and
reference-token overlap (ρ = 0.4301) are in a similar range. The 0.4825/0.4832 difference is not
resampling noise — both are fixed point estimates on the same 64 items — and is fully explained: applying
the deployed mapping formula to the raw logit reproduces the stored $R$ value to within 0.0005 per item,
and the residual is entirely storage-precision rounding (to 3 decimals) that creates two tied pairs among
64 items, shifting 4 items' ranks by a fraction of a rank and the resulting Spearman ρ by 0.0007;
independently verified by tracing the deployed mapping code against the stored values. This was that
arm's registered *exploratory*, not primary confirmatory,
endpoint — a planned, pre-run-noted analysis, not post-hoc fishing, but not designed or powered as a
formal head-to-head test, so its result is suggestive, not decisive. Read plainly: the CrossEncoder's
advantage over a naive length/lexical baseline is not established on this benchmark.

**Length-confound analysis.** This motivated a more direct question: does the CrossEncoder carry
information about human judgment beyond answer length itself? A partial-correlation analysis
(method fixed in a pre-run note before computation; exploratory/sensitivity status; same 64-case
benchmark) is computed on the same **raw, unmapped CrossEncoder logit** used immediately above (not the
deployed $R$ signal; the two differ only by the monotonic clamp/rescale mapping and storage rounding
detailed above, which does not materially affect a rank-based partial-correlation analysis) and found the
CrossEncoder's own score is associated with length (Spearman ρ = 0.6594 against
raw token count, 95% CI [0.457, 0.831] — this specific association, unlike what follows, is
confidently established on this benchmark; it is an association, not a demonstrated causal
mechanism). Controlling for length, the CrossEncoder's partial correlation with human judgment drops
from 0.4825 to **0.2434** — this drop is itself statistically supported (95% CI of the drop: [0.048,
0.429], excludes zero) — but the partial correlation's own remaining level has a 95% CI of
**[−0.008, 0.507]**: the lower bound touches zero, so a length-independent contribution is not
confidently established. This is not the same as establishing there is none — the upper bound (0.51)
is equally consistent with a real, moderate contribution this 8-question sample cannot resolve. A
direct, paired, question-aware comparison against BM25's own partial correlation (0.2458) gives a
point-estimate difference of −0.0024 and a 95% CI of **[−0.341, 0.360]**: far too wide to conclude
either that the CrossEncoder and BM25 differ or that they are equivalent once length is controlled
for. We describe this component in this paper as a *reasoning-scoring signal whose independent
contribution beyond length and simple lexical overlap is not established on the current benchmark*,
not as validated "reasoning verification."

Separately, the same analysis arm found the project's own fine-tuned CrossEncoder correlates with the
human-reference score better than the public, un-fine-tuned upstream checkpoint on identical inputs
(paired Spearman difference 0.337, 95% CI [0.042, 0.606]) — real evidence the fine-tuning changed
something, though exactly what cannot be fully characterized without the missing training record
(§XII), and this does not by itself establish that what it learned is length-independent reasoning
quality rather than, e.g., a stronger length-sensitivity than the upstream model.

We report the favorable robustness evidence and the unfavorable length-confound finding together,
rather than either overstating the CrossEncoder's validation or omitting the null result. A benchmark
specifically designed to separate reasoning quality from answer length is the concrete next step; it
does not need to be designed from scratch — the project's existing, not-yet-registered X2-C
confirmatory protocol already specifies six strata with length deliberately crossed with correctness,
and a length-confound-specific analysis amendment to it is drafted. This is real, reviewable future
work, gated on an institutional ethics determination not yet sought, and is not available before this
paper's submission; the existing 64-case benchmark was not built for this purpose, and no further
reanalysis of it will resolve the question with more precision than an 8-question effective sample
allows.

## XI. Results and Discussion

The hybrid evaluator's dampening mechanism (§IV) functions as specified and is code-verified. The
communication-confidence model (§V) is fully code-verified and decoupled from technical scoring, with
one disclosed, narrow lexical exception. The follow-up mechanism is deterministic and evidence-gated
as intended, though its actual trigger logic is coarser than the system's originally-designed
five-condition trigger table (§VII, §XII). Automated tests confirm implementation correctness across
the evaluator,
orchestrator, RL environment bounds, and audio pipeline (§X.A). We do not claim the PPO difficulty
controller demonstrably improves question-difficulty tracking over simpler alternatives: this paper
has no evidence of its own on that question, and no evidence yet eligible for citation from elsewhere
in the project establishes it either way. The composite evaluator's correlation with
human judgment is moderately stable under resampling of questions and raters (§X.B). A per-signal
association analysis (§X.B, Table V) finds $R$'s own correlation with human judgment is confidently
non-zero under two independently frozen bootstrap analyses, $S_1$'s is not, and $S_2$'s is ambiguous
between the two — three separate per-signal readings. A follow-up paired, question-aware bootstrap
contrast (§X.B, Table VI) tests the comparison directly and finds none of the four pairwise gaps —
including $R$ against $S_1$ or $S_2$, or the deployed composite against $R$ alone — statistically
distinguished from zero at this sample size; this is a disclosure worth making explicit about the
evidentiary basis for the three components' 0.15/0.35/0.50 weighting rather than leaving it implicit,
and it means that weighting is not itself justified by a demonstrated between-signal performance gap.
The CrossEncoder
(R) component specifically shows a real marginal correlation with human judgment, but the
length-confound analysis found that correlation is substantially explained by the CrossEncoder's own
strong association with answer length; a length-independent contribution is not confidently
established (the CI's lower bound is near zero, not the point estimate), and a direct paired
comparison against a simple lexical baseline (BM25) is too imprecise at this sample size to say
whether the two differ. We report this as a genuine, currently unresolved limitation of the
evaluator's reasoning-verification claim: the component functions as a reasoning-scoring signal whose
independent value is not yet demonstrated, a materially different — and more honest — claim than
"reasoning verification."

## XII. Limitations and Threats to Validity

Local LLM inference introduces noticeable response latency during follow-up and feedback generation;
speech-feature extraction is sensitive to background noise and microphone quality; technical
evaluation precision depends on the completeness of curated question rubrics; and no human user study
of learning outcomes has been run. In addition:

- The CrossEncoder reasoning model's training data, training code, and exact train/test split are not
  established in the project's own records; its correlation with human judgment should be read as
  exploratory (n = 64 constructed answers, 8 questions), not general-purpose validity. The
  length-confound analysis (§X.B) found this correlation is substantially explained by the
  CrossEncoder's own association with answer length; a length-independent contribution is not
  confidently established — not the same as establishing there is none.
- This paper does not claim the PPO difficulty controller's own contribution to tracking accuracy
  beyond a simple guardrailed constant policy, because no evidence eligible for citation here
  establishes it (§VI). The project's internal PPO research on this exact question belongs to a
  separate, not-yet-public companion manuscript and is withheld accordingly. The frozen PPO
  checkpoints were trained against a single simulated candidate persona with an unseeded noise
  generator, so no claim of cross-candidate generalization, or of exact checkpoint reproducibility
  from the training seeds alone, is supported.
- The 64-case benchmark's rater provenance and ethics records are incomplete; this benchmark must not
  be described as independent, expert, or ethics-cleared human evaluation, only as an exploratory
  construction.
- The per-signal association analysis (§X.B, Table V) has the same 8-question effective sample size
  as every other analysis on this benchmark; $S_1$'s CI spanning zero, and $S_2^{effective}$'s
  boundary-ambiguous CI (excluding zero under one independently frozen bootstrap, including it under
  another), could reflect a genuinely weak marginal correlation or insufficient power to detect a real
  but modest one — the data available cannot distinguish these. A follow-up paired, question-aware
  bootstrap contrast (§X.B, Table VI) now exists between $S_1$, $S_2$, $R$, and the deployed composite;
  none of its four tested pairwise gaps excludes zero, so no claim that $R$ differs significantly from
  $S_1$ or $S_2$, or that the composite differs significantly from $R$ alone, is made — this is now a
  tested null result rather than an untested comparison, but a null result at n = 64/8 reflects limited
  power as much as it reflects a genuine absence of difference. The comparison is descriptive, with no
  multiplicity correction applied across the four rows of Table V or the four contrasts of Table VI.
- A defect in the follow-up/feedback generation path — a bare (non-list) evaluator field could
  corrupt follow-up text into single characters — has been identified, fixed, and covered by regression
  tests on the development snapshot described in §X.A, but has **not yet been merged** into the codebase
  the deployed system currently runs from. Authors should confirm merge status before any submission that
  implies the fix is live.
- The deployed model checkpoint and the checkpoint referenced by this project's simulation evidence
  are not confirmed to be the same file (different content hashes); no claim in this paper assumes
  they are identical, and no claim in this paper depends on which specific checkpoint is described.

## XIII. Ethics, Provenance, and Data Statement

No new human-subjects data was collected for this paper. The 64-case benchmark used throughout §X.B was
constructed and rated internally by the project team, following the project's own internal working
practices. This paper's evidentiary characterization of that benchmark — exploratory, not an independent,
expert-panel, or formally ethics-approved evaluation — describes the strength and scope of the resulting
correlation evidence, not an assertion that the project's internal procedures were improperly followed;
the project's own records do not include a separate, independently documented consent, blinding, or
institutional-ethics record for this internal exploratory benchmark beyond its own working files, and this
paper does not claim one exists. A confirmatory human-rated benchmark (X2-C) is designed but, as of the
time of writing, not yet started under a separate, ongoing effort: no item has been authored for it, no
rater has been contacted, and no data has been collected, pending an institutional ethics/venue
determination that has been drafted but not yet sent. All simulated-candidate and PPO training evidence
referenced in this paper (§VI, §XII) derives from a single synthetic simulated persona and synthetic
reward signal; none of it is treated, described, or cited as evidence about real users, real candidate
learning, or real interview outcomes.

## XIV. Reproducibility and Data/Code Availability

PrepAIred is implemented in **Python 3.12** and React 18. The backend uses FastAPI, **PyTorch
(pinned `>=2.3.0,<2.7.0`)**, SentenceTransformers, FAISS-CPU, Stable-Baselines3, and a **local
GGUF/llama.cpp runtime** for LLM inference. All evaluator weights, thresholds, and model identifiers
reported in this paper (§IV, Table III) are exact values from the deployed configuration, not
illustrative examples.

**Methodological reproducibility.** Every statistical result reported in this paper was computed with a
fixed, documented method and seed: the two-level (question-then-case) cluster bootstrap
(`numpy.random.default_rng(42)`, B = 10,000) used throughout §X.B respects the benchmark's 8-question
clustering by resampling questions first and then resampling each drawn question's answers; the
length-confound analysis (§X.B) additionally used a rank-transform-and-residual-regression method, fixed
in a written protocol note before computation; the paired signal contrast (§X.B, Table VI) used the same
two-level bootstrap with both signals resampled from the same draw per replicate, also fixed in a written
protocol note before computation. Every load-bearing statistic in Tables V and VI, and in the
length-confound analysis, was independently re-derived a second time via a differently
structured implementation (a separate statistics library and a separately written resampling loop, or a
mathematically distinct method), reproducing the original figures exactly or to within ordinary Monte
Carlo noise — reported in this paper as independent verification of an existing calculation on the same
already-collected data, not as independent replication on new data.


**Data and code availability.** The evaluator source code, RL training/environment code, and the 64-item
benchmark dataset (human-reference scores, category labels, and per-signal scores) used throughout this
paper are maintained in the authors' project repository. A public release of the repository, or of a
de-identified subset sufficient to reproduce Tables III–VI, has not been finalized at the time of writing.

## XV. Conclusion and Future Work

This paper presented PrepAIred's architecture as implemented and verified: a hybrid, precisely
specified technical evaluator; an independent, precisely specified speech-confidence model; a
deterministic evidence-gated follow-up mechanism, simpler than the system's originally-designed
five-condition trigger table (§VII, §XII); and a PPO-based difficulty controller whose own marginal
tracking benefit is not asserted here because no evidence eligible for citation in this paper
establishes it. We report a length-confound analysis showing the CrossEncoder's correlation with
human judgment is substantially explained by answer length, with a length-independent contribution
not established on the current benchmark, as a genuine, disclosed limitation rather than omitting it.
A paired, question-aware bootstrap contrast among the evaluator's three signals and their deployed
composite (§X.B, Table VI) finds no statistically distinguished pairwise difference at this sample
size, including between the composite and the CrossEncoder alone — a null result that reflects the
benchmark's limited power as much as any genuine equivalence, and a question a properly powered,
preregistered confirmatory study (§X.B) would need new data to settle. Future work includes: closing the gap between the follow-up mechanism's original five-condition design
intent and its current implementation, or documenting the simpler mechanism as the intended design; a
benchmark designed to separate reasoning quality from answer length (a protocol amendment for which is
already drafted, pending institutional ethics clearance); a registered simulation evaluation of the
specific deployed checkpoint; incorporating the project's companion PPO research once it is publicly
available; and, contingent on ethics clearance and further governance decisions, a human
feasibility/usability study. This paper makes no claim about candidate learning outcomes, which
require direct evidence that does not yet exist.

## Acknowledgments

The authors thank the Department of Computer Science and Engineering, PES University, Bengaluru, for
institutional support.

## References

[1] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks," in
*Proc. EMNLP-IJCNLP*, 2019, pp. 3982–3992.

[2] P. Bajaj et al., "MS MARCO: A Human Generated Machine Reading Comprehension Dataset,"
arXiv:1611.09268, 2016.

[3] P. Boersma, "Praat, a system for doing phonetics by computer," *Glot International*, vol. 5, no.
9/10, pp. 341–345, 2001.

[4] I. Naim, M. I. Tanveer, D. Gildea, and M. E. Hoque, "Automated prediction and analysis of job
interview performance: The role of what you say and how you say it," in *Proc. IEEE FG*, 2015, pp.
1–6.

[5] L. Chen et al., "Automated scoring of interview videos using doc2vec multimodal feature
extraction paradigm," in *Proc. ACM ICMI*, 2016, pp. 161–168.

[6] A. T. Corbett and J. R. Anderson, "Knowledge tracing: Modeling the acquisition of procedural
knowledge," *User Modeling and User-Adapted Interaction*, vol. 4, no. 4, pp. 253–278, 1994.

[7] J. R. Anderson, A. T. Corbett, K. R. Koedinger, and R. Pelletier, "Cognitive tutors: Lessons
learned," *The Journal of the Learning Sciences*, vol. 4, no. 2, pp. 167–207, 1995.

[8] J. Schulman, F. Wolski, P. Dhariwal, A. Radford, and O. Klimov, "Proximal Policy Optimization
Algorithms," arXiv:1707.06347, 2017.

[9] A. Graves, M. G. Bellemare, J. Menick, R. Munos, and K. Kavukcuoglu, "Automated Curriculum
Learning for Neural Networks," in *Proc. ICML*, 2017, pp. 1311–1320.

[10] R. Portelas, C. Colas, L. Weng, K. Hofmann, and P.-Y. Oudeyer, "Automatic Curriculum Learning For
Deep RL: A Short Survey," in *Proc. IJCAI*, 2020, pp. 4819–4825.

[11] D. J. Weiss, "Improving measurement quality and efficiency with adaptive testing," *Applied
Psychological Measurement*, vol. 6, no. 4, pp. 473–492, 1982.

[12] Z. Ji et al., "Survey of Hallucination in Natural Language Generation," *ACM Comput. Surv.*, vol.
55, no. 12, Art. 248, pp. 1–38, 2023.

[13] Qwen Team, "Qwen2.5 Technical Report," arXiv:2412.15115, 2024.

[14] S. Sablok, S. Sharma, P. K. Singh, J. Singh, A. Sharma, D. Shrivastava, and A. Singh, "Ascend AI:
An Intelligent, Multimodal Framework for Personalized Career Direction and Adaptive Technical
Interview Simulation," *Int. J. Creative and Open Research in Engineering and Management (IJCOPE)*,
vol. 2, no. 4, Apr. 2026, doi: 10.55041/ijcope.v2i4.743.

[15] N. Gomez, S. S. Batham, M. Volonte, and T. D. Do, "Virtual Interviewers, Real Results: Exploring AI-Driven Mock Technical Interviews on Student Readiness and Confidence," in *Proc. ACM CSCW Companion 2025*, pp. 209–213, 2025, doi: 10.1145/3715070.3749227.

[16] Y. Hong, H. Yao, B. Shen, W. Xu, H. Wei, and Y. Dong, "From Rubrics to Reliable Scores: Evidence-Grounded Text Evaluation with LLM Judges," arXiv:2601.08654, version 3, 2026 (accepted to EMNLP 2026 Main Conference).

[17] E. Kim, J. Suk, S. Kim, N. Muennighoff, D. Kim, and A. Oh, "LLM-as-an-Interviewer: Beyond Static Testing Through Dynamic LLM Evaluation," in *Findings of the Association for Computational Linguistics: ACL 2025*, pp. 26456–26493, 2025, doi: 10.18653/v1/2025.findings-acl.1357.

