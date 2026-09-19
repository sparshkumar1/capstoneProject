# Phase 0 Decision Lock (2026-09-19)

**Status: LOCKED record of user-approved decisions.** Source: the user's Phase-0 approval message following `RESEARCH_STRENGTHENING_MASTER_PLAN.md`. This file records decisions; it does not add scientific content. Changing any locked decision requires a new dated entry in the change log at the end of this file, approved by the user. Nothing in Phase 0 runs an experiment, retrains a model, changes code logic, changes dependencies or edits a frozen result.

Scope of this lock: Phase 0 only. Phase 1 has **not** been started and requires a separate instruction.

---

## 1. Approved decisions (verbatim in substance)

### Paper 1 (systems)
1. Remove "secure" from the title and framing. Use failure-aware / sandboxed framing.
2. Prepare protocols X1-A (fault injection), X1-B (Qwen authority isolation), X1-C (security oracles), X1-D (test report + latency).
3. Positive/mutation controls are **mandatory** for every oracle.
4. Do **not** implement `FeedbackValidator`.
5. Defect policy: (i) report any defect found; (ii) fix only under a **new tag**; (iii) rerun the **complete relevant campaign** on the fixed build; (iv) retain both builds and both result sets.
6. "Fault-tolerant" stays **conditional** on X1-A evidence.

### Paper 2 (evaluator)
1. The current CrossEncoder remains frozen and retained (`services/evaluator/models/tuned_model2/model.safetensors`, SHA-256 `6a241a55bef24355378db16a6380f03226fc9394312122afa648ec9e03a94450`).
2. Remove "off-the-shelf / zero fine-tuning" wording. Describe it as a **partially fine-tuned derivative with incomplete provenance** unless records are recovered.
3. Send the trainer provenance enquiry (draft only in Phase 0: `MODEL_PROVENANCE_REQUEST.md`).
4. X2-A approved (stored-data re-analysis).
5. X2-B approved: upstream-checkpoint sensitivity + lexical/length baselines. **Primary upstream comparison = mapping-independent R-only metrics.** No composite mapping may be invented or fitted after seeing results.
6. **One** new confirmatory human benchmark. It becomes the confirmatory set; the old 64-case benchmark becomes exploratory/initial evidence. The new benchmark must be: question-disjoint from the old benchmark and all tuning questions; temporally disjoint; independently authored; protected against evaluator-aware answer filtering; properly documented; rated by ≥ 3 fully crossed raters.
7. **No second human round.**

### Paper 3 (adaptive RL, simulation)
1. Reframe as a controlled decomposition: shield vs rules/oracle vs heuristic/controller vs learned policy.
2. PPO is a studied component, **not** the headline claim.
3. X3-0 and X3-A approved. X3-B **conditionally** approved.
4. Equivalence margin **δ = 0.12 MAE**. Superiority margin **m = 0.20 MAE**.
5. **X3-B trigger (frozen before X3-A is run):** run X3-B if X3-A is inconclusive **or** if a method-level PPO claim is to be made. (Operational definition in `X3_PROTOCOL_DRAFT.md` §6.)
6. No PPO hyperparameter tuning. No reward redesign. No second simulator yet.

### Human / ethics
1. Start the institutional/venue enquiry now, in parallel with record recovery; include the planned confirmatory human round.
2. Never fabricate or backdate consent, independence, qualifications or timestamps.
3. Start the trainer provenance enquiry now.
(External contacts are **drafted, not sent** in Phase 0. Sending is a user action.)

### Canonical truth
1. One new authoritative current source: `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`.
2. The two older canonical files are historical/superseded; a supersession record is added; old files are not deleted or edited.
3. `CLAUDE.md` is updated so future sessions cannot revive ρ = 0.6975 as the current human result, or "session" as the Paper 3 statistical unit.

### Scientific corrections (new addendum files only; no frozen file edited)
P0-3 (boundary-saturated/attempted boundary actions, not "0 violations"); P0-4 (563 activations vs 99 action overrides); P0-5 (five-seed guarded volatility 0.186; 0.088 not an aggregate); P1-11, P1-13, P1-14, P1-15 errata.

