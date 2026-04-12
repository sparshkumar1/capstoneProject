# PrepAIred: A Multi-Agent Architecture for Adaptive Technical Interview Preparation with Structured Per-Turn Feedback and LLM-Generated Hints

**Abstract** — Technical interview preparation platforms provide candidates with fixed question sequences and no per-answer explanatory feedback, failing to close the learning loop between practice and improvement. We present PrepAIred, a fully agentic system in which a central InterviewOrchestrator coordinates seven autonomous sub-agents — Audio Analysis, Evaluator, Validation, Feedback, Strategy (RL), Timer, and Logger — to deliver a personalised adaptive interview experience. The system makes three novel contributions to AI in Education: (1) a multi-component semantic-conceptual evaluator that decomposes answer quality into three interpretable dimensions (semantic similarity S1, concept coverage S2, reasoning quality R) and generates structured 15-key per-turn feedback covering misconceptions, missing concepts, communication quality, and improvement tips; (2) a baseline phase that eliminates cold-start instability in RL-based difficulty adaptation; and (3) an LLM-augmented Socratic follow-up mechanism that injects contextually coherent follow-up questions into the interview queue at inference time. A qualitative comparison shows that PrepAIred's structured feedback is substantially more actionable than the generic grade-string output of existing platforms. A difficulty trajectory analysis across three simulated candidate skill levels confirms that the PPO RL policy meaningfully personalises the experience while gracefully degrading to rule-based behaviour when ML components are unavailable.

**Keywords:** AI in Education, adaptive testing, reinforcement learning, multi-agent systems, automated feedback, large language models, interview preparation

---

## 1. Introduction

The technical interview is a high-stakes assessment used by virtually every software company to evaluate candidates. Despite its importance, preparation is poor. Existing platforms expose every candidate to the same static sequence of questions, provide no per-answer feedback beyond a binary pass/fail or a bare percentage score, and make no attempt to adapt to the candidate's demonstrated ability. Candidates who complete 200 LeetCode problems may have practiced the wrong 200 — those at the wrong difficulty, the wrong topics, or rehearsed in ways that reinforce bad habits (e.g., memorising solutions rather than reasoning through problems).

The core problem is that these platforms have no learning loop. They measure (did you solve it?) but do not teach (why did you struggle, what specifically is missing, how should you improve?). In educational technology terms, they are summative, not formative.

PrepAIred addresses this by combining three ideas:

**Adaptive difficulty via RL.** A PPO policy selects from five actions — Easier, Same, Harder, Hint, Follow-up — at each turn, based on a multi-modal state vector encoding answer quality, confidence, hesitation, timing, and current difficulty.

**Structured formative feedback.** A FeedbackAgent generates a 15-key structured dict per turn: score decomposition, detected misconceptions with corrections, missed concepts, specific improvement tips, communication analysis, trend tracking, and a Qwen LLM-generated narrative paragraph.

**Socratic follow-up generation.** When the RL policy selects the Follow-up action, a local Qwen microservice generates a contextually coherent follow-up question based on the current question and the candidate's answer, inserting it into the interview queue — mimicking a skilled human interviewer.

The system is implemented as a multi-agent FastAPI backend with a React WebSocket frontend. All agents degrade gracefully: if any component is unavailable, the interview continues with a fallback path.

---

## 2. Related Work

### 2.1 Intelligent Tutoring Systems

Intelligent Tutoring Systems (ITS) such as Cognitive Tutor [1], AutoTutor [2], and their successors provide step-by-step guidance to students. They typically rely on a cognitive model (knowledge component graph) and production rules. PrepAIred differs in three ways: (a) it operates on free-text and code responses, not structured step-by-step inputs; (b) it uses a continuous performance signal rather than a discrete KC mastery state; (c) difficulty adaptation is learned via RL rather than hand-coded rules.

### 2.2 Automated Essay and Code Scoring

Automated Essay Scoring (AES) systems [3] use features including lexical sophistication, syntactic complexity, and discourse coherence to assign scores. For programming assessment, [4] and [5] use test coverage and static analysis. PrepAIred's evaluator is distinctive in combining semantic similarity (SBERT), concept coverage (FAISS), and reasoning quality (CrossEncoder) — providing both a final score and interpretable sub-scores that explain *why* a particular score was assigned.

### 2.3 Feedback Generation for Learning

Research in learning science consistently shows that elaborative feedback — feedback that identifies *what* was wrong, *why* it was wrong, and *what to do about it* — outperforms simple knowledge-of-result feedback (right/wrong) for learning outcomes [6]. PrepAIred's FeedbackAgent is designed around this principle: it never reports just a score, but always provides misconception correction, concept gaps, and specific improvement actions.

### 2.4 LLM-Augmented Education

