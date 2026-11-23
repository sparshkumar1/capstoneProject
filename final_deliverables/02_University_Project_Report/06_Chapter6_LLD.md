# Chapter 6: Low-Level Design (LLD)

This chapter documents verified, code-level design detail for the three components most central to this project's technical contribution: the evaluator, the RL/guardrail strategy layer, and the database schema. All signatures and logic below were read directly from the current source in this phase, not reproduced from the Phase-2 report without verification.

## 6.1 Evaluator — `services/evaluator/app.py`

**Core function:** `evaluate(qn: str, candidate: str, rubric: dict) -> dict`

```
S1 = semantic_score(candidate_text, rubric)              # SBERT cosine similarity
S2, concept_details = concept_detection(candidate_text, rubric)   # FAISS concept coverage
reasoning_score = cross_encoder_verification(qn, candidate_text, rubric)

effective_S2 = S2 if reasoning_score > 0.30 else S2 * 0.60   # keyword-stuffing defense

base_score = 0.15*S1 + 0.35*effective_S2 + 0.50*reasoning_score
final_score = clip(base_score + bonus - penalty, 0.0, 1.0)

if not mandatory_pass:
    final_score = min(final_score, rubric.scoring_policy.mandatory_cap)  # default 0.60
```

Grade bands: ≥0.75 Excellent, ≥0.60 Good, ≥0.40 Average, else Poor. Returns a dict including `final_score`, `grade`, per-component breakdown, `strong_points`/`missing_concepts` (from S2's FAISS concept-group matches), and `incorrect_claims` (substring-based misconception detection against a per-topic trigger-phrase dictionary).

**REST surface** (Flask, port 5000): `GET /health`; `POST /api/evaluator/set-question` (loads a question+rubric into `current_session`, 400 if `qid` missing, 404 if rubric not found); `POST /api/evaluator/evaluate-answer` (requires a prior `set-question` call, 400 if no transcript or no session loaded, 200 with the full evaluation dict on success). All 7 of these contract behaviours were directly re-verified in this phase against the live Flask `test_client()` (Ch.10 §10.4), not assumed from documentation.

## 6.2 RL / Guardrail Strategy Layer

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

**6-D observation vector** (`build_rl_observation`): `[perf, avg_perf (last-5 rolling mean), conf, hes, progress (t/T), diff_norm (diff/5)]`, each clamped to [0,1] with NaN/Inf guarded to a safe default (0.5 for confidence when unmeasured, `1 - conf` for hesitation when unmeasured).

**Guardrail function:** `rl.guardrails.apply_canonical_guardrails(perf, avg_perf, conf, hes, progress, difficulty, proposed_action, consecutive_failures=0, is_infrastructure_failure=False) -> (final_action, was_overridden, guardrail_id)`, evaluated in strict priority order:

1. Infrastructure-failure override → Same (always)
2. **G4** (perf < 0.30 AND hes > 0.60) → Easier
3. **G1** (perf < 0.30 AND 0.4 ≤ diff_norm ≤ 0.7) → Easier
4. **G2** (conf < 0.30 AND hes > 0.70 AND perf < 0.80) → Same
5. **G5** (0.30 ≤ perf < 0.65 AND avg_perf < 0.60 AND consec_failures < 2) → Same — **lower bound widened from the original 0.40 to 0.30 in this phase, closing a verified coverage gap (Ch.10 §10.3)**
6. **G6** (perf ≥ 0.90 AND gap > 0.25 AND not nervous_expert) → Harder
7. else: the raw proposed action stands

## 6.3 Database Schema — `data/prepaired.db` (SQLite, verified directly in this phase)

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

Relational integrity (`question_attempts.session_id → sessions.id`, `sessions.candidate_id → candidates.id`) was verified to hold with zero orphaned rows against the real, populated database (26 sessions, 52 question_attempts) in this phase (Ch.10 §10.5).

## 6.4 Question Selector — `agents/question_selector/question_selector.py` (corrected design)

```
AVAILABLE_DIFFICULTIES = sorted distinct difficulty values in the question bank
nearest_difficulty(target) -> closest value in AVAILABLE_DIFFICULTIES

select_next_question(difficulty):
    1. target = nearest_difficulty(difficulty)
    2. candidates = questions at that exact difficulty
    3. valid_topics = topics not yet at the per-session TOPIC_LIMIT and
                       not equal to the immediately previous turn's topic
    4. topic = least-asked among valid_topics (random tie-break)
    5. question = random choice among not-yet-asked questions in that topic+difficulty
```

No embedding computation, no vector index query, and no ranking step exist in this function — it is a deterministic filter-and-rotate algorithm, not the FAISS-retrieval design the Phase-2 report's architecture diagrams depicted.