### Reproducibility / preregistration
1. Environment-lock mechanism for **new runs only**; the current `.venv` is not modified.
2. Run-manifest format (git commit, tag, OS, Python, package versions, hardware, checkpoint hashes, seeds, config hashes).
3. Claim registry skeleton at `research/claims/CLAIM_REGISTRY.csv`, with currently verified claims only (everything else clearly marked).
4. Claim → artifact → script → hash → environment verification structure.
5. **No new experiment may start without a protocol hash and tag.**
6. Prepare both a git-tagged protocol structure and external-preregistration draft material. **Do not submit externally** unless the user explicitly asks.

---

## 2. Prohibited until preregistration is complete (protocol hashed and tagged)

- Running any X1, X2 or X3 experiment, dry-run on confirmatory data, or partial "pilot" of a registered design (harness dry-runs on non-confirmatory fixtures are a Phase 2 activity, after the relevant protocol is drafted and only when approved).
- Retraining or fine-tuning any model; training or evaluating any new PPO/BC checkpoint.
- Modifying evaluator logic, thresholds (θ, dampening, weights, grade thresholds, R mapping), PPO/reward/state/action definitions, guardrail semantics, or the simulator.
- Implementing `FeedbackValidator`; any frontend implementation; any code-logic change.
- Changing dependencies or the current `.venv`; installing packages.
- Authoring or rating any new benchmark item; contacting raters; sending any external message.
- Evaluating the upstream CrossEncoder on any benchmark item.
- Editing, regenerating or deleting any frozen artifact (list below).
- Drafting any manuscript text.
- Populating Zotero.
- Populating the claim registry with manuscript claims beyond currently verified evidence.

Allowed in Phase 0: documentation, provenance, source-of-truth, claim-registry skeleton, protocol drafts, spec documents, draft enquiries, static checks (hashing, `git diff`, file listing, CSV parse checks).

---

## 3. Immutable / frozen artifacts (never edit, regenerate or delete)

Baseline hashes were captured at the start of Phase 0 (366 files, SHA-256) and re-verified at the end (see `PHASE0_CHANGE_MANIFEST.md` §5).

| Path | Note |
|---|---|
| `research/CANONICAL_SCIENTIFIC_TRUTH.md` | Historical/superseded (SHA-256 `d8ac0c0a…571a4a`); never edited |
| `research/CLAUDE_HANDOFF/*` | Includes the handoff `CANONICAL_SCIENTIFIC_TRUTH.md` (`7714dc16…dce9`) |
| `research/papers/*` | Frozen paper material |
| `research/results/*` (paper1/, paper2/, paper3/, top-level result files) | Frozen results |
| `research/experiments/paper2/`, `research/experiments/paper3/` (incl. `frozen_config.yaml`, checkpoints) | Frozen configs and checkpoints |
| `research/data/evaluator_benchmark/final_human_gold.csv` | SHA-256 `363dbe6d848a04fe18be5ef1d30b6bbf63b54248fe758e5e6bd4c27a26c06ce2` |
| `research/annotation/FROZEN_HUMAN_RATINGS/*` | Hash-pinned rater files |
| `research/scripts/*` | Frozen study scripts (`execute_paper1/2/3_study.py`) |
| `research/audit/*` created before Phase 0 (all `CLAUDE_*`, `P0_*`, `P0_P1_*`, `RESEARCH_STRENGTHENING_MASTER_PLAN.md`, and older audit files) | Historical audit record; corrections go in new files |
| `rl/checkpoints/*` | Deployed PPO checkpoints (`seed_123/ppo_final.zip` `2ab8d514…4575`) |
| `ablation/results/*`, existing `experiments/*` results and figures | Legacy results |
| `services/evaluator/models/tuned_model2/*` | CrossEncoder derivative; retained unchanged |
| `research/experiments/paper3/checkpoints/*` | Evaluated PPO checkpoints (`seed_123` `299437ea…24e0`) |

Files created in Phase 0 (listed in `PHASE0_CHANGE_MANIFEST.md`) are new documents. Once tagged with a protocol, a protocol file becomes frozen too.

---

## 4. Open items (not decided by this lock)

Not part of Phase 0 and to be decided later, with the user: X3-A persona generator specification and N; X2-C item counts (set by a precision simulation in Phase 2); the pre-set ρ bound for X2-C; the pre-registration platform if external submission is later requested; venue (TBD; `CLAUDE.md` says target venue is TBD); the ATIS/ICTCS/SmartCom venue plan in the old root canonical file is unconfirmed historical text.

## 5. Change log

| Date | Change | Approved by |
|---|---|---|
| 2026-09-19 | Initial lock | User (Phase-0 approval message) |
