# PrepAIred System & Evidence Improvement Plan — Audit and Prioritized Roadmap

**Status: analysis and proposal only. Nothing executed, no code changed, no experiment run, no item generated, no model retrained, no tag/commit/push.** This document answers a request to act as a critical reviewer of the actual system and produce a prioritized improvement plan — not another protocol revision of D1. It is grounded in direct reads of the live code (`services/evaluator/app.py`, `rl/guardrails.py`, `rl/env/interview_env.py`), the current audit-style manuscript (`FINAL_MANUSCRIPT_EVIDENCE_V2.md`), the frozen canonical results, and the pre-existing `paper/manuscripts/system_paper/` workspace (a separate, already-completed audit track — see §0).

## 0. A framing note that must be resolved before anything else

Two separate manuscript tracks already exist in this repository, and this request's title ("PrepAIred: A Reinforcement-Based LLM-Powered Technical Interview Preparation System") could refer to either:

1. **`research/paper_strengthening/FINAL_MANUSCRIPT_EVIDENCE_V2.md`** — the audit-framed paper ("Auditing Design Commitments in a Decoupled Technical-Interview Assessment System"), built entirely on already-collected evidence and code-level verification. **No new human data. This is the track compatible with the instruction "I do not want a new human-participant study."**
2. **`paper/manuscripts/system_paper/`** — a separate, already fully-audited track (dated 2026-09-21) that concluded the *only* scientifically credible system paper is **Type B: a system + usability/feasibility paper requiring a small randomized human pilot**, currently **blocked** on ethics clearance (no determination exists) and nine unresolved author decisions (`SYSTEM_PAPER_BLOCKERS.md`). That track's own research-decision memo states an effectiveness or adaptation-benefit claim is **not supportable** without new human data.

**This plan assumes track (1)** — the no-new-human-study, evidence-and-engineering track — because that is what this request explicitly asks for, and because track (2) is already fully analyzed elsewhere and cannot proceed without approvals (ethics, study design decisions) that are out of scope here. If the actual target is track (2), the work below is still useful (better system, stronger D1, cleaner evidence) but does not by itself unblock that paper.

---

## PHASE 1 — Real bottlenecks (verified against code, not assumed)

### 1.1 What is genuinely novel
The contribution is **systems integration plus a disciplined audit**, not a new algorithm: a decoupled, LLM-free scoring path (SBERT + FAISS concept matching + a partially fine-tuned CrossEncoder), evidence-gated LLM follow-up generation, and a PPO difficulty controller behind a deterministic guardrail layer — combined into one working, continuous interview session, with an honest, code-verified account of which design commitments actually hold. That audit discipline, applied to a real, substantial, already-built system, is the paper's actual intellectual content right now. There is no new learning algorithm, no new architecture, and (per §1.3 below) no strong evidence the learned component earns its place over the deterministic one.

### 1.2 Weakest components / worst measured results (all already evidenced, re-verified here)
1. **PPO adds no measurable value.** Frozen P3: PPO+guardrails (MAE 0.677) ≈ constant-Same+guardrails (MAE 0.673), 120/125 sessions identical; a threshold heuristic (MAE 0.473) beats both.
2. **The full evaluator composite underperforms simpler subsets** on the 64-item human benchmark (question-clustered ρ: full 0.381–0.414 vs. R-only 0.483–0.496 vs. S1+R 0.488–0.509).
3. **Speaking-rate unit mismatch, live in production**: `transcriber.py` emits words-per-minute; `confidence_scorer.py`/`hesitation_scorer.py` expect words-per-second; no conversion at the call site. The rate term is pinned at its worst-case value (0.000) for every realistic real speaking rate — 13% of the confidence score's design weight is silently dead on real audio, and (via `hesitation = 1 − confidence` in the live orchestrator) inflates hesitation into the guardrail/PPO state for every real session.
4. **CrossEncoder provenance is incomplete** (16.28% of parameters changed from `ms-marco-MiniLM-L-6-v2`; no training data or code preserved).
5. **Metamorphic robustness gaps already on record**: MG-5 (keyword-stuffing, score ≤ 0.50 criterion) fails in 2 of 3 tested cases (0.578, 0.664) — the "dampening" defense against keyword stuffing is demonstrably incomplete, not just theoretically imperfect.

