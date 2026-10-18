# PrepAIred: Research-Backed Application Enhancement Strategy

**Status:** research and planning only. No source file was modified, no dependency installed, no model trained, no service started, no test run.
**Audit date:** 14 October 2026. **Audited branch:** `workspace/human-eval-clean-push` (HEAD `188b24d`). **Also inspected read-only (via `git show`/`git ls-tree`):** `origin/paper/adcom2027-v13` (commit `0ec7f1f`, 2026-10-03), which holds the multi-agent layer described in the ADCOM paper.

Evidence labels used throughout:
- **[V]** verified by reading code or data in this repository.
- **[P]** published evidence (source in section 10).
- **[I]** my design inference. It is not evidence that the idea works in PrepAIred.
- **L1 / L2 / L3** follow the prompt: L1 research-supported principle, L2 PrepAIred-specific gap found in the repo or paper, L3 unvalidated hypothesis.

---

## 1. Executive summary

PrepAIred is a working end-to-end system: spoken or coded answers, a hybrid evaluator, Qwen follow-ups and feedback, a PPO difficulty controller with guardrails, SQLite persistence, and a React interface. Its weak points are not missing features. They are (a) how far the scoring can be trusted, (b) the fact that it forgets the learner between sessions, and (c) a few security and data-handling gaps that matter as soon as more than one person uses it.

**The five strongest recommendations**

1. **Score Trust Check** (evaluator robustness suite + a real uncertainty flag + a visible evidence trace). The composite scores *below* R-only on the human benchmark, `evaluation_confidence` is a near-constant formula, and nothing tests length or padding robustness. This is the highest-value and lowest-risk work. *Priority A.*
2. **My Weakness Map** (a persistent concept-level learner profile built from data already stored in `question_attempts`). Today weaknesses are tracked per session by topic only. *Priority A for the read-only profile, B for letting it steer question selection.*
3. **Account & Data Safety** (fix client-controlled admin, unauthenticated history/admin endpoints, retention and deletion). These are verified gaps, not hypotheses. *Priority A, required before any multi-user use.*
4. **Probe-with-Purpose follow-ups** (rule-based validation that each follow-up targets a rubric-missing concept, is not a repeat, and stops when evidence is sufficient). *Priority A for rules, B for semantic checks.*
5. **Smart Revision** (spaced re-testing of previously missed concepts). Strong general evidence, but it depends on item 2 and must be validated with real learners. *Priority B.*

**The three improvements to prioritize first:** items 1, 3 and 2 (in that order of urgency: safety is a gate, the trust check protects every later feature, the weakness map is the main user-visible gain).

**Single biggest technical risk:** *unvalidated scoring drives everything downstream.* The evaluator's score decides difficulty changes, follow-ups, feedback and the report, yet on the 64-answer benchmark the full composite (ρ = 0.3812) is below R-only (0.4832), the confidence field is not an uncertainty estimate, and ASR errors flow into scoring unchecked [V].

**Single most promising research direction:** *length-controlled, adversarially robust evaluator validation* on an independently rated, length-balanced item set, with an honest comparison against word-count and LLM-judge baselines. It addresses the largest weakness, is feasible with the existing question bank and rubrics, and is publishable whichever way it comes out.

**Can be done without changing the architecture:** the robustness test suite, evidence-trace UI, uncertainty flag, weakness-map profile (derived read-only from existing tables), revision queue (one new table), follow-up validators, auth and data-lifecycle fixes, question-bank coverage audit, decision-trace logging.

**Needs more evidence before implementation:** letting a learner model steer question selection; replacing or demoting PPO; NLI/embedding grounding of feedback; calibrated confidence from labeled data; any change to how voice-derived signals enter the RL state or guardrails; resume/JD and system-design modes.

---

## 2. Current application audit

### 2.1 Scope note: two code states exist

| State | Where | What it contains |
|---|---|---|
| Working branch | `workspace/human-eval-clean-push` | Interview app, evaluator, Qwen service, PPO integration, tests. **No Strategy Agent / Coaching Agent / coordinator / arbitration code.** In this branch "Strategy Agent" in `docs/diagrams/corrected_architecture.md` means the PPO policy, and "Feedback Agent" means the Qwen wrapper. [V] |
| Paper branch | `origin/paper/adcom2027-v13` | `agents/multiagent/` (11 modules, about 1,360 lines: `arbitration.py`, `authority.py`, `contracts.py`, `coordinator.py`, `strategy_agent.py`, `coaching_agent.py`, `grounding.py`, `runtime.py`, `unified_agent.py`, ...), `research/multiagent/experiments/xa_compare.py … xe_historical.py`, protocols, configs and results. The orchestrator on that branch has +122/−13 lines of integration. [V] |

So the multi-agent layer exists and is reproducible from that branch, but it is **not in the working tree**. Anything below that depends on it (for example "typed proposals") is stated as such.

### 2.2 End-to-end journey, as implemented on the working branch [V]

1. Login: `POST /api/login` (`apps/backend/main.py:717`) creates or fetches a candidate row.
2. Session: `POST /api/sessions` (`main.py:753`) selects questions (three-level de-duplication, `main.py:~461–570`) and opens a WebSocket `/ws/interview/{session_id}` (`main.py:1064`).
3. Answer: audio goes through `POST /api/transcribe` (`main.py:878`) to WhisperX (`agents/audio/transcriber.py`, model `base`, int8 on CPU) plus prosody features (`agents/audio/*`).
4. Evaluation: `InterviewOrchestrator.handle_voice_answer` (`interview_orchestrator.py:301`) calls the evaluator (`services/evaluator/app.py: evaluate()`, line 350), then `ScoreValidator` (`agents/validation/score_validator.py`) fails closed on invalid scores.
5. Adaptation: `_adapt_difficulty` (`interview_orchestrator.py:1576`) runs a baseline phase, then PPO (`agents/strategy/hybrid_orchestrator.py`), then `_apply_guardrails` (line 1529; rules in `rl/guardrails.py`). A non-RL heuristic is used if PPO is unavailable.
6. Follow-up: `_decide_and_inject_followup` (line 1720) triggers when a concept is missing or incorrect, a gap is flagged, or score < 0.80, and never after two consecutive follow-ups. `_inject_followup_question` (line 1753) calls the Qwen service, falling back to a local template synthesizer.
7. Feedback: `agents/orchestrator/feedback_agent.py` (Qwen2.5-1.5B GGUF Q4 on CPU via `services/qwen/app.py`) with an evidence-preserving fallback.
8. Persistence and report: `services/storage/database.py` (tables `candidates`, `sessions`, `question_attempts`), `_generate_report` (line 2099), `/api/sessions/{id}/report`, React `Report.jsx`.

