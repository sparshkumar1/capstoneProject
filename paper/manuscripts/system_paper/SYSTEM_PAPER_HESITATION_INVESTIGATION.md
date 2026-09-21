# Hesitation discrepancy — where each value comes from (2026-09-21)

**Nothing was changed.** Read-only investigation of the code, the tests, the audit documents and git history. No code was run.

## The question
Audit documents say the runtime hesitation input is `session["last_hesitation_score"]` (an acoustic value). Production PPO/guardrail code appears to use `1 − confidence`. Which is it, and why?

## What produces each "hesitation" number at runtime
| # | Quantity | Where it originates | Where it goes |
|---|---|---|---|
| 1 | **Acoustic hesitation score** (a six-term blend: pause ratio 0.30, pause frequency 0.20, long pauses 0.15, filler density 0.20, jitter 0.10, speaking-rate deviation 0.05) | `agents/audio/hesitation_scorer.py:17-66`, called from `apps/backend/main.py:650` and returned in the analysis dict at `:691` | `FeedbackAgent` reads `audio_result["hesitation"]["hesitation_score"]` for communication tips (`agents/orchestrator/feedback_agent.py:114-115`, tip at `:485`). **It is not written into the orchestrator state used for adaptation** |
| 2 | **PPO observation dimension 3** | `build_rl_observation` (`agents/strategy/hybrid_orchestrator.py:108-114`): reads `session["last_hesitation_score"]`, else `session["last_hesitation"]`, else **`1 − conf`** | PPO input |
| 3 | **Guardrail `hes`** | `interview_orchestrator.py:1678-1679`: `conf = last_confidence_score`, **`hes = max(0, 1 − conf)`** — computed directly, never reading `last_hesitation_score` | guardrails G4 (`perf<0.30 & hes>0.60`), G2 (`conf<0.30 & hes>0.70 & perf<0.80`), and the nervous-expert rule |
| 4 | **Report "hesitation_rate"** | `interview_orchestrator.py:2185, 2237`: 0.6 is appended when a feedback tip mentions more than three fillers; otherwise the value defaults to **0.15** | the end-of-session report (`"behaviour"` block, `:2293`) |

## Where `last_hesitation_score` is written
Search of every `*.py` file in the repository (excluding dependencies): the key appears in `agents/strategy/hybrid_orchestrator.py` (the reader), in tests (`tests/unit/test_rl_env.py`, `test_stage11_5_coding_adaptation.py`, `test_stage11_6_full_interview_e2e.py`), in verification scripts (`scripts/verify_stage11_*`), and in experiment/simulation runners (`experiments/experiment_1_adaptive_difficulty/runner.py:121`, `experiment_5_ablation/runner.py:108-111`, `research/scripts/run_rl_experiments.py:111`), where it is assigned from simulated candidates' hesitation. **No file under `agents/`, `apps/backend/` or `services/` assigns it.** `ingest_audio_analysis` (`interview_orchestrator.py:270`) and the backend fallback (`main.py:929-937`) copy only `confidence_score`. The communication-indicators block (`:2032-2039`) stores confidence, speaking rate, pause count and pause time, not a hesitation score.

So in production the key is never set, and both the observation and the guardrails use `1 − confidence`.

## The other side of the ledger
- The training simulator generates hesitation as **`clip(1 − conf + N(0, 0.08))`**, with persona-specific floors that decouple the two for some personas (`rl/training/simulated_candidate.py:53-89`). The PPO was therefore trained on states in which hesitation is mostly a noisy complement of confidence, so the runtime proxy is in-distribution with respect to that structure. A measured acoustic hesitation would not be guaranteed to be.
- The reader code documents the fallback explicitly (comment "Hesitation Signal", `hybrid_orchestrator.py:108-114`; docstring line 16 "Measured or estimated"), and `research/audit/rl_state_definition.md:57` says the value "defaults to 1.0 − conf if unvoiced data is unavailable".
- The stored probe sweep of the evaluated seed-123 checkpoint (`P0_P1_DECISION_PLAN.md` P1-6; P3 §9.7) shows that confidence, hesitation, performance and progress probes at a neutral state always gave "Same", and only average performance and difficulty changed the action (8 of 66 probes non-Same). For that checkpoint the audio dimensions barely move PPO; their influence at runtime is mainly through the guardrails.
- Confidence and hesitation share input features (pauses, speaking rate, jitter/voice measures), so a correlation is expected, but confidence also contains a linguistic-content term (0.27) and shimmer/HNR terms that hesitation does not, so `1 − conf` is **not** equivalent to the hesitation score. The size of the difference is unknown: no recorded audio sessions with both values exist in the repository, and none was analysed.