### 1.3 New finding from this pass: *why* PPO cannot separate from the guardrail baseline, read directly from the code
This is not previously documented anywhere in the repository as far as I can find, and it follows directly from `rl/env/interview_env.py` and `rl/guardrails.py`:

- The **dominant reward term** (`hybrid_decision_weight`, default 0.60 of the hybrid reward) is `decision_component = 1.0 if action == oracle_action else -1.0`, where `oracle_action_from_obs` is a **hand-coded rule table** (R1–R7 in `interview_env.py`).
- The **guardrail layer** (`rl/guardrails.py`, `apply_canonical_guardrails`) is a **separate, deterministic rule table** (G1/G2/G4/G5/G6) applied to the *proposed* action both during training and at evaluation/deployment.
- These two rule tables overlap almost one-to-one: R1/G4 (stuck → Easier), R2/G1 (weak → Easier), R3/G2 (nervous expert → Same), R5/G5 (partial understanding → Same) are essentially the same condition under each system. **PPO is trained to imitate a rule table that the guardrail layer separately and deterministically enforces on its output anyway.**
- The only region where PPO's learned action could ever differ from "guardrail-forced action, or Same by default" is where the **oracle** recommends Harder/Easier via a rule the **guardrail** does not independently force — concretely, oracle rule R6 (`gap > 0.25 → Harder`) fires more broadly than guardrail G6 (`perf ≥ 0.90 AND gap > 0.25 AND not nervous_expert → Harder`). That gap band is narrow.
- **This is a mechanistic, falsifiable explanation for the null P3 result**, not just a restatement of it: PPO's ceiling over "constant + guardrails" is architecturally bounded by how often a state falls in that narrow non-guardrail-covered band where the oracle disagrees with the trivial default. This can be **quantified from already-frozen P3 replay data** with no new simulation (see Phase 3, item E1) — a real, cheap, high-value addition the paper does not currently make.

### 1.4 Does the evaluation mostly validate its own assumptions?
- **RL:** largely yes. The reward's dominant term scores agreement with an oracle that shares logic with the guardrails enforced on top of it, so "PPO learns the sanctioned behavior" is close to tautological by construction; the MAE gain over unguarded difficulty mostly reflects the deterministic guardrail, not anything learned (§1.3 makes this precise rather than just asserted).
- **D1 (evaluator benchmark):** partially. D1's correct/misconception/keyword-stuffed answer categories are constructed directly from the same rubric fields (`logic_markers`, `common_mistakes`, `semantic_targets`) that parameterize the evaluator's own `concept_detection`, `mistake_penalty`, and `_detect_misconceptions` functions. V6's C5b category (independently-worded misconceptions, <0.30 lexical overlap) is a real, honest mitigation, but the semantic content still originates from the same concept space the evaluator was built to match. **D1 is legitimate evidence that the evaluator behaves in the qualitatively expected direction on constructed cases — it is not evidence that the evaluator tracks true answer quality**, and V7–V14 have already been careful never to claim otherwise. This is a genuine, disclosed scope limit, not a defect to fix.

### 1.5 Is D1 worth executing as designed?
**Yes, but as a secondary, diagnostic piece of evidence, not the paper's evidentiary anchor.** It is low-cost, already rigorously audited across fourteen versions, and produces real (if narrowly-scoped) evidence with zero new human data. But two cheaper, higher-value analyses (§1.3's mechanism decomposition; a threshold/calibration sensitivity sweep, Phase 2 item C) can be produced first, from data that already exists, and should not wait on D1's registration.