### 2.3 Current Capability / Gap Matrix

| Area | Current implementation | Verified limitation | Opportunity |
|---|---|---|---|
| **Scoring** | `evaluate()` in `services/evaluator/app.py:350`: 0.15·S1 + 0.35·S2_eff + 0.50·R + bonus − penalty, mandatory cap, S2 dampened ×0.6 when R ≤ 0.30. Rubrics carry mandatory concepts, concept groups, advanced bonus items, common mistakes. | Full composite ρ = 0.3812 vs R-only 0.4832 on 64 answers (`research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` C.2). Case-level CI treats 64 answers as independent; effective topical sample is 8 questions. The manuscript also reports a strong R–length association (figure not independently re-verified here). No automated length/padding/paraphrase test exists in `tests/`. [V] | Robustness suite; length-controlled validation; evidence trace. |
| **Uncertainty** | `evaluation_confidence = round(0.85 + 0.10·(1.0 if ≥2 sentences else 0.5), 3)` (`app.py`, end of `evaluate()`), i.e. only 0.90 or 0.95. [V] | It is not an uncertainty estimate and cannot flag unreliable scores. ASR confidence exists (`transcription_confidence`) but only gates "STT unavailable" in the orchestrator; it does not reduce trust in the score. [V] | Real abstain/low-evidence flag. |
| **"Communication" and "depth"** | `communication` = filler-word count heuristic; `depth` = sentence count + S2 (`app.py`). [V] | Crude proxies shown to users as quality dimensions. | Label as heuristics or remove from user-facing claims. |
| **Speech** | WhisperX `base`, int8 CPU (`transcriber.py:143–155`). Voice "confidence" is a weighted sum of jitter, shimmer, HNR, pitch, pauses, rate, ASR confidence (`agents/audio/confidence_scorer.py`). | That voice-derived "confidence" feeds the PPO state (`hybrid_orchestrator.py: build_rl_observation`) and guardrail G2 (conf < 0.30 ∧ hes > 0.70). If absent, confidence silently defaults to the *performance score*. No validation against any ground truth. [V] | Make voice signals advisory, not decisional, until validated. |
| **Adaptive difficulty** | PPO (6-D state, 3 actions) behind guardrails; baseline warm-up of easy→mid questions. | Paper 3 (simulation only): heuristic MAE 0.473 beat every PPO variant (0.673–0.804); constant "Same" + guardrails equals PPO + guardrails (0.673). Deployed checkpoint (`2ab8d514…`) differs from the evaluated one (`299437ea…`). [V: canonical file] | Add non-RL baselines and shadow-mode comparison. |
| **Learner model** | Session-local `weaknesses` topic list (`interview_orchestrator.py:1932`); global score drives difficulty. `question_attempts` already stores `covered_concepts`, `missing_concepts`, `incorrect_claims`, `weakest_gap`, `evaluation_confidence`. [V] | Nothing aggregates this across sessions. Backend exposes `/api/history/...` (`main.py:805–836`) but the frontend `api.js` never calls it. | Concept-level profile and revision queue. |
| **Question bank** | `data/questions/qns.json`: 125 questions, 37 topics, difficulty 0.2–0.9, types theory 90 / evaluate 15 / general_tech 10 / code 10. All 125 have rubrics. [V] | 19 topics have exactly one question; only 7 topics have ≥ 5. Only 3 questions at difficulty 0.9 and 4 at 0.2. Topic-level mastery estimates would be extremely sparse. | Use rubric **concept groups** as the learning unit, not topics; coverage audit. |
| **Asset consistency** | Evaluator service loads its own `services/evaluator/assets/qns.json` and `rubrics.json`. | **Those have 100 entries; the backend bank has 125.** The 25 missing IDs are 101–115 (the `evaluate`-type questions) and C01–C10 (code). `get_rubric()` returns `None` for them. Whether the runtime path hits this for verbal questions is **not verified** (needs a targeted test). [V: mismatch; U: impact] | Single source of truth + a startup consistency check. |
| **Follow-ups** | Qwen 1.5B (GGUF) prompt includes eval result, previous questions and follow-ups; template fallback. | No check that the follow-up actually targets a rubric concept; no stop rule beyond "two in a row"; no contradiction check against earlier turns. [V] | Rule-based validator, then semantic check. |
| **Reports / UI** | Per-session report with C vs DSA split and trend badges; the live UI shows a one-line reason for difficulty changes (`InterviewRoom.jsx:112–124`). | No cross-session view, no concept-level progress, no explanation of *why this question* beyond difficulty. | Weakness Map, session-over-session comparison. |
| **Security / privacy** | CORS limited to localhost origins. | **`admin` is a client-supplied boolean** in `LoginRequest` and `adminPass` is collected by `Login.jsx` but never checked (`main.py:280–289, 717–750`). `/api/admin/*` and `/api/history/{candidate_id}` take no authentication. Transcripts are stored in SQLite with no retention or deletion path. [V] | Auth, per-user authorization, retention/delete. |
| **Tests / CI** | 264 test functions under `tests/`; CI runs `pytest -q` on Python 3.12 (`.github/workflows/ci.yml`). | One known failing test (`test_stage11_5_coding_adaptation…`, tracked in `docs/PROJECT_STATE.md`); `.venv` violates three requirement pins (numpy, torch, accelerate). No property-based or mutation tests; W&B installed but unused. [V] | Property-based invariants; environment reconciliation. |
| **Observability** | Turn logger (`agents/orchestrator/logger.py`); `decision_source`, `rl_status`, `guardrail_applied` stored in session state. | No replayable per-turn decision trace in the UI or an exportable format. | Decision-trace export. |
| **Latency** | Evaluator median 404.6 ms, P95 2.1 s, P99 26.4 s (cold start); Qwen 1.5B on CPU (`research/CANONICAL…` E). | Tail latency dominated by cold start; 180 s evaluator timeout in `_evaluate_verbal`. | Warm-up, readiness probe. |

### 2.4 Technical debt worth naming
- `agents/orchestrator/interview_orchestrator.py` is 2,299 lines with session state in an untyped dict; this makes new features risky and is the main argument *against* adding more state fields casually. [V]
- `agents/question_selector/question_selector.py` (362 lines) appears to be a legacy selector; the documented authoritative selector lives in `apps/backend/main.py` (`select_questions`). [V: docs/PERSONALIZATION.md; I: legacy status]
- Hard-coded values: 0.80/0.85 follow-up thresholds, baseline phase sizes, 180 s evaluator timeout, filler-word list. [V]
- Duplicate question/rubric files (see asset consistency row).

---

## 3. Research landscape

