# PREPAIred — Research Strengthening Master Plan (2026-09-19)

**Status: planning document only.** Nothing was run, retrained, tuned, deleted or modified. No frozen artifact was touched and no manuscript text was written. Every experiment below is a *specification*; none may start before the approvals listed in the last section.

**What this is.** An independent review of the proposed direction (Part I), followed by the master plan built on that review, not on the proposal (Parts II–VII). Where I disagree with the proposal, I say so and the plan follows my recommendation.

**Evidence labels.** *(frozen)* = read from a frozen file. *(code)* = read from source this pass. *(audit)* = established in `P0_*` / `P0_P1_*` / `CLAUDE_*` files earlier, not re-verified this pass. *(arith)* = my arithmetic on numbers already in the repo. *(estimate)* = my judgement, not measured. Anything unlabelled is a design recommendation.

**Sources read this pass (beyond the earlier audit files).** `research/experiments/paper3/frozen_config.yaml`; `research/scripts/execute_paper3_study.py` (persona table, heuristic, evaluation loop); `rl/env/interview_env.py` (oracle rules, reward mode, docstring); `research/scripts/build_comprehensive_benchmark.py` (first 70 lines: how the 64 answers are constructed); `P0_P1_DECISION_PLAN.md`, `P0_P1_USER_DECISIONS.md`, `P0_3_BOUNDARY_FORENSIC.md`.

---

# PART I — INDEPENDENT REVIEW OF THE PROPOSED DIRECTION

## I.0 Verdict table

| # | Your proposal | Verdict | One-line reason |
|---|---|---|---|
| 1 | Paper 1: full new fault + Qwen + security campaign | **AGREE WITH MODIFICATION** | A campaign is what turns Paper 1 into a testable systems paper, but the drafted design is too big in one place (30 repeats of deterministic faults) and missing the one control that makes it credible (positive/mutation controls). Drop "secure" from the title regardless. |
| 2 | Paper 2: keep derived CrossEncoder, correct provenance, remove "off-the-shelf", recover records | **AGREE** | Correct and cheap. Add a per-checkpoint provenance card. |
| 3 | Paper 2: strongly consider the upstream sensitivity run | **AGREE WITH MODIFICATION** | Worth doing, but only with a pre-frozen analysis plan; the composite is *not* rank-invariant to the R mapping, so "rank-based primary" applies to R-only only. It should also run on the new benchmark, not just the old 64. |
| 4 | Paper 2: a new, larger, documented human benchmark | **AGREE WITH MODIFICATION** | Yes, but as a *confirmatory* set designed for question-disjointness, temporal disjointness and answer-source independence, not "more of the same". Size alone would repeat the construction artefact. Design it once and merge it with P0-7 route C. |
| 5 | Paper 3: keep PPO as a genuine research objective | **DISAGREE as the central *claim*; AGREE as a studied component** | The frozen evidence cannot support a PPO claim, and structurally (oracle-imitation reward, undertrained checkpoints, MAE metric that the reward never optimises) a PPO win is unlikely. The strongest paper is a controlled *decomposition* of what guardrails, rules and PPO each contribute. |
| 5b | Paper 3 Stage 1 as drafted | **NEEDS SUBSTANTIAL MODIFICATION** | Persona-only bootstrap ignores training-seed variance; evaluation-only on five 24 576-step checkpoints cannot license "PPO doesn't help"; missing oracle, state-shuffle, behaviour-cloning and equivalence-margin controls. |
| 6 | Paper 3 corrections for P0-3/4/5 by analysis | **AGREE** | Confirmed. Add P1-13/14/15. |
| 7 | P0-7 sequence: records → institution → new round? | **AGREE WITH MODIFICATION** | Run the institutional enquiry *in parallel* with the record search and include the *planned* new round in it, so consent is designed once. |
| 8 | P1-12: fix stale canonical truth first | **AGREE** | Add a machine-checkable superseded-values registry and note that `CLAUDE.md` itself carries two stale statements. |
| 9 | Technology: no churn | **AGREE** | No technology is implicated. Only additions: an environment lock and run manifests for *new* runs (needs approval; the `.venv` violates pins). |
| 10 | Frontend after science is locked | **AGREE WITH MODIFICATION** | Documentation/accessibility work is safe to run in parallel on a separate branch; anything that touches backend/evaluator/score presentation waits, and there must be a code freeze on the system under test during Paper 1 experiments. |
| 11 | No manuscript drafting yet | **AGREE** | Gates in Part XII. |

## I.1 Paper 1 — is the full campaign necessary?

**Verdict: AGREE WITH MODIFICATION.**

*Evidence.* Fault "10/10" and Qwen "5/5" are literal PASS strings (evidence classes A×1/B×5/C×4 and B×3/C×2) *(audit)*. Of nine security runs, four have discriminating outcomes *(audit)*. The 213-test count has no log. Concurrency and latency are real but narrow. `FeedbackValidator` does not exist *(audit)*.

*Is the campaign necessary?* Not for a *correct* paper: the narrow paper (design + concurrency + latency + partial sandbox evidence) is honest but is a modest systems description. It **is** necessary for the paper's stated identity ("secure and fault-tolerant"): those adjectives are properties, and a property claim without a discriminating test is the first thing a systems reviewer will reject. Value/cost: high for fault and security; low for Qwen QWN-04 (see below).

*Strongest alternative.* A **minimal rigorous core** instead of the full drafted set:
1. **Fault injection derived from the dependency graph**, not a hand-picked list of ten: every external dependency (Qwen, evaluator, Docker daemon/compiler, SQLite, WebSocket, audio/STT) × failure mode (down / slow / corrupt output). This is the strongest defence against "your ten faults are arbitrary".
2. **Positive (mutation) controls for every oracle.** For each scenario, run a deliberately broken variant (handler disabled, or container started with `--network bridge` to a *local canary*) and show the harness reports FAIL. Without it, a harness that can only say PASS is exactly the defect found in the frozen script.
3. **Qwen authority isolation = mostly a structural claim.** Test it with (a) a static/AST check that no LLM output path writes score, difficulty or `is_best`, and (b) a bit-identity test of the evaluator score and orchestrator state with vs without adversarial prompts. Do **not** build a `FeedbackValidator` in order to pass QWN-04: that changes the system under test to satisfy the test. Either the paper says feedback is unvalidated, or the validator is a separately approved, separately tagged change.
4. **Security with the five-way separation** (execution / containment / status / host impact / resource impact) and canaries; a stored JUnit report.

*What a skeptical reviewer would say about my earlier draft.* Where the earlier plan (`P0_P1_DECISION_PLAN.md` §8.2) said "≥30 independent trials per scenario, Wilson lower bound 0.887 at 30/30", this is **statistically misleading for deterministic injections**: repeating a deterministic scenario 30 times measures flakiness, not a sampling proportion over a population of faults; the Wilson interval would pretend to a population that was never sampled. I therefore **revise my own earlier design**: deterministic scenarios get 5–10 repetitions reported as counts (flakiness check); only scenarios whose outcome depends on *timing* (lock contention, mid-request socket reset, slow-Qwen timeout) get randomised injection points with N ≈ 30 and a Wilson interval, where the interval actually describes a sampled timing space. The inferential scope is "the enumerated fault classes on this build on this machine", never "fault-tolerant in general".

*Hidden problem.* If the campaign finds a real defect, fixing it changes the code under test. Pre-specified **defect policy**: report all failures as found; fix only under a new tag; re-run the *entire* campaign on the fixed build; report both builds. Never edit the harness or the criteria after seeing results.

*Title.* Drop "secure" regardless: nine attacks in one harness cannot support it, and "sandboxed" is what the flags describe. Keep "fault-tolerant" only if the campaign passes its pre-specified criteria, and then scoped ("for the enumerated fault classes"); otherwise "failure-aware".

*Necessity:* scientifically necessary **if** a fault or security property stays in the title; strongly beneficial otherwise.

## I.2 Paper 2 — provenance correction

**Verdict: AGREE.** "Off-the-shelf" is false for the weights (embeddings and layers 0–3 identical, layers 4–5/pooler/head changed, 16.28 % of parameters) and independently for the R mapping `(raw−0.20)/0.70`, which presupposes the derivative's output range *(audit; app.py:163-168)*. The file is hash-pinned, so results reproduce as a file. Correction plus record recovery is **scientifically necessary and nearly free**. A skeptic will ask "what was it fine-tuned on and does it overlap the benchmark?" — only the trainer can answer; ask now. Add a provenance card (N6) for every checkpoint so this cannot recur.

## I.3 Paper 2 — upstream-checkpoint sensitivity

**Verdict: AGREE WITH MODIFICATION. Strongly beneficial; cost small (evaluation only).**

*Why it is worth doing.* Both outcomes are informative: if the upstream model scores about the same, the fine-tune is irrelevant and the paper can rest on a **public, reproducible model**, which removes P0-1 as a reviewer objection entirely; if the derived model is clearly better, the fine-tune matters and the undetermined-leakage caveat becomes central, which the reviewer would otherwise discover unaided.

