# Chapter 6: Low-Level Design (LLD)

This chapter goes down to code-level detail for the five pieces that matter most to what this project actually contributes: the orchestrator, the evaluator, the RL/guardrail strategy layer, the FeedbackAgent, and the database schema. Every signature and every piece of logic described below was pulled straight from the current source — none of it is carried over from the Phase-2 report without being checked first.

## 6.1 Interview Orchestrator (`agents/orchestrator/interview_orchestrator.py`)

If there's one module that counts as this project's centrepiece, it's this one — at roughly 2,300 lines of Python (`wc -l`, re-counted in this correction pass; an earlier draft of this chapter had understated it as "approximately 600 lines," which is corrected here). Baseline-phase management, evaluator invocation, RL policy consultation, feedback generation, question selection, report assembly — all of it lives inside this single class, and nothing outside it is allowed to make a domain decision. That concentration of responsibility isn't free, though: a WebSocket-driven async backend can deliver duplicate or out-of-order events, the class still has to be testable in isolation without spinning up every dependent service, its session state has to stay simultaneously readable by REST endpoints with backward-compatible contracts while also being mutated by async WebSocket handlers, and termination itself has to behave safely even when disconnect and end-session signals arrive at almost the same moment. Four implementation decisions, described below, are what actually make that work:

**Concurrency safety via `asyncio.Lock`.** One orchestrator instance lives for exactly one WebSocket session, and because an async FastAPI handler is what's touching it, events can and do arrive out of order or duplicated — picture a client retransmitting a `voice_answer` after a network hiccup, which lands two evaluations of the same answer at once. Without a guard, that scenario mutates session state from two coroutines simultaneously, and the damage shows up as inconsistent scores, a wrong performance history, a difficulty trajectory that no longer makes sense. The fix is a per-instance `asyncio.Lock`, taken at the start of every public mutating method and released on the way out. Scoping it to the instance rather than the module matters: two sessions running at once in the same process never block each other, they're fully independent, while inside any one session everything is still serialised one event at a time with no cross-session cost. A thread lock was never really in the running here — FastAPI's async handlers all share one single-threaded event loop, so a thread lock would add overhead for no benefit; it wouldn't even stop interleaving within that loop.

**Dependency injection for testability.** Rather than importing the evaluator function and the question-selection function directly, the orchestrator takes both as constructor arguments — its two most complex dependencies, handed in rather than reached for. That one choice is what makes full test isolation possible: swap in a deterministic mock evaluator that always hands back a fixed score tuple, or a mock selector that always returns the same question, and nothing needs the FAISS index loaded, Sentence-BERT weights pulled in, or the Qwen microservice running. Every logical branch — baseline-phase transitions, guardrail activations, follow-up injections, session termination — ends up testable in milliseconds with zero external dependencies, which is exactly what this phase's own 25-file automated test suite (Chapter 10) leans on.

**State management and REST compatibility.** One dictionary holds all mutable session state and serves as the single source of truth for it. When a REST endpoint needs to read that state, it gets a shallow copy back through a dedicated accessor, never the dictionary itself. Things that are really just internal bookkeeping — the question queue, the current question index, attempt counts, the timer snapshot, the cached report — live as plain instance variables instead, which is why the state dictionary stays clean and serialisable while those operational details stay out of view.

**Idempotent session termination.** Calling the session-termination method the first time generates the full report, caches it, and hands it back; every call after that just returns what's already cached, no regeneration. That matters because a WebSocket disconnect and an explicit end-session message from the client have a habit of arriving almost together, especially on mobile connections, and without idempotency those two concurrent termination calls could each spin up their own report generation — producing two different reports, or a race in which one overwrites the cache the other just wrote. Pairing the lock with a cache check closes that off completely.