---

## PHASE 2 — Candidate system improvements

Each item states: weakness addressed → mechanism → metric → baseline/ablation → dev data → leakage/overfitting risk → effort/cost → **approval status**.

### A. CrossEncoder score calibration (evaluator quality)
- **Weakness:** `reasoning_score = (raw_score − 0.20) / 0.70` in `cross_encoder_verification()` is a hand-picked linear remap based on assumed score bands ("~0.20 for noise, 0.40–0.55 partial, 0.70–0.95 strong"), never fit to data.
- **Mechanism:** replace with a data-fit calibration (isotonic regression) against human gold labels — could improve correlation/MAE without touching model weights.
- **Metric:** Spearman ρ / MAE vs. human gold, leave-one-question-out cross-validated across the existing 8 questions.
- **Baseline/ablation:** current linear map vs. LOOCV-isotonic vs. raw uncalibrated score.
- **Dev data:** the existing frozen 64-item benchmark, reused via **leave-one-question-out CV** (fit on 7 questions, evaluate on the held-out 1, repeat 8×) — no new human data, and no reuse of confirmatory results for tuning, since each fold's evaluation question is excluded from its own fit.
- **Risk:** only 7 questions per fold — very low power, wide CIs; report as a development diagnostic only, not a confirmatory claim. **Blocker to check first:** the stored `paper2_case_level_results.csv` may only contain the *already-calibrated* `R`, not the raw pre-transform CrossEncoder score; if so, obtaining raw scores means re-running the frozen CrossEncoder checkpoint on already-fixed (question, answer) pairs — a deterministic re-derivation from frozen inputs, not new data collection, but flagged for the same light approval as Category A2's precedent in `EXPERIMENT_PLAN.md`.
- **Effort:** low (hours), contingent on the raw-score availability check above.
- **Approval:** light (matches A2's precedent) if raw scores are stored; otherwise needs the same sign-off as re-running a frozen model on frozen inputs.

### B. Threshold / calibration sensitivity sweep (evaluator robustness) — **recommended first**
- **Weakness:** `CONCEPT_THRESHOLD=0.30`, `MANDATORY_THRESHOLD=0.40`, `MISTAKE_THRESHOLD=0.55`, `BONUS_THRESHOLD=0.50` are fixed constants with no disclosed robustness evidence; the manuscript itself already flags that the concept threshold was calibrated on a pilot partially overlapping the confirmatory set.
- **Mechanism:** none — this is a measurement, not a system change. Sweep each threshold ±0.05/±0.10 and recompute S2/mandatory_pass/bonus/penalty/final_score on the already-computed similarity matrices from the 64-item benchmark.
- **Metric:** how much `final_score`, ρ, and mandatory-pass rate move per threshold perturbation — a sensitivity/fragility table.
- **Baseline/ablation:** current thresholds vs. the swept grid.
- **Dev data:** the existing 64-item benchmark's stored embeddings/similarities — no new model calls if cached, otherwise a deterministic, cheap recomputation (same embeddings, different threshold comparison).
- **Risk:** none beyond the benchmark's existing small-N limitation, which is already disclosed.
- **Effort:** low (this is an offline re-scoring exercise, analogous to the already-approved evaluator-ablation reanalysis — no live-code change).
- **Approval:** light — same precedent as A2 ("recomputing a derived statistic from frozen inputs").

### C. Broaden negation/contrast handling (evaluator correctness)
- **Weakness:** `bonus_score`, `mistake_penalty`, `_detect_misconceptions` all filter negation using the same fixed six-word list (`avoid, avoids, not, without, instead, unlike, "no "`) — misses contractions (`isn't`, `doesn't`, `can't`, `won't`) and phrasal negation (`fails to`, `lacks`).
- **Mechanism:** expand the negation cue list; optionally add lightweight scope detection. Reduces false bonus/concept credit for negated mentions of a concept.
- **Metric:** deterministic before/after comparison on a small, hand-built adversarial sentence set (not a statistical claim — a code-correctness check, like the speaking-rate sweep).
- **Baseline/ablation:** current 6-word list vs. expanded list, on the same adversarial set.
- **Dev data:** newly authored adversarial sentences (author-constructed, disclosed as such, not claimed as independent).
- **Risk:** none statistically; this is a scoring-logic change to a live path.
- **Effort:** low-medium.
- **Approval: required** — this changes scoring logic in `services/evaluator/app.py`, which CLAUDE.md gates explicitly.

### D. Guardrail-coverage decomposition (RL mechanism) — **recommended first, alongside B**
- **Weakness addressed:** the paper currently states PPO doesn't help; it does not quantify *why*, or how much room there ever was for it to help.
- **Mechanism:** none — a re-analysis of already-frozen P3 replay logs. Compute, per session/turn: (i) fraction of turns where any guardrail fires; (ii) within guardrail-free turns, the fraction where the oracle's own recommended action is "Same" (the trivial default) vs. Harder/Easier. This directly operationalizes §1.3's mechanistic finding.
- **Metric:** guardrail-coverage %, and within the remainder, oracle-non-trivial-action %— the real "addressable ceiling" for any learned policy under this reward/guardrail design.
- **Baseline/ablation:** none needed — this is a structural decomposition of existing data, not a comparison.
- **Dev data:** frozen `research/experiments/paper3/` replay logs (already used for the audited replay analysis in the current manuscript).
- **Risk:** none — pure re-analysis of frozen, already-published data.
- **Effort:** low (a script over already-stored CSVs).
- **Approval:** none needed beyond confirming it reads, not modifies, the frozen `research/experiments/paper3/*` artifacts (matches the existing frozen-artifact rule — read-only).

### E. Legitimate PPO retraining attempt: reward restricted to the guardrail-free region
- **Weakness addressed:** §1.3's mechanism suggests PPO's current reward wastes its own learning signal inside guardrail-covered states, where nothing it decides can ever be observed at eval/deployment time.
- **Mechanism:** retrain PPO with the `decision_component`/`outcome_component` reward terms active only (or up-weighted) in states where no guardrail would fire, concentrating learning signal on the one region where a learned policy could matter.
- **Metric:** MAE / oracle-agreement specifically **within the guardrail-free subset** (development scenarios), vs. constant-Same and vs. the current PPO checkpoint, all under the same guardrail code.
- **Baseline/ablation:** current PPO; constant-Same; heuristic — all restricted to the same guardrail-free comparison, on **development-only** personas/seeds never used for the eventual confirmatory comparison.
- **Dev data:** new development-phase simulated personas/seeds (simulation-only, no human data), explicitly held apart from whatever seed set is later frozen for confirmatory reporting.
- **Risk:** real reward-hacking/overfitting risk if tuned and confirmed on the same data; must follow a strict development → freeze → confirmatory-run split, exactly as CLAUDE.md and the existing C2 experiment plan already require. This is the highest-uncertainty item on this list — it might still fail to separate PPO from constant-Same, and that is an acceptable, reportable outcome, not a reason to keep tuning.
- **Effort:** medium-high (new reward variant, retraining, a proper development/confirmatory split, replicated seeds).
- **Approval: required, explicit** — this is exactly the reward/state redesign + retraining CLAUDE.md requires sign-off for (already named, in less specific form, as C2 in `EXPERIMENT_PLAN.md`; this sharpens its rationale using §1.3's mechanism).

### F. Fix the speaking-rate unit mismatch
- **Weakness addressed:** §1.2 item 3 — a fully diagnosed, high-confidence, one-line-scope bug.
- **Mechanism:** convert one side to match the other's units at the call site (`apps/backend/main.py`) or inside `transcriber.py`.
- **Metric:** re-run the existing deterministic WPM/WPS sweep post-fix; confirm `rate_score`/`hesitation_score` now vary with actual pacing instead of pinning at the worst case; run the existing test suite for regressions.
- **Baseline/ablation:** before (documented defect) vs. after (corrected function), same sweep.
- **Dev data:** none needed — deterministic, no randomness.
- **Risk:** none to any frozen result — already confirmed the frozen P3 simulation study never calls the audio pipeline, so this only affects the live system, not any existing paper number.
- **Effort:** low (the fix itself); medium to re-verify properly (regression suite + sweep).
- **Approval: required** — a change to a live scoring path (`agents/audio/*` / `apps/backend/main.py`), per CLAUDE.md.

### G. Basic efficiency/latency table (currently a total evidence gap)
- **Weakness addressed:** the original ablation's untraceable latency table was removed; nothing replaced it. Phase 2.5's "system efficiency" is currently zero-evidence.
- **Mechanism:** none — pure measurement. Replay the 64 existing benchmark answers through the live evaluator (S1/S2/R) and the orchestrator's per-turn path, ≥10 warmed-up repetitions per stage, report mean/median/P95 latency and peak RAM.
- **Metric:** latency (ms) and peak RAM per stage, with variance — not a single-run number (this is explicitly the mistake the original table made).
- **Baseline/ablation:** per-component (S1 vs. S2 vs. R vs. full pipeline) breakdown.
- **Dev data:** the existing 64 answers — no new content, just timing instrumentation around already-fixed inputs.
- **Risk:** none scientifically; hardware/environment must be disclosed since `.venv` violates the project's own pins (numpy/torch/accelerate) — the measurement environment must be recorded alongside the numbers.
- **Effort:** low-medium.
- **Approval: required** (new measurement, per the existing C4 item in `EXPERIMENT_PLAN.md`), but low-risk and cheap.

---

## PHASE 3 — Experimental case: prioritizing D1 vs. alternatives

**D1 remains worth running, but not first, and not alone.** Two of the items above (B, D) are cheaper, require no new item generation, no model scoring calls, and no registration overhead (they are Category-A/B re-analyses of already-frozen or already-derivable data under the existing plan's own precedent) — and they directly answer open questions the paper currently only asserts qualitatively. Recommended sequencing:

| Priority | Item | Category | New data? | Approval | Directly strengthens |
|---|---|---|---|---|---|
| 1 | D — Guardrail-coverage decomposition | A (frozen-data re-analysis) | No | None (read-only) | §XI.2's PPO finding, turning it from descriptive to mechanistic |
| 2 | B — Threshold/calibration sensitivity sweep | A/B (frozen-data re-analysis) | No | Light | §XI.1 and Limitations — converts a disclosed weakness into a reported result |
| 3 | D1 — Synthetic category-discrimination benchmark (V14) | C (new synthetic items, no human data) | Yes (synthetic only) | Registration (ready) | A new, secondary, honestly-scoped piece of evaluator evidence |
| 4 | A — CrossEncoder calibration (LOOCV) | A/B, contingent on raw-score availability | No (reuses existing benchmark) | Light–moderate | §XI.1, if raw scores are recoverable |
| 5 | F — Speaking-rate fix + re-verification | C (code change + regression) | No | Full | §XI.3 — turns a found bug into a found-and-fixed bug |
| 6 | G — Efficiency/latency table | C (new measurement) | No (existing inputs) | Full | Limitations — closes a total evidence gap |
| 7 | E — PPO retraining, reward restricted to guardrail-free states | C (new training) | Yes (new dev-phase simulation only) | Full, explicit | §XI.2 — the only path to an actual positive RL finding; highest risk/reward, should follow 1 and be development/confirmatory-split from the start |
| 8 | C — Broaden negation handling | C (scoring-logic change) | New adversarial test set only | Full | Robustness story around the existing MG-5 keyword-stuffing finding |

Items 1–2 should happen **before** D1 execution, not instead of it — they cost nothing D1 doesn't already cost less of, and they make the paper's existing claims sharper without waiting on any approval beyond a light confirmation.

---

## PHASE 4 — Reviewer-level assessment

- **Clear research question?** Yes — unusually so for a systems paper: three explicit, falsifiable audited propositions (evaluator weighting, PPO value-add, speech-channel integrity), each answered with sourced evidence. This is a real strength.
- **Is the novelty substantial enough for a full-system paper?** Marginal at a demanding algorithmic venue; solid at an applied/education-technology or software-engineering-of-ML-systems venue. The contribution is integration + audit discipline, not a new method.
- **Are claims demonstrated experimentally?** Yes, for what is claimed — nothing here outruns its evidence. The risk is scope, not rigor: three (largely negative) findings on modest-N data may read as thin for a "full-system paper."
- **Does it distinguish from simpler alternatives?** Yes for PPO (explicitly benchmarked against constant/heuristic). The evaluator is not compared against a non-hybrid, LLM-as-judge baseline — a reviewer may ask why, though the LLM-free design is a deliberate, statable architectural choice, not an oversight.
- **Independence of evaluation data?** A real, already-disclosed weakness: 8 questions, a pilot-and-confirmatory concept-threshold overlap, incomplete rater provenance.
- **Proportional conclusions?** Yes — this manuscript is already unusually careful here.
- **What would cause rejection?**
  1. Perceived thinness — three largely-negative findings plus a description, no clear positive headline.
  2. Small-N evaluator benchmark (8 questions) undermining any quantitative table.
  3. A "we tried RL and it didn't help" story with no attempted fix or mechanism (Phase 2 items D and E directly address this).
  4. Zero efficiency/latency evidence.
  5. Venue mismatch if submitted to a top algorithmic ML/RL venue rather than an applied systems/education-technology one.
- **Top 5 changes, ranked by expected value:**
  1. **Guardrail-coverage decomposition (D)** — cheapest, turns a null result into a quantified mechanism.
  2. **Threshold/calibration sensitivity sweep (B)** — cheapest, turns a disclosed weakness into reported evidence.
  3. **PPO retraining attempt with a guardrail-aware reward (E)** — highest-risk, highest-reward; the only realistic path to a positive algorithmic finding.
  4. **Speaking-rate fix and re-verification (F)** — closes a fully-diagnosed bug, strengthens the paper's own "we audit ourselves" narrative.
  5. **Efficiency/latency table (G)** — closes a total evidence gap cheaply.
- **System-integration or algorithmic contribution — candidly?** **System-integration and audit methodology**, not algorithmic. Nothing here should be sold as an RL or NLP methods contribution unless item E produces a genuine, held-out-confirmed separation from constant-Same — and even then, the contribution would be narrow (a reward-shaping fix for a specific guardrail interaction), not a general RL advance.

---

## PHASE 5 — Prioritized plan

### 1. Current state and main weaknesses
`FINAL_MANUSCRIPT_EVIDENCE_V2.md` is an honest, well-sourced audit paper with a real, clear RQ structure. Its main weaknesses are: thin positive content (three largely-negative/audit findings), no mechanistic explanation for the PPO null result, no efficiency evidence, an unfixed but fully-diagnosed audio bug, and a small, partially-overlapping evaluator benchmark.

### 2. Highest-impact improvements, ranked (see Phase 4's top-5 and Phase 3's table)
Items **D** and **B** first (free, no new data, no real approval friction); then **D1** (already registration-ready); then **A**, **F**, **G**; then **E** (highest effort/risk, highest potential payoff); then **C**.

### 3. Experimental matrix
See the Phase 3 table for baselines, data source, and approval status per item. Seeds/splits: D1 uses its already-frozen 122/26/67/29 split (V14); the PPO retraining attempt (E) requires a **new** development/confirmatory persona-seed split, frozen before any tuning, per CLAUDE.md.

### 4. Development vs. diagnostic vs. confirmatory
- **Diagnostic (no registration needed):** D (guardrail decomposition), B (threshold sweep), G (efficiency table's per-stage breakdown) — these describe existing system behavior, not a hypothesis test.
- **Development-only (not reported as confirmatory):** E's initial reward-restriction experiments, C's adversarial negation set.
- **Confirmatory (needs a hashed/tagged protocol + approved manifest):** D1 (already there, V14); any final PPO-vs-constant comparison from E, on a held-out seed set never used while designing the reward change.

### 5. Decision tree
- If **D** shows guardrail coverage is near-total (e.g., >90% of turns): report this as the primary explanation for the null RL result; **do not** pursue E — there would be almost no room for a learned policy to matter, and retraining would be a low-value use of approval and compute.
- If **D** shows a meaningful guardrail-free region (e.g., >20% of turns) where the oracle disagrees with "Same": **E becomes worth attempting**, with a strict development/confirmatory split.
- If **E**'s confirmatory comparison still shows no separation: report that honestly as a stronger, now-mechanistically-explained negative result — do not iterate further on reward shaping without a new, separately-justified hypothesis.
- If **E** does separate PPO from constant-Same in the confirmatory run: report it as a narrow, mechanism-specific finding (a reward-shaping fix for a specific guardrail-interaction failure mode), not a general claim about learned difficulty control.

### 6. Publication-oriented plan
- Evaluator claims (§XI.1) ← items **B**, **A** (if feasible), plus the existing question-clustered reanalysis.
- RL claims (§XI.2) ← item **D** always; item **E** conditionally, per the decision tree.
- Speech-channel claims (§XI.3) ← item **F**, turning a found bug into a found-and-fixed one with before/after evidence.
- New Limitations content ← item **G** (efficiency), explicitly filling the currently-empty gap.
- D1 → a clearly-labeled secondary/diagnostic result, not the paper's evidentiary center, consistent with §1.4's circularity discussion.

### 7. Effort and compute estimate
- D, B, G's per-stage breakdown: hours each, CPU-only, no new model calls (pending the raw-score check for A).
- A: hours to a day, contingent on raw-score recovery; otherwise needs one CrossEncoder inference pass over 64 fixed pairs (seconds of GPU/CPU time).
- F: hours for the fix and sweep; a full regression-suite run (~6 minutes per the project's own test command) before/after.
- C: half a day (lexicon + adversarial set + verification).
- G (full latency table): half a day including warm-up protocol.
- E: the largest item — likely multiple days: new reward variant, a properly-split development/confirmatory persona-seed design, multi-seed PPO training runs, replay-based evaluation, and write-up. This is the only item requiring meaningful new compute (RL training, not LLM inference).

---

## What can be done now vs. what needs explicit approval
- **Can be scoped/drafted now, no approval needed beyond this document:** nothing is actually executed by this plan itself.
- **Needs only light confirmation (matches existing A2 precedent) before running:** D, B, and A (if raw scores are already stored).
- **Needs full explicit approval before any execution:** C, F, G, E, and D1's actual registration/execution (already awaiting that approval independently of this plan).

## Single highest-impact next step

**Item D — the guardrail-coverage decomposition of the frozen P3 replay logs.** It costs nothing (no new data, no model calls, read-only against already-frozen artifacts), requires no approval beyond confirming it only reads `research/experiments/paper3/*`, and it converts the paper's current weakest-sounding finding ("PPO doesn't help") into a precise, quantified, mechanistic one ("X% of turns are guardrail-determined; of the remainder, the oracle recommends the trivial default Y% of the time — leaving only Z% of turns where any learned policy's choice could ever matter"). It also directly determines whether item E (the one path to an actual positive RL finding) is worth attempting at all, so it should come before any decision about retraining.

**Stopping here, as instructed. No code changed, no experiment run, no item generated, no retraining, no tag/commit/push. Awaiting approval on which items to proceed with, starting with D.**