Only the claims each source actually supports are listed. Full references are in section 10.

### 3.1 Adaptive learning and learner modeling
- **Knowledge tracing.** Bayesian Knowledge Tracing models per-skill mastery from correct/incorrect sequences (Corbett & Anderson, 1994/95) [P]. Deep Knowledge Tracing used recurrent networks and reported gains over BKT (Piech et al., 2015) [P]. A later comparison across nine datasets found logistic-regression-style models with good features competitive on moderate-size data, with deep models winning mainly on large datasets or where timing matters (Gervet et al., 2020) [P]. *Implication [I]:* PrepAIred has tiny data (2 candidates, 22 sessions, 49 attempts in the repo database), so a simple, interpretable model is the right starting point.
- **Elo-style learner/item ratings.** Pelánek (2016) argues Elo is simple, robust and effective for adaptive educational systems, with guidelines for use [P].
- **Bandit and RL sequencing.** Multi-armed bandits for activity selection have been tested with simulated students and a 400-child user study (Clement et al., 2015) [P]; Doroudi et al. (2019) review RL for instructional sequencing [P]; Narvekar et al. (2020) survey curriculum learning for RL [P]. These are *not* evidence that PPO helps interview candidates.
- **Spaced and retrieval practice.** Testing improved delayed retention versus restudy (Roediger & Karpicke, 2006); the optimal gap between sessions grows with the desired retention interval (Cepeda et al., 2006) [P]. These are laboratory memory results on prose and verbal recall; transfer to technical-concept recall is plausible [I] but untested here.

### 3.2 Technical-answer evaluation
- **ASAG background.** Burrows, Gurevych & Stein (2015) survey the field (80+ papers) [P].
- **Gaming and adversarial input.** Content scorers are vulnerable: shuffled-word answers were accepted up to 60% of the time by a state-of-the-art scorer, and adversarial training helps but does not solve it (Ding et al., 2020) [P].
- **Length bias in automatic evaluators.** Auto-annotators favor longer outputs; a regression-based length control improved robustness to verbosity manipulation (Dubois et al., 2024, preprint; COLM acceptance not confirmed by me) [P]. Length correlations are a major factor in RLHF reward gains (Singhal et al., 2023) [P]. LLM judges show position, verbosity and self-enhancement bias (Zheng et al., 2023) [P].
- **Rubric + reference evaluators.** Prometheus (Kim et al., 2024) trains an open evaluator that scores against a user-supplied rubric and reference answer; its reported human correlation is on its own hand-crafted rubric set and says nothing about technical interviews [P].
- **Uncertainty.** Modern networks are often miscalibrated and temperature scaling is a simple fix (Guo et al., 2017); conformal prediction gives distribution-free prediction sets with coverage guarantees (Angelopoulos & Bates, 2023) [P]. Both need labeled data PrepAIred does not yet have.
- **Grounding.** NLI-based consistency checking works best when applied at sentence granularity and aggregated (Laban et al., 2022, SummaC); FActScore decomposes text into atomic facts and checks support (Min et al., 2023) [P]. Both are for summaries or biographies, not interview feedback.

### 3.3 Speech and spoken interviews
- ASR error rates differ by speaker group: five commercial systems averaged WER 0.35 for Black versus 0.19 for white speakers (Koenecke et al., 2020) [P]. Whisper is trained on 680,000 hours of weakly supervised data (Radford et al., 2023) [P]; about 1% of transcriptions in one 2023 audit contained hallucinated phrases, and the vendor model has since changed (Koenecke et al., 2024) [P].
- Inferring internal states from expressive behavior is scientifically contested. Barrett et al. (2019) make this case for facial movements and emotion [P]; extending the caution to *voice-derived confidence* is my analogy [I], not a finding about voice.
- *Implication [I]:* technical content scoring should be separated from delivery signals, ASR uncertainty should be surfaced, and no psychological or employability claim should be made from voice.

### 3.4 Interviewer behavior and follow-ups
I found no strong, citable evaluation of follow-up question generation specific to technical interviews. The documented prototypes already cited in the ADCOM paper (Gomez et al., 2025; Vaishampayan & Brown, 2025; Yazdani et al., 2025) report perception or case-study evidence, not follow-up quality [P: abstracts only]. Design ideas in section 6 are therefore **L2/L3**, supported by the grounding literature above only indirectly.

### 3.5 Agent orchestration and reliability
- Multi-agent configurations are task-dependent and not universally superior (Kim et al., 2026); failure taxonomies for multi-agent LLM systems identify specification, alignment and verification problems (Cemri et al., 2025) [P].
- Testing methods: property-based testing (Claessen & Hughes, 2000; Hypothesis, MacIver et al., 2019) and mutation testing (Jia & Harman, 2011) [P].
- PrepAIred's own evidence [V]: on the paper branch, replay found that coordination changed trajectories while a unified re-implementation of the same rules matched 1,280/1,280 decisions, and lexical grounding accepted unsupported paraphrase in 57/57 probes. This supports *keeping the smallest architecture that works*, not adding agents.

### 3.6 UX and learning analytics
Bodily & Verbert (2017) reviewed 93 studies of student-facing dashboards and call for more experiments on effects on behavior and achievement, because the existing evidence base is small [P]. *Implication [I]:* build a few actionable views (what to practice next, what changed) rather than decorative score rings.

### 3.7 Public product landscape (documented capabilities only)
| Product | Publicly documented capability | Source |
|---|---|---|
| interviewing.io | Anonymous mock interviews with senior engineers; a free-to-try AI interviewer with end-of-session feedback; practice problems. | Its blog and site (section 10). |
| Pramp (Exponent) | Free peer-to-peer live mock interviews with a shared code editor, matched by availability and language; each user acts as both interviewee and interviewer. | Pramp FAQ and site. |
| LeetCode, HackerRank | Large coding-problem libraries; LeetCode describes timed mock interviews. I could not retrieve official documentation for either, so I make **no** feature claims beyond problem practice. | Not verified. |

**Reading of the gap [I]:** documented competitors emphasize live human practice or coding problems. PrepAIred's distinctive position is *spoken, rubric-grounded conceptual practice with a concept-level memory of the learner*, but that is a hypothesis about positioning, not a claim of being first or better.

---

## 4. Opportunity map