**Adaptive-difficulty pipeline.** There's a single private method that runs after every answer is scored and carries the whole baseline-plus-RL-plus-guardrail decision inside it. The first thing it checks is whether the current question index is still inside the baseline phase. If so, it applies the deterministic baseline logic and returns without consulting the RL policy. Otherwise it builds the six-dimensional observation vector from session state and applies the stored normalisation statistics. Next it calls the strategy layer's `suggest()` method for the raw policy action, then passes that action through the guardrail pipeline (priority order G4 → G1 → G2 → G5 → G6). The resolved action executes last, and it always updates difficulty. ("G3" does not name a separate rule; it is an alternate label the canonical module's own docstring uses for G5; see Section 6.3.) Hint and follow-up generation are a separate, independently-triggered behaviour, not an alternative outcome of this same action-resolution step. Chapter 8 draws the precise distinction between the PPO policy's three-action output and these guardrail-triggered behaviours. Keeping this pipeline centralised in one method means any change to the adaptation logic (a new guardrail, a change to the reward-relevant state, a different RL policy) only needs to happen in one place. **This method is the live orchestrator's own guardrail implementation, not a call into the canonical `rl.guardrails.apply_canonical_guardrails()` function documented in Section 6.3.** **The two have diverged.** See Section 6.3's disambiguation note and Chapter 10, Section 10.3.

**Follow-up question injection.** When the resolved action calls for a follow-up, the orchestrator sends a request to the Qwen microservice (port 8001), with the current question and the candidate's most recent answer as context. The microservice returns a contextually coherent follow-up question, which gets inserted into the question queue immediately after the current position. The client never notices the difference: the next "advance to next question" call just retrieves the next item in the queue. That item happens to be the injected follow-up, treated identically to any other question. No change to the WebSocket protocol or the frontend was needed to support this.

## 6.2 Evaluator (`services/evaluator/app.py`)

**Core function:** `evaluate(qn: str, candidate: str, rubric: dict) -> dict`

```
S1 = semantic_score(candidate_text, rubric)                      # SBERT cosine similarity
S2, concept_details = concept_detection(candidate_text, rubric)  # FAISS concept coverage
reasoning_score = cross_encoder_verification(qn, candidate_text, rubric)

effective_S2 = S2 if reasoning_score > 0.30 else S2 * 0.60        # keyword-stuffing defense

base_score = 0.15*S1 + 0.35*effective_S2 + 0.50*reasoning_score
final_score = clip(base_score + bonus - penalty, 0.0, 1.0)

if not mandatory_pass:
    final_score = min(final_score, rubric.scoring_policy.mandatory_cap)  # default 0.65
```

Grade bands run ≥0.75 Excellent, ≥0.60 Good, ≥0.40 Average, else Poor. The function returns a dictionary that includes `final_score`, `grade`, the per-component breakdown, `strong_points`/`missing_concepts` (from S2's FAISS concept-group matches), and `incorrect_claims` (substring-based misconception detection run against a per-topic trigger-phrase dictionary).

**On the evaluator's robustness mechanism, corrected.** The Phase-2 report's version of this was a "four-level fallback chain" spread across four named modules — `qwen_integration/evaluate_upgraded.py`, `Evaluator_final/Evaluator/evaluate.py`, a legacy rule-based evaluator, and a word-count heuristic. Checking the repository directly turns up none of those paths; they simply don't exist here. What actually does the job is smaller and sits entirely inside `services/evaluator/app.py` — the R-gated S2-dampening rule shown above (`effective_S2 = S2 if R > 0.30 else S2 * 0.60`), which discourages keyword-stuffed answers by cutting the weight given to concept-coverage matches whenever the CrossEncoder's reasoning score comes back low. That's correction #2 of the nine factual discrepancies catalogued in Chapter 10, Section 10.12.

**REST surface** (Flask, port 5000): `GET /health`. `POST /api/evaluator/set-question` loads a question and rubric into the current session (400 if the question ID is missing, 404 if the rubric is not found). `POST /api/evaluator/evaluate-answer` requires a prior `set-question` call (400 if no transcript or no session is loaded, 200 with the full evaluation dictionary on success). All of these contract behaviours were re-verified directly in this phase against the live Flask `test_client()` (Chapter 10, Section 10.4), not assumed from documentation.

**Production call path, clarified in this correction pass.** `docker-compose.yml` defines this Flask app as a standalone containerized service, reachable at an address set by the `PREPAIRED_EVALUATOR_URL` environment variable. Direct inspection confirms `apps/backend/main.py` never reads that variable and never makes an HTTP call to this service at all. It imports `evaluate()` and `get_rubric()` directly as Python functions and calls them in-process. So the containerized standalone service sits in the deployment configuration but is dead infrastructure as far as the actual production scoring path is concerned. The REST surface above exists and is tested, but it is not how a live interview session's answers get scored.

**FAISS index construction and query.** The FAISS flat index (`logic_vectors.faiss`) gets built offline, straight from the question-bank rubrics — every question's concept-group descriptions go through `all-MiniLM-L6-v2` encoding and into the index, with a companion metadata file (`logic_metadata.pkl`) keeping track of which vector maps back to which question ID, concept-group name, and category. A query at evaluation time pulls the top-k nearest concept-group vectors from the whole index, not just the current question's slice of it, and only afterward does a Python-side filter narrow that down to the vectors that actually belong to the current question's concept groups — the coverage fraction comes from what survives that filter. One global index rather than many small per-question ones was a deliberate call: it means one index load at startup and one query per turn, and the extra cost of filtering after the fact is small next to what the embedding step itself already costs.

## 6.3 RL / Guardrail Strategy Layer

**Class:** `agents.strategy.hybrid_orchestrator.HybridOrchestrator`

```
__init__(model_path="rl/checkpoints/seed_123/ppo_final.zip",
          vec_path="rl/checkpoints/seed_123/vecnormalize.pkl")
    -> loads and validates the PPO checkpoint (rejects it if action_space != Discrete(3)
       or observation_space != Box(6,)); sets self.ready / self.is_compatible

suggest(score, current_difficulty, session) -> (new_difficulty, reason, action_name)
    1. if baseline phase: return the fixed baseline schedule, RL not consulted
    2. build 6D observation: build_rl_observation(score, current_difficulty, session)
    3. normalize: (obs - obs_mean) / sqrt(obs_var + 1e-8), clipped to [-10, 10]
    4. if PPO ready: action_idx = model.predict(norm_obs, deterministic=True)
       else: action_idx = heuristic fallback (score >= 0.75 -> Harder,
                                               score <  0.40 -> Easier, else Same)
    5. clamp resulting difficulty to [1, 5]
```

That `deterministic=True` flag isn't a default left over from somewhere — it's doing real work. Training wants the policy sampling stochastically from its action probabilities, since that's how exploration happens, but carrying that same stochasticity into inference would mean the same candidate state could produce a different decision on different runs. Setting `deterministic=True` instead makes the policy always take the highest-probability (greedy) action, so the same input gives the same output every time, which is what a deployed system actually needs. Separately, the VecNormalize statistics (`obs_rms.mean`, `obs_rms.var`, saved in `vecnormalize.pkl`) don't apply themselves — they have to be applied by hand at inference time, because VecNormalize wraps the Gym environment during training rather than living inside the model. Skip that step and the policy network, whose weights were calibrated against normalised inputs, tends to degrade quietly — a known failure mode for deployed PPO systems generally.

**6-D observation vector** (`build_rl_observation`): `[perf, avg_perf (last-5 rolling mean), conf, hes, progress (t/T), diff_norm (diff/5)]`, each clamped to [0,1] with NaN/Inf guarded to a safe default (0.5 for confidence when unmeasured, `1 - conf` for hesitation when unmeasured).

**Canonical vs. live implementation: read before the rule list below.** This guardrail logic actually exists twice in the codebase, and the two copies disagree. One is the **canonical** module, `rl.guardrails.apply_canonical_guardrails(perf, avg_perf, conf, hes, progress, difficulty, proposed_action, consecutive_failures=0, is_infrastructure_failure=False) -> (final_action, was_overridden, guardrail_id)` — documented below, called by the RL training/simulation environment (`rl/env/interview_env.py`), and the thing this phase's own boundary tests (Chapter 10, Section 10.3) exercise directly. The other is what actually runs in **production**: `agents/orchestrator/interview_orchestrator.py::_apply_guardrails`, invoked from `_adapt_difficulty`. It isn't a call into the canonical function at all — it's a separately hand-written copy that was never kept in sync with it. Checking the two against each other in this correction pass turned up three confirmed places where they disagree:

- **G5 boundary**: canonical uses `0.30 <= perf < 0.65` (the widened, fixed boundary below); the live copy still uses the original, unfixed `0.40 < perf < 0.65`; already disclosed in Chapter 10, Section 10.3 and Chapter 11, Section 11.4.
- **G6 "gap" definition**: canonical computes `gap = perf - diff_norm` (performance relative to the *current question's difficulty*); the live copy computes `gap = perf - avg_perf` (performance relative to the candidate's *own rolling average*): a substantively different signal, not a renamed variable.
- **G6 "nervous_expert" definition**: canonical is `(0.80 < perf < 0.95 AND hes > 0.65) OR (conf < 0.40 AND hes > 0.60)`; the live copy implements only the second disjunct, so a high-performing-but-hesitant candidate (the first disjunct's case) is not protected from escalation in the live path the way the canonical module's own documented rationale (below) describes.

This report doesn't quietly fix any of those three in the live copy — they stay as open, disclosed findings instead (Chapter 10, Section 10.3; Chapter 11, Section 11.4), consistent with this project's rule against silently patching something once it's been flagged. The rule list, priority order, and rationale that follow all describe the **canonical** module:

1. **Infrastructure-failure override** → Same (always). If a turn failed for an infrastructure reason rather than a genuine answer-quality one, difficulty degradation simply doesn't apply.
2. **G4** (perf < 0.30 AND hes > 0.60) → Easier. This one goes first because a candidate who is both struggling and anxious is in the most vulnerable state the system can see, and that calls for immediate support.
3. **G1** (perf < 0.30 AND 0.4 ≤ diff_norm ≤ 0.7) → Easier. Catches a candidate who keeps underperforming at a moderate difficulty and backs off the load.
4. **G2** (conf < 0.30 AND hes > 0.70 AND perf < 0.80) → Same (or Easier if hesitation exceeds 0.85). The point of this rule is telling a nervous expert apart from someone who's genuinely struggling, so a confidence dip alone doesn't get penalised as if it were a knowledge gap.
5. **G5** (0.30 ≤ perf < 0.65 AND avg_perf < 0.60 AND consecutive_failures < 2) → Same. Mid-range performance combined with a below-average trend over the session is read as a reason to hold difficulty steady rather than push it up. **This phase widened the lower bound from 0.40 to 0.30, closing a verified coverage gap** (Chapter 10, Section 10.3) — before that fix, a candidate scoring in [0.30, 0.40) with moderate confidence/hesitation had no guardrail watching them at all, and the raw policy was free to escalate their difficulty with nothing to stop it.
6. **G6** (perf ≥ 0.90 AND gap > 0.25 AND NOT nervous_expert) → Harder. This sits last because escalating a strong candidate is the least time-sensitive of these corrections — waiting one extra turn to escalate costs less than escalating too early or missing real anxiety would. The `nervous_expert` flag (canonical definition: `(0.80 < perf < 0.95 AND hes > 0.65) OR (conf < 0.40 AND hes > 0.60)`; see this section's divergence note above) holds this escalation back for candidates whose audio signals read as anxious despite strong content — on the theory that their hesitation is about delivery nerves, not an actual knowledge gap.
7. **Else:** nothing fires, and the raw proposed action goes through unchanged.

**Table 6.1.** Guardrail rules, in evaluation priority order (verified against `rl/guardrails.py::apply_canonical_guardrails`).

| Priority | Rule | Condition | Action |
|---|---|---|---|
| 1 | Infrastructure-failure override | Turn failed for an infrastructure reason, not an answer-quality reason | Same (always) |
| 2 | G4 | perf < 0.30 AND hes > 0.60 | Easier |
| 3 | G1 | perf < 0.30 AND 0.4 <= diff_norm <= 0.7 | Easier |
| 4 | G2 | conf < 0.30 AND hes > 0.70 AND perf < 0.80 | Same (Easier if hes > 0.85) |
| 5 | G5 | 0.30 <= perf < 0.65 AND avg_perf < 0.60 AND consecutive_failures < 2 | Same |
| 6 | G6 | perf >= 0.90 AND gap > 0.25 AND NOT nervous_expert | Harder |
| 7 | Else | No rule fires | Raw proposed action stands |

## 6.4 FeedbackAgent: Fifteen-Field Structured Feedback

Every evaluated turn triggers the FeedbackAgent, and what comes out the other end is a fifteen-field feedback dictionary — readable by the session logger as data, and readable by a human in the frontend report view. Under the hood it works in four stages.

**Score decomposition and grading.** The report opens by taking the score apart: the final weighted number, the letter grade that range maps to, and the S1/S2/R components individually alongside how much each one actually contributed. A candidate looking at this can tell at a glance which dimension of their answer dragged the score down.

**Misconception detection, corrected in this correction pass.** `feedback_agent.py` has its own topic-keyed dictionary of trigger phrases mapped to corrections (`_detect_incorrect()`), plus two more helpers, `_strong_points()` and `_improvement_tips()`. Checking the file directly in this correction pass turned up something unexpected: none of those three methods is ever actually called. They're dead code, sitting there but never wired into `generate()`'s real execution path. What the live `incorrect_or_incomplete`, `strong_points`, and `missing_concepts` fields actually draw on is the evaluator's own `eval_result` output (`covered_concepts`, `missing_concepts`, `incorrect_claims`) — numbers that the evaluator's FAISS concept-matching and substring misconception detection already produced back in Section 6.2, not anything these FeedbackAgent helpers touch. The underlying technique doesn't change — it's still substring matching either way, just running inside the evaluator rather than inside `FeedbackAgent` — so the precision/recall trade-off below still applies; only the attribution changes. That makes this a dead-code finding at the FeedbackAgent level, not a finding about how misconception detection itself works, and it's logged as a newly-found limitation in Chapter 11. On the trade-off itself: substring matching over embedding-based similarity is a deliberate choice, because a correction firing only when the candidate demonstrably said something wrong is worth more here than firing whenever an answer merely resembles a known misconception. That buys precision at the cost of recall, and Chapter 11 states that trade-off as an acknowledged limitation rather than hiding it.

**Communication analysis.** Four signals feed this stage — filler-word count, hesitation rate (the audio pipeline's `hesitation_score`), how often hedging language shows up, and how long the response runs — each one checked against its own threshold to produce a targeted delivery tip. When the audio pipeline isn't available and confidence/hesitation fall back to a neutral 0.5, `communication_tips` comes back as an empty list rather than a guess dressed up as an assessment. That's the right call: saying nothing about delivery beats reporting delivery metrics that were never actually measured.

**Content analysis and trend tracking.** Four fields make up the content side — `strong_points`, `missing_concepts`, `incorrect_or_incomplete`, and `vague_points` (things the candidate gestured at without developing enough to count as covered) — which together read as a revision checklist tied directly to the rubric that produced the score. Trend tracking runs alongside this: the current turn's score gets compared against the rolling mean of the last three, and a swing of ±0.08 or more is reported as "Improving" or "Declining," while anything smaller stays "Stable." That threshold exists specifically so ordinary score noise doesn't get reported as a trend that isn't really there.

**Table 6.2.** FeedbackAgent structured-feedback output fields (representative, verified against `agents/orchestrator/feedback_agent.py`).

| Field | Description |
|---|---|
| `final_score`, `grade` | Final weighted score and its letter-grade band |
| `score_breakdown` | Per-component S1/S2/R values and confidence signal |
| `strong_points` / `what_was_correct` | Concepts the candidate covered correctly |
| `what_was_incorrect` | Misconception-flagged claims |
| `missing_concepts` / `what_was_incomplete` | Concepts not covered |
| `vague_points` | Ideas mentioned but not developed precisely enough to count as covered |
| `communication_tips` | Delivery feedback; standardised empty list if the audio pipeline is unavailable |
| `trend`, `trend_note` | Improving / Declining / Stable, vs. the rolling mean of the last three turns |
| `how_to_answer`, `stronger_answer_guide`, `actionable_improvements` | Qwen-generated (or template-fallback) improvement guidance |
| `narrative_feedback` / `justification` | Free-text explanation of the score |
| `decision_source`, `llm_status` | Provenance flags distinguishing a genuine Qwen response from the deterministic fallback |

## 6.5 Database Schema: `data/prepaired.db` (SQLite, verified directly in this phase)

```
candidates(id PK, ...)
sessions(id TEXT PK, candidate_id TEXT NOT NULL REFERENCES candidates(id),
         interview_mode, c_topics, dsa_topics, duration_minutes, num_questions,
         start_difficulty, status, overall_score REAL, created_at NOT NULL, completed_at)
question_attempts(id PK, candidate_id, session_id REFERENCES sessions(id), question_id,
                  question_version, attempt_number, session_attempt_number, attempt_type,
                  parent_question_id, answer_type, transcript, code_submitted,
                  raw_score, validated_score, is_best, covered_concepts, missing_concepts,
                  incorrect_claims, weakest_gap, strong_points, evaluation_confidence,
                  feedback_json, created_at)
```

This phase checked relational integrity directly against the real, populated database (26 sessions, 52 question_attempts) — `question_attempts.session_id → sessions.id` and `sessions.candidate_id → candidates.id` — and came back with zero orphaned rows (Chapter 10, Section 10.5).

## 6.6 Question Selector: corrected attribution, this correction pass

**There are actually two question-selector implementations, and an earlier version of this section pointed at the wrong one as "the" production design.** `agents/question_selector/question_selector.py` says as much in its own module docstring — it labels itself a "BASELINE / RESEARCH" artifact, explicitly superseded by `apps.backend.main.select_questions`, which that same docstring calls the "Authoritative Production Selector." The live interview flow runs the latter. Both are worth documenting, so both appear below.

**Production selector: `apps.backend.main.select_questions(c_topics, dsa_topics, num, difficulty, exclude_ids, candidate_state)`.** Nothing random happens here — direct inspection in this correction pass confirms there's **no `random` call of any kind** in this function. It runs three layers of deduplication (seen question IDs, a normalised exact-text match, and a ≥0.75 Jaccard token-overlap check against everything already asked this session), on top of a topic-diversity penalty that grows the more a topic gets reused and a personalisation adjustment that nudges weak topics toward easier questions and strong ones toward harder questions. Every remaining candidate gets scored on a weighted penalty combining difficulty distance, diversity penalty, and the personalisation term, and whichever one scores lowest in a first-minimum-found scan is what gets asked next.

**Baseline/research artifact: `agents/question_selector/question_selector.py`.**

```
AVAILABLE_DIFFICULTIES = sorted distinct difficulty values in the question bank
nearest_difficulty(target) -> closest value in AVAILABLE_DIFFICULTIES

select_next_question(difficulty):
    1. target = nearest_difficulty(difficulty)
    2. candidates = questions at that exact difficulty
    3. valid_topics = topics not yet at the per-session TOPIC_LIMIT and
                       not equal to the immediately previous turn's topic
    4. topic = least-asked among valid_topics (random.choice tie-break)
    5. question = random.choice among not-yet-asked questions in that topic+difficulty
```

This one, unlike the production function, really does call `random.choice(...)` twice — once for the topic tie-break, once for the final question choice — so calling it deterministic would be wrong. Wherever this report says "the" question selector is deterministic without further qualification, it means the production function above, not this baseline module. Either way, neither implementation runs an embedding computation, a vector index query, or a ranking step of any kind, which corrects the Phase-2 report's FAISS-retrieval claim no matter which selector it originally had in mind. When this phase's correctness testing (Chapter 10, Section 10.8) simulated a full 15-question session against this baseline module specifically, all 15 selections came back distinct, topic rotation was perfect with no two consecutive turns sharing a topic, and every difficulty-matching query it ran returned a value that genuinely exists in the question bank. The result itself still holds — it's just now correctly attributed to the baseline artifact rather than to the production selector.