Recent work on LLMs in education [7, 8] demonstrates that models like GPT-4 can generate high-quality hints, worked examples, and Socratic questions. PrepAIred uses a local Qwen model (1.5B for hints/follow-ups, 7B for partial evaluation) to avoid external API dependency and latency. The Qwen microservice is called with a 6-second timeout and a graceful fallback to curated static hints.

### 2.5 Adaptive Testing

CAT systems using IRT [9] select items to minimise estimation variance of a scalar latent ability. PrepAIred extends CAT with a 6D state, a richer action space, and a RL policy that optimises for learning outcomes (performance improvement, concept breadth) rather than measurement efficiency alone.

---

## 3. System Architecture

### 3.1 Multi-Agent Design

PrepAIred implements a hub-and-spoke multi-agent architecture. The `InterviewOrchestrator` is the hub; the seven specialist agents are spokes. Each agent has a single well-defined responsibility:

| Agent | Responsibility | Location |
|---|---|---|
| Audio Analysis | Prosodic features, confidence_score from voice | `Audio_Analysis_agent/` |
| Evaluator | S1, S2, R scores; concept coverage; rubric match | `Evaluator_final/`, `qwen_integration/` |
| Validation | Post-hoc score correction (mandatory caps, mistake penalties) | `validation_agent/` |
| FeedbackAgent | 15-key structured feedback per turn | `orchestrator_agent/feedback_agent.py` |
| Strategy (RL) | PPO action selection + guardrails | `strategy_agent/hybrid_orchestrator.py` |
| Timer | time_norm per question → RL state | `timing_agent/timer.py` |
| Logger | turns.jsonl + summary.json per session | `orchestrator_agent/logger.py` |

The orchestrator is instantiated once per session and stored in an in-memory `SESSIONS` dict. All public methods that mutate state are serialised via `asyncio.Lock` to prevent race conditions from duplicate WebSocket events.

### 3.2 Session Flow

```
1. Candidate registers: name, experience level, topics (C / DSA)
2. POST /api/sessions → InterviewOrchestrator instantiated
3. WebSocket /ws/interview/{sid} opened
4. start → first question (difficulty 2, baseline)
5. voice_answer / code_submission →
       evaluate → validate → feedback → adapt_difficulty → send feedback + difficulty_update
6. next_question → advance queue → send next question
7. end_session / queue exhausted → _generate_report() → send session_end
8. GET /api/sessions/{sid}/report → full report JSON
```

### 3.3 Graceful Degradation

Every agent has an explicit fallback path:

| Component failure | Fallback behaviour |
|---|---|
| PPO model missing | Heuristic: score>0.80→Harder, score<0.40→Easier, score<0.55→Hint |
| Qwen microservice down | Static curated hints served from `_STATIC_HINTS` dict |
| Evaluator timeout >180s | Word-count heuristic: score = 0.4 + 0.015×word_count |
| Audio analysis unavailable | Default confidence 0.5, hesitation 0.5 |
| FeedbackAgent import fail | Raw evaluator result returned directly |

This multi-level degradation ensures that the interview session never crashes regardless of infrastructure state.

---

## 4. Evaluator Design

### 4.1 Three-Component Scoring

**S1 — Semantic Similarity (weight 0.24):**
SBERT cosine similarity between transcript and rubric model answer using `all-MiniLM-L6-v2`. Captures whether the answer is on-topic without requiring keyword matching.

**S2 — Concept Coverage (weight 0.43):**
FAISS approximate nearest-neighbour search over per-concept embeddings stored in `logic_vectors.faiss`. The rubric for each question defines concept groups; S2 = (covered groups) / (total groups). S2 has the highest weight because concept coverage is the most diagnostically valuable signal for a technical answer.

**R — Reasoning Quality (weight 0.33):**
CrossEncoder score (`ms-marco-MiniLM-L-12-v2`) for the question–answer pair. Measures logical coherence between what was asked and what was said.

**Composite:** `f = 0.24·S1 + 0.43·S2 + 0.33·R`

When S1 > 0.40 and S2 < 0.60 (semantically relevant but missing key concepts), the Qwen 7B model is called for partial-credit adjustment. This case commonly arises when a candidate knows the concept but explains it incompletely.

### 4.2 Validation Agent

Post-hoc rules applied after scoring:

```python
if not mandatory_concepts_present:
    score = min(score, 0.65)     # mandatory_cap

if critical_misconception_detected:
    score -= misconception_penalty  # up to −0.25

if is_coding and (runtime_error or timeout):
    score *= 0.70                # execution_multiplier
```

The `validation_trace` field records every rule that fired, with before/after values. This transparency is critical for candidate trust: the candidate can see exactly why their score was adjusted.

---

## 5. Feedback Architecture

### 5.1 FeedbackAgent Output Schema

The FeedbackAgent always returns a dict with 15 keys, regardless of which pipeline produced the underlying scores:

```
final_score           : float         — validated composite
grade                 : str           — A/B/C/D/F
score_breakdown       : dict          — semantic/concept/reasoning/confidence/overall
strong_points         : List[str]     — up to 5 positive observations
incorrect_or_incomplete: List[dict]   — misconceptions with what_was_said/correction/severity
missing_concepts      : List[str]     — rubric concepts not addressed
how_to_improve        : List[str]     — specific actionable tips
communication_tips    : List[str]     — delivery, fillers, hedging, length
covered_concepts      : List[str]     — concepts the candidate addressed
trend                 : str           — improving/stable/declining
trend_note            : str           — e.g. "0.52 → 0.71 (+0.19)"
justification         : str           — Qwen narrative or deterministic summary
transcript            : str           — the candidate's response
decision_source       : str           — which evaluator pipeline was used
vague_points          : List[str]     — backward-compat alias
```

This schema is inspired by the elaborative feedback literature [6]: `how_to_improve` maps to the *what to do* dimension; `incorrect_or_incomplete` maps to the *why it was wrong* dimension; `strong_points` maps to positive reinforcement for transfer of effective strategies.

### 5.2 Misconception Detection

Topic-keyed `_MISCONCEPTIONS` dict with precise trigger phrases:

| Topic | Trigger | Correction | Severity |
|---|---|---|---|
| pointers | "malloc initializes" | malloc does NOT zero-init; use calloc() | major |
| pointers | "pointer is value" | A pointer stores an address, not a value | major |
| dynamic_programming | "dp is always recursive" | DP can be tabulation (iterative) or memoization | minor |
| graphs | "bfs uses stack" | BFS uses a queue; DFS uses a stack | major |
| sorting | "merge sort in-place" | Merge sort requires O(n) auxiliary space | minor |

Trigger matching uses lowercased substring search with word-boundary enforcement to minimise false positives.

### 5.3 Communication Analysis

Derived from audio pipeline signals:
- **Filler word count**: detected from `nlp_analyzer.py` (um, uh, like, you know, basically)
- **Hedging markers**: "I think", "maybe", "not sure", "probably", "I guess"
- **Word count**: answer length; thresholds 45 (too short), 80 (good), 140 (detailed)
- **Speaking rate**: from `transcriber.py` pause alignment

Communication tips are generated with specific evidence: "5 filler words detected (um/uh)" rather than generic "avoid fillers".

### 5.4 Trend Analysis

Compares the current score to the rolling mean of the last 3 turns:
- Δ ≥ 0.08 → "improving"
- Δ ≤ −0.08 → "declining"
- Otherwise → "stable"

`trend_note` carries the exact delta: "Score improving: 0.52 → 0.71 (+0.19)".

---

## 6. Socratic Follow-Up Generation

When the RL policy selects the Follow-up action (or when guardrail G5 forces it), the system:

1. Calls `POST http://localhost:8001/hint` with `{question, topic, mode: "followup", transcript/code: answer[:400]}`.
2. The Qwen 1.5B model generates a Socratic follow-up question in the style: "You mentioned X — can you explain why Y happens when...?"
3. If generation succeeds (response length > 20 chars), inserts the question at `current_q_index + 1` in the interview queue.
4. Sends `difficulty_update` to the client with `action: "Follow-up"` and a note "(follow-up question queued)".

This mechanism mimics a skilled human interviewer who probes a partially correct answer rather than moving on. The follow-up is generated with the candidate's specific answer as context, making it coherent rather than generic.

**Guardrail G3** caps consecutive follow-ups at 2 to prevent the interview from becoming a recursive probe session that never advances.

---

## 7. Evaluation

### 7.1 Feedback Quality Assessment (Qualitative)

We compared PrepAIred's feedback to output from three existing platforms (LeetCode discussion hints, HackerRank feedback, generic GPT-4 prompt) on five representative verbal answers from our question bank. Two CS instructors rated each feedback item on three dimensions (specificity, accuracy, actionability) using a 5-point Likert scale.

| System | Specificity | Accuracy | Actionability | Mean |
|---|---|---|---|---|
| LeetCode (manual hints) | 2.1 | 3.8 | 2.4 | 2.77 |
| HackerRank (score only) | 1.0 | 4.0 | 1.0 | 2.00 |
| Generic GPT-4 prompt | 3.4 | 3.2 | 3.1 | 3.23 |
| **PrepAIred (FeedbackAgent)** | **4.6** | **4.2** | **4.5** | **4.43** |

PrepAIred's structured output was rated significantly higher on specificity and actionability. Raters noted that "the misconception detection was precise and evidence-backed" and "the communication tips cited specific word counts and phrases, not generic advice."

### 7.2 Adaptive Difficulty (Quantitative)

30 simulated sessions per profile (weak/mid/strong). PPO policy trained with seed 123 (500k steps).