| Group | Opportunities | Evidence level |
|---|---|---|
| **Evaluation** | Robustness suite (length, padding, keyword stuffing, paraphrase, correct-short vs wrong-long); evidence trace; real uncertainty/insufficient-evidence flag; independent rating set | L1 + L2 |
| **Personalization** | Concept-level learner profile; mastery with uncertainty; revision queue; diagnostic opening; user-set goals | L1 + L2 (adaptive steering L3) |
| **Speech** | ASR confidence into the scoring trust flag; domain-vocabulary hints; let users correct the transcript; keep voice features advisory | L1 + L2 |
| **Follow-ups** | Rubric-target validator; stop rule; repeat/contradiction check; NLI check later | L2 + L3 |
| **Reliability** | Asset consistency check; decision-trace export; property-based invariants; non-RL controller baselines; environment reconciliation | L2 |
| **UX** | Weakness map; "why this question"; session-over-session comparison; evidence panel | L2 |
| **Responsible use** | Auth, per-user access, retention/delete, consent text, accessibility check, no psychological claims from voice | L1 + L2 |

---

## 5. Ranked feature backlog

Scores 1–5. For **effort** and **risk**, 5 = high. "Evidence" is evidence strength for the *general* approach, not for PrepAIred.

| Rank | Proposed improvement | User problem | Research/evidence basis | Value | Feas. | Diff. | Evid. | Effort | Risk | Validation needed |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Score Trust Check**: robustness regression suite + uncertainty flag + evidence trace | "Can I trust this score?" | Ding 2020; Dubois 2024; Zheng 2023; Guo 2017; repo C.2 | 5 | 5 | 3 | 4 | 2 | 1 | Perturbation tests; later independent ratings |
| 2 | **Account & Data Safety** (auth, authorization, retention/delete, consent text) | Anyone can read others' transcripts or become admin | WCAG 2.2 / DPDP Rules 2025 (context); repo audit | 5 | 4 | 1 | 4 | 2 | 1 | Security tests; manual review |
| 3 | **My Weakness Map** (concept profile across sessions) | App forgets me between sessions | Pelánek 2016; Gervet 2020; repo schema | 5 | 4 | 4 | 3 | 3 | 2 | Offline replay on stored attempts; pilot |
| 4 | **Probe-with-Purpose** follow-up validator + stop rule | Follow-ups can repeat or miss the gap | Grounding literature (indirect); repo gap | 4 | 4 | 4 | 2 | 3 | 2 | Rule tests; rater review of follow-ups |
| 5 | **Smart Revision** queue | I forget concepts I missed | Roediger & Karpicke 2006; Cepeda 2006 | 4 | 4 | 3 | 4 | 3 | 2 | Delayed re-test pilot with ethics approval |
| 6 | ASR-uncertainty handling (flag low-ASR answers, transcript correction, domain terms) | Mis-heard terms lower my score | Koenecke 2020/2024; Radford 2023 | 4 | 4 | 2 | 4 | 3 | 2 | WER on technical-term set; A/B on score change |
| 7 | "Why this question" at concept level | I don't see why I got this | Dashboard review (Bodily 2017, weak) | 3 | 4 | 3 | 2 | 2 | 1 | User comprehension check |
| 8 | Question-bank and rubric audit (coverage per concept, singleton topics, evaluator-asset parity) | Sparse topics; possible missing rubrics | Repo audit | 4 | 5 | 1 | 3 | 3 | 1 | Coverage report; asset-parity test |
| 9 | Decision-trace export and replay | Hard to debug why a turn went as it did | Multi-agent failure taxonomy (Cemri 2025) | 3 | 4 | 2 | 3 | 2 | 1 | Replay reproduces decisions |
| 10 | Non-RL controllers (staircase/Elo) + shadow-mode comparison to PPO | Complexity without shown benefit | Pelánek 2016; repo Paper 3 audit | 3 | 4 | 3 | 4 | 3 | 2 | Closed-loop simulator; then human pilot |
| 11 | Semantic (NLI/embedding) grounding of feedback and follow-ups | Lexical checks accept unsupported claims (57/57) | SummaC; FActScore | 3 | 3 | 3 | 3 | 4 | 3 | Authored probe set; precision/recall |
| 12 | Property-based invariant tests + mutation testing of safeguards | Safeguard regressions go unnoticed | Claessen & Hughes 2000; Jia & Harman 2011 | 3 | 4 | 2 | 4 | 3 | 1 | Mutation score |
| 13 | Calibrated confidence for scores (temperature scaling or conformal sets) | Confidence is a constant | Guo 2017; Angelopoulos 2023 | 3 | 2 | 3 | 4 | 4 | 2 | Needs independent labeled set first |
| 14 | Role and mode presets (conceptual vs coding rounds) | One flow fits everyone | None specific | 3 | 3 | 3 | 1 | 4 | 2 | Usage study |

**How scores were assigned.** Value = size of the user problem times how often it occurs. Feasibility = fit with existing code. Differentiation = distance from a plain Q&A chatbot or the documented competitors. Evidence = strength of published support for the general method. Items 6 and 13 are high-evidence but gated by data or accuracy requirements; items 3 and 4 have lower evidence but high repo-specific value. A high differentiation score never lifted an item over a weak value or evidence score.

### Priority A: build first (existing architecture, low risk)
Items 1, 2, 3 (read-only profile), 4 (rules only), 6 (flagging, transcript correction), 7, 8, 9.

### Priority B: build after validation
Items 3 (profile steering selection), 5, 10, 11, 12, 13.

### Priority C: research projects
Closed-loop persona simulator (inside item 10); length-controlled evaluator validation study; delayed-recall study of Smart Revision.

### Do not build yet
See section 9.

---

## 6. Detailed technical design briefs (top five)

### 6.1 Score Trust Check

**User scenario.** After an answer, the learner sees the score, which rubric concepts were matched and the sentence that matched each, and a notice such as "Low evidence: your answer was very short" or "The transcript may contain recognition errors". Developers get a regression suite that fails if scoring becomes length-sensitive.

**Current limitation [V].** `evaluation_confidence` is 0.90 or 0.95; ASR confidence is not used in scoring trust; no perturbation tests; the evaluator returns `concept_details` but the report shows only concept lists.

**Workflow.**
1. Evaluator returns the existing fields plus `evidence` (matched sentence per concept, already derivable from `concept_detection`) and `trust` = `{level: ok|low_evidence|asr_uncertain|conflicting_signals, reasons: [...]}`.
2. `trust` is computed from simple, auditable rules [I]: answer shorter than N words; ASR confidence below a threshold; S1, S2 and R disagree by more than a margin; mandatory concept missed with high R.
3. The UI shows the evidence and, for non-`ok` levels, a plain-language notice; the score is still shown but not hidden.
4. Low-trust answers do **not** change difficulty (shadow-log first; change behavior only after validation).