*Hidden methodological problem in the proposed plan.* The earlier plan says "rank-based primary because Spearman is invariant to monotone maps". That is true for **R-only ρ** but **not for the composite** `0.15·S1 + 0.35·S2_eff + 0.50·R`: R is combined linearly with S1/S2, so a different R scale changes the composite ranking, and the `R ≤ 0.30` dampening threshold is on the mapped scale. Therefore:
- **Primary:** R-only Spearman ρ and AUROC (correct vs incorrect answers), both mapping-free.
- **Secondary:** composite with a **label-free, pre-specified** mapping (e.g., align the upstream score distribution to the derived checkpoint's on the *benchmark answers themselves without using any gold labels*, by quantile matching, fixed before running). No fitting to gold, no choosing among mappings after seeing results.
- Report per-question and cluster-bootstrap CIs (Part V).

*Forking-paths risk.* High if the mapping is chosen after viewing gold-correlated output. Mitigation: freeze the analysis plan (hash + tag) first, run once, report all arms.

*Also run it on the new benchmark* (X2-C) so the comparison is not confined to eight questions.

## I.4 Paper 2 — does it need a new human benchmark?

**Verdict: AGREE WITH MODIFICATION.** Strongly beneficial; effectively necessary for any *validity* claim beyond "pilot-scale".

*Evidence.* 64 cases = 8 questions × 8 constructed answers, 10 categories *(audit; `build_comprehensive_benchmark.py`: topic list, per-question categories concise/verbose/partial/incorrect/verbose-wrong/keyword-stuffed/misconception/contradictory/paraphrase/suboptimal, all authored in one script)*. Human reliability is driven by the construction categories (η² ≈ 0.98–0.99) *(audit)*. Pooled ρ = 0.381, case-bootstrap CI [0.158, 0.577]; question-cluster CI [0.302, 0.589] *(audit, diagnostic)*. Four of eight questions overlap the pilot on which θ = 0.30 and the dampening were tuned; ρ = 0.709 there vs 0.425 on the other four (exploratory, unpowered) *(audit)*. Within-category ρ is mixed or negative for several categories (n = 2–8 each) *(audit)*.

*What is wrong with "more data".* Simply authoring more of the same constructed categories would (i) reproduce the construction artefact (ρ largely reflects ordering between categories), (ii) still be author-generated, and (iii) not address leakage or the tuning overlap. What helps is not N but **structure**:

| Design property | Why it matters | How |
|---|---|---|
| **Question-disjoint from every tuning set** | Removes the pilot-overlap objection | New questions, none from the N=20 pilot or the 8 existing |
| **Temporally disjoint stratum** | Only design that decisively addresses undetermined fine-tune leakage | ~half the questions and *all* reference answers newly authored after the checkpoint's commit date (2026-04-13), never posted publicly, not derived from the legacy bank |
| **Bank-sampled stratum** | Deployment relevance: the product asks bank questions | ~half the questions drawn from the deployed bank, disjoint from the pilot/benchmark; leakage status undetermined and labelled |
| **Answer-source independence** | Author-built answers can be (unintentionally) built to be easy for the scorer | Answers written by someone who has never seen evaluator output, or generated by a fixed, recorded generator (model, prompt, seed) and **not filtered**; a constructed-contrast subset is kept for adversarial validity, and reported separately |
| **Score-after-freeze ordering** | Prevents selecting items after seeing scores | Freeze evaluator (hash) → author answers → blind human rating → freeze gold → run evaluator **once** |
| **Documented provenance** | Solves P0-7 for the confirmatory set | Consent, roles, ledger, timestamps (Part X) |

*Size (rationale, not a guess).* Fix N by **precision simulation before data collection**, using the 64-case variance components: choose the number of questions so that the *question-cluster* bootstrap CI for ρ has half-width ≤ 0.12 at the observed effect size. A rough scale, unverified *(estimate)*: with 8 clusters the CI half-width is ≈ 0.14 by cluster bootstrap; reaching ≤ 0.12 with real between-question variance plausibly needs on the order of 20–30 questions × 8 answers (≈ 160–240 items). The final number comes from the simulation, written into the pre-registration.

*Primary or sensitivity?* **Primary confirmatory set = the new benchmark; the existing 64 become "exploratory/initial" evidence.** Reason: θ and the dampening were tuned on a pilot that overlaps four of the old questions, so the old set is not clean confirmation. The old set's numbers remain valid, hash-pinned results and stay in the paper, labelled.

*If P0-7 routes to a new round anyway (likely), design the new benchmark once, not two rounds.* That is why this decision must be merged with I.7.

*Skeptic's remaining objections:* still one domain family (DSA/systems); still simulated candidates unless volunteers answer; raters still few. Not fixable within scope; disclose.

## I.5 Paper 3 — should PPO remain the central contribution?

**Verdict: DISAGREE as the central claim.** Compare the four routes:

| Route | Supportable now? | What it needs | My judgement |
|---|---|---|---|
| Current frozen evidence as a PPO paper | **No** | — | Const-Same + guardrails = 0.673 = PPO + guardrails 0.673–0.687; 5/125 sessions differ; heuristic 0.473 beats every PPO variant *(audit)* |
| Re-framed guardrail/adaptive-control paper | Yes | Corrections only | Honest, small; the PPO story becomes a footnote |
| Controlled PPO-contribution study | Only with a better design (below) | New pre-registered study | Necessary if any PPO statement is kept |
| Broader simulation-policy comparison | Yes, with controls | Same study, more policies | **Best fit** — merges the two above |

**Recommended framing:** *a controlled decomposition of what each layer — trivial policy, rule oracle, heuristic, guardrail shield, learned policy — contributes to simulated difficulty control.* PPO is a studied component; the claim survives any outcome (positive, null, negative). This is a better paper than a PPO-superiority paper because it is robust to the likely result and it uniquely surfaces the guardrail-vs-learning confound that most adaptive-difficulty papers do not test.

**Why a PPO win is structurally unlikely *(code, config)*:**
1. **The reward is largely oracle imitation:** `decision_alignment: 0.60` = 1 if action equals a hand-coded rule oracle (`oracle_action_from_obs`, rules R1–R7), plus `outcome_delta: 0.30`, `multimodal_shaping: 0.10`, `stability_penalty: −0.10`. A policy trained mainly to match a rule cannot be expected to beat rules on the rules' own criterion; only the 0.30 outcome term could move it beyond the teacher, and nothing in the frozen data isolates that term.
2. **The evaluation metric is not the training objective.** Evaluation is mean |difficulty − persona target|. The reward never mentions the target.
3. **The task is nearly skill estimation.** The five persona targets are all reproduced by `round(10·skill)/2` *(arith: 0.20→1.0, 0.30→1.5, 0.60→3.0, 0.80→4.0, 0.88→4.5)*, i.e. target ≈ 5 × skill. The frozen Heuristic (`perf>0.75 & diff<5 → Harder; perf<0.40 & diff>1 → Easier; else Same` *(code)*) is boundary-aware and threshold-tuned to this mapping. Its win over PPO says as much about the persona/target design as about PPO.
4. **The checkpoints are small-budget:** `total_timesteps_per_seed: 24576` = 12 rollouts of 2 048 steps *(frozen config)*. A null result on these five checkpoints says nothing about PPO as a method; a reviewer will call them undertrained.
5. **Train ≠ evaluation environment** (T=15 continuous 0.1 steps vs T=10 integer ±1) *(audit)*.

**Where your Stage 1 design is wrong or incomplete** (I.5b below).

## I.5b Stage 1 as drafted

| Element | Assessment |
|---|---|
| Persona-level unit | **Right**, and stronger than session-level. But persona is one of *two* random factors: the five training seeds are the other. A persona-only bootstrap treats the five checkpoints as if they were one fixed policy. Use a **two-way cluster bootstrap (persona × training seed)**; with 5 training seeds the seed dimension will be wide — say so. |
| ≥ 24 pre-specified personas from a generator | Right, with two additions: the generator must vary the non-skill traits that matter (confidence bias, hesitation/anxiety) with target set by the *documented* rule, **and** the five original personas must be flagged as the training-distribution subset, because personas outside them test *generalisation of the checkpoint*, which is a different estimand from "PPO's contribution". Report both strata. |
| 20 evaluation seeds/persona | Adequate for within-persona noise; the persona/seed count sets the CI, not the eval seeds. |
| Conditions: Fixed, Const-Same, Random, Heuristic, raw PPO, PPO+G | Missing **Const-Same+G, Random+G, Heuristic+G** (the guardrail effect must be crossed with every base policy), the **oracle rule policy (raw and +G)** (the reward's teacher — the natural ceiling), and a **proportional/estimator controller** (difficulty ≈ 5·running mean perf), which is what the persona rule invites. |
| Missing causal control | **State-shuffle / state-ablation evaluation** (evaluation-only, existing checkpoints): feed PPO permuted or constant observations; if MAE is unchanged, PPO is not using state. This isolates "PPO learned state-dependent behaviour" from "PPO's outputs are 67–96 % Same" directly. |
| Missing control | **Behaviour-cloning of the oracle** (a small supervised classifier on oracle labels): if BC ≈ PPO ≈ oracle, RL machinery adds nothing over supervised distillation. |
| Guarded/raw comparisons | Right; both *within* base policy. |
| "No post-hoc tuning" | Right. Extend to margins and endpoints (fixed in advance; see X3-A). |
| Interpretation of a null | A null CI that includes zero is **not** "no contribution". Pre-specify an **equivalence margin** δ and claim "no detectable contribution" only if the whole CI lies within ±δ. Candidate δ = 0.12 MAE (10 % of the Fixed-baseline error 1.200); to be fixed with you. |
| Stage 1 evaluation-only + Stage 2 conditional | The conditional creates a forking path: if Stage 2 is decided after seeing Stage 1, that is a data-dependent design. Pre-specify the rule *now* ("Stage 2 runs iff …") or run the whole design as one pre-registered study. Retraining is cheap computationally for a 6-D MLP policy *(estimate: tens of minutes to a few hours for ~10⁶ steps on CPU, unmeasured)*; the cost is design discipline and your approval, not compute. |
| Estimand mismatch | Because the reward is imitation, the fair PPO question has **two** endpoints: (a) *agreement with the oracle* (what it was trained for) and (b) *tracking MAE* (what the paper reports). Report both; do not judge PPO on (b) alone. |

**Stage 2 recommendation.** One pre-registered retraining study in an environment **consistent with evaluation** (T and difficulty grid), reward/state/action **unchanged** (so the causal question stays "what does PPO add under this reward"), a **training-budget series** (e.g., 25 k / 100 k / 500 k steps, fixed in advance, same hyperparameters for every condition, ≥ 10 training seeds), guardrails-in-the-loop vs post-hoc, and the BC control. An **outcome-only reward arm** is a *different research question* (P1-5) and should be labelled as a separate optional study, not folded in as an extra arm here (forking paths). It requires your explicit approval because it changes environment/training (CLAUDE.md).

## I.6 Paper 3 corrections (P0-3/4/5)

**Verdict: AGREE.** Confirmed from code and frozen files: `"constraint_violations": 0` is a literal at `execute_paper3_study.py:774, 886, 895`; the same script's counter records *attempted* out-of-range actions before the clamp; the frozen seed CSV records 26/71/41/33/61 = 232 *(audit; code re-read this pass via P0-3)*. 563 = rule activations, 99 = action changes *(audit)*. 0.088 = seed 123; five-seed guarded volatility 0.186 vs heuristic 0.160 *(audit)*. Additions: report P1-13 (persona-level, not session-level), P1-14 (leaked loop variable in the Safety Shield ablation rows: interv 112 / viol 46/0 instead of 563/232), P1-15. Hidden problem worth stating: because the persona targets are ≈ 5 × skill, "volatility lower than the heuristic" partly measures "did not adapt" (Const-Same+G volatility 0.080; PPO+G volatility 0 on the two high-skill personas) *(audit)*.

## I.7 P0-7 — human provenance sequence

**Verdict: AGREE WITH MODIFICATION.** Records-first is right; the institution enquiry should not wait for it. Send the institutional/venue question **now** and include the *planned* new round in it (consent form, roles, compensation, data handling), so the confirmatory round is designed once against the institution's actual requirement. Serial sequencing costs weeks and may force two rounds. Never fabricate or backdate consent, independence or blinding statements; a present-day statement is dated and labelled retrospective. I infer no misconduct from the missing records *(audit)*.

## I.8 P1-12 canonical truth

**Verdict: AGREE, with additions.** The root `research/CANONICAL_SCIENTIFIC_TRUTH.md` (declared sole authority by `CLAUDE.md`) still states ρ = 0.6975 (N=20); the handoff copy states 0.3812 (N=64) *(audit)*. `CLAUDE.md` itself carries two stale statements that would resurrect old values in future sessions: "Human evidence is 1 rater, N=20 (rho 0.6975)" and "Paper 3 statistical unit is the session, not the seed" (the audit shows persona is the true unit). These edits need your approval (Part IX); this pass changes neither.

## I.9 Technology stack

**Verdict: AGREE — no swaps.** Nothing in the findings implicates SBERT, FAISS, the CrossEncoder family, Gymnasium, SB3, Docker or SQLite. Every failure found is a reporting, analysis, controls or provenance failure. Additions that have a reproducibility rationale are in Part XI. One observation that is a *method* control, not a technology change: for a 6-D state, 3-action, 10-turn problem with an imitation-heavy reward, behaviour cloning and simple controllers are the natural comparators for PPO; they belong in the study as controls.

## I.10 Frontend / product

**Verdict: AGREE WITH MODIFICATION.** Not a science blocker; the audit found ≈ zero accessibility hooks (aria-live ×2, aria-label ×1) and two frontend test files *(audit, source text only, app not run)*. Safe documentation/accessibility work can proceed on a separate branch/worktree while experiments run, **provided** it does not touch `apps/backend`, `services/`, `agents/` or `rl/` (the Paper 1 system under test). No paper may claim UI properties (accessibility, graceful failure messaging) that were not tested.

## I.11 Cross-cutting: where I think the proposal is wrong or incomplete

1. **Paper 3 as PPO-centred is the weakest part of the proposal.** The reward design, the training budget, the metric mismatch and the persona/target rule together make the PPO question uninformative in its current form. Reframe the contribution.
2. **The proposal has no controls for the harnesses themselves** (Paper 1 oracles) — the exact failure of the frozen script. Positive controls are non-negotiable.
3. **Two human rounds must not happen.** P0-7 route C and the "larger benchmark" are one design decision.
4. **The Paper 2 composite < R-only (ρ 0.381 vs 0.483; S1+R 0.488) *(audit)* is unaddressed by "more data".** A new benchmark can also fail to justify the composite. The composite's defensible role is adversarial robustness — test that specifically (false-accept rate on keyword-stuffed/misconception/contradictory items), pre-specified as a secondary endpoint (Part V). Existing stored data can already show whether that story holds; it should be computed before the new round is designed.
5. **"Recover training provenance" is one person's answer** and may fail; the plan must not depend on it. Temporal disjointness of new items is what makes it non-blocking.
6. **A new benchmark can create new leakage/selection bias** through authorship (answers built with the evaluator in mind), through LLM-generated answers being stylistically uniform, through reference answers that the S2/FAISS component can retrieve, and through rater contamination. Each is controlled in X2-C.
7. **Fixing Paper 1 defects without a policy** invites post-hoc changes; a defect policy is in I.1.
8. **Statistical language:** "≥ 0.887 lower bound at 30/30" and "PPO CI includes 0 so no effect" are both over-reads (deterministic repetition; absence of evidence).

## I.12 Experiments I recommend NOT running

| # | Experiment | Why not |
|---|---|---|
| N1 | Re-run of the frozen Paper 1 script | Reprints the same literal PASS strings; presenting it as a rerun is a false claim |
| N2 | 30 repetitions of *deterministic* fault injections + Wilson CI as "evidence" | Repetition ≠ sampling (I.1) |
| N3 | Building a `FeedbackValidator` in order to pass QWN-04 | Changes the system to satisfy the test; a separate approved change if wanted |
| N4 | Option C (re-fine-tune from scratch) or Option D (switch the primary evaluator to upstream) | New model with no labelled data, or a post-hoc change of the primary result |
| N5 | PPO hyperparameter search / reward tuning inside Paper 3's confirmatory study | Forking paths; any tuning is a separate, labelled study |
| N6 | More hand-authored personas *claimed* as generalisation | Same author, same simulator ⇒ same misspecification; only a second, differently-built candidate model addresses that |
| N7 | Tuning θ, the dampening or weights on the new benchmark | Destroys its confirmatory status |
| N8 | Large expansion of same-category constructed answers | Repeats the construction artefact |
| N9 | LLM-as-judge comparison as a *headline* | Only worth doing if the paper claims superiority over LLM judging; otherwise frame as a design choice (determinism, no LLM authority) |
| N10 | Re-running the old 64-case evaluation "to be safe" | Frozen results reproduce from hashes; record library versions instead |

## I.13 Experiments/analyses you did not propose that would materially help

| # | Addition | Paper | Type | Value |
|---|---|---|---|---|
| A1 | Mutation/positive controls for every Paper 1 oracle | 1 | new (harness) | Very high |
| A2 | Dependency-graph enumeration of the fault set | 1 | design | High |
| A3 | Adversarial false-accept analysis (keyword-stuffed / misconception / contradictory items scored above partial-correct), composite vs R-only vs S1 | 2 | **stored data** | High — tests the only defensible reason to ship the composite |
| A4 | Lexical/length baselines (TF-IDF cosine, BM25, token overlap, length-only) on the 64 cases | 2 | evaluation-only | High — the answer to "does it beat keyword matching?" (keyword-stuffed items are in the benchmark) |
| A5 | Rater leave-one-out sensitivity of ρ | 2 | stored data | Medium |
| A6 | Oracle-policy, proportional-controller, Heuristic+G and rule-ablation (each of G1/G2/G4/G5 on/off) conditions | 3 | evaluation-only | Very high |
| A7 | State-shuffle evaluation of existing checkpoints | 3 | evaluation-only | Very high |
| A8 | Behaviour-cloning control | 3 | small training | High |
| A9 | Second, differently built simulated candidate (e.g., IRT-style response model with drift) | 3 | optional | Medium |
| A10 | Persona-level pilot variance extracted from frozen files for sample-size planning | 3 | stored data | Needed for the pre-registration |
| A11 | Claim registry with recomputation (Part VIII) | all | tooling | Very high |

## I.14 Claims that remain too strong even after the proposed fixes

- Paper 2: "validated evaluator" — at best "moderate rank agreement on constructed answers"; also "safety-hardened" until A3 supports it.
- Paper 3: any statement about learners, learning gains, or "adaptive difficulty benefits" — simulation only, author-defined personas and targets.
- Paper 1: any general "secure"/"fault-tolerant" wording; "isolated" for Qwen unless the validator/structural tests exist; single-machine scope for concurrency/latency.
- All: "independent human experts" (P0-7) until records establish it.

---

# PART II — STATUS OF EXISTING RESULTS

| Category | Items |
|---|---|
| **Frozen results that remain scientifically valid (as the numbers they are)** | Paper 2: 64-case score table, ICC/α of the human ratings (as computed), ablation numbers, hash-pinned gold and model (with corrected provenance). Paper 3: per-seed MAE/oscillation/volatility values and `paper3_seed_results.csv` counts (232 attempted boundary actions, 563 activations as counted). Paper 1: concurrency/persistence (scope-limited), latency percentiles, the nine executed attack runs' raw outputs, the four discriminating security outcomes. |
| **Useful only as historical/diagnostic evidence** | Paper 1 fault (10/10) and Qwen (5/5) tables (design-level handling matrix, not results); the `constraint_violations: 0` summary rows; Paper 3 single-seed-123 "main" comparison; the pilot N=20 ρ = 0.6975 (pilot label only); N-session pooled tests (pseudo-replicated); Paper 3 const-Same/random diagnostics (post-hoc replay); Paper 2 overlap-subset and per-category numbers (exploratory). |
| **Claims that must be withdrawn** | "off-the-shelf / zero fine-tuning"; "0 violations / eliminates 100 % out-of-bounds"; "563 interventions"; "volatility 0.088 vs heuristic 0.160 / smoother"; "PPO improves tracking" (attribution); Paper 1 "10/10 faults recovered", "5/5 Qwen boundaries verified", "9/9 contained", "213 tests passed"; "100 % acoustic insulation"; "independent expert raters / committee / approved"; the long commit hash `b7cad49b6b7a…` (real: `b7cad49529c3…`, tag `v1.0-paper3-complete`). |
| **Claims that can be strengthened by new evidence** | Paper 2 evaluator validity (new confirmatory benchmark, upstream sensitivity, baselines, adversarial false-accept); Paper 3 PPO/guardrail attribution (controlled decomposition); Paper 1 fault-tolerance and sandbox containment (campaign with positive controls). |
| **New experiments that will create new frozen result sets** | X1-A…D (Paper 1 campaign), X2-B/C (Paper 2), X3-A/B/C (Paper 3). Each gets a new config, a new results directory, a new git tag, and hashes in the registry. None overwrites an existing frozen path. |

---

# PART III — PHASE 0–5 EXECUTION ORDER

| Phase | Goal | Contents | Gate to leave |
|---|---|---|---|
| **0 — Decisions, controls, freezes** (no science) | Remove ambiguity; start slow processes | User approvals (last section); start P0-7 record search **and** institutional enquiry; ask the model trainer for provenance; create the supersession note and superseded-values registry; errata/addenda in *new* files (P0-1/3/4/5, P1-11/14); decide pre-registration venue (git-hash tag ± an external registry); approve the environment-lock plan; declare code freezes | All Phase-0 approvals recorded; enquiries sent |
| **1 — Stored-data analyses** (no new data) | Correct what can be corrected, and learn what the experiments need | Paper 3 corrected tables (P0-3/4/5, persona-level, P1-13/14/15) and persona-level pilot variances (A10); Paper 2 clustering/leave-one-question-out/per-category/rater-LOO/adversarial false-accept (A3, A5); Paper 1 claim-survival table and latency re-analysis. All as new scripts + new result files, hashed | Analyses reviewed; results informing designs |
| **2 — Pre-registration and construction** | Freeze designs before any confirmatory data exist | Write and hash protocols X1–X3; build harnesses and *dry-run them on non-confirmatory fixtures*; build the persona generator; precision simulation for the new-benchmark N; author new questions/references (temporal stratum) and answers under the independence rules; consent/ethics design per institution; environment lock | Each protocol tagged; harness dry-runs demonstrate positive controls can fail |
| **3 — Execute** | Generate confirmatory data once | Order: X3-A (cheap, informs X3-B via its **pre-specified** rule) → X3-B; X1-A…D; X2-B (baselines + upstream on the old 64); X2-C human round → gold freeze → evaluator run | Each experiment closed per its stopping rule; failures reported |
| **4 — Analysis, freeze, registry** | Convert results to registered claims | Run analysis scripts unchanged; write new frozen result sets; tags; fill the claim registry; verify recomputation tiers; errata for any changed claim | Cross-paper reproducibility gate (Part XII.4) |
| **5 — Readiness review** | Independent check before drafting | External-style adversarial review against Part VII; only then manuscript drafting may begin | Per-paper publication-readiness gates (Part XII) |

---

# PART IV — PAPER 1 PLAN

**Central research question.** Which safety and failure-handling properties of the multi-agent interview-assessment architecture (sandboxed code execution, LLM-authority isolation, persistence, evaluator) actually hold under adversarial and fault conditions, measured with oracles that can fail?

**Current evidence.** Real: concurrency (0 lock errors, 0 isolation violations up to 25 threads, no evaluator/LLM in the loop), latency (median 404.6 ms, mean contaminated by a 26 s outlier, n=20), nine attack runs (four discriminating), sandbox flags in code, unit tests for evaluator failure / Qwen unreachable / Docker unavailable / empty input *(audit)*.

**Unsupported/weak claims.** "10/10 faults recovered", "5/5 Qwen boundaries", "9/9 contained", "213 passed", "secure", "fault-tolerant" as measured properties, `FeedbackValidator`-based statements.

**Recommended final framing.** A *failure-aware, sandboxed* multi-agent architecture with a **preliminary, scoped systems evaluation** (or "fault-tolerant" only after X1-A passes). Contribution = architecture + a reusable, falsifiable evaluation harness + honest defect reporting. It is an engineering/architecture paper; do not dress it as a security or reliability guarantee.

**Evidence needed for the final claims.** Discriminating, computed PASS/FAIL per scenario with positive controls; stored logs, JUnit report, environment manifest; scoped statements.

| | |
|---|---|
| **Mandatory experiments** | X1-A fault-injection core (dependency-graph derived, mutation-controlled); X1-C security campaign with five-way separation and positive controls; X1-D stored test report (`--junitxml`) and latency re-measure *(only if a latency number appears in the paper; otherwise report existing percentiles with the outlier labelled)* |
| **Strongly recommended** | X1-B Qwen authority-isolation (structural + bit-identity) |
| **Optional** | Cold-vs-warm latency with N ≥ 100; a second machine for concurrency; evaluator-in-the-loop concurrency |
| **Do NOT do** | N1, N2, N3 (I.12) |
| **Strongest controls/baselines** | Mutation controls (handler disabled; permissive container config against a *local* canary); no-fault control runs for every fault scenario; identical inputs with/without adversarial prompts |
| **Statistical unit** | The *scenario/attack* (an enumerated fault class), not the trial |
| **Tests / CIs / effect sizes** | Deterministic scenarios: counts of repetitions passed (5–10), reported per scenario. Timing-randomised scenarios (lock contention, mid-request reset, slow-Qwen): N ≈ 30 randomised injection points, per-scenario Wilson 95 % CI. Latency: median/P95/P99 with bootstrap CIs. No pooling into one "x/y". Effect sizes not applicable (proportions and latencies reported directly). |
| **Seeds** | Order-shuffle and timing-jitter seeds logged in the run manifest; no learned components |
| **Sample-size rationale** | Deterministic classes need repetition only to detect flakiness; timing-randomised classes use N ≈ 30 to characterise the sampled timing space (interval width ≈ ±0.09–0.12 near 90–100 %); scenario count is set by the dependency-graph enumeration, not by convenience |
| **Stopping criteria** | Fixed scenario list and repetitions; no early stopping; harness failure is a reported outcome, never silently retried; a defect ends the pass on that build and triggers the defect policy (I.1) |
| **Contamination/leakage controls** | Criteria and observables frozen and hashed before running; harness dry-run on fixtures only; canaries are local and outside the container; no reuse of frozen PASS strings; system under test frozen by commit/tag |
| **Reproducibility artifacts** | Harness code + config, scenario table, run manifest (commit, env lock hash, versions, hardware), per-trial logs, DB dumps with hashes, JUnit XML, `docker ps`/process lists before/after, results CSV, registry rows |
| **Interpretation — positive** | "For the enumerated fault classes on build X, the pre-specified criteria were met" (scenario-level, with mutation controls showing the harness can fail) |
| **Interpretation — null/mixed** | Report which scenarios failed; the corresponding property is dropped from the title/claims; if defects are fixed, both builds are reported |
| **Interpretation — negative** | A failed containment or fault scenario is a finding, not a harness error; it is reported with the fix policy |

---

# PART V — PAPER 2 PLAN

**Central research question.** How well does the hybrid, deterministic, LLM-free evaluator (SBERT S1 + FAISS S2 + CrossEncoder R, safety-hardened) agree with blinded human expert ratings on technical-interview answers, and where does it fail?

**Current evidence.** Composite ρ = 0.381 on 64 constructed answers to 8 questions; case-bootstrap CI [0.158, 0.577]; question-cluster CI [0.302, 0.589]; per-question ρ 0.44–0.91; within-question (demeaned) ρ 0.580; R-only 0.483; S1+R 0.488; concise-correct human 0.912 vs model 0.397 (systematic under-scoring); pilot-overlap ρ 0.709 vs 0.425 *(audit)*. Human ICC(2,1) 0.953 driven by construction. Undocumented fine-tune; undocumented rater provenance.

**Unsupported/weak claims.** Off-the-shelf; any general validity claim; independence/qualification of raters; "held-out" for the four pilot-overlap questions; composite as "better than components".

**Recommended final framing.** *"Moderate rank agreement with human raters on a constructed benchmark, and a confirmatory result on a question-disjoint, temporally disjoint benchmark; a safety-hardened deterministic evaluator whose composite trades some average agreement for robustness to adversarial answers, with a documented under-scoring bias against terse correct answers."* Novelty = deterministic, auditable evaluator + adversarial/metamorphic evaluation + honest provenance; not "state-of-the-art agreement".

**Evidence needed.** (1) Provenance-corrected model description; (2) question-cluster inference; (3) confirmatory ρ on a new benchmark; (4) baselines; (5) adversarial false-accept evidence for the composite; (6) documented human provenance for the confirmatory set.

| | |
|---|---|
| **Mandatory** | Provenance correction (P0-1 A+B); stored-data re-analysis package X2-A (cluster bootstrap, leave-one-question-out, per-category, rater-LOO, adversarial false-accept A3, non-overlap-subset reporting); P0-7 records + institutional determination |
| **Strongly recommended** | X2-B lexical/length baselines + upstream sensitivity (evaluation-only); X2-C confirmatory benchmark |
| **Optional** | LLM-judge comparison *(only if the paper claims to compare with LLM judging)*; 4th rater; volunteer-written answers stratum |
| **Do NOT do** | N4, N7, N8, N9 (unless claimed), N10 |
| **Strongest controls/baselines** | S1-only, S2-only, S1+S2, R-only, S1+R (existing); TF-IDF/BM25/token-overlap and length-only; upstream CrossEncoder; a shuffled-label null (permutation reference for ρ); a length-matched subset |
| **Statistical unit** | The **question** (cluster) for inference; the answer for descriptive statistics; rater as a crossed factor for reliability |
| **Tests / CIs** | Spearman ρ (primary), Kendall τ-b (ties); AUROC for correct-vs-incorrect (threshold fixed in advance); Lin's CCC and Bland–Altman bias for absolute agreement; per-question ρ combined by Fisher-z random-effects with a heterogeneity report; **two-level cluster bootstrap (resample questions, then answers within question), B ≥ 10 000**, percentile and BCa; dependent-correlation differences (composite vs R-only vs S1+R) by the same paired bootstrap. ICC(2,1)/(2,k) with CIs for raters. |
| **Effect sizes** | ρ and τ themselves; paired ρ-difference with CI; AUROC; MAE and signed bias in score units |
| **Seeds** | Deterministic evaluator, so none; bootstrap RNG seed recorded; generator seed if answers are model-sampled |
| **Sample-size rationale** | Precision-driven: number of questions chosen by simulation so the cluster-CI half-width for ρ ≤ 0.12 (I.4); raters ≥ 3 fully crossed; answers/question fixed |
| **Stopping criteria** | Fixed item list frozen before rating; no item added, removed or re-worded after any rater or evaluator output is seen; adjudication rule as in the frozen protocol (spread > 0.20) |
| **Contamination/leakage controls** | Score-after-freeze ordering; question-disjoint from pilot and old set; temporally disjoint stratum; references authored before answers and before evaluator runs; answers not filtered on evaluator output; FAISS reference bank checked to ensure new items are absent (or the S2 behaviour on unseen questions is stated as the tested condition); raters blind to category and to model score; evaluator, R checkpoint, mapping, θ and weights frozen by hash before rating starts |
| **Reproducibility artifacts** | Benchmark item file + hash; generator prompts/config (if model-sampled); rater instrument version; rater ledger (identities off-repo, code + dates in repo); frozen gold hash; evaluator hash set; analysis script + config; results CSV; environment lock; registry rows |
| **Interpretation — positive** | Confirmatory ρ CI lower bound above a *pre-set* value (e.g., 0.30) on the confirmatory set → "moderate agreement, generalising beyond the pilot questions"; still bounded to constructed/simulated answers |
| **Interpretation — null/weak** | ρ CI includes ≈ 0.2 or lower → the 64-case result is reported as an optimistic pilot; claim narrows to "agreement on constructed contrast sets" |
| **Interpretation — negative** | Derived-vs-upstream gap large on the temporally disjoint stratum but not the bank stratum → leakage suspicion documented as such (not proven); the public model becomes the primary if it performs comparably |

**The composite question.** If R-only ρ > composite ρ persists, the paper must say so and defend the composite only through the pre-specified adversarial endpoint (false-accept rate on keyword-stuffed/misconception/contradictory items relative to R-only and S1). If that endpoint does not favour the composite either, the honest recommendation is to present R-only as the accuracy-optimal component and the composite as a design choice with a measured cost.

---

# PART VI — PAPER 3 PLAN

**Central research question.** In a simulated adaptive-difficulty task, how much of the tracking performance is attributable to (i) a guardrail shield, (ii) a rule oracle/heuristic, and (iii) a learned PPO policy, once trivial and state-blind policies receive the same shield?

**Current evidence.** MAE: Fixed 1.200; Heuristic 0.473; raw PPO 0.958 (0.804–1.138); PPO+G 0.677 (0.673–0.687); Const-Same+G 0.673; 5/125 sessions differ between PPO+G and Const-Same+G; PPO's proposals 67–96 % Same; rules decide 40–49 % of guarded turns; 563 activations vs 99 overrides; attempted boundary actions 136 raw vs 232 guarded; volatility guarded 0.186 vs heuristic 0.160 *(audit)*. Five personas × five evaluation seeds × five training seeds; 24 576 timesteps per seed; train ≠ evaluation environment.

**Unsupported/weak claims.** PPO superiority or contribution; "0 violations"; "563 interventions"; "smoother than the heuristic"; any learner-level claim; seed stability attributed to PPO.

**Recommended final framing.** *"A controlled decomposition of guardrail, rule, heuristic and learned-policy contributions to simulated difficulty control"* — simulation only. PPO's role is an empirical finding (whatever it is).

| | |
|---|---|
| **Mandatory** | X3-0 corrected accounting from stored data (P0-3/4/5, P1-13/14/15, persona-level); X3-A Stage 1 decomposition (evaluation-only, including state-shuffle, oracle, controller, rule-ablation, +G crossing) |
| **Strongly recommended** | X3-B Stage 2 training-consistent retraining study with budget series and BC control, **only after your approval**, with its trigger rule fixed in advance |
| **Optional** | X3-C second simulated-candidate model; outcome-only reward study (separate question, separate pre-registration) |
| **Do NOT do** | N5, N6 |
| **Strongest controls/baselines** | Const-Same(+G), Random(+G), Heuristic(+G), Oracle-rule policy(+G), proportional controller, BC-of-oracle, PPO raw/+G, Fixed; state-shuffle and state-zero PPO evaluations; guardrail-rule ablation |
| **Statistical unit** | **Persona** for the primary contrast; training seed as a second random factor; evaluation seeds nested (averaged within persona × training seed). Session and turn are descriptive only. |
| **Tests / CIs** | Paired difference in persona-level MAE within training seed, averaged over training seeds; **two-way cluster bootstrap over personas and training seeds**, B ≥ 10 000, 95 % percentile CI; equivalence assessed by the CI lying within ±δ; secondary: mixed model MAE ~ policy + (1 | persona) + (1 | train seed) as a sensitivity check |
| **Effect sizes** | Mean paired MAE difference (primary, in difficulty units); Cohen's d_z on persona-level differences; override/activation rates with denominators |
| **Seeds** | Training: ≥ 10 for X3-B (5 existing for X3-A); evaluation: 20 per persona; env seeding + model `seed=` recorded; `deterministic=True` at evaluation; same seed sets across comparable conditions |
| **Sample-size rationale** | ≥ 24 generated personas (precision-based: half-width ≈ 2.07·SD_d/√24, with SD_d taken from the persona-level paired differences in the frozen data in Phase 1 [A10] and written into the registration); 20 evaluation seeds bounds within-persona noise; ≥ 10 training seeds for the seed dimension |
| **Stopping criteria** | Fixed persona list, seeds, budgets; no personas added/removed; no optional stopping; Stage 2 trigger rule stated before X3-A runs |
| **Contamination/leakage controls** | Persona generator, target rule, margins, δ and endpoints fixed and hashed before checkpoints are evaluated; the five frozen personas never used to choose margins; generated personas not used for any tuning; guardrail rules and reward frozen; the state-shuffle and controller conditions specified in advance |
| **Reproducibility artifacts** | New frozen config; persona table with generator seed; per-turn logs including perf/conf/hes (missing in the frozen study, blocking counterfactuals); checkpoint hashes; environment lock; commit; W&B run IDs for *new* runs only (API key never in the repo); CSVs; registry rows |
| **Interpretation — positive** | PPO+G better than every state-blind+G and controller condition by ≥ the pre-set superiority margin in a majority of training seeds → a PPO-specific claim, scoped to the simulator and the oracle-imitation reward |
| **Interpretation — null** | CI within ±δ → "no detectable PPO contribution beyond the shield" (equivalence result); CI wide and spanning both → "inconclusive", not "no effect" |
| **Interpretation — negative** | PPO worse than the heuristic/oracle → reported; paper stands as a decomposition study |

**Train/evaluation mismatch and pseudo-replication.** X3-A is explicitly *evaluation of frozen checkpoints trained in a different environment*, so it answers "what do these checkpoints contribute", not "what does PPO contribute". Only X3-B (training and evaluation in one environment, budget series, ≥ 10 seeds) answers the latter. Pseudo-replication is handled by making persona × training seed the resampling units (not sessions or turns), and by reporting the session-level result only as descriptive.

---

# PART VII — EXPERIMENT SPECIFICATIONS

*Rule: no experiment may be changed after seeing results without being documented and registered as a new experiment.*

## X1-A — Fault-injection core (Paper 1)
- **Research question:** Does the system handle each enumerated dependency failure without losing state, fabricating a score, or hanging?
- **Hypothesis:** For each scenario the pre-specified observable criteria are met; the corresponding mutation control fails the same criteria.
- **Independent variables:** fault scenario (dependency × {down, slow, corrupt}); injection timing (randomised where timing matters); build (default; mutated).
- **Dependent variables:** response status/flags, latency vs SLA, score field, DB state hash and row counts, recovery on the next request.
- **Controls:** no-fault run per scenario; mutation variant per scenario.
- **Unit:** the scenario. **Sample:** scenario list from the dependency graph (expected ≈ 8–12); 5–10 repetitions deterministic; N ≈ 30 randomised timings for timing scenarios.
- **Seeds:** order/jitter seeds logged. **Test:** per-scenario counts; Wilson 95 % CI for randomised scenarios only. **CI:** as stated. **Effect size:** n/a.
- **Stopping rule:** fixed scenario/repetition counts; a failure is reported and triggers the defect policy.
- **Success/failure:** PASS is computed by the harness from asserted fields; success = criteria met and mutation control detected; failure of either is reported.
- **Contamination controls:** criteria hashed first; dry-run on fixtures; no reuse of frozen PASS strings.
- **Artifacts:** harness, scenario table, manifests, logs, DB dumps, JUnit XML, results CSV.

## X1-B — Qwen authority isolation (Paper 1)
- **Question:** Can LLM output alter score, difficulty or ranking?
- **Hypothesis:** No path exists; outputs are bit-identical with vs without adversarial prompts.
- **IV:** prompt set (fixed list, ≥ 30 adversarial prompts written in advance) × {adversarial, benign}. **DV:** evaluator score bytes, orchestrator difficulty state, `is_best` rows.
- **Controls:** benign prompts; static/AST check as an independent structural test. **Unit:** the prompt (paired with its benign control). **Sample:** ≥ 30 prompts.
- **Seeds:** Qwen decoding seed/temperature recorded (`temperature` fixed). **Test:** exact equality per pair. **CI:** Wilson on proportion of identical pairs (informative only if the LLM path is stochastic). **Effect size:** n/a.
- **Stopping:** fixed prompt list. **Success:** 100 % identical **and** static check clean; any difference is a defect. QWN-04 (validator) is **excluded** unless a validator is separately approved.
- **Contamination:** prompts frozen before running. **Artifacts:** prompt file, logs, diffs, AST-check output.

## X1-C — Security oracle campaign with positive controls (Paper 1)
- **Question:** For each attack, did the payload execute, was the effect contained, and did the host remain unchanged?
- **Hypothesis:** Contained for all attacks under the shipped configuration; the permissive-configuration control shows the oracle detects a breach.
- **IV:** attack (the nine existing plus any pre-listed additions) × configuration {shipped, permissive local-canary control}. **DV:** the five quantities (execution, containment, status, host impact, resource impact) per attack.
- **Controls:** permissive-config runs against a local canary listener/file (never a real network target). **Unit:** the attack. **Sample:** 9 attacks × 5 repetitions.
- **Seeds:** none. **Test:** per-attack outcome table; no pooled percentage. **CI/effect:** n/a.
- **Stopping:** fixed list. **Success:** shipped config passes and permissive control fails on the same oracle. **Failure:** reported per attack.
- **Contamination:** oracles frozen first. **Artifacts:** programs, oracle code, host-side canary hashes, resource counters, logs.

## X1-D — Test report and latency (Paper 1)
- **Question:** What is the state of the test suite and the warm/cold latency distribution?
- **Hypothesis:** descriptive. **IV:** cold vs warm. **DV:** pass/fail/skip counts (incl. the known failing test, disclosed), latency percentiles.
- **Unit:** request (latency), test (suite). **Sample:** latency N ≥ 100 warm, cold recorded separately. **Test/CI:** median/P95/P99 with bootstrap CI. **Stopping:** fixed N.
- **Interpretation:** cite only the stored, dated report. **Artifacts:** `--junitxml` report with commit/env, raw per-request latency list.

## X2-A — Stored-data re-analysis package (Paper 2; analysis, not an experiment)
- Question: how sensitive is the frozen ρ to question clustering, rater choice and category composition? Inputs: `paper2_case_level_results.csv`, hash-pinned gold, rater files. Outputs: cluster bootstrap, leave-one-question-out, per-category, rater-LOO, adversarial false-accept (A3), overlap/non-overlap reporting. Fixed B and RNG seed. Results labelled *exploratory* except the cluster bootstrap. New script + new result file; the old files untouched.

## X2-B — Baselines and upstream sensitivity (Paper 2; evaluation-only)
- **Question:** Does the composite/R beat lexical baselines, and how much does the undocumented fine-tune matter?
- **Hypothesis:** none directional for upstream; composite/R > lexical baselines on ρ and AUROC.
- **IV:** scorer ∈ {derived R, upstream R, TF-IDF, BM25, token overlap, length-only, existing components}. **DV:** ρ, τ-b, AUROC, MAE (mapping-dependent, secondary).
- **Controls:** permutation-null ρ. **Unit:** question (cluster). **Sample:** old 64 (exploratory) and, once available, X2-C (primary).
- **Seeds:** bootstrap seed. **Test:** two-level cluster bootstrap, paired differences. **CI:** 95 %. **Effect size:** ρ/AUROC difference.
- **Stopping:** single run per scorer. **Success/failure:** small derived–upstream gap → adopt public model as primary; large gap → leakage caveat central.
- **Contamination:** mapping and metrics frozen and hashed before running; label-free mapping only.
- **Artifacts:** model hashes, per-case scores, config, environment lock, results CSV.

## X2-C — Confirmatory benchmark and human round (Paper 2)
- **Question:** Does the evaluator's agreement with human raters replicate on a question-disjoint, temporally disjoint benchmark?
- **Hypothesis:** composite ρ ≥ pre-set bound (fixed with you; suggested 0.30 CI lower bound); R-only ≥ composite; composite's adversarial false-accept rate < R-only's.
- **IV:** scorer; item stratum {temporally disjoint, bank-sampled} × {constructed contrast, natural/generated}. **DV:** human consensus score; scorer output.
- **Controls:** blind rating; permuted order; no category/model score visible; unseen-question S2 condition explicit.
- **Unit:** question. **Sample:** by precision simulation (expected ≈ 20–30 questions × 8 answers); ≥ 3 fully crossed raters.
- **Seeds:** ordering seed; generator seed if model-sampled. **Test/CI/effect:** as Part V. **Stopping:** item list frozen before rating.
- **Interpretation:** as Part V. **Contamination controls:** score-after-freeze; independence rules for answer authors; ledger.
- **Artifacts:** item file + hash, instrument, ledger, frozen gold, evaluator hashes, analysis script, results, environment lock.

## X3-0 — Corrected accounting from stored data (Paper 3; analysis)
- Recompute from frozen files: attempted boundary actions (raw/final, per seed), activations vs overrides with denominators and per-rule/persona/session breakdown, five-seed volatility with paired persona-level contrasts, P1-14 corrected ablation rows, persona-level paired differences and their SD (A10). New script; frozen files untouched.

## X3-A — Stage 1 decomposition (Paper 3; evaluation-only on existing checkpoints)
- **Question:** With the frozen checkpoints, what do the shield, rule policies, heuristic and PPO contribute across a pre-specified persona set?
- **Hypotheses (pre-specified):** H1 (primary) PPO+G differs from Const-Same+G by less than δ (equivalence) — *or* is lower by ≥ margin m (superiority), with δ and m fixed with you; H2 Heuristic+G vs PPO+G (exploratory); H3 raw PPO vs Fixed (secondary); H4 shuffled-state PPO ≈ intact PPO (PPO ignores state).
- **IV:** base policy {Fixed, Const-Same, Random, Heuristic, Oracle-rule, controller, PPO} × shield {off, on}; PPO observation {intact, shuffled, constant}; rule ablation {each of G1/G2/G4/G5 off}. **DV:** MAE (primary), oracle agreement, attempted boundary rate, volatility, oscillation, override rate.
- **Controls:** as above. **Unit:** persona (× training seed for PPO). **Sample:** ≥ 24 generated personas (generator fixed; five original personas flagged), 20 evaluation seeds, 5 existing checkpoints.
- **Seeds:** evaluation seeds fixed list; `deterministic=True`. **Test:** two-way cluster bootstrap on paired persona-level differences; equivalence via CI within ±δ. **CI:** 95 %, B ≥ 10 000. **Effect size:** mean paired difference, d_z.
- **Stopping:** fixed. **Interpretation:** Part VI. **Contamination:** all margins/endpoints hashed before running; no tuning.
- **Artifacts:** config, persona table + generator seed, per-turn logs with perf/conf/hes, checkpoint hashes, CSVs, registry rows.
- **Stage-2 trigger (pre-specified):** X3-B runs only if X3-A's H1 is inconclusive or if you elect the PPO-method question; the rule is recorded before X3-A is executed.

## X3-B — Stage 2 training-consistent retraining study (Paper 3; needs approval)
- **Question:** In an environment consistent with evaluation and at a stated budget series, what does a learned policy add over the shield and over behaviour cloning?
- **IV:** learner {PPO, BC-of-oracle, none} × budget {25 k, 100 k, 500 k steps — fixed in advance} × shield in-the-loop {on, off}; reward/state/action **unchanged**. **DV:** as X3-A plus learning curves.
- **Controls:** the X3-A baselines re-run in the same environment. **Unit:** persona × training seed. **Sample:** ≥ 10 training seeds; same persona set as X3-A.
- **Seeds:** model `seed=`, env seeding, evaluation seeds; SB3 versions/hardware recorded (identical seeds do not guarantee cross-platform equality). **Test/CI/effect:** as X3-A. **Stopping:** fixed budgets; no early stopping on results; no hyperparameter tuning.
- **Interpretation:** as Part VI. **Contamination:** hyperparameters frozen from the existing config; nothing tuned on generated personas. **Artifacts:** new frozen config, checkpoints + hashes, W&B run IDs (new runs; explicit `model_save_path`/`model_save_freq`; `wandb.init()` first), environment lock, per-turn logs.

## X3-C — Second simulated-candidate model (optional)
- Purpose: separate PPO/shield conclusions from the author's single generative simulator. Same conditions on an independently specified candidate model (e.g., item-response-style responses with learning/fatigue drift), specified and hashed before use. Reported as robustness; no new tuning.

---

# PART VIII — REVIEWER-ATTACK MATRIX

| # | Objection | Why plausible | Evidence needed | Answer |
|---|---|---|---|---|
| 1 | "Fault-tolerant claim is unfalsified" (P1) | Frozen results are literal PASS strings *(audit)* | Oracles that can fail | X1-A with mutation controls |
| 2 | "Your fault list is arbitrary" (P1) | Ten hand-picked scenarios | Systematic coverage | Dependency-graph enumeration; scope statement |
| 3 | "Sandbox 'secure' from 9 attacks" (P1) | Five outcomes were not discriminating | Five-way separation + canaries + controls | X1-C; drop "secure" |
| 4 | "Qwen has zero authority — prove it" (P1) | No validator; two rows had no evidence | Structural + differential test | X1-B; state feedback is unvalidated |
| 5 | "Single machine, synthetic load" (P1) | Concurrency excludes evaluator/LLM | Scope statement or extra test | Scope in text; optional evaluator-in-loop test |
| 6 | "Model is undocumented" (P2) | 16.28 % of weights changed | Provenance or a public-model arm | P0-1 A+B; X2-B upstream arm |
| 7 | "Possible train/test leakage" (P2) | Four benchmark questions in legacy bank | Temporally disjoint items | X2-C stratum design |
| 8 | "Eight questions" (P2) | Effective independent sample = 8 | More questions; cluster CI | X2-A now; X2-C confirmatory |
| 9 | "Constructed answers inflate agreement" (P2) | η² ≈ 0.98 between categories | Natural answers; within-category results | X2-C natural stratum; report within-category |
| 10 | "Beats trivial baselines?" (P2) | Keyword-stuffed items exist | Lexical/length baselines | X2-B |
| 11 | "Composite is worse than R-only" (P2) | 0.381 vs 0.483 | Adversarial endpoint | X2-A/X2-C false-accept analysis |
| 12 | "Tuned on overlapping pilot" (P2) | θ/dampening from a pilot sharing four questions | Non-overlap/confirmatory results | X2-A + X2-C; disclosure |
| 13 | "Terse-answer bias / fairness" (P2) | Concise-correct 0.912 vs 0.397 | Per-category table; limitation | Report as principal limitation |
| 14 | "Human raters undocumented" (P2) | No identities/consent/timestamps | Records + determination | Part X |
| 15 | "PPO adds nothing" (P3) | Const-Same+G = PPO+G | Decomposition study | X3-A/B |
| 16 | "Guardrails ≠ PPO — where's the control?" (P3) | No PPO-free guarded control originally | Const-Same+G etc. | X3-A crossing of all base policies |
| 17 | "PPO undertrained / wrong environment" (P3) | 24 576 steps; T and step mismatch | Budget series, consistent env | X3-B |
| 18 | "Reward is circular" (P3) | Oracle imitation + rules restate oracle | Framing; oracle & BC controls; optional outcome reward | Frame as imitation; X3-B controls |
| 19 | "Pseudo-replication" (P3) | Sessions/seeds treated as independent | Persona × training-seed resampling | Two-way cluster bootstrap |
| 20 | "Personas are author-defined; target = 5 × skill" (P3) | Rule reproduces all five targets *(arith)* | Documented generator; second simulator | Generator pre-registered; X3-C optional; limitation |
| 21 | "Simulator only" (P3) | No human evidence | Scope | Explicit scope; no learner claims |
| 22 | "Numbers not traceable" (all) | Hard-coded literals found | Recomputable registry | Part IX |
| 23 | "Stale/contradictory numbers in repo" (all) | Two canonical files; wrong hash | Supersession control | Part X (docs) |
| 24 | "Not reproducible" (all) | `.venv` violates pins; cross-platform RL variance | Env lock, manifests | Part XI |

---

# PART IX — CLAIM → ARTIFACT → SCRIPT → HASH → ENVIRONMENT VERIFICATION

**Registry** (`research/claims/CLAIM_REGISTRY.csv`, new; proposed). One row per *sentence-level number or property* that may appear in a manuscript.

| Column | Meaning |
|---|---|
| `claim_id` | Stable ID (e.g., `P2-C012`) |
| `paper`, `wording` | Paper and the **exact permitted wording** (with scope words) |
| `status` | VALID / HISTORICAL / WITHDRAWN / NEW-FROZEN / EXPLORATORY |
| `value`, `tolerance`, `n`, `unit_of_analysis`, `ci` | The number, its precision, denominator and CI method |
| `artifact_path`, `artifact_sha256` | The stored result file and its hash |
| `script_path`, `script_commit`, `config_path` | The generator and the commit that produced the artifact |
| `env_lock_sha256`, `seed_set` | Environment and seeds |
| `recompute_tier` | T1 hash check · T2 recompute the number from stored per-item data · T3 full rerun reproduction |
| `verify_cmd` | Command that checks it |
| `superseded_by`, `last_verified` | Supersession pointer and date |

**Rules.**
1. No number enters a manuscript without a registry row. Manuscript numbers are inserted from the registry by macro (`\claim{P2-C012}`), never typed.
2. **Literal-constant detector** (static check over result-writing scripts): fail on hard-coded metric literals in result rows (the pattern that produced `constraint_violations: 0`).
3. **T2** verification is mandatory for every headline number; **T3** for every new experiment.
4. Environment mismatch is *recorded* (the frozen `.venv` violates pins); re-running under a different environment is reported as such.
5. A `verify_claims` script (proposed, new) exits non-zero if any hash, recomputed value or superseded wording mismatches; run in CI before any paper build.

---

# PART X — HUMAN PROVENANCE / ETHICS GATE

**Gate structure.** G0 record inventory → G1 institutional/venue determination → G2 consent/ledger design for any new round → G3 documentation attached to the dataset.

| Class | Items |
|---|---|
| **Recoverable from the repo** | Frozen protocol and hash/tag; package manifests; raw/frozen rater files and hashes; adjudication form/rationales; blinded-sheet design; final gold and hashes; Git timestamps; computed reliability statistics *(audit)* |
| **To be requested from people/institution (existing records only)** | Identities and roles of raters/adjudicator (kept off-repo, coded ID in repo); qualifications; the instructions each received; send/return times (email/chat/drive metadata); time spent; whether external tools/AI assisted; any informal consent or acknowledgement; compensation/acknowledgement terms; institutional correspondence; the signed checklist if it exists |
| **Cannot be reconstructed** | Consent never obtained; independence/blinding attestations never collected; pre-distribution sign-off; true rating times if no records exist. A present-day statement is *retrospective*, dated today, never backdated. |
| **Requires institutional/academic determination — INSTITUTIONAL DECISION REQUIRED** | Whether the existing round needs an exemption/approval statement; whether a retrospective account is acceptable; what consent/data-handling the new round needs; venue disclosure requirements (venue TBD) |

**A new human round becomes necessary when any of:** (a) the institution or venue requires prospective consent/approval that cannot be established retrospectively; (b) records cannot establish rater independence/blinding and the venue requires it; (c) a confirmatory benchmark is wanted for the validity claim (my recommendation regardless, per I.4). In cases (a)/(b) the old gold becomes a pilot and the new round is the primary set.

**New-round documentation (X2-C).** Consent and roles recorded before distribution; instrument version pinned; ledger with coded rater IDs, send/return timestamps, time spent, tool-use declaration, independence declaration collected at the time; adjudicator role separated; data handling; hashes of every rater file at return.

---

# PART XI — SCIENTIFIC-TRUTH / DOCUMENTATION CONTROL, TECHNOLOGY, PRODUCT

## XI.1 Source-of-truth hierarchy
1. Frozen raw result files and their hashes.
2. `CLAIM_REGISTRY.csv` (Part IX), the permitted wording.
3. A *new* supersession note designating the authoritative canonical file (handoff copy currently carries ρ 0.3812/N=64) and listing the stale root file's superseded statements.
4. Handoff and audit documents, read as historical unless the registry says otherwise.
5. README/docs — never a source of numbers.

## XI.2 Supersession rules
Every document that carries results has a status header (`status: frozen | superseded | active`, `superseded_by`). Frozen files are never edited; corrections are new files that cite the original path and hash. Errata list the old text, the correct value and the evidence.

## XI.3 Known corrections to register
Hash `b7cad49b6b7a…` → `b7cad49529c3…` (tag `v1.0-paper3-complete`); ρ 0.6975 relabelled *pilot*; ρ 0.7400 / 0.9152 / 0.8358 (synthetic/superseded per `CLAUDE.md`); "off-the-shelf / zero fine-tuning / MiniLM-L12"; "0 violations"; "563 interventions"; "0.088"; "10/10, 5/5, 9/9, 213"; "100 % acoustic insulation"; seed-123 deployed vs evaluated checkpoint (2ab8d514… vs 299437ea…); README "11 categories / 8 questions per domain" (data: 10 categories, 8 questions total).

## XI.4 Protection against future sessions
- A `SUPERSEDED_VALUES` list checked by the registry script and by CI over `paper/`; any draft containing a superseded string fails.
- After your approval, update `CLAUDE.md` (via claude-md-management) to point to the registry and fix its two stale lines; keep it concise.
- New session start: read `CLAUDE.md` → registry → supersession note; frozen files read-only by rule.
- Never regenerate frozen files "to refresh" numbers; regeneration creates a new experiment ID.

## XI.5 Technology (only reproducibility-motivated additions; no swaps)
| Item | Recommendation |
|---|---|
| SBERT / FAISS / CrossEncoder / Gymnasium / SB3 / Docker / SQLite / Qwen | **Keep.** No finding implicates any of them. |
| Environment | Create a **lock file for new experiment runs** (versions, hashes) and record the existing `.venv` pin violations; do **not** silently change `.venv` (needs approval). |
| Run manifests | Every new run writes commit, lock hash, versions, hardware, seeds, config path, data hash |
| SB3 | Model `seed=`, env seeding, `deterministic=True`, record PyTorch/SB3 versions (identical seeds not guaranteed across platforms) *(Context7, earlier pass)* |
| W&B | New runs only (`WandbCallback`, `wandb.init()` first, explicit `model_save_path`/`model_save_freq`); log config/seed/commit/data hash; never the API key; not a reproducibility guarantee |
| Testing | pytest + `--junitxml` for Paper 1; no new test framework |
| Fault injection | Container stop/pause, stubs, local proxies; a dedicated fault-injection tool is optional and would be a new dependency needing approval |
| Statistics | Use libraries already in the environment where possible; new statistical dependencies need approval |

## XI.6 Frontend / product (separate from science)
| Class | Items |
|---|---|
| **Safe, no scientific semantics** | Accessibility hooks (labels, `aria-live` regions, keyboard operability, alt text, reduced-motion CSS); component tests; failure-state copy *that does not alter scoring*; README/docs fixes; reproduction pages per paper; guardrails docstring correction *(needs your approval per CLAUDE.md; behaviour unchanged)* |
| **Could affect scientific semantics (E)** | Score/grade presentation and thresholds; how infrastructure failure vs candidate 0.0 is displayed *if* it changes what the backend records; re-pointing the runtime to the evaluated PPO checkpoint; dependency reconciliation; the known failing test |
| **Require explicit approval** | Anything in `apps/backend`, `services/`, `agents/`, `rl/`; changes to `.venv`; deletion of any legacy file/checkpoint |
| **Constraint** | No modification of the system under test between X1 pre-registration and X1 completion (code freeze by tag); frontend work on a separate branch/worktree |

---

# PART XII — PUBLICATION-READINESS GATES

Drafting may begin for a paper only when **all** its gates are met and the independent review (Phase 5) has passed.

## XII.1 Paper 1
- [ ] Title/claims scoped to what X1 supports (no "secure"; "fault-tolerant" only if X1-A passed).
- [ ] Discriminating oracles with computed PASS/FAIL and mutation controls, stored logs and JUnit report with commit/env.
- [ ] Every frozen literal-PASS claim registered as WITHDRAWN/HISTORICAL.
- [ ] Defect policy applied to any failure; both builds reported.
- [ ] Latency reported as percentiles with outlier labelled (or re-measured).
- [ ] Threat-model table labelled as design mapping.
- [ ] Registry rows + T2 verification for all numbers.

## XII.2 Paper 2
- [ ] Provenance statement corrected (hash, "partially fine-tuned derivative", data/code/hyperparameters not available or recovered).
- [ ] P0-7 records inventory closed; institutional/venue determination obtained or explicitly disclosed as pending.
- [ ] X2-A cluster analyses done; X2-B baselines + upstream arm done (or the reason for omission recorded).
- [ ] Confirmatory benchmark (X2-C) completed, frozen and analysed per protocol — **or** the paper is explicitly scoped as pilot-scale with the narrow claim and the omission justified.
- [ ] Composite-vs-R-only question answered with the pre-specified adversarial endpoint.
- [ ] Under-scoring bias reported.
- [ ] Registry rows + T2 verification.

## XII.3 Paper 3
- [ ] P0-3/4/5, P1-13/14/15 corrections published as new files and registered.
- [ ] Persona × training-seed inference for the primary contrast.
- [ ] Decomposition conditions (X3-A) complete, with equivalence/superiority margins fixed beforehand.
- [ ] Train/evaluation mismatch resolved (X3-B) or explicitly disclosed with the claim restricted to "these checkpoints".
- [ ] Reward framed as oracle imitation + rule shield.
- [ ] Explicit simulation-only scope.
- [ ] Registry rows + T2 verification; per-turn logs stored.

## XII.4 Cross-paper reproducibility gate
- [ ] Registry complete; `verify_claims` passes from a clean checkout on the locked environment.
- [ ] Environment lock and manifests for every new experiment; frozen environments' pin violations disclosed.
- [ ] All hashes in the registry match; `git` tags exist for each new frozen set; long-hash errata applied.
- [ ] No superseded string in `paper/` (CI check).
- [ ] The three papers cite each other's evidence only through the registry; evidence streams stay separate (systems / human benchmark / simulation).
- [ ] References only from Zotero or verified sources.

---

# PART XIII — WORK CLASSIFICATION

| Class | Items |
|---|---|
| **Mandatory** | P0-1 A + trainer enquiry; P0-3/4/5 and P1-11/13/14/15 corrections; P1-12 supersession + registry; P0-7 records inventory + institutional enquiry; Paper 1 claim withdrawal/narrowing + X1-A + X1-C (+ X1-D report) *if any fault/security property stays*; Paper 2 X2-A; Paper 3 X3-0 + X3-A |
| **Strongly recommended** | X2-B (baselines + upstream); X2-C (confirmatory benchmark, merged with P0-7 route C); X3-B (with pre-specified trigger); X1-B; provenance cards; environment lock; A3/A4/A6/A7/A8 |
| **Optional** | X3-C; LLM-judge comparison; 4th rater; volunteer-answer stratum; warm/cold latency N ≥ 100; second machine; frontend accessibility branch; outcome-only reward study (separate) |
| **Future work only** | Outcome-based reward and independent evaluator (P1-5); length/paraphrase-robust scoring (P1-2); real-learner studies; broader domains; multi-simulator benchmark suites |

---

# PART XIV — MOST LIKELY REJECTION REASONS EVEN AFTER STRENGTHENING

- **Paper 1:** engineering rather than research novelty; single-machine, synthetic evaluation; no user study; no comparison with existing interview platforms; Qwen feedback unvalidated; "fault-tolerant" scoped to enumerated faults; the evaluator's validity is Paper 2's burden.
- **Paper 2:** moderate ρ (~0.4) and composite below R-only; one domain family; constructed/simulated answers; few raters; undocumented fine-tune (unless provenance recovered or public model comparable); retrospective human-provenance documentation for the original round; terse-answer under-scoring; no LLM-judge comparison.
- **Paper 3:** simulator-only with author-defined personas and target rule; oracle-imitation reward is circular; negative/null PPO result may be judged low-impact by RL venues; no human evidence; small state/action space where simple rules suffice.

---

# PART XV — SEQUENCE (SCIENTIFIC STRENGTH PER UNIT EFFORT)

Effort classes are my estimates (S ≈ hours, M ≈ days, L ≈ weeks); not measured.

1. **Phase 0 (S–M, blocking slow processes):** send trainer and institutional enquiries; record search; approve decisions; supersession note + registry skeleton; errata; environment-lock plan.
2. **Phase 1 (S–M, highest value/effort):** X2-A, X3-0, A3, A10, Paper 1 claim table. These correct most P0s and inform the designs.
3. **Phase 2 (M–L):** pre-register X1/X2/X3; harness with mutation controls; persona generator; benchmark authoring and ethics design; precision simulation.
4. **Phase 3:** X3-A (S, cheap) → X3-B (M) → X1-A/C/D (L) → X2-B (S–M) → X2-C (L; gated by P0-7/G2).
5. **Phase 4–5 (M):** analyse, freeze, registry, readiness review.

**Highest value per effort:** Phase 1 analyses; Paper 1 positive controls; X3-A (evaluation-only with state-shuffle/oracle/controller); X2-B baselines. **Highest total value but most costly:** X2-C and X1-A/C. **Lowest value:** X3-C, LLM-judge comparison.

---

# FINAL INDEPENDENT RECOMMENDATION

- **Paper 1 strategy.** Narrow the title/claims now (drop "secure"). Run a **minimal rigorous campaign**: dependency-graph fault set with mutation controls, five-way security oracles with local-canary positive controls, a structural + differential Qwen isolation test, and a stored JUnit report. Deterministic scenarios reported as counts, Wilson intervals only for timing-randomised ones. Fix defects only under a new tag with full re-run. Do not build a validator to pass a test.
- **Paper 2 strategy.** Correct provenance (A + trainer enquiry); reframe as a deterministic, safety-hardened evaluator with moderate, honestly scoped agreement; add question-cluster inference, baselines, an adversarial false-accept analysis and the upstream arm; make a **new question-disjoint, temporally disjoint, independently authored, properly documented benchmark the primary confirmatory set** and demote the old 64 to exploratory/initial evidence. Merge with P0-7 route C so there is one human round, not two.
- **Paper 3 strategy.** Reframe as a **controlled decomposition** (shield vs rules vs heuristic vs learned policy) in simulation; PPO is a studied component, not the claimed contribution. Persona × training-seed inference; add the oracle, controller, +G crossing, rule-ablation, state-shuffle and BC controls; equivalence margins fixed in advance; retrain in a consistent environment with a budget series if you want a claim about PPO as a method.
- **Is a new human benchmark needed?** Yes, as a confirmatory set — strongly beneficial and effectively necessary for a validity claim beyond pilot-scale; not necessary for a correct, narrowly scoped paper. Its value is in question-disjointness, temporal disjointness and answer-source independence, not raw N.
- **Experiments that should actually be run.** X2-A, X3-0 (analyses); X3-A; X1-A, X1-C, X1-D; X2-B; X2-C (with approvals); X3-B (with pre-specified trigger); X1-B.
- **Experiments that should NOT be run.** N1–N10 (I.12), notably the frozen-script rerun, deterministic-repetition Wilson claims, a validator built to pass a test, Option C/D, PPO tuning, more same-author personas as "generalisation", tuning on the new benchmark.
- **What must happen before manuscript writing.** Phase 0–4 complete, registry verified from a clean checkout, per-paper gates (XII.1–XII.3) met, cross-paper gate (XII.4) met, and the Phase 5 independent review passed.

# DECISIONS STILL REQUIRING USER APPROVAL

1. **Paper 3 framing:** approve the decomposition framing (PPO not the claimed contribution), and decide whether to authorise **X3-B** (retraining in a training-consistent environment; touches training/environment definitions, which CLAUDE.md reserves to you) and the pre-specified Stage-2 trigger; fix the equivalence margin δ and superiority margin m.
2. **Paper 1 scope/title:** approve dropping "secure"; approve the minimal campaign (X1-A/C/D, X1-B without a validator); approve the defect policy (fix only under a new tag, full re-run); decide whether a `FeedbackValidator` is wanted as a separate change.
3. **New human benchmark go/no-go** (X2-C), including who authors the questions/answers, who the raters are, and whether volunteer-written answers are in scope.
4. **P0-7 and P0-1 external actions:** send the institutional/venue enquiry now (including the planned new round) and the trainer enquiry; provide the records you can recover. (Institutional determination is the institution's, not mine or yours alone.)
5. **Upstream sensitivity (X2-B):** approve running it, and approve the label-free mapping rule for the composite.
6. **P1-12:** choose the authoritative canonical file; approve the supersession note, the claim registry, and the two `CLAUDE.md` corrections (human-evidence line; "statistical unit is the session").
7. **Wording:** approve the replacement wording for P0-3/4/5 and the P1 errata (boundary-saturated actions; activation vs override; five-seed volatility table; P1-11 hash).
8. **Environment lock for new runs** (a dependency-management change; the `.venv` pin violations remain untouched unless you say otherwise).
9. **Pre-registration mechanism:** git-hash tag only, or an external registry (which requires an account you would create).
10. **Frontend:** whether an accessibility/docs branch may proceed in parallel, and the code-freeze scope for Paper 1.

---

# LIMITS OF THIS PLAN

- Sizes/effort classes and the ≈ 20–30 question estimate are my estimates; the actual N comes from the precision simulation in Phase 2.
- The persona-target rule `round(10·skill)/2` is my arithmetic on five numbers; the frozen config does not state it.
- I did not verify whether training used the five evaluation personas, the deployed question-bank size, or how the 64 benchmark answer texts were produced beyond the first 70 lines of the builder script (all authored in one script; generation method for the remaining items not read).
- Paper 1 statements are from reading code and stored results; nothing was executed. Upstream-checkpoint behaviour under the R mapping is untested.
- I did not search for or cite literature; any RL-evaluation-methodology or benchmark-design references must come from Zotero or verified sources before use.
- Institutional and venue requirements are unknown (venue TBD); I do not determine policy.
