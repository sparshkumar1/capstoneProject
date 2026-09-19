# Preregistration Specification (Phase 0, 2026-09-19)

**Status: specification and draft material only. Nothing was registered externally, no tag was created, no protocol was hashed.** External submission happens only if the user explicitly asks. **Rule (locked): no new experiment may start without a protocol hash and a git tag.**

Two mechanisms, used together: **Part A** a git-tagged protocol structure (always required, immutable, local proof of ordering); **Part B** external-preregistration draft material (optional, adds a third-party timestamp).

---

# PART A — Git-tagged protocol structure

## A.1 Layout (new directories only; nothing under a frozen path)
```
research/preregistration/<EXP_ID>/            # e.g., X3-A
    PROTOCOL.md                # the final protocol (from the corresponding X*_PROTOCOL_DRAFT.md after Phase 2 completion)
    protocol_manifest.json     # SHA-256 of PROTOCOL.md and of every file the protocol depends on (see A.3)
    AMENDMENTS/AMEND-001.md    # dated amendments (A.5)
    DEVIATIONS.md              # deviation log written during/after the run
```

## A.2 Tag naming and rules
- Annotated tag `prereg/<EXP_ID>/v<N>` on the commit that contains `PROTOCOL.md` and `protocol_manifest.json`. The tag message contains the SHA-256 of `PROTOCOL.md` and of `protocol_manifest.json`.
- Tags are never moved, deleted or re-created. Any change after tagging is an amendment (A.5) with a new tag `v<N+1>`.
- A run's manifest (`RUN_MANIFEST_SPEC.md`) cites the tag, the tag commit and the protocol hash; the run preflight **aborts** if the tag is missing, the commit is not an ancestor of the run commit, or a hash differs.
- SUT/build tags for X1 (`sut/X1/build-A`, …) and lock IDs are separate tags recorded in the protocol.

## A.3 Files hashed in `protocol_manifest.json`
`PROTOCOL.md`; configuration file(s); persona table and generator seed (X3); benchmark item file and prompt/generator config (X2-C); adversarial prompt set and scenario/attack tables (X1); analysis script skeleton and its parameters (bootstrap B, RNG seed, thresholds, margins); environment lock (`env_lock_sha256`); frozen-dependency hashes (evaluator weights, checkpoints, gold file); SUT tag/commit; decision notes (e.g., the X3-B method-level-claim decision, the ρ_min value).

## A.4 Freeze procedure (per experiment)
1. Complete every **[FIX IN PHASE 2]** item in the draft; record who reviewed it and when.
2. Confirm the environment lock exists and is verified (`ENVIRONMENT_LOCK_SPEC.md`).
3. Confirm no confirmatory data exist yet (no benchmark scores, no X3 evaluation on generated personas, no upstream outputs, no fault-injection results).
4. Compute the SHA-256 of every dependency file; write `protocol_manifest.json`.
5. Commit; create the annotated tag; record the tag commit and hashes in a dated note in `research/audit/`.
6. Only then may the harness/run start; the first action of a run is writing its manifest with `status: started`.

## A.5 Amendments and new experiments
- **Before data exist:** amendments allowed with a dated `AMEND-nnn.md` (what, why, who approved), a new manifest and tag `v<N+1>`.
- **After any confirmatory data exist:** no amendment may change hypotheses, endpoints, margins, thresholds, exclusions, analysis or stopping rules. Such a change defines a **new experiment** with a new ID, protocol and tag; the original remains reported. Corrections of typographical errors are allowed only if they cannot change any result and are logged.
- **Harness/SUT defects (X1):** handled by the defect policy in `X1_PROTOCOL_DRAFT.md` §2 (new build tag, complete campaign rerun, both retained).

## A.6 Timing requirements (what must be tagged before what)
| Experiment | Tag must precede |
|---|---|
| X1-A/B/C/D | the first fault injection/attack/prompt run on the SUT build (harness dry-runs on fixtures are allowed only after the draft is complete and approved) |
| X2-A | (analysis of stored data the authors have already seen — cannot be confirmatory; registered as exploratory/transparent) |
| X2-B | the first upstream-checkpoint or baseline output on any benchmark data |
| X2-C | authoring of items, distribution to any rater, and any evaluator run on the new items |
| X3-0 | (analysis of stored/replayed frozen data the authors have already seen; exploratory/transparent) |
| X3-A | evaluation of any checkpoint on generated personas; the **X3-B trigger and the method-level-claim decision are inside this tag** |
| X3-B | any retraining; also the user's confirmation of the environment definition |

## A.7 Required contents of every protocol (checklist)
- [ ] Research question and hypotheses (primary, secondary, exploratory clearly separated)
- [ ] Primary/secondary endpoints with exact definitions and units
- [ ] Independent variables, dependent variables, controls (including positive/mutation controls for oracles)
- [ ] Unit of analysis and nesting
- [ ] Margins (X3: δ = 0.12 MAE, m = 0.20 MAE; X2: ρ_min, AUROC threshold, τ_accept; X1: SLAs) and outcome classification rules
- [ ] Sample-size strategy and its computation (with input data)
- [ ] Seeds (training, evaluation, bootstrap, ordering, generator)
- [ ] Statistical tests, CIs (method, B, RNG seed), effect sizes, multiplicity handling (declared primary endpoint; secondary reported as such)
- [ ] Stopping rules and exclusion rules (fixed in advance)
- [ ] Contamination/leakage controls and the ordering of operations
- [ ] Interpretation rules for positive, null and negative outcomes
- [ ] Reporting rules (terminology, scope statements)
- [ ] Artifacts to store; manifest and lock requirements
- [ ] Disclosures (authors built both the evaluator and the benchmark; prior exposure to related frozen results)
- [ ] Reviewer and approval record