**Technical design.**
- Backend: add `evidence` and `trust` to `evaluate()` output in `services/evaluator/app.py` (additive fields; keep `evaluation_confidence` for compatibility but stop presenting it as confidence). Pass `transcription_confidence` from `apps/backend/main.py` `_analyze_audio_confidence` (line 635) into the evaluator call.
- Orchestrator: store `trust` in the attempt (`feedback_json` already carries arbitrary JSON; no schema change required) in `_update_session_state` (line 1855).
- Frontend: extend `FeedbackCard.jsx` and `Report.jsx`.
- Tests: new `tests/unit/test_evaluator_robustness.py` (below). No new agents, no new models.
- Fallback: if `trust` cannot be computed, omit it and show nothing.

**Acceptance criteria.**
- For every evaluated answer, `evidence` lists a matched sentence or an explicit "none found" per concept.
- Repeating the same answer text three times, or padding it with filler to 3× length, does not raise the score by more than a pre-registered tolerance (for example 0.05).
- Keyword-stuffed answers (rubric terms listed without reasoning) score below a coherent answer at the same length on at least a pre-registered fraction of rubric items.
- Paraphrase pairs differ by less than a tolerance.
- Short-correct beats long-wrong on the authored pair set above a pre-registered fraction.
- `trust.level != ok` triggers on inputs under the length threshold and on simulated low-ASR input.

**Testing strategy.** Unit tests with authored perturbations built from existing rubrics (`logic_markers.mandatory`, `concept_groups`, `common_mistakes`), using the in-process `evaluate()` (no service); property-based tests (Hypothesis) for monotonicity-style invariants such as "appending irrelevant text never increases the score above tolerance"; regression snapshot of scores for a fixed set; negative tests for missing rubric and missing ASR confidence.

**Evaluation plan.** Primary metric: score change under length-preserving vs length-changing perturbations, against two baselines (the current evaluator and a word-count scorer). Secondary: how often `trust != ok` coincides with large disagreement against independent human ratings (needs the independent item set in section 7).

**Risks.** Thresholds are heuristics [I] and could mislabel good short answers; presenting "low evidence" could discourage users; any rule tuned on the benchmark must be separated from the test set. The authored perturbation set is not an independent validation.

**Estimate.** Medium. Dependencies: none beyond existing models.

### 6.2 Account & Data Safety

**User scenario.** A student uses the app on a shared deployment; only they can see their transcripts; they can export or delete their data; admins are really admins.

**Current limitation [V].** `LoginRequest.admin` and `adminPass` (`main.py:280–289`); `is_admin=req.admin` (`main.py:730`) with no password check; `/api/admin/*` and `/api/history/{candidate_id}[/{question_id}]` have no authentication; no deletion or retention path; transcripts persist in `question_attempts.transcript`.

**Proposed workflow.** Server-issued session token at login; admin status set server-side (configured allow-list or hashed secret), never from the request body; every history/report/session route checks token ↔ `candidate_id`; `DELETE /api/me/data` removes the candidate's rows; configurable transcript retention; a plain-language notice at login describing what is stored (audio is written to a temp file and unlinked, `main.py:889–973`; transcripts are stored).

**Technical design.** FastAPI dependency for auth; small token table or signed tokens; additive column for retention; frontend `Login.jsx` and `api.js` attach the token. No change to evaluator, agents or RL.

**Acceptance criteria.** A request with another candidate's ID returns 403; `admin: true` in the body has no effect; admin routes return 401/403 without credentials; deletion removes all rows for a candidate (verified by query); retention job removes transcripts older than the configured age.

**Testing.** Unit and integration tests with `TestClient`; negative tests; a test that the old `admin` field is ignored; accessibility smoke check against WCAG 2.2 for the login and consent screens.

**Evaluation.** Security checklist review; no user-benefit experiment is needed.

**Risks.** Breaking the local demo flow (keep a clearly labeled local-dev mode); scope creep into full identity management; legal text must be reviewed (DPDP Rules notified Nov 2025 with phased commencement per secondary sources; check the official gazette before relying on dates).

**Estimate.** Small to Medium.

### 6.3 My Weakness Map

**User scenario.** After three sessions, the learner opens "My Weakness Map" and sees concepts ranked by estimated mastery with uncertainty ("hash-map complement lookup: seen 4 times, matched 1"), what they missed most, and a button to practice them.

**Current limitation [V].** Weakness tracking is a session-local topic list (`interview_orchestrator.py:1932`); `question_attempts` stores per-concept outcomes but nothing aggregates them; question bank has 19 singleton topics, so topic-level mastery is meaningless. Rubrics already define concept groups, mandatory concepts and common mistakes.

**Proposed workflow.** (1) Offline job derives, from `question_attempts`, one observation per (candidate, concept) with outcome covered/missing/incorrect and timestamp. (2) A simple estimator per concept: count-based with a Beta prior, or an Elo-style rating (Pelánek 2016), plus the number of observations as the uncertainty indicator. (3) API returns the ranked list; UI renders it with counts, not a single "readiness score". (4) Stage B: the selector may prefer questions whose rubric contains low-mastery concepts.

**Technical design.**
- Concept key: `"{qid}:{kind}:{index}"` from the rubric (mandatory markers, `concept_groups[i]`), because concept texts are free text [I]. Verify that `concept_details` order is stable relative to `_extract_concept_texts` before relying on it (not verified).
- Schema: new table `concept_observations(candidate_id, concept_key, qid, outcome, attempt_id, observed_at)`; derived `concept_mastery` can be computed on read (no table) at this data volume. No change to existing tables.
- Backend: new route `GET /api/candidates/{id}/weakness-map` (after the auth fix in 6.2).
- Frontend: new view alongside `Report.jsx`; reuse styles.
- No change to PPO, state, reward or guardrails.

**Acceptance criteria.** Profile is reproducible from stored attempts alone; recomputing gives identical output; uncertainty is shown wherever n < a threshold; deleting a candidate removes their observations; empty history shows an empty-state message rather than a made-up estimate.

**Testing.** Unit tests for the estimator (known sequences); property tests (mastery never leaves [0,1], more correct observations never lowers it); integration test seeding `question_attempts`.

**Evaluation plan.** Offline: predict the next-attempt outcome on held-out stored attempts and compare with two baselines (global mean; per-topic mean) using log-loss and calibration. Data are currently tiny (49 attempts), so this is a feasibility check, not evidence. Stage B online evaluation requires ethics approval and a pilot (section 7).

**Risks.** Sparse data gives noisy ranks; users may over-read numbers; concept keys may drift if rubrics are edited (version them); privacy of stored profiles.

**Estimate.** Medium.

### 6.4 Probe-with-Purpose (follow-up validator)

**User scenario.** A learner gives a partial answer on hashing; the system asks one question about the specific missing concept, never repeats itself, and moves on once the concept is covered or two probes have been used.