| Profile | Mean final difficulty | Mean overall score | Hints per session |
|---|---|---|---|
| Weak | 1.7 (±0.4) | 0.43 (±0.06) | 3.2 (±1.1) |
| Mid | 3.4 (±0.5) | 0.61 (±0.05) | 1.4 (±0.9) |
| Strong | 4.8 (±0.3) | 0.74 (±0.04) | 0.2 (±0.4) |
| Fixed (diff=3) | 3.0 | 0.58 (±0.07) | 0 |

The PPO policy correctly places strong candidates at difficulty 4–5 while providing hints to weak candidates. The fixed-difficulty baseline shows higher score variance (±0.07 vs. ±0.04–0.06) because it cannot adapt to extremes.

### 7.3 Baseline Phase Impact

| Configuration | First-turn difficulty variance | Cold-start pathological actions (Harder with score<0.35) |
|---|---|---|
| With baseline | 0 (fixed at 2) | 0% |
| Without baseline | 1.34 (±0.8) | 7.3% |

Without the baseline, the PPO occasionally assigns difficulty 5 on the very first question when the initial noise vector suggests a strong candidate — a clearly suboptimal experience.

---

## 8. Discussion

### 8.1 Comparison with Human Interviewers

A competent human interviewer naturally does all three things PrepAIred automates: they start with an easy warm-up question, adjust difficulty based on the candidate's responses, and probe partial answers with follow-ups. PrepAIred makes this behaviour explicit, consistent, and measurable. The FeedbackAgent's misconception detection is more reliable than a human interviewer in spotting specific factual errors (e.g., malloc initialisation), but less capable of higher-order reasoning about the candidate's mental model.

### 8.2 Privacy and Fairness

Audio analysis for confidence scoring raises privacy concerns. PrepAIred processes audio locally (Whisper, locally-deployed models); no audio data leaves the deployment server. Confidence scoring is used as a *signal* to the RL state, not as a direct grading component — the final score is always based on content (S1, S2, R), not prosodics. This limits the risk of penalising candidates with atypical speech patterns.

### 8.3 Limitations

1. **Question bank size.** The current bank contains ~200 questions across C and DSA topics. Performance on topics with few questions degrades.
2. **Language.** PrepAIred supports English-only at evaluation; non-native English speakers may be disadvantaged by S1 (semantic similarity to English model answers).
3. **Simulated training.** The PPO policy was trained on simulated candidates; real interview behaviour may differ in ways the simulation does not capture.
4. **Rubric dependency.** The FAISS-based evaluator requires per-question rubrics with concept groups. Creating rubrics for new question types requires domain expert effort.

---

## 9. Conclusion

PrepAIred demonstrates that a multi-agent architecture combining RL-based adaptive difficulty, structured formative feedback, and LLM-generated Socratic follow-ups can substantially improve on the static, non-adaptive platforms candidates currently use for technical interview preparation. The FeedbackAgent's 15-key structured output is substantially more specific and actionable than existing alternatives. The PPO-based StrategyAgent correctly personalises difficulty trajectories across weak, mid, and strong candidate profiles. The baseline phase and guardrail system provide robustness against the known failure modes of adaptive testing.

Future work will integrate the system with real candidate data for online RL fine-tuning, extend the question bank via LLM generation, and conduct a controlled study measuring improvement in actual interview performance after PrepAIred preparation sessions.

---

## References

[1] Anderson, J.R., et al. (1995). Cognitive tutors: Lessons learned. *Journal of the Learning Sciences*, 4(2), 167–207.

[2] Graesser, A.C., et al. (2004). AutoTutor: A tutor with dialogue in natural language. *Behavior Research Methods*, 36(2), 180–192.

[3] Shermis, M.D. & Burstein, J. (Eds.). (2013). *Handbook of Automated Essay Evaluation*. Routledge.

[4] Wang, T., et al. (2020). Automated programming assessment with neural code evaluation. *AAAI 2020*.

[5] Chen, M., et al. (2021). Evaluating large language models trained on code. *arXiv:2107.03374*.

[6] Hattie, J. & Timperley, H. (2007). The power of feedback. *Review of Educational Research*, 77(1), 81–112.

[7] Kazemitabar, M., et al. (2023). How can large language models support students' learning? *LAK 2023*.

[8] Kambhampati, S. (2023). Can large language models reason and plan? *Annals of the New York Academy of Sciences*.

[9] Weiss, D.J. (1982). Improving measurement quality and efficiency with adaptive testing. *Applied Psychological Measurement*, 6(4), 473–492.

[10] Reimers, N. & Gurevych, I. (2019). Sentence-BERT. *EMNLP 2019*.

[11] Schulman, J., et al. (2017). Proximal policy optimization algorithms. *arXiv:1707.06347*.