---

# PART B — External-preregistration draft material (NOT submitted)

Platform-agnostic content that can be pasted into a registry template (e.g., an open-science registry) if and when the user asks. It must contain **no personal data** and no secrets. An external timestamp supplements, and never replaces, the git tag. If the user selects a platform, the fields below are mapped to that platform's template at that time (the template fields are not assumed here).

## B.1 Common sections (copy per experiment)
1. **Title and authors** (user).
2. **Study description** — one-paragraph plain-language summary.
3. **Prior data / transparency statement** — *Required disclosures:* the authors built the evaluator, the simulator and the PPO code; earlier frozen results exist for Papers 1–3 and were seen by the authors (this is why X2-A and X3-0 are exploratory and X3-A is planned with new personas); the CrossEncoder is a partially fine-tuned derivative with incomplete provenance; the original human ratings have incomplete provenance documentation.
4. **Hypotheses** — from the protocol.
5. **Design** — conditions, controls, positive/mutation controls.
6. **Sampling** — unit, N, sample-size strategy, seeds.
7. **Variables and measures** — endpoints with exact definitions.
8. **Analysis plan** — tests, CIs, effect sizes, margins, classification rules, sensitivity analyses.
9. **Stopping and exclusion rules.**
10. **Contamination controls and order of operations.**
11. **Interpretation rules** for positive/null/negative outcomes.
12. **Exploratory analyses** — listed and labelled.
13. **Materials/artifacts** — hashes, tags, lock, manifest.
14. **Deviation policy** — amendments before data; new experiment after data.

## B.2 Per-experiment registration summaries (content to be finalised in Phase 2)

**X1-A/B/C/D (Paper 1).** *Hypotheses:* per enumerated fault class the SUT meets the pre-specified criteria and the mutant fails them; no LLM path reaches score/difficulty/ranking; each attack is contained in the shipped configuration and breaches under the permissive control. *Endpoints:* per-scenario/attack outcomes from computed oracles (never typed PASS). *Controls:* no-fault runs, mutants, permissive-configuration controls, benign prompt pairs. *Unit:* scenario/attack (prompt for X1-B). *Sample:* dependency-derived scenarios; deterministic 5–10 repetitions; N ≈ 30 randomised timings for timing-sensitive classes (Wilson 95 % CI); ≥ 30 prompts; 9 attacks × 5. *Stopping:* fixed. *Contamination:* oracles hashed before running; SUT tag fixed. *Interpretation:* defect policy; "fault-tolerant" only if X1-A passes; no "secure".

**X2-A (Paper 2, exploratory).** *Question:* sensitivity of the frozen ρ to clustering, raters, categories, overlap. *Analyses:* two-level cluster bootstrap, leave-one-question-out, per-category, within-question, rater leave-one-out, adversarial false-accept (τ_accept fixed from the documented grade boundary), bias by category/length. *Status:* exploratory; existing data already seen.

**X2-B (Paper 2).** *Hypotheses:* composite/R > lexical baselines on ρ and AUROC; derived–upstream difference estimated without a directional hypothesis. *Primary:* mapping-independent R-only ρ, τ-b, AUROC. *No composite mapping* for the upstream arm unless frozen in advance and label-free. *Unit:* question (cluster); two-level bootstrap B ≥ 10 000. *Order:* metrics fixed before the first upstream output; one run per dataset.

**X2-C (Paper 2, confirmatory).** *H1:* composite ρ cluster-CI lower bound > ρ_min; *H2:* R-only ≥ composite; *H3:* composite false-accept < R-only's. *Design:* question-disjoint, temporally disjoint stratum + bank-sampled stratum, independently authored, no evaluator-aware filtering, ≥ 3 fully crossed blind raters, score-after-freeze. *Sample size:* precision simulation (CI half-width ≤ 0.12). *Stopping:* fixed item list; no second round. *Interpretation:* as in the protocol.

**X3-0 (Paper 3, exploratory accounting).** Stored-data corrections (boundary-saturated actions, activations vs overrides, five-seed volatility, corrected ablation rows, persona-level paired differences and SD).

**X3-A (Paper 3).** *H1:* PPO+G vs Constant-Same+G persona-level ΔMAE; equivalence δ = 0.12, superiority m = 0.20; classification rule and **X3-B trigger** frozen. *Conditions:* Fixed, Const-Same, Random, Heuristic, Oracle-rule, proportional controller, PPO, each ± shield; state-shuffle/constant PPO; guardrail-rule ablation. *Unit:* persona × training seed (two-way cluster bootstrap). *Sample:* ≥ 24 generated personas, 20 evaluation seeds, 5 checkpoints. *Stopping:* fixed. *No tuning.*

**X3-B (Paper 3, conditional).** Trigger per X3-A; reward/hyperparameters unchanged; consistent environment; budget series; ≥ 10 training seeds; PPO vs behaviour cloning vs none, shield in-loop on/off.

## B.3 Not to be put in an external registration
Personal data, rater identities, contact details, API keys, unpublished third-party material, and any hypothesis not already fixed in the tagged git protocol.

## B.4 Status
Drafts of the content exist (this file and the three protocol drafts). No account was created, nothing was uploaded, no registration was requested. Decision pending with the user: git tags only, or git tags plus an external registry (which would require the user to create the account and submit).