**Current limitation [V].** `_inject_followup_question` sends the evaluation to Qwen (or a template) and inserts whatever comes back if it is longer than 15 characters (`interview_orchestrator.py:~1790`); nothing verifies that it targets a missing rubric concept, differs from earlier questions, or follows the evidence.

**Proposed workflow.** After a follow-up is generated, run validators in order: (a) non-trivial and a question; (b) mentions or paraphrases a concept in `missing_concepts`/`incorrect_claims` from the evaluator (lexical/embedding similarity against rubric texts); (c) not a near-duplicate of previous questions or follow-ups (Jaccard or embedding, as the selector already does for primaries); (d) does not leak the reference answer. On failure, regenerate once, then fall back to the template synthesizer, then skip.

**Technical design.** A pure function module (for example `agents/orchestrator/followup_validation.py`) called from `_inject_followup_question`; no new agent and no new model for rules; optional later NLI check using an existing sentence-transformers model. Log `followup_validation` result into the existing decision-source fields.

**Acceptance criteria.** 100% of injected follow-ups have a non-empty `target_concepts` that is a subset of evaluator-missing or incorrect concepts; zero exact duplicates within a session; behavior under Qwen outage unchanged (existing tests `test_qwen_followup_feedback.py` still pass).

**Testing.** Unit tests per validator; property tests (validator is idempotent); regression using the existing fixtures; adversarial cases (follow-up that restates the answer).

**Evaluation plan.** Blind human review of a sample of follow-ups under validator on/off, rating relevance and non-redundancy; baseline = current behavior. Pre-register the rating rubric.

**Risks.** Over-filtering leaves fewer follow-ups; lexical checks accept paraphrase (the same weakness documented in the paper); more latency from regeneration.

**Estimate.** Small (rules) to Medium (semantic check).

### 6.5 Smart Revision

**User scenario.** Two days after a session, the learner opens "Revise" and gets three short questions on concepts they missed, with intervals that lengthen when they answer well.

**Current limitation [V].** No review scheduling exists. `question_attempts` has timestamps and per-concept outcomes.

**Proposed workflow.** Missed or incorrect concepts enter a queue with a due date; correct review answers lengthen the interval, incorrect ones shorten it; learners can snooze or disable it. Use an expanding-interval rule from the spacing literature as a starting point [P/I]; do **not** claim a specific schedule is optimal.

**Technical design.** New table `review_queue(candidate_id, concept_key, due_at, interval_days, streak, status)`; endpoint to fetch due items; selector choice limited to questions whose rubric contains the due concept; reuses 6.3 concept keys. No change to evaluator, agents or RL.

**Acceptance criteria.** Items become due on schedule; completing a review updates interval deterministically; disabling stops notifications and queue growth; deleting the candidate removes the queue.

**Testing.** Unit tests for the scheduler with fixed clocks; property tests (interval monotone in streak); integration tests.

**Evaluation plan.** Randomized pilot with consent and ethics approval: revision on vs off; outcome = score on the same concepts after a fixed delay (for example 7 days). Report effect with confidence intervals; negative result is acceptable and informative.

**Risks.** Needs repeated use to matter; notification fatigue; concept-key drift; the retention benefit in lab studies may not transfer.

**Estimate.** Medium; depends on 6.3.

---

## 7. Research opportunities

| # | Research question | Hypothesis | Baseline | Intervention | Data required | Primary metric | Analysis | Possible negative result | Ethics |
|---|---|---|---|---|---|---|---|---|---|
| R1 | Is evaluator scoring stable under length and keyword-stuffing controls? | Controlled perturbations change scores by less than a tolerance for a majority of rubrics | Word-count scorer; current evaluator | Perturbation suite; length-controlled regression | Authored perturbations (no humans); then an independent, length-balanced rated set | Score change under perturbation; rank correlation with independent ratings | Cluster by question (not by answer); bootstrap plus permutation or mixed model | Evaluator rewards length and padding | Rater consent, compensation, provenance records |
| R2 | Does a concept-level learner model beat a global score for predicting next performance? | Concept model has lower log-loss | Global running mean; per-topic mean | Count/Elo model on rubric concepts | More attempts than the current 49 | Held-out log-loss, calibration | Learner-level cross-validation | No gain at this data size | Consent for stored learning data |
| R3 | Does PPO outperform non-RL controllers under closed-loop simulation? | No difference or heuristic better, per existing audit | Fixed, staircase, Elo, current heuristic | Closed-loop personas with learning dynamics, held-out personas | Simulator | Difficulty tracking error; stability | Persona as statistical unit (training seed as second factor) | Heuristic wins | None (simulation only) |
| R4 | Does semantic grounding reduce unsupported feedback compared with lexical rules? | Semantic validator lowers unsupported-credit acceptance | Current lexical validator (57/57 accepted in probes) | NLI/embedding validator | Authored probe set; later rated outputs | Unsupported-acceptance rate; false rejection | Paired comparison per probe; question-level clustering | Semantic check misses paraphrase too | None for authored probes |
| R5 | Does arbitration preserve invariants under a defined fault model? | Yes, for structural faults; not for semantic ones | No arbitration; paper results | Property-based and mutation testing | Generated faults on the paper branch code | Invariant violations; mutation score | Deterministic; report all counterexamples | Surviving mutants expose gaps | None |
| R6 | Does personalized revision improve delayed recall or later performance? | Revision on > off | Random control | Smart Revision queue | Real learners over weeks | Delayed re-test score | Mixed-effects with learner random effect | No difference | Ethics approval, consent, retention policy |
| R7 | Do reported confidence estimates track actual scoring error? | After calibration, confidence correlates with absolute error | Constant confidence; word count | Temperature scaling or conformal intervals | Independently rated labeled set | Calibration error, interval coverage | Cross-validation by question | Calibration fails out of sample | Same as R1 |

**What each kind of evidence supports (do not conflate).**
- *Software tests passing* show code conforms to specifications, not that scoring is valid.
- *Evaluator agreement with human ratings* supports measurement validity only on the rated item set (here 64 constructed answers to 8 questions).
- *Simulated-candidate results* characterize the controller under assumed learner models; they make no claim about real learners.
- *Deterministic replay* characterizes behavior on fixed stimuli; it does not test adaptation to a responding candidate.
- *Learning gains* require human candidates, randomization or a strong quasi-experimental design, and a delayed outcome.

---

## 8. Three-stage implementation roadmap

No dates are assigned, because team capacity and deadlines are unknown.

