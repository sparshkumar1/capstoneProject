# Research Audit — ADCOM 2027 Track-2 Paper (`main.pdf`)

**Date:** 2026-10-06
**Scope:** Audit only. No manuscript text was changed, no code was changed, no experiment was run.
**Author of this audit:** Claude Code, at the user's request, following the task brief pasted into this session.

---

## 0. Headline finding (read this first)

`main.pdf` (root of `capstoneProject`, 20 pages) presents a complete empirical paper — title, abstract, specific
numbers, tables, ablations, fault-injection results — about a **bounded-authority Strategy Agent + Coaching Agent
coordination layer** arbitrating over a frozen PPO policy, tested across:

- 160 deterministic replay sessions (8 clusters × 20 order permutations)
- leave-one-cluster-out sensitivity analysis
- a split-vs-unified implementation check (1,280/1,280 matched turns)
- a fault-injection campaign (headline: 0/40 vs 38/40 sessions with guardrail bypass)
- a cluster-bootstrap interval on level-change difference: −2.67 [−4.50, −0.24]
- a 57/57 grounding-probe weakness finding

**None of this exists anywhere in the `capstoneProject` repository.** I searched:
- every `.py` file for `StrategyAgent`, `CoachingAgent`, `strategy_agent`, `coaching_agent`, `arbitration`,
  `bounded_authority`, `coordination_layer`, `mas_coordinator` (case-insensitive) — the only hit is
  `agents/strategy/hybrid_orchestrator.py`, which is the **single-policy** PPO wrapper already documented in
  `CLAUDE.md` (6-D state, `Discrete(3)` actions, heuristic fallback). There is no second agent and no arbitration
  module.
- the whole repo for the distinctive numeric fingerprints above (`1,280/1,280`, `57/57`, `38/40`, `0/40`, `160
  deterministic`, `M1-B0`/`M1–B0`, `eight replay clusters`) — zero matches outside `main.pdf` itself.
- `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`, the project's sole authority on verified metrics — it documents
  Papers 1–3 (containment/fault-injection in the C sandbox, evaluator-vs-human diagnostics, PPO-vs-guardrail
  equivalence) and explicitly states, in its own Section G, *"No confirmatory X1/X2/X3 experiment has been run"*
  (that line is stale relative to git history — X1/X2/X3 work has since landed — but nothing it ever referred to is
  a Strategy/Coaching coordination study).
- `research/confirmatory/` — contains `X1`, `X1-D`, `X2-B`, `X2C`, `X3-A`. These map to Papers 1–3. No `XA`/`XB`/`XC`/`XD`
  directories exist, and none of X1/X1-D/X2-B/X2C/X3-A concerns a two-agent coordination layer.
- `research/papers/archived/abandoned_titles/paper_aied_multiagent_feedback.md` — an explicitly **archived/superseded**
  draft describing a *different* 7-sub-agent architecture (Audio, Evaluator, Validation, Feedback, Strategy(RL),
  Timer, Logger). Marked "NOT A SOURCE OF CURRENT FACTS." Not the source of `main.pdf` either.
- `main.pdf` itself has no LaTeX/Markdown source file anywhere in the repo (confirmed by searching for its exact
  title string and for `Coaching Agent`, `M1-B0`, etc. in every text file). It is a compiled-only artifact.

**Per the user's direction (2026-10-06): this is accepted as genuinely-not-yet-built work.** The instruction received
was explicit: *"keep the things as it is there... don't assume and add some new, imaginary things."* This audit
therefore does **not** propose inventing evidence, does **not** propose running the XA–XD experiments described in
the task brief as if they already exist, and does **not** recommend silently rewriting `main.pdf` to match
whatever the repo happens to contain. It documents the gap and lays out option-neutral next steps in
`Experiment_Decisions.md`.

This also means most of the task brief's instructions (verify XA/XB/XC/XD raw units; keep the 57/57 grounding
probe; keep the split-vs-unified 1,280/1,280 result; etc.) are **not actionable as written**, because there is
nothing in the repository to verify them against. Section 4 below records this explicitly for each one.

---

## 1. What *is* real and grounded (the actual system `main.pdf` would need to describe)

This is the material that genuinely exists in the repo and could support a truthful Track-2 paper about the
*current* system, if the user chooses to rescope rather than build the fictional MAS layer.

### 1.1 Architecture (CODE, verified)
- Single hub-and-spoke orchestrator (`agents/orchestrator/interview_orchestrator.py`): session state, question
  queue, attempts, follow-ups. One authoritative state writer.
- One RL component: `agents/strategy/hybrid_orchestrator.py` wraps a frozen SB3 PPO policy (`seed_123`), 6-D state
  (`perf, avg_perf, confidence, hesitation, time_norm/progress, difficulty/5`), `Discrete(3)` actions
  (Easier/Same/Harder), with explicit validation and a heuristic fallback when RL is unavailable.