## Documentation that disagrees with the code
| Document (frozen audit files; not edited) | Statement | Code reality |
|---|---|---|
| `research/audit/rl_state_definition.md:49-57` | hesitation = pause ratio × 1.5 from Parselmouth silence segmentation, "stored in `session["last_hesitation_score"]`" | the scorer is the six-term blend above, uses WhisperX pause data, fillers and jitter, and its output is not stored under that key |
| `research/audit/rl_state_definition.md:37-45` | `conf = max(0.10, 1 − 0.15·filler_count − 0.10·disfluency_ratio)` | `confidence_scorer.py:67-82` is a weighted blend of voice quality (0.28), linguistic score (0.27), fluency (0.22), rate (0.13), rhythm (0.10), with an ASR-confidence adjustment; **the documented formula is not the implemented one** |
| `research/audit/speech_ethics.md:26-27` | guardrail G2 uses "acoustic hesitation (`hesitation > 0.70`)" | G2 uses `1 − conf` |
| `docs/FINAL_PRODUCTION_CALL_GRAPH.md:90` | hesitation score feeds `InterviewOrchestrator` | it reaches `FeedbackAgent`, not the adaptation state |

## Verdict
The evidence does not support a single label. Established:
- **A. Intentional proxy — supported for the code's fallback**: the substitution is written out explicitly in two places, is described as a default in an audit document, and matches how the training simulator generated the state.
- **B. Implementation gap — supported for the missing writer**: the reader accepts a measured value, tests inject one directly, but nothing in production ever supplies it, so the fallback is *always* taken. Tests that set the key therefore give no assurance that the live path is wired.
- **C. Stale or inaccurate documentation — supported**: three audit/design documents describe an acoustic hesitation input and a confidence formula that the code does not implement.
- **D. Another explanation — partly**: the guardrail call bypasses the key altogether (`hes = 1 − conf`), so wiring the key alone would fix the PPO observation but not the guardrails.

What cannot be established from the repository: **whether omitting the writer was a deliberate scope decision or an oversight.** Git history does not show it: the key first appears in the squashed snapshot commit `ea15e3c` ("Release PrepAIred research artifact and reproducibility package") and the `1 − conf` guardrail line and `ingest_audio_analysis` first appear in `4e320d6` ("chore: sync cleaned workspace snapshot"). **The author must say which it was.**

## Consequences
- Any statement that the system adapts to acoustic hesitation is currently **false as written**; it adapts to `1 − confidence`. This affects `speech_ethics.md`, the call graph, the state definition, and any system-paper sentence about "speech-aware" or "multimodal" adaptation.
- P1 and P3 are not contradicted: P3 does not claim runtime acoustic hesitation and already states a runtime state-definition mismatch; P1 does not touch it. (One P3 sentence was checked while investigating: "the demonstration policy deployed in the application is a different checkpoint from the evaluated seed-123 checkpoint" is correct: deployed `2ab8d514…` versus evaluated `299437ea…`, as `P0_P1_DECISION_PLAN.md` P1-7 records.)
- For a human study the report's "hesitation_rate" (item 4) must not be presented as a measurement.

## Options for the author (no change was made)
1. **Keep the proxy and document it** (no behavioural change; the honest minimum). All papers say: confidence is acoustic + linguistic and hesitation is its complement.
2. **Log both values every turn without changing behaviour**, so a paper can report their empirical relationship and the study can show how often the two disagree. Low risk; still a code change and needs approval.
3. **Wire the measured hesitation into the state and guardrails.** This changes an input the frozen checkpoints were not trained on, creates a new runtime/training mismatch and needs a new registered evaluation. Not recommended for the first study.