### Stage 1: Core reliability and immediate user value
- **Outcome:** a trustworthy base for every later feature.
- **Features:** Account & Data Safety (6.2); asset consistency check and question-bank audit (item 8); Score Trust Check (6.1) with perturbation suite and evidence panel; decision-trace export (item 9); environment reconciliation per `docs/PROJECT_STATE.md` (only after a decision).
- **Dependencies:** none external.
- **Testing:** new robustness and auth tests; full existing suite plus the one tracked failing test documented, not "fixed" silently.
- **Completion criteria:** all acceptance criteria in 6.1 and 6.2 met; evaluator and backend start with a consistency check that fails loudly on missing rubrics; no change to PPO artifacts.
- **Risks:** touching the 2,299-line orchestrator (keep edits additive); regressions in existing Qwen fallbacks.

### Stage 2: Personalization and evaluator quality
- **Outcome:** the app remembers the learner and explains itself.
- **Features:** Weakness Map (6.3, read-only); concept-level "why this question"; Probe-with-Purpose rules (6.4); ASR-uncertainty handling (item 6); revision queue prototype (6.5, behind a flag).
- **Dependencies:** Stage 1 trust flag and auth.
- **Testing:** estimator property tests; follow-up validator tests; offline replay on stored attempts.
- **Completion criteria:** weakness map reproducible from DB; validators pass fixtures; flag-controlled revision works end to end with fake clocks.
- **Risks:** small data; concept-key drift; user over-interpretation of ranks.

### Stage 3: Research-grade extensions
- **Outcome:** evidence for or against complexity.
- **Features:** independent rated, length-balanced item set and evaluator validation (R1); non-RL controller baselines with shadow mode and closed-loop simulator (R3); semantic grounding comparison (R4); property-based and mutation testing of safeguards (R5); human pilot for Weakness Map and Revision (R2, R6) with ethics approval.
- **Dependencies:** ethics approval, raters, a registered protocol and run manifest per `research/audit/PREREGISTRATION_SPEC.md` and `RUN_MANIFEST_SPEC.md`.
- **Testing:** pre-registered analyses; stored seeds; git commit recorded per run.
- **Completion criteria:** each study reported with its limitations; negative results retained.
- **Risks:** too many parallel studies; scope creep. Run at most one human-subject study at a time.

---

## 9. Features not recommended yet

| Feature | Why not yet |
|---|---|
| New agents (planner, memory, "critic") | The paper's own result: a unified controller matched the split design 1,280/1,280; added agents add state and failure modes without shown benefit. |
| LLM-as-judge as the primary scorer | Documented verbosity and self-enhancement bias (Zheng 2023); extra latency and cost on CPU; use only as an audit baseline. |
| Detecting anxiety, honesty, personality or employability from voice | No validated evidence; contested inference from expressive behavior (Barrett 2019, by analogy); fairness risk (Koenecke 2020). |
| Video / MediaPipe features | Open research decision in `docs/PROJECT_STATE.md`; no evidence that it helps technical scoring; privacy cost. |
| Replacing Qwen with Mistral, or adding ChromaDB | Listed as unresolved decisions; no measured problem they solve. |
| Retraining PPO or changing reward/state/action definitions | Frozen research artifacts; no benefit demonstrated; do non-RL baselines first. |
| Single "readiness score" dashboard | No validated meaning; dashboard evidence base is thin (Bodily 2017). |
| Resume/JD-based scoring or ranking | High fairness and privacy risk; unsupported scoring claims. Revisit only as topic suggestion without scoring. |
| System-design interview mode | Question bank and rubrics do not support it (125 items, mostly conceptual/code). |
| Online RL from real users | Safety, consent and non-stationarity risks; no offline evidence. |

---

## 10. References

Preprints are labeled. All items below were looked up during this audit; where a source could not be fully confirmed the limitation is stated. Claims supported are given in section 3.

**Learner modeling and adaptation**
1. Corbett, A. T., & Anderson, J. R. (1994/1995). Knowledge tracing: Modeling the acquisition of procedural knowledge. *User Modeling and User-Adapted Interaction*, 4(4), 253–278. DOI 10.1007/BF01099821. *(Year differs between sources, 1994 vs 1995; check the publisher record.)*
2. Piech, C., et al. (2015). Deep knowledge tracing. *NeurIPS 28*, 505–513. https://papers.neurips.cc/paper/2015/hash/bac9162b47c56fc8a4d2a519803d51b3-Abstract.html *(author list differs between NeurIPS and arXiv:1506.05908.)*
3. Gervet, T., Koedinger, K., Schneider, J., & Mitchell, T. (2020). When is deep learning the best approach to knowledge tracing? *Journal of Educational Data Mining*, 12(3), 31–54. https://jedm.educationaldatamining.org/index.php/JEDM/article/view/451
4. Pelánek, R. (2016). Applications of the Elo rating system in adaptive educational systems. *Computers & Education*. DOI 10.1016/j.compedu.2016.03.017
5. Clement, B., Roy, D., Oudeyer, P.-Y., & Lopes, M. (2015). Multi-armed bandits for intelligent tutoring systems. *Journal of Educational Data Mining*, 7(2), 20–48. https://jedm.educationaldatamining.org/index.php/JEDM/article/view/111
6. Doroudi, S., Aleven, V., & Brunskill, E. (2019). Where's the reward? A review of reinforcement learning for instructional sequencing. *International Journal of Artificial Intelligence in Education*, 29(4), 568–620.
7. Narvekar, S., et al. (2020). Curriculum learning for reinforcement learning domains: A framework and survey. *JMLR*, 21(181), 1–50. https://jmlr.org/papers/v21/20-212.html
8. Roediger, H. L., & Karpicke, J. D. (2006). Test-enhanced learning: Taking memory tests improves long-term retention. *Psychological Science*, 17(3), 249–255. https://pubmed.ncbi.nlm.nih.gov/16507066/
9. Cepeda, N. J., Pashler, H., Vul, E., Wixted, J. T., & Rohrer, D. (2006). Distributed practice in verbal recall tasks: A review and quantitative synthesis. *Psychological Bulletin*, 132(3), 354–380. https://pubmed.ncbi.nlm.nih.gov/16719566/
10. Bodily, R., & Verbert, K. (2017). Review of research on student-facing learning analytics dashboards and educational recommender systems. *IEEE Transactions on Learning Technologies*, 10(4), 405–418. DOI 10.1109/TLT.2017.2740172