- Evaluator (`services/evaluator/app.py`): `base_score = 0.15·S1 + 0.35·effective_S2 + 0.50·R`; `effective_S2 = S2`
  if `R > 0.30` else `0.6·S2`. The weights carry an in-code comment: `"FIX 4: R-heavy weights 0.15 / 0.35 / 0.50"`
  — a numbered engineering adjustment, not a labeled tuning experiment. See Section 2 below.
- Docker C sandbox (`agents/coding_executor/`), SQLite storage, local Qwen for feedback text (no path into
  `evaluate()`), no video/MediaPipe.
- There is no second decision-making agent, no proposal/arbitration protocol, and no "bounded authority" enforcement
  layer anywhere in the code. "Strategy" in the codebase is a module name for the PPO wrapper, not a second agent.

### 1.2 Question bank / Bloom taxonomy (CODE, verified)
- Schema (`data/questions/qns.json`, 125 questions): `qid, question_text, topic, difficulty (float 0.2–0.9),
  type (code/evaluate/general_tech/theory), time_limit_sec, bloom_level`.
- Bloom bands actually used: **`L1`–`L6`** (six coded bands), **not** the five-band
  Understand/Apply/Analyze/Evaluate/Create scheme the task brief asked me to verify. Do not assume that scheme;
  it is not what the data contains.
- Bloom level is **descriptive metadata only**. `agents/question_selector/question_selector.py` selects questions
  by nearest-match on the per-question `difficulty` float alone (`AVAILABLE_DIFFICULTIES`,
  `nearest_difficulty()`, `filter_by_difficulty()`) — `bloom_level` plays no role in selection. It is not read by
  the evaluator's scoring path, the RL 6-D state, or the follow-up logic; it is only passed through for display.
- `services/evaluator/app.py` uses the field name `blooms_level` (with an "s") in three places, including a
  **hardcoded literal default `"Apply"`** (line 623) that does not derive from the question's own `bloom_level`.
  The question-bank schema uses `bloom_level` (no "s"). This is a real field-name mismatch, independent of the
  MAS question — worth noting in any paper that touches Bloom, and worth fixing in code regardless of the paper.
- There is no evidence anywhere (code, logs, or canonical truth doc) of a Bloom-aware vs. non-Bloom-aware
  comparison, or of any claim that Bloom levels improve adaptivity or learning. None should be made.
- Per-question `difficulty` (continuous, 0.2–0.9, author-assigned in the question bank) is a **different** quantity
  from the system's adaptive numeric difficulty (integer 1–5, the RL/guardrail state dimension). There is no
  documented formula mapping one to the other, and no "3 coarse pools: Easy/Medium/Hard" mapping was found in code.
  Do not assert one.

### 1.3 Evaluator weight provenance (CODE + canonical truth, verified)
- `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §C.2: the full composite (0.3812) correlates **below** R-only
  (0.4832) and S1+R (0.4884) against the human benchmark; the canonical framing is explicitly "safety-hardened, not
  accuracy-optimal."
- The in-code comment ("FIX 4") and the absence of any stored grid-search/tuning artifact indicate the weights are
  an **engineering default**, not a result of a documented, held-out tuning procedure. θ = 0.30 (the S2 effective
  threshold) was chosen on an earlier N=20 pilot that shares 4 of the 8 current benchmark questions — i.e. it was
  not tuned independently of the evaluation data either.
- Conclusion for the paper: never call 0.15/0.35/0.50 "optimal," "tuned," or "learned." "Engineering default,
  chosen for robustness rather than measured accuracy" is the supportable wording.

### 1.4 PPO simulator / training design (FROZEN-VERIFIED, from canonical truth §D.1)
- SB3 PPO, `MlpPolicy`, net `[64, 64]`; 24,576 timesteps per training seed (12 rollouts × 2,048); training seeds
  42/123/456/789/999; evaluation seeds 1001/2002/3003/4004/5005.
- State: 6-D in [0,1] as above. Actions: Easier/Same/Harder.
- Reward (config weights): 0.60 decision-alignment-with-a-hand-coded-rule-oracle + 0.30 outcome delta + 0.10
  multimodal shaping − 0.10 stability penalty. **The reward is substantially imitation of a rule oracle**; the
  evaluation metric (mean |difficulty − persona target|) is not the training objective.
- Five authored personas (skill → target difficulty), evaluation T=10 integer difficulty steps; training used
  T=15 continuous 0.1 steps — training environment ≠ evaluation environment (documented mismatch).
- Deployed checkpoint (`rl/checkpoints/seed_123/ppo_final.zip`, hash `2ab8d5…`) differs from the evaluated
  checkpoint (`research/experiments/paper3/checkpoints/seed_123/ppo_final.zip`, hash `299437…`). Any paper must say
  which one a given number refers to.
- Existing Paper-3 finding (already frozen, already published-grade): **guardrails, not PPO, account for
  essentially all of the improvement over the Fixed baseline** — PPO+guardrails (MAE 0.673) ≈ Constant-Same+same
  guardrails (MAE 0.673, 5/125 sessions differ). "PPO improves tracking" is an explicitly **withdrawn** claim in
  the canonical truth doc. This is directly relevant background for any paper about whether an added coordination
  layer changes PPO's effective contribution — but it is Paper-3's finding, not evidence for a Strategy/Coaching
  layer.

---

## 2. Audit against the task brief's section numbers

### 3.1 Current paper strengths (of `main.pdf` as text, independent of evidence)
- Clear, falsifiable RQs (RQ1–RQ4) with appropriate hedging language ("no human-learning claims are made,"
  "results are limited to deterministic replay").
- Good discipline on scope-of-claim language in the extracted abstract/intro (e.g. explicitly separating
  coordination from specialization from arbitration as distinct constructs) — this is the right analytical frame
  *if* the underlying system and data existed.
- Introduction correctly identifies that decomposition-without-evidence is a common weak spot in MAS papers; the
  rhetorical structure (coordination vs. specialization vs. arbitration vs. authority) is sound and reusable.

### 3.2 Missing scientifically important content
- The entire evidentiary basis. Every number in the Results section (XA/XB/XC/XD, M1-B0, split-vs-unified,
  grounding probe, fault injection) has no traceable artifact. This is not a "missing section" problem; it is a
  missing-foundation problem.
- No architecture section grounded in actual code (the real single-policy PPO wrapper, not a two-agent system).

### 3.3 Content that should be removed or shrunk
- Not applicable until the user decides a direction (see `Experiment_Decisions.md`). I am not recommending
  deletions from `main.pdf` in this pass — only flagging that none of the Results-section claims can currently be
  retained as "verified."

### 3.4 New experiments worth running / 3.5 Experiments that should NOT be run
- Deferred to `Experiment_Decisions.md`, which applies the brief's own ADD NOW / RUN EXPERIMENT FIRST / KEEP AS-IS /
  DO NOT ADD framework per proposed item. Headline: **no new experiment should be started in this session.**
  CLAUDE.md requires a hashed, git-tagged preregistration (`research/audit/PREREGISTRATION_SPEC.md`) and an
  approved run manifest before any X-series experiment begins, and building the Strategy/Coaching layer itself
  would be a major architecture change requiring explicit approval first (CLAUDE.md: "Major architecture/experiment
  changes: state what/why/affected components/reproducibility impact and get approval first").

### 3.6 Evidence conflicts
- `main.pdf`'s Results section conflicts with `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` by omission: the
  canonical doc is the sole authority on verified metrics, and it contains no entry for any of `main.pdf`'s
  headline numbers. Per CLAUDE.md's own rule ("if this file conflicts with any other document, this file wins"),
  `main.pdf`'s claims cannot currently be asserted.
- `main.pdf`'s architecture conflicts with `CLAUDE.md`'s own architecture section, which documents one PPO policy,
  not two coordinating agents.

### 3.7 Reproducibility gaps
- No config file, no seed, no committed code, and no git commit reference for any XA–XD number.
- No LaTeX/Markdown source for `main.pdf` itself — it cannot currently be rebuilt or diffed against prior versions.
- `capstonePapers/` holds ~10 prior PDF-only versions of what appears to be the same paper lineage (`v8`, `v13`,
  `v13.1`, several "Merged_Final"/"Publish_Grade" variants) with no sources either, so even the paper's own
  revision history is not reproducible from this repo.

### 3.8 Page-budget implications
- Moot until a direction is chosen. A rescoped paper describing only the real single-policy system (Section 1
  above) plus the real Paper-1/2/3 evidence would likely run well under the 20-page Springer limit, since it is
  reusing already-written, already-audited material (`paper/manuscripts/paper1-3`).

### 3.9 Final recommendation table
See `Experiment_Decisions.md` for the per-item ADD NOW / RUN EXPERIMENT FIRST / KEEP AS-IS / DO NOT ADD table.

---

## 3. What I deliberately did not do in this pass

- Did not edit `main.pdf`, any file under `capstonePapers/`, or any frozen/canonical artifact.
- Did not run any experiment, training run, or script.
- Did not invent a Strategy/Coaching architecture, mock results, or filler numbers to make the gap in Section 0
  disappear.
- Did not decide, on the user's behalf, whether to (a) build the real MAS layer and run real XA–XD experiments,
  (b) rescope the paper around the real single-policy system and existing Papers 1–3 evidence, or (c) something
  else. That decision is recorded as open in `Experiment_Decisions.md`.

---

## 4. Immediate next step

This audit is a stopping point, not a continuation into manuscript rewriting. The task brief itself says "Start
with the audit. Do not immediately rewrite the paper." Given the Section 0 finding, the next decision is the
user's: see the three options at the top of `Experiment_Decisions.md`.