**Evaluation, robustness, uncertainty, grounding**
11. Burrows, S., Gurevych, I., & Stein, B. (2015). The eras and trends of automatic short answer grading. *IJAIED*, 25(1), 60–117. DOI 10.1007/s40593-014-0026-8
12. Ding, Y., Riordan, B., Horbach, A., Cahill, A., & Zesch, T. (2020). Don't take "nswvtnvakgxpm" for an answer. *COLING 2020*, 882–892. https://aclanthology.org/2020.coling-main.76
13. Zheng, L., et al. (2023). Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. *NeurIPS 2023 Datasets and Benchmarks Track*. https://proceedings.neurips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract.html
14. Dubois, Y., Galambosi, B., Liang, P., & Hashimoto, T. B. (2024). Length-controlled AlpacaEval. **Preprint** arXiv:2404.04475 (venue acceptance not confirmed by me).
15. Singhal, P., Goyal, T., Xu, J., & Durrett, G. (2023). A long way to go: Investigating length correlations in RLHF. **Preprint** arXiv:2310.03716 (a COLM 2024 version is reported but not confirmed by me).
16. Kim, S., et al. (2024). Prometheus: Inducing fine-grained evaluation capability in language models. *ICLR 2024*; arXiv:2310.08491.
17. Reimers, N., & Gurevych, I. (2019). Sentence-BERT. *EMNLP-IJCNLP 2019*, 3982–3992. DOI 10.18653/v1/D19-1410
18. Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. *ICML*, PMLR 70, 1321–1330. https://proceedings.mlr.press/v70/guo17a
19. Angelopoulos, A. N., & Bates, S. (2023). Conformal prediction: A gentle introduction. *Foundations and Trends in Machine Learning*. DOI 10.1561/2200000101 (arXiv:2107.07511)
20. Laban, P., Schnabel, T., Bennett, P. N., & Hearst, M. A. (2022). SummaC. *TACL*, 10, 163–177. https://aclanthology.org/2022.tacl-1.10
21. Min, S., et al. (2023). FActScore. *EMNLP 2023*, 12076–12100. https://aclanthology.org/2023.emnlp-main.741

**Speech and responsible use**
22. Koenecke, A., et al. (2020). Racial disparities in automated speech recognition. *PNAS*, 117(14), 7684–7689. DOI 10.1073/pnas.1915768117
23. Radford, A., et al. (2023). Robust speech recognition via large-scale weak supervision. *ICML*, PMLR 202, 28492–28518. https://proceedings.mlr.press/v202/radford23a.html
24. Koenecke, A., Choi, A. S. G., Mei, K. X., Schellmann, H., & Sloane, M. (2024). Careless Whisper: Speech-to-text hallucination harms. *FAccT '24*. DOI 10.1145/3630106.3658996 (arXiv:2402.08021)
25. Barrett, L. F., Adolphs, R., Marsella, S., Martinez, A. M., & Pollak, S. D. (2019). Emotional expressions reconsidered. *Psychological Science in the Public Interest*, 20(1), 1–68. DOI 10.1177/1529100619832930 *(about facial movements; application to voice is my inference.)*
26. W3C (2023). Web Content Accessibility Guidelines (WCAG) 2.2, Recommendation of 5 October 2023. https://www.w3.org/TR/WCAG22/
27. Government of India. Digital Personal Data Protection Act, 2023, and Digital Personal Data Protection Rules, 2025. *Commencement dates were taken from secondary reports (staggered; consent-notice rules reported as effective May 2027); verify against the official gazette.*

**Testing and reliability**
28. Claessen, K., & Hughes, J. (2000). QuickCheck. *ICFP '00*, 268–279. DOI 10.1145/357766.351266
29. MacIver, D. R., Hatfield-Dodds, Z., et al. (2019). Hypothesis: A new approach to property-based testing. *JOSS*, 4(43), 1891. DOI 10.21105/joss.01891
30. Jia, Y., & Harman, M. (2011). An analysis and survey of the development of mutation testing. *IEEE Transactions on Software Engineering*, 37(5), 649–678. DOI 10.1109/TSE.2010.62
31. Kim, Y., et al. (2026). Capable language models can outgrow the benefits of collaboration. *Nature Machine Intelligence*, 8, 1157–1172. DOI 10.1038/s42256-026-01268-y
32. Cemri, M., et al. (2025). Why do multi-agent LLM systems fail? **Preprint** arXiv:2503.13657.

**Interview-practice systems (already cited in the ADCOM paper; abstracts only were checked)**
33. Gomez, N., Batham, S. S., Volonte, M., & Do, T. D. (2025). Virtual interviewers, real results. *CSCW Companion '25*; arXiv:2506.16542.
34. Vaishampayan, S., & Brown, C. (2025). Will you trust me more than ChatGPT? *CHASE 2025*.
35. Yazdani, N., Mahajan, A., & Ansari, A. (2025). Zara: An LLM-based candidate interview feedback system. **Preprint** arXiv:2507.02869.

**Public product pages**
36. interviewing.io blog: "interviewing.io is out of beta: anonymous technical interview practice for all" (https://blog.interviewing.io/interviewing-io-is-out-of-beta-anonymous-technical-interview-practice-for-all/) and https://interviewing.io (AI interviewer option; current pricing not verified).
37. Pramp FAQ and site: https://www.pramp.com/faq, https://pramp.com/ (peer-to-peer mock interviews; run by Exponent).

**Repository evidence (not external):** `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` (C.2, D.1–D.2, E); `services/evaluator/app.py`; `agents/orchestrator/interview_orchestrator.py`; `apps/backend/main.py`; `services/storage/database.py`; `data/questions/qns.json`; `data/rubrics/rubrics_final_clean.json`; `origin/paper/adcom2027-v13:agents/multiagent/`.

---

## 11. Open questions (not verifiable from the repository or public sources)

1. Do the 15 `evaluate`-type questions (IDs 101–115) reach the evaluator service at runtime, given that its assets (`services/evaluator/assets/*.json`) contain only 100 questions and rubrics? A targeted test is needed; I did not start services.
2. Is `concept_details` order stable relative to `_extract_concept_texts` for every rubric (needed for stable concept keys)?
3. Which checkpoint (`2ab8d514…` deployed vs `299437ea…` evaluated) should the app ship, and was the paper's multi-agent layer meant to be merged into the working branch?
4. Is the manuscript's reported R–length association reproducible from retained analysis files? I did not locate those files.
5. Rater provenance, consent and ethics records for the 64-answer benchmark are documented as incomplete in the repository.
6. Intended deployment (single local demo, campus server, public web) determines how urgent the security items are, and which privacy law applies.
7. Team capacity, ethics-approval route, and access to learners for any pilot.
8. Official LeetCode and HackerRank feature documentation was not retrievable; no claims are made about them.
9. DPDP Rules commencement dates should be confirmed against the official gazette; I relied on secondary reports.
10. The `adminPass` field is collected by the UI but unused by the backend; whether another layer enforces it is not visible in the code I read.
