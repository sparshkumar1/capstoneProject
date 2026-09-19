# P0 / P1 Decision Plan — what is wrong, what survives, what needs a new experiment (2026-09-19)

**Status: decision document only.** No experiment was run, no model retrained or tuned, no frozen artifact edited, no manuscript text written, no fix implemented. Every recommendation below waits for the user (`P0_P1_USER_DECISIONS.md` is the short version).

Sources: `P0_FORENSIC_SUMMARY.md` and `P0_1…P0_7_*_FORENSIC.md`; `research/CLAUDE_HANDOFF/*`; `research/CANONICAL_SCIENTIFIC_TRUTH.md`; `CROSS_PAPER_CLAIM_EVIDENCE_MATRIX.csv`; `CLAUDE_NUMERICAL_VERIFICATION.csv`; `CLAUDE_IMPROVEMENT_PLAN.csv`; `CLAUDE_STALE_ARTIFACT_AUDIT.csv`. Raw files were opened only where a disputed finding needed checking (listed in §12).

**Evidence labels.** *(frozen)* = read from a frozen file. *(replay)* = evaluation-only replay of frozen code/checkpoints, reproduced the frozen numbers, scratchpad only (P0 pass). *(diagnostic, this pass)* = new read-only calculation on stored frozen files, exploratory, not part of any frozen study, scripts in the session scratchpad only.

**Classification key (as requested).** A documentation error · B reporting/wording error · C analysis error · D frozen result invalid *for the claim* (the number is fine, the claim it was attached to is not) · E evidence gap · F reproducibility gap · G human/ethics documentation gap · H new experiment required · I user decision required · J institutional decision required. **H is used only when the intended claim cannot be supported by any existing data.** Where a new experiment is only needed *if a stronger claim is kept*, I write "H (conditional)" and list the no-experiment path first.

---

## 1. Decision matrix (summary)

Full columns (CURRENT_EVIDENCE, OPTIONS, RERUN_SCOPE, ARTIFACTS_AFFECTED, …) are in the per-issue blocks in §3–§4. Priority: **P0** = blocks any manuscript; **P1** = must be disclosed/corrected before submission; **P2** = hygiene.

| ID | Paper | Problem (short) | Classification | New experiment? | User dec. | Instit. dec. | Recommended path (one line) | Prio |
|---|---|---|---|---|---|---|---|---|
| P0-1 | 2 | CrossEncoder is a partially fine-tuned derivative, not off-the-shelf; training provenance unrecoverable | A, B, D(for "off-the-shelf"), E, F, I | **No** for disclosure; H (conditional, optional) for an upstream sensitivity run | Yes | No | Disclose now (A); ask the trainer for records (B) in parallel; decide on E only if records fail and a leakage statement is wanted | P0 |
| P0-2 | 3 | PPO's contribution is not identified (const-Same+guardrails = PPO+guardrails) | C, D(for "PPO"), E, I | **No** for reframing; **H (conditional)** if a PPO-specific claim is kept | Yes | No | Reframe Paper 3 (Option A/C); run the minimal two-stage study only if the user wants a PPO claim | P0 |
| P0-3 | 3 | "0 out-of-bounds violations" is a simulator invariant; real attempted count is 232 | B, C, A(docstring), D | **No** | Yes (wording) | No | Analysis correction in an addendum; replace metric set | P0 |
| P0-4 | 3 | 563 = rule activations, not interventions; 99 actual changes (7.9 %) | B, C | **No** | Yes (wording) | No | Report activation, override, no-op share separately | P0 |
| P0-5 | 3 | 0.088 is seed 123 only; five-seed 0.186 vs heuristic 0.160 | B, C, D | **No** | Yes (wording) | No | Replace with five-seed trade-off table; drop "smoother" claim | P0 |
| P0-6 | 1 | Fault (10/10) and Qwen (5/5) are literal PASS; security oracle weak; 213-test count has no log | A, B, D, E, F, H (conditional), I | **No** to narrow; **H (conditional)** to keep fault-tolerance / Qwen-isolation / containment claims | Yes | No | Narrow now (Option A); build protocol in §8 only if the title keeps "fault-tolerant" | P0 |
| P0-7 | 2 | Rater/adjudicator provenance, consent, ethics determination absent from repo | E, G, A(wording), I, **J** | **No** analysis rerun; new human data only if provenance can't be documented | Yes | **Yes** | Obtain records → ask the institution → disclose transparently; do not create retrospective evidence | P0 |
| P1-1 | 2 | Benchmark = 8 questions × 8 constructed answers (README says 8 questions/domain, 11 categories; data has 10) | A, B, C, F | **No** (re-analysis of stored data) | Approve reanalysis | No | Correct description; add question-clustered, leave-one-question-out, per-category and overlap-subset analyses as a *new* file; claim the narrower result | P1 |
| P1-2 | 2 | Correct-but-concise answers systematically under-scored | B, E | No | No | No | Report as principal limitation with per-category table | P1 |
| P1-3 | 2 | θ = 0.30 / dampening chosen on N=20 pilot that shares 4 of 8 benchmark questions | A, B, C, E | No (optional analysis) | Approve wording | No | Disclose; report non-overlap-subset result; do not claim held-out validation for those 4 questions | P1 |
| P1-4 | 3 | Training env (T=15, continuous 0.1 steps) ≠ evaluation env (T=10, integer ±1) | B, E, D(for "learns X") | H (conditional) | Yes | No | Disclose; a training-consistent evaluation belongs to the P0-2 study | P1 |
| P1-5 | 3 | Reward is oracle imitation; guardrails restate the oracle rules | B, E | No | Approve framing | No | Frame as "imitation of a rule oracle + rule-based shield"; drop implied tracking optimisation | P1 |
| P1-6 | 3 | Sensitivity narrative contradicts stored sweep | B, C | No | No | No | Restrict to what the sweep shows (only avg-performance and difficulty change the action at the neutral point) | P1 |
| P1-7 | 3 | Deployed PPO (`rl/checkpoints/seed_123`, sha 2ab8d514…) ≠ evaluated PPO (299437ea…) | A, B | No | No | No | State which checkpoint each claim refers to | P1 |
| P1-8 | 1 | Latency mean 1960.8 ms contaminated by a cold-start-scale outlier (P99 26 369 ms); raw samples not stored | B, C, E | No (optional re-measure) | Optional | No | Report median/percentiles; label the outlier; re-measure only if a "warm latency" claim is wanted | P1 |
| P1-9 | 1 | Security pass criterion is weak (see P0-6) | B, E | H (conditional) | Yes | No | Word as "did not compromise the host in this harness"; discriminating oracles only in the §8 campaign | P1 |
| P1-10 | 1/2 | Hedging words reduce the technical score (≤ 0.03), contradicting "100 % acoustic insulation" | A, B | No | No | No | Reword: acoustic features never reach the evaluator; a small lexical hedging penalty applies to the transcript | P1 |
| P1-11 | Cross | Long commit hash `b7cad49b6b7a…` does not exist; real hash is `b7cad49529c3…` | A | No | No | No | Errata note citing the tag `v1.0-paper3-complete` (verified to resolve to the real hash) | P1 |
| P1-12 | Cross | Root `CANONICAL_SCIENTIFIC_TRUTH.md` (declared sole authority in CLAUDE.md) still says ρ = 0.6975, N=20 | A, I | No | **Yes** (which file is authoritative) | No | Designate the handoff copy authoritative via a new supersession note; CLAUDE.md update after approval | P1 |
| P1-13 | 3 | Session-level N=25 is pseudo-replicated (5 personas × 5 seeds); persona-level test weaker | C | No | No | No | Report persona-level and session-level analyses side by side | P1 |
| P1-14 | 3 | Frozen ablation "Safety Shield" rows use a leaked loop variable (interv 112, viol 46/0) | C, A | No | No | No | Errata with corrected values (563 / 232 / 0.160) | P1 |
| P1-15 | 3 | Dimension-4 ablation equality arises from guardrail masking, not policy insensitivity | B | No | No | No | Reword | P1 |

P1-13…P1-15 come from `CLAUDE_IMPROVEMENT_PLAN.csv`; they were not in your list of twelve but belong to the same forensic set.

**Bottom line of the matrix.** Of 22 issues only three carry a *conditional* need for a new experiment that no documentation change can replace (P0-2, P0-6, and P1-4 folded into P0-2). Everything in P0-3/4/5 and all twelve listed P1 items except P1-12's decision can be handled without any rerun. P0-7 is the one blocker that is neither analysis nor experiment.

---

## 2. Cross-cutting facts established or refined in this pass

1. **The R calibration in the evaluator is built around the fine-tuned model's output range** *(code, `services/evaluator/app.py:163-168`)*: `R = clip((raw − 0.20) / 0.70, 0, 1)` with a comment that "baseline floor is ~0.20 for unrelated/noise pairs, 0.40–0.55 for partial/weak reasoning, 0.70–0.95 for strong logical entailment". The tuned checkpoint's config declares one label and an `Identity` activation, consistent with a bounded regression head trained with a Huber + rank objective (`best_model_info.json`). This is a second, independent reason "off-the-shelf" is wrong for the *pipeline* (the mapping constants presuppose the derivative's score distribution). It also means **swapping in the upstream checkpoint is not a drop-in change**: whether upstream's output lies in the assumed range is untested (my hypothesis: it will not — its published outputs are unbounded relevance logits — but I did not run it). Any upstream run needs a pre-specified R mapping, i.e. a new design decision, before it is executed.
2. **Question clustering does not inflate ρ; it deflates it** *(diagnostic, this pass, from `paper2_case_level_results.csv`, n = 64)*. Human means are equal across the 8 questions by construction (question-level ICC(1) of human gold = −0.13), whereas model means differ strongly by question (ICC(1) = 0.49; e.g. OS & Concurrency: human 0.49 vs model 0.066). Pooled ρ = 0.381; within-question (demeaned) ρ = 0.580. Per-question ρ ranges 0.44–0.91 and is positive for all 8 questions. Percentile bootstrap over cases (frozen): [0.158, 0.577]; resampling questions as clusters (4 000 draws, 8 clusters): [0.302, 0.589]; leave-one-question-out ρ: 0.352–0.434. So the frozen case-level CI is *not* anti-conservative for this balanced design, but the estimand is limited to **8 questions**.
3. **The pilot-overlap questions carry the stronger correlation** *(diagnostic, this pass)*: composite ρ = 0.709 on the 4 questions (qid 1, 3, 10, 41; 32 cases) that overlap the N=20 pilot and the legacy question bank, versus ρ = 0.425 on the other 4 (qid 7, 15, 22, 50; 32 cases). R-only: 0.584 vs 0.449; MAE 0.246 vs 0.338. This is post-hoc, unpowered (four clusters per side), and question difficulty also differs, so it is **not** evidence of leakage or tuning bias; it is a reason to report the non-overlap subset and not to describe the 64-case result as held-out for all 8 questions.
4. **The very high human reliability mostly reflects the benchmark construction** (P0-7 §4: author-assigned categories explain ≈ 98–99 % of each rater's variance). Within categories the evaluator's correlation with the gold is mixed: e.g. verbose_correct ρ = −0.55 (n = 8), keyword_stuffed −0.51 (n = 8), concise_correct −0.11 (n = 8), misconception +0.36, verbose_wrong +0.45 *(diagnostic)*. Overall ρ is therefore largely between-category ordering of constructed answers. Per-category n is 2–8; none of these within-category values is a reliable estimate.
5. Stored Paper 1 raw JSON contains no per-sample latency lists, so "cold vs warm" cannot be separated from stored data (P1-8).

---

## 3. P0 issues, one by one

### P0-1 — CrossEncoder provenance (Paper 2)

- **CURRENT_EVIDENCE.** Tensor comparison *(P0-1 §1.1)*: embeddings and layers 0–3 bit-identical to `cross-encoder/ms-marco-MiniLM-L-6-v2`; layers 4–5, pooler, classifier changed (16.28 % of parameters); no published upstream revision matches (§1.2); `best_model_info.json` = a Huber+rank fine-tune record (epoch 5, step 660, val Spearman 0.785); a second fine-tuned sibling (`1_best_model_zip`, step 1245, val ρ 0.7918) existed and was deleted 2026-08-29; config stamped by transformers 5.0.0 / sentence-transformers 5.2.3, i.e. not the project environment; no training code, data, split, hyperparameters, or author record anywhere in the repo, history, or machine. Plus §2 fact 1 above (R calibration constants).
- **CLASSIFICATION.** A, B, D (for the claim "off-the-shelf / zero fine-tuning"), E, F, I.
- **Answers to your eight questions.**
  1. *Exact status:* a partially fine-tuned derivative of `ms-marco-MiniLM-L-6-v2` with undocumented training. Reproducible **as a file** (SHA-256 `6a241a55…4450`, byte-identical to the 2026-04-13 commit); not reproducible **as a construction**.
  2. *"Off-the-shelf" definitely false?* Yes, for the weights (bit-exact frozen bottom, changed top) and independently supported by the R calibration constants. Nothing in the repo supports it; only prior audit documents assert it, and their explanation for `best_model_info.json` has no evidence.
  3. *"Fine-tuned" supported?* Yes as a fact about the weights. **What it was fine-tuned on is unsupported**, so "fine-tuned on interview data / passage pairs" must not be written.
  4. *"Partially fine-tuned derivative" the safest wording?* Yes: it states only what the tensors show (top layers, pooler and head modified; lower layers unchanged). Add the hash and "training data, code and hyperparameters not available".
  5. *Can training be reconstructed?* Not from anything on this machine or in Git. It could exist off-machine (the notebook environment, download archive, cloud drive, the trainer's records). Only the person who ran it can settle this. A new fine-tune would be a **different model**, not a reconstruction.
  6. *Is inference reproducible without training provenance?* Yes: same file + same evaluator code + same benchmark + hashes ⇒ same scores (subject to library versions — the project `.venv` violates the pinned versions per CLAUDE.md, which should be recorded with any rerun).
  7. *Can Paper 2 use the checkpoint?* Yes, **as a disclosed, hash-pinned derived checkpoint validated as a black box**, provided leakage is stated as *undetermined* (4 of the 8 benchmark questions appear verbatim in the legacy evaluator bank; the benchmark itself first appears in Git five months after the checkpoint).
  8. *Rerun required?* **No for correctness of the paper's numbers.** Recommended-but-not-required: an upstream sensitivity run, useful only to (a) bound how much the undocumented fine-tune contributes and (b) give a leakage-free reference if provenance is not recovered.
- **Options** (evaluated, none chosen):

| | Scientific benefit | Scientific risk | Reproducibility | Time/cost | Effect on existing Paper 2 results | Existing results remain useful? | New human benchmark? | Full 64-case evaluation? |
|---|---|---|---|---|---|---|---|---|
| **A** keep current, disclose as derived with incomplete provenance | Honest, immediate, no new data | Reviewers may discount R; leakage stays undetermined; no train/test statement possible | Inference reproducible; construction not | Hours (writing/errata) | None | Yes, all | No | No |
| **B** recover provenance from the creator | Could convert "incompletely documented" into "documented fine-tune" and allow a leakage statement | Records may not exist, or may show overlap with benchmark items/references; must then be reported | Fully documented only if artifacts recovered | Depends on person; likely days | None unless overlap is found | Yes; if overlap found, some results need caveats | No | Only an overlap check against the 8 questions/64 references (no model rerun) |
| **C** reproduce the fine-tune from scratch with documented data, code, config, seed | A fully reproducible, leakage-controlled model | It is a *new* model: R, all R-containing ablations, dampening and θ may shift; new labelled training data needed (labels from where?); scope creep; risk of tuning to the benchmark | Best | Weeks; needs labelled training data that does not exist in the repo | Replaces R everywhere; old results become "historical checkpoint" | Only as a comparison point | Not for the current gold; training data must be independent of it | Yes (full rerun of the ablation table and robustness suites) |
| **D** switch Paper 2 to the true upstream checkpoint and rerun | Removes the undocumented-fine-tune issue entirely; public, verifiable model | Upstream output scale ≠ the (raw−0.20)/0.70 mapping (§2 fact 1) — needs a new, pre-specified mapping; θ and the 0.30 dampening were chosen for the old R; results will change and may be worse or better; a change made after seeing the gold results is a garden-of-forking-paths risk unless pre-specified | Fully reproducible | 1–3 days (evaluation only, no training, no new human data) | All R-dependent numbers change (composite, R-only, S1+R, S2+R, dampening, metamorphic/adversarial); S1-only, S2-only, S1+S2 unchanged | Old results become the "derived-checkpoint" arm only if kept | **No** — the gold is independent of any model | Yes, full 64 cases plus ablations and robustness suites |
| **E** both checkpoints as a controlled provenance sensitivity study | Bounds the effect of the undocumented fine-tune; keeps existing results as the primary arm; strongest honest position if B fails | Extra text and complexity; needs the pre-specified upstream mapping (as in D) | Reproducible (both hash-pinned) | 1–3 days evaluation-only | None to existing results; adds an arm | Yes, all | **No** | Yes for the upstream arm (all 64, same gold, same protocol) |

- **Do we need a new human benchmark if the model changes?** No. The 64-case gold is human-labelled from blinded sheets that contain neither model scores nor category labels (P0-7 §1); it does not depend on which scorer is later evaluated. Caveat to verify before any claim of model independence: the answers were generated by `build_comprehensive_benchmark.py` by the study authors (method of text generation is not documented in the files I read), so I cannot state whether any answers were selected or edited while looking at evaluator outputs. I did not find evidence either way.
- **CURRENT_CLAIM_STATUS.** "Off-the-shelf / zero fine-tuning / no PREPAIred-specific adaptation": **refuted**. "Fine-tuned": supported by the weights, unsupported as to data. Leakage: undetermined.
- **DEFENSIBLE NOW.** The wording in P0-1 §3 (supportable list), with the hash.
- **RECOMMENDED PATH (sequenced, nothing executed).** A now (errata + manuscript wording); B in parallel because it is cheap and decisive; E only if B fails *and* the paper wants a leakage-free reference; C and D not recommended (C invents a new model with no labelled data; D changes the primary result after the fact).
- **NEW_EXPERIMENT_REQUIRED.** No. **Conditional H:** E (spec in §9.2).
- **RERUN_SCOPE.** None (A/B). E: 64 cases × the R-containing configurations, evaluation-only.
- **ARTIFACTS_AFFECTED.** `PAPER2_MODEL_PROVENANCE_GATE.md`, `data_lineage.md`, `benchmark_integrity_audit.md`, `PRIORITY_0_FINAL.md`, `FINAL_CROSS_PAPER_AUDIT.md`, `CLAUDE_HANDOFF/*` (incl. `CANONICAL_SCIENTIFIC_TRUTH.md` §A/§B, `MANUSCRIPT_AUTHORING_GUIDELINES.md`), `data_leakage_report.md`, README/docs that say "MiniLM-L12" or "fine-tuned on X". All frozen → errata in a new file. **Paper 2 only**; the capstone app is unaffected numerically.
- **OLD_RESULTS_RETAINED?** Yes (A, B, E). Only C/D make them historical.
- **USER_DECISION_REQUIRED.** Yes: who trained it; A vs A+B vs A+B+E. **INSTITUTIONAL:** No.
- **RISK.** High if "off-the-shelf" survives into a manuscript (falsifiable by anyone who hashes the weights). Moderate for undetermined leakage.

### P0-2 — PPO contribution (Paper 3)

- **CURRENT_EVIDENCE** *(P0-2, replay)*. MAE: Fixed 1.200; Heuristic 0.473; raw PPO 0.804–1.138 (mean 0.958); PPO+guardrails 0.673–0.687 (mean 0.677); **constant-Same + same guardrails 0.673**; constant-Harder + G 0.502; random + G mean 0.795. PPO+G vs Const-Same+G: 5 of 125 sessions differ (pooled ΔMAE +0.0044, PPO marginally worse). PPO+G equals Fixed on both high-skill personas in every seed. Rules decide 40–49 % of guarded turns; PPO's own proposals are 67–96 % "Same". Heuristic beats every PPO variant (paired +0.200, CI [+0.07, +0.35]).
- **CLASSIFICATION.** C (attribution), D (frozen result invalid *for the claim "PPO improves tracking"*), E (no PPO-free guardrail control in the frozen design), I. Not F: the numbers reproduce.
- **What the evidence supports, separated.**
  1. *PPO-specific contribution:* raw PPO beats fixed modestly and seed-dependently, only for the two low-skill personas (−0.06 to −0.40 MAE by seed). With guardrails on, no measurable PPO-specific contribution in this design.
  2. *Guardrail contribution:* essentially all of the 1.200 → ≈0.67 improvement, and all of the cross-seed "stability" (SD 0.006).
  3. *Constant-Same behaviour:* reproduces guarded MAE to three decimals; matches PPO's final action on 200/250 turns in every seed.
  4. *Heuristic behaviour:* better than every PPO variant on tracking (0.473) and on oscillation (0 vs 0.160); volatility comparable (P0-5).
  5. *Simulated-environment behaviour:* five author-defined personas, a persona-target MAE, training ≠ evaluation environment; conclusions are about this simulator only; no real-user claim.
- **Options.**

| | Scientific question | Required experiment | Sample/unit | Expected evidence | Claim that becomes defensible | Claim that remains impossible |
|---|---|---|---|---|---|---|
| **A** reframe around guardrailed adaptive-policy behaviour, state that PPO's contribution is not isolated | "What does a rule-based guardrail policy achieve in a simulated difficulty-control task, and what does PPO add?" | None (frozen data + P0 replay; the controls are diagnostics) | 25 sessions/condition; persona is the real unit | Existing tables + a labelled const-Same+G control | "Guardrails account for the improvement; raw PPO helps modestly for low-skill personas; the heuristic is better; PPO's marginal contribution under guardrails is not detectable here" (a negative result) | "PPO learned adaptive difficulty"; PPO superiority over heuristic/constant; real-learner benefit; seed-stability of PPO |
| **B** new controlled PPO-contribution experiment | "Does a learned policy improve tracking beyond a state-blind action + the same guardrails?" | §9.1 (two-stage) | persona (n ≥ 24 proposed), evaluation seeds nested, training seeds nested | Direct, pre-specified paired contrasts | A PPO-specific statement **if** the pre-specified criterion is met; otherwise a properly powered negative | Real-learner effect; general RL advantage; anything about the deployed app |
| **C** redesign as a guardrail / adaptive-control paper | "Is a small transparent rule set enough for simulated difficulty control?" | Optionally a rule-ablation (each of G1/G2/G4/G5 on/off) — **not** required | as A | Rule-level attribution (how much each rule contributes) | "Transparent guardrails suffice in this simulator; PPO is a comparator" | Any PPO-centred claim; generalisation beyond the simulator |
| **D** change scope/title/research question | — | None | — | — | Needed only if neither A nor B yields a standalone contribution | — |

- **CURRENT_CLAIM_STATUS.** PPO-centred headline: **unsupported**. Guardrail-centred description: supported in simulation.
- **RECOMMENDED PATH.** A/C combined for the manuscript unless the user wants a PPO claim, in which case run §9.1 Stage 1 (evaluation-only, existing checkpoints, expanded personas). Stage 2 (retraining in a training-consistent environment) only after approval and only if Stage 1 leaves the question open. Change the title only if the final framing is D.
- **NEW_EXPERIMENT_REQUIRED.** No for A/C; H (conditional) for a PPO claim. **RERUN_SCOPE.** Stage 1: evaluation only. Stage 2: retraining — needs explicit approval and a new frozen config.
- **ARTIFACTS_AFFECTED.** `PAPER3_FINAL_REPORT.md`, `PAPER3_FINAL_FREEZE.md`, `CLAUDE_HANDOFF/*`, `CANONICAL_SCIENTIFIC_TRUTH.md` §E, claim-matrix rows. Frozen → errata/addendum. New freeze/tag only if a new experiment is run. **OLD_RESULTS_RETAINED?** Yes.
- **USER_DECISION_REQUIRED.** Yes. **INSTITUTIONAL.** No. **RISK.** High: the current headline attributes the guardrails' effect to PPO.

### P0-3 — Out-of-bounds (Paper 3)

- **CURRENT_EVIDENCE.** The environment/orchestrator clamp difficulty to [1, 5] for every policy; the frozen counter counts *pre-clip* attempts; the "0" in summary/report/handoff is a hard-coded literal (`execute_paper3_study.py:774, 886, 895`), while the frozen seed CSV records 26/71/41/33/61 = 232. Attempts (replay): raw PPO 136/1,250, PPO+G 232/1,250 (all at the floor, none above 5). A constant-Harder policy with **no** guardrails also has 0 actual out-of-bounds states.
- **CLASSIFICATION.** B, C, A (guardrail docstring advertises a boundary clamp the code lacks), D (for "guardrails eliminate 100 % OOB"). **ANALYSIS CORRECTION — NO NEW SCIENTIFIC EXPERIMENT.** Every number already exists.
- **Metrics separation (the four things you asked to distinguish).**

| Quantity | Definition | Available? | Value |
|---|---|---|---|
| Attempted violation | final (post-guardrail) action would leave [1,5] before clamping (the frozen counter) | Yes (frozen CSV + replay) | 232/1,250 (18.6 %) |
| Raw attempted violation | PPO's own proposed action would leave [1,5] | Replay (raw runs) | 136/1,250 (10.9 %) |
| Guardrail intervention on an attempt | a rule changed an out-of-range proposal into an in-range one | **Not separable from stored data** — the rule module has no boundary logic, so this is 0 by construction | 0 (structural) |
| Simulator clipping | attempts absorbed as no-ops by `np.clip` | Yes | equals attempts (all at floor) |
| Final actual invalid states | post-clip difficulty outside [1,5] | Yes | 0, an invariant for every policy — not a result |

  "Unblocked attempts" cannot be reported as a guardrail statistic: no rule ever blocks a boundary move. State the actual origin: of the 232, 112 came from rule G4 ("stuck → Easier") at the floor and 120 from PPO's own "Easier".
- **DEFENSIBLE NOW.** "The environment clamps difficulty to [1,5]; 10.9 % (raw) / 18.6 % (guarded) of turns proposed an Easier move at the difficulty floor, absorbed as a no-op." Call it "boundary-saturated actions", not "violations".
- **RECOMMENDED PATH.** Addendum with the table above; do not use "0 violations" or "eliminates 100 %". Optional later: fix or stop advertising the boundary rule in the docstring (behaviour unchanged; needs approval).
- **NEW_EXPERIMENT_REQUIRED.** No. **RERUN_SCOPE.** None. **ARTIFACTS.** report, freeze, handoff, canonical §E, claim-matrix, `rl/guardrails.py` docstring. **OLD_RESULTS_RETAINED?** Yes. **USER_DECISION.** Yes (wording). **INSTITUTIONAL.** No. **RISK.** High until corrected (it is an outright false headline).

### P0-4 — Guardrail interventions (Paper 3)

- **CURRENT_EVIDENCE** *(replay, matches frozen per-seed counts)*. 5 seeds × 25 sessions × 10 turns = 1,250 turns. Activations 563 (45.0 %); action changes 99 (7.9 %); no-op activations 464 (82.4 % of activations); sessions with ≥ 1 change 41/125. By rule: G5 205 activations/0 changes; G4 167/15; G1 111/49; G2 80/35; G6 0. Directions: Harder→Easier 34, Same→Easier 30 (64 lowered difficulty); Easier→Same 30 (blocked a decrease); Harder→Same 5 (blocked an increase; 39 Harder proposals in total overridden). "Normal" persona: 250 activations, 0 changes.
- **CLASSIFICATION.** B, C. **No new experiment.**
- **Correct interpretation and denominators.**

| Measure | Value | Denominator | Use |
|---|---|---|---|
| Rule activation | 563 | 1,250 turns (45.0 %) | diagnostic count; **not** "interventions" |
| Action override (raw ≠ final) | 99 | 1,250 turns (7.9 %); per-seed 4.8–14.8 % | the primary intervention rate |
| Activation with unchanged action | 464 | 563 activations (82.4 %) | shows how often rules agreed with PPO |
| Blocked from decreasing | 30 | 1,250 turns (2.4 %); of 99 overrides (30.3 %) | direction breakdown |
| Blocked from increasing | 39 (34 to Easier, 5 to Same) | 1,250 turns (3.1 %) | direction breakdown |
| Session-level | 41 of 125 | sessions (32.8 %) | prevalence |

  Two further cautions: per-turn rates are path-dependent (an override changes the subsequent trajectory), and `paper3_guardrail_results.csv` has **213** rows (seed 123 + historical-mismatch), not 563.
- **DEFENSIBLE NOW.** "Guardrail rules matched on 45.0 % of turns but changed PPO's action on 7.9 %, concentrated in two of five personas."
- **RECOMMENDED PATH.** Addendum with the six-row table; correct the trace-file description. **USER_DECISION.** Yes (wording). **INSTITUTIONAL.** No. **OLD_RESULTS_RETAINED?** Yes. **RISK.** Medium.

### P0-5 — Volatility (Paper 3)

- **CURRENT_EVIDENCE.** Definition: mean |Δdifficulty| per turn, averaged over 25 sessions. 0.088 = seed 123 only (raw and guarded coincide). Five-seed guarded volatility per seed: 0.268 / 0.088 / 0.208 / 0.240 / 0.128, mean 0.186 (population SD 0.068 as frozen; sample SD 0.076). Heuristic 0.160. Raw PPO mean 0.078. Guarded − heuristic, paired: seed 123 −0.072 [−0.112, −0.032]; seed 999 −0.032 [−0.096, +0.032]; the other three positive; pooled +0.026 [−0.024, +0.078] (pseudo-replicated across seeds). Frozen `volatility_reduction_pct = −140.21` (guardrails *raised* volatility 2.4×). Low volatility partly equals not adapting (const-Same+G 0.080; PPO+G volatility 0 on the two high-skill personas).
- **CLASSIFICATION.** B, C, D. **No new experiment.**
- **Answers.** (1) Correct five-seed statistic: 0.186 (0.088–0.268). (2) Heuristic comparison: 0.160; no reliable difference; 2 of 5 seeds lower. (3) Raw-PPO comparison: raw 0.078 is lower than both, but raw PPO tracks worse (MAE 0.958). (4) Any statistically supported difference: only in the seed-123 pair, which is the lowest-volatility seed and has no documented primary-seed rationale (the frozen config has no primary-seed field; git cannot show it was designated before results were seen; I draw no inference about intent). (5) Documentation/analysis only: yes.
- **On "guardrails increase volatility by a large percentage".** Check done against the stored value: `volatility_reduction_pct = −140.21` is arithmetically consistent with raw 0.078 → guarded 0.186 (+139 %); the direction is supported. It is a comparison of *means over the same five checkpoints*, so it is defensible as "≈ 2.4× higher", not as a percentage with a CI. Do not repeat it as a precise figure until the denominator (five checkpoints × 25 sessions, guarded vs raw, same evaluation seeds) is stated.
- **RECOMMENDED PATH.** Five-seed trade-off table (MAE, volatility, oscillation) for heuristic / PPO+G / raw PPO / const-Same+G. **USER_DECISION.** Yes (wording). **INSTITUTIONAL.** No. **OLD_RESULTS_RETAINED?** Yes. **RISK.** Medium-high (a favourable single-seed number stands in for an aggregate).

### P0-6 — Paper 1 evidence (Paper 1)

- **CURRENT_EVIDENCE** *(P0-6, by reading; nothing was executed)*. Fault scenarios: A×1, B×5, C×4 (literal PASS). Qwen: B×3, C×2. Security: all nine attacks were run; four outcomes discriminate (SEC-01/03/04/05), five do not (02/06/07/08/09). "213 passed" has no stored log (only `204 passed, 1 skipped`, 383.87 s). `FeedbackValidator` does not exist. SEC-09's pass predicate is vacuous. Concurrency and latency are real measurements.
- **CLASSIFICATION.** A, B, D (for "10/10", "5/5", "9/9 contained", "213 passed"), E, F, H (conditional), I.
- **What survives.** See the claim table in §8.1.
- **Options** (Paper 1):
  - **A narrow** to genuinely evidenced results — no rerun; the title needs narrowing too (§10).
  - **B fault-injection campaign** — §8.2.
  - **C Qwen-isolation campaign** — §8.3.
  - **D both, plus discriminating security oracles and a stored test report** — §8.2–§8.5. Note that a security-oracle upgrade is a *third* piece (§8.4) that neither B nor C contains.
- **RECOMMENDED PATH.** A now. B+C+§8.4 only if the title keeps "fault-tolerant"/"secure"; a rerun of the frozen script would merely reprint the literal PASS strings and must not be presented as a rerun of the experiment.
- **NEW_EXPERIMENT_REQUIRED.** No for A; H (conditional) for B/C/D. **RERUN_SCOPE.** New harness, new artifacts; the frozen `execute_paper1_study.py` is left as is. **ARTIFACTS.** `PAPER1_FINAL_REPORT.md`, `paper1_fault_injection_results.csv`, `paper1_qwen_isolation_results.csv`, `paper1_security_results.csv` (weak oracle), `fault_injection.csv`, handoff/canonical §C, `PAPER1_EXECUTION_COMPLETION.md`. **OLD_RESULTS_RETAINED?** Concurrency, latency, security run outputs: yes. Fault and Qwen tables: retained only as "design-level handling matrix", not as results. **USER_DECISION.** Yes. **INSTITUTIONAL.** No. **RISK.** High (core claims resting on literal PASS strings).

### P0-7 — Human ethics / provenance documentation (Paper 2)

- **CURRENT_EVIDENCE** *(P0-7)*. Frozen protocol (hash-pinned; tag `pre-human-annotation` at 13:59), rater and adjudication files hash-pinned, gold reproducible; `ETHICS_CHECKLIST.md` unsigned with every field blank; no consent, compensation, Gate 1 approval, rater/adjudicator identity or qualification record; rater files last modified 22–53 minutes after the freeze commit (packages built 12:52); identical `timestamp_received` (14:54:35) for all three files; adjudication of 10 items with rationales spans about 6.5 minutes by file times. No PII in the repo. Objective note: the ICC is driven by construction categories.
- **CLASSIFICATION.** E, G, A (wording), I, **J**. **I infer no misconduct;** the repository is silent, which is different from "did not happen".
- **Records audit.**

| Class | Items |
|---|---|
| **Recoverable from the repository** | Frozen protocol and its hash/tag; rater package manifests and zips; raw/frozen rater files and manifests; adjudication guidelines, form and rationales; blinded-sheet design (no category/model score); final gold and completion reports; Git timestamps; the statistics (ICC, α, agreement) |
| **Missing from the repository (may exist elsewhere)** | Who the three raters and the adjudicator were; recruitment and relationship to the authors; qualifications; the instructions/emails each rater actually received; send and return timestamps of the packages (chat/email/drive metadata); time spent; whether external tools/AI assisted a rating or rationale; any consent (even informal, e.g. email acknowledgement) and compensation/acknowledgement terms; any institutional determination or "not human-subjects research" statement; Human Gate 1 approval record; who the "Principal Investigator / Lead Ethics Coordinator" would be |
| **Must be obtained (from people/institution)** | The items above marked missing, **as existing records**: original messages, files with native metadata, institutional correspondence, a dated statement from each rater/adjudicator of what they did and when, labelled as *retrospective* |
| **Cannot be reconstructed** | Consent that was never obtained or recorded; independence/blinding attestations that were not collected at the time (a statement made now is a retrospective declaration and must be dated and labelled as such, never backdated); actual rating times if no send/return records exist; the checklist's pre-distribution sign-off (the checklist required sign-off *before* distribution) |

- **What can and cannot be claimed.** Can: three raters scored 64 constructed answers with a frozen rubric; files hash-pinned; ICC(2,1) 0.953, ICC(2,k) 0.984, α 0.952; ten items above the 0.20 spread were adjudicated; the rest averaged. Cannot (now): independence, qualifications, "committee", "authentic explanations", voluntary informed participation, compensation terms, any approval/exemption/"not human-subjects" status, and "frozen before annotation" if packages were sent before 13:59.
- **Manuscript routes** (institution- and venue-dependent items marked **INSTITUTIONAL DECISION REQUIRED**; I do not decide policy).
  - **A. Proceed with transparent limitation** — technically possible; whether it is *acceptable* depends on the institution and the venue (TBD), so it is not a stand-alone answer. **INSTITUTIONAL DECISION REQUIRED.**
  - **B. Clarification with venue/institution before submission** — sensible before any human-study submission because the record cannot answer the standard ethics-statement questions. **INSTITUTIONAL DECISION REQUIRED.**
  - **C. New documented human rating round** — only if the records cannot be obtained or the institution/venue will not accept a retrospective account. Would need consent, roles, time logs, the protocol unchanged; the existing gold would then be a pilot. (User decision; no rerun of the evaluator is implied.)
  - **D. Institutional determination** — whether one is required, and its form, is the institution's call. **INSTITUTIONAL DECISION REQUIRED.**
- **RECOMMENDED PATH.** Obtain records first (cheapest, and it determines everything else), then ask the institution, then choose A or C. Add findings as a *new* provenance/ethics addendum; do not edit the frozen checklist, manifests or rater files.
- **NEW_EXPERIMENT_REQUIRED.** No analysis rerun; new human data only under route C. **ARTIFACTS.** `ETHICS_CHECKLIST.md` (frozen — addendum), manuscript author lines/wording, handoff wording. **OLD_RESULTS_RETAINED?** Yes (as reproducible data of undocumented provenance). **USER_DECISION.** Yes. **INSTITUTIONAL.** **Yes.** **RISK.** High for publication, not for the numbers.

---

## 4. P1 issues

For each: current evidence · risk · affects the paper? · documentation-only? · analysis correction? · new experiment? · future work · recommended action.

| # | Current evidence | Risk | Affects paper? | Doc-only? | Analysis correction? | New experiment? | Future work | Recommended action |
|---|---|---|---|---|---|---|---|---|
| **P1-1 Benchmark clustering** (Paper 2) | 64 cases = 8 questions × 8 answers (10 categories, 2–8 cases each: concise/verbose/partial/verbose_wrong/keyword_stuffed/misconception 8 each, incorrect 6, contradictory 4, paraphrase 4, suboptimal_correct 2). README says "8 questions per domain" and "11 categories"; claim matrix says "10 topics". Cluster diagnostics: §2 facts 2–4 | Over-generalising from 8 questions; treating 64 as independent; per-category n too small to interpret | Yes — defines the claim's scope | Partly (README/description) | Yes: add question-clustered CI, leave-one-question-out, per-category and pilot-overlap analyses in a **new** file from stored data | **No** | More questions (a wider question sample) | Correct the description; report ρ with case-level CI (frozen) *and* question-level sensitivity; describe as "8-question constructed benchmark" |
| **P1-2 Concise-answer under-scoring** | concise_correct: human 0.912 vs model 0.397 *(diagnostic, matches audit)*; paraphrase 0.844 vs 0.361; verbose_correct 0.984 vs 0.591; overall bias −0.134; 59.4 % of cases under-estimated | Systematic bias against terse correct answers (also a fairness concern for candidates) | Yes — a principal limitation | Yes | No | No | Answer-length/paraphrase-robust scoring | Report the category table; no mitigation claim |
| **P1-3 θ = 0.30 / dampening tuned on N=20 pilot** | Pilot shares 4 of 8 benchmark questions (qid 1, 3, 10, 41). Overlap-subset ρ 0.709 vs non-overlap 0.425 *(diagnostic, exploratory)*. Earlier audit: evaluator code unchanged since 2026-08-27, 64-case gold not used for tuning | Optimism on overlapping questions; leakage undecided (P0-1) | Yes | Mostly | Yes — non-overlap subset result | No | Question-disjoint pilot/test split for any future tuning | State plainly what was tuned on what; report the four non-overlap questions as the closest thing to held-out, with its small n |
| **P1-4 Train/eval environment mismatch** | Training: T=15, continuous difficulty in [0.1, 1.0] with ±0.1 steps (`interview_env.py:63, 402-404`); evaluation: T=10, integer difficulty 1–5, ±1 | The evaluation does not measure what PPO was trained to do; weakens any PPO claim | Yes (Paper 3) | Disclosure yes | No | H (conditional): fold into the P0-2 study; no separate experiment | Train and evaluate in one consistent environment | Disclose; do not change environments without approval |
| **P1-5 Hand-coded reward oracle** | Reward has an oracle-match component (`decision_component = 1 if action == oracle_action`); the guardrails G4/G5 restate the oracle rules; persona targets are author constants | PPO is trained to imitate a rule policy and then wrapped by the same rules; tracking error is not the objective | Yes (framing) | Yes | No | No (an outcome-only reward run would be a new study; future work) | Outcome-based reward, independent evaluator | Frame as "imitation of a rule-based oracle plus a rule-based shield"; do not imply optimisation of target tracking |
| **P1-6 Sensitivity interpretation** | Stored sweep, neutral state, 11 values per dimension: only `s1_avg_perf` (2 of 11 → Easier) and `s5_diff` (6 of 11 → Harder) change the action; perf, confidence, hesitation and progress: always Same | Prose in Paper 3 §5 claims modulation by confidence/hesitation/progress | Yes | Yes | Minor (restate) | No | Sweep around several operating points | Restrict statements to the sweep; no causal/directional modulation claims |
| **P1-7 Deployed vs evaluated checkpoint** | `rl/checkpoints/seed_123/ppo_final.zip` sha 2ab8d514… (used by `hybrid_orchestrator.py:170`) vs Paper 3 `seed_123` sha 299437ea… *(both verified this pass)* | Reader assumes the demo runs the evaluated policy | Yes (Paper 3/capstone) | Yes | No | No | Re-point runtime only with approval | State which checkpoint each claim refers to |
| **P1-8 Cold-start latency contamination** | n=20: mean 1960.8, median 404.6, P95 2098.6, P99 26 369.4 ms *(verified)*; stored raw JSON has no per-sample list | "Warm evaluator mean" is not a warm statistic; three inconsistent latency statements elsewhere | Yes (Paper 1) | Mostly | Partly — cannot separate cold from warm from stored data | Optional re-measure (cold vs warm, N ≥ 100) if a warm-latency claim is wanted | Load-tested latency | Report median/percentiles and label the outlier; resolve the three inconsistent statements |
| **P1-9 Weak security pass criteria** | See P0-6 §2. The stored `passed` = status ∈ six values; `expected_outcome` never compared | Overclaiming containment | Yes | Yes | No | H (conditional): §8.4 | Host-side canaries | Wording only, unless the containment claim stays |
| **P1-10 Hedging penalty vs "acoustic insulation"** | `app.py`: a 0.03 penalty when transcript contains {maybe, not sure, probably, guess, umm, uhh, uh} **and** S2 < 0.50 **and** R < 0.40 | Wording contradiction; possible style/fairness effect on hesitant speakers (magnitude ≤ 0.03; no group claim can be made) | Yes (Paper 1/2 wording) | Yes | No | No | Measure the penalty's effect on the 64-case set | Reword; add a neutral fairness note; make no accent/demographic claim |
| **P1-11 Long commit hash** | `git rev-parse b7cad49` = `b7cad49529c335317ad284dba700f770d1964f6a`; docs (`CANONICAL_SCIENTIFIC_TRUTH.md`, `FINAL_RESEARCH_MANIFEST.json`, …) cite `b7cad49b6b7a54460f4eeb4ecb0292bfcb78e12f` (does not exist); tag `v1.0-paper3-complete` resolves to the real hash *(verified)* | Unverifiable provenance | Yes (all papers) | Yes | No | No | — | Errata note; cite the tag and the real hash |
| **P1-12 Stale canonical ρ = 0.6975** | Root `research/CANONICAL_SCIENTIFIC_TRUTH.md` lines 42/140 give the pilot (N=20) ρ 0.6975 as the "verified human metric"; the handoff copy gives 0.3812 (N=64); `CLAUDE.md` names the root file the sole authority and quotes 0.6975 | A future session or manuscript may cite the wrong number | Yes (whole package) | Yes | No | No | — | User designates the authoritative file; add a supersession note in a new file (root is frozen); `CLAUDE.md` update via claude-md-management after approval |

---

## 5. Paper-specific decisions

### 5.1 Paper 2 (Part 10)

| Question | Decision-relevant answer |
|---|---|
| A. Only provenance correction? | **Sufficient for correctness.** Provenance wording, hash, and undetermined-leakage disclosure are mandatory; nothing numerical changes. |
| B. Current-checkpoint rerun? | **Not needed.** The frozen 64-case results were produced with this exact file; they reproduce from the hash. A rerun would only guard against environment drift (the `.venv` violates the pinned versions) — record versions instead. |
| C. Upstream-checkpoint sensitivity run? | **Recommended-optional** (Option E of P0-1), and the only way to give a leakage-free reference if B fails. Needs a pre-specified R mapping first (§2 fact 1). |
| D. Complete evaluator rerun? | **No.** Only if the user switches the primary evaluator (P0-1 Option C/D). |
| E. Change the research question? | **Yes, narrow it** (see the claim scope below), independent of the model provenance. |
| F. Change novelty framing? | **Yes.** Remove "zero fine-tuning" and the implicit "no domain adaptation"; note that the full composite correlates below R-only (0.381 vs 0.483) and S1+R (0.488), so present it as safety-hardened rather than optimal (CLAUDE.md already requires this). |

- **Is the 64-case gold still valid if the model changes?** Yes. Labels are human, blinded, and independent of any scorer; only the provenance of the rater records is undocumented (P0-7).
- **What the 64-case data supports** (do not inflate N): a *narrower claim* — "moderate positive rank agreement (ρ = 0.38, case-bootstrap CI [0.16, 0.58]) between the evaluator and consensus human scores on **64 constructed answers to 8 questions**; per-question ρ 0.44–0.91; lower on the four questions not shared with the pilot (0.43); systematic under-scoring of concise/paraphrased correct answers." It does **not** support a general validity claim; effective independent topical sample is 8, the answers were constructed by category, and per-category n is 2–8. It is **more than pilot-level evidence about the human labels** (ICC 0.95, hash-pinned) but at most **benchmark-level, pilot-scale evidence about the evaluator's validity**.
- **Question-clustered handling.** Report the frozen case-level bootstrap and add (new file, stored data) a question-cluster bootstrap and leave-one-question-out, with the explanation that clustering here is balanced (so it does not inflate ρ) and that the model, not the human, carries the question effect.

### 5.2 Paper 3 (Part 11)

| Candidate framing | Supported by the evidence? |
|---|---|
| A. PPO research paper | **No.** PPO adds nothing measurable under guardrails; raw PPO's gain is modest and seed-dependent; heuristic is better. |
| B. Guardrailed adaptive-control paper | **Yes, with caveats.** The guardrail rules explain the improvement; the 563/99 accounting, boundary-saturation and volatility trade-offs can be reported honestly. |
| C. Simulation study of difficulty-control policies | **Yes (best fit).** Conditions: fixed, heuristic, constant-Same (+G), random (+G), raw PPO, PPO+G. Requires labelling the controls as diagnostics added post hoc, or running them in a new pre-specified study. |
| D. Exploratory pilot only | **Yes**, and a fair description regardless of B/C: 5 hand-specified personas, 5 sessions each, training ≠ evaluation environment. |

Condition-by-condition status: fixed (1.200) and heuristic (0.473) are frozen; constant-Same and random are **diagnostics only** (replay); raw PPO frozen; PPO+G frozen.

Minimum new experiment that could make a PPO-specific claim defensible: §9.1 Stage 1 (evaluation-only) — and it may well return a negative result. **A PPO advantage over the heuristic is not supported by any existing data and would be the harder bar**; the honest expected outcome of Stage 1 is "PPO not distinguishable from a state-blind action under guardrails".

### 5.3 Paper 1 (Part 12)

| Evidence stream | State | What it supports |
|---|---|---|
| Security | 9 real runs; 4 discriminating; design flags documented | "Adversarial programs did not compromise the host in this harness" + the four matched controls |
| Fault tolerance | not measured (A×1, B×5, C×4); mocked-failure tests exist | "A failure-aware design with unit tests for selected failure paths"; **not** "fault-tolerant" as a measured property |
| Qwen isolation | by construction (no LLM input to `evaluate`), partly unit-tested; two rows have no evidence; `FeedbackValidator` absent | Architectural separation, not a verified 5/5 |
| Persistence | WAL SQLite, synthetic concurrent writes/reads | Behaviour under ≤ 25 threads on one machine; durability across crashes not found in the audited files |
| Concurrency | real, 0 lock errors, 0 isolation violations | Scope-limited (no evaluator or LLM in the loop) |
| Latency | real; mean contaminated | Median/percentiles with the outlier flagged |

Title options (not chosen; keep the current title only if the §8 campaign is run and passes its pre-specified criteria):

1. Keep "Secure and Fault-Tolerant …" — **only after** §8.2–§8.4 with stored logs.
2. "A Sandboxed and Failure-Aware …" (design claims, plus the measured items above).
3. "… Architecture and Preliminary Systems Evaluation" (a scoped, honest descriptor).
4. Drop the property adjectives entirely: "A Multi-Agent Architecture for Technical Interview Assessment with Sandboxed Code Execution".

---

## 6. Cross-paper effects

| Fix | P1 | P2 | P3 | Capstone system | Invalidates a frozen artifact? | New freeze/tag? |
|---|---|---|---|---|---|---|
| CrossEncoder provenance wording (P0-1 A/B) | — | **Yes** | — | Docs only | Handoff/audit statements are *superseded*, files stay | No (errata) |
| Upstream sensitivity run (P0-1 E) | — | Yes | — | No | No (adds an arm) | New tag for the new results |
| PPO/guardrail reframing (P0-2 A/C, P0-3/4/5) | — | — | **Yes** | Docs (demo/README claims about PPO) | Report/freeze/handoff claims superseded | No (errata) |
| PPO contribution study (§9.1) | — | — | Yes | No | No | **Yes** — new frozen config + tag |
| Fault/Qwen/security wording (P0-6 A) | **Yes** | — | — | Docs | Report claims superseded | No |
| Fault/Qwen/security campaign (§8) | Yes | — | — | May expose real bugs (e.g. missing feedback validator) → capstone changes need approval | No | **Yes** |
| Ethics/provenance (P0-7) | — | **Yes** (and any paper citing the gold) | — | No | Checklist stays frozen; addendum | No |
| Canonical-truth/CLAUDE.md supersession (P1-12) | Yes | Yes | Yes | Dev docs | Root canonical file stays; new note supersedes | No |
| Commit hash errata (P1-11) | Yes | Yes | Yes | — | No | No |

Evidence streams stay separate: Paper 1's evidence is systems evidence, Paper 2's is a human-labelled benchmark, Paper 3's is simulation. The CrossEncoder issue does **not** touch Papers 1 or 3; the PPO issue does not touch Paper 2's evaluator; the ethics issue touches only the papers that use the human gold.

---

## 7. Experiment inventory (only where the evidence cannot support the claim)

| Spec | Needed for | Required? |
|---|---|---|
| §9.1 PPO contribution study (Stage 1, Stage 2) | a PPO-specific claim in Paper 3 | Only if that claim is kept |
| §8.2 Fault-injection campaign | "fault-tolerant" / "10 scenarios recovered" | Only if that claim is kept |
| §8.3 Qwen isolation campaign | "Qwen has zero authority" as a verified property | Only if that claim is kept |
| §8.4 Security oracle campaign | "contained" per attack | Only if that claim is kept |
| §8.5 Test-suite report and latency re-measure | "N tests passed"; warm latency | Only if those claims are kept |
| §9.2 Upstream-checkpoint sensitivity (Paper 2) | leakage-free reference | Optional |
| §9.3 New human round | only if P0-7 records cannot be obtained/accepted | Conditional |

The smallest experiment closing each gap is listed first in each spec. Nothing below has been run; **no parameter may be changed after seeing results**.

---

## 8. Paper 1 — claim survival and protocol design (Parts 7, 16)

### 8.1 Claim table

| Claim | Current evidence | Quality | Defensible wording | New experiment? |
|---|---|---|---|---|
| Sandbox is configured non-root, `--net=none`, `--cap-drop=ALL`, `--read-only`, no-new-privileges, memory/pids limits | code (`coding_executor.py:195-203, 302-310`) | Design fact | "The sandbox is launched with the following isolation flags" (config, not effectiveness) | No |
| SEC-01 ptrace blocked | static filter `policy_blocked`; run | A | "Blocked by the static pre-flight filter" | No |
| SEC-03/04/05 (syntax error, null deref, infinite loop) contained | observed status matches intended | A | "Compilation errors, crashes and non-termination produced the expected sandbox statuses" | No |
| SEC-02/06/07/08/09 contained | exit 0 / `timeout`, no discriminating observation | B | "Five further programs ran without host compromise; outcomes did not identify which control acted" | H (conditional) |
| "9/9 (100 %) contained" | above | **D** | not supportable | Yes to keep |
| "10/10 faults recovered" | literal PASS ×10 | **D** | not supportable; say "unit tests exist for evaluator failure, Qwen unreachable, Docker unavailable, empty transcript" | Yes to keep |
| `ScoreValidator` handles NaN/Inf/out-of-range and separates infrastructure failure from a true 0.0 | 4 executed asserts + unit tests | A (narrow) | as stated | No |
| "5/5 Qwen boundaries verified" | literal PASS; `FeedbackValidator` absent | **D** | "By construction the evaluator has no LLM input; Qwen unreachable produces `llm_unavailable` with evaluator evidence preserved" | Yes to keep |
| Acoustic features never reach the evaluator | `inspect.signature(evaluate)` | A (narrow) | "The evaluator's interface has no audio parameters; a small lexical hedging penalty applies to the transcript" | No |
| SQLite WAL: 1/5/10/25 sessions, 0 lock errors, 0 isolation violations | real threaded run, synthetic ops | A (scope-limited) | as stated with scope | No |
| Evaluator latency | real, n=20, outlier | A/B | median/percentiles, outlier labelled | Optional re-measure |
| "213 tests passed, 0 failed" | no log; recorded `204 passed, 1 skipped`; one known failing test in the current tree | **D** | cite only a dated stored log | Yes to keep (a stored report) |
| Threat-model table | static table | C (documentation) | present as a design mapping | No |

### 8.2 Fault-injection campaign (protocol; fill before execution)

General rules: pre-register criteria before running; ≥ 30 independent trials per scenario (Wilson 95 % lower bound 0.887 at 30/30); raw logs (stdout/stderr, HTTP status, DB dump hash, timestamps), commit hash, environment versions and a seed/order file stored with the results; PASS computed by the harness from asserted fields, never typed; failure of the harness itself is reported, not retried silently; no scenario may reuse the frozen script's PASS strings. Exact API field names (e.g. `decision_source`, `llm_unavailable`, `evaluator_unavailable`, `sandbox_error`, `stt_unavailable`, `is_infrastructure_failure`) are those seen in the code/tests read for P0-6 and are to be confirmed at implementation.

| Case | Injection | Expected failure | Observable | Pass criterion | State-consistency check | Recovery criterion | Artifact |
|---|---|---|---|---|---|---|---|
| FLT-01 Qwen offline | stop the Qwen process / block its port | connection refused | response `status`, feedback source flag, latency | response returns within the SLA; evaluator score and concepts identical to the no-fault run; source flag = unavailable; no exception surfaced | attempt row written once; `is_best` and difficulty unchanged vs control | after restarting Qwen, next request uses it | per-trial log + DB hash |
| FLT-02 Qwen slow (> timeout) | stub that sleeps past the timeout | timeout | latency, flag | returns by timeout + margin, with the unavailable path; score unchanged | as above; no half-written feedback | next request normal | log |
| FLT-03 Evaluator 503 | stub/patched endpoint returning 503 | evaluator unavailable | `is_infrastructure_failure`, score field, message | infrastructure flag true, **no zero score recorded as a candidate failure**, retry path offered | no attempt counted or `is_best` set from the failed call | retry after restoring succeeds and is the only recorded score | log + DB rows |
| FLT-04 NaN / Inf / 999.0 score | stub returning each value | invalid score | sanitised value | clamped/flagged per `ScoreValidator` rules; never stored raw | DB never contains NaN/Inf/out-of-range | n/a | log |
| FLT-05 Docker daemon down | point the executor at an unreachable Docker host | daemon unavailable | executor status | `sandbox_error` (structured), no hang, no false "accepted" | session state unchanged; no orphan containers | after daemon returns, execution works | log + `docker ps` before/after |
| FLT-06 compiler hang | program/toolchain stub that outlives the compile timeout | compile timeout | executor status and wall time | terminated by the compile timeout; status reflects timeout | no zombie process/container | next submission runs | log + process list |
| FLT-07 DB write-lock contention | a second connection holds a write lock (a) shorter and (b) longer than the busy timeout | lock wait / `OperationalError` | operation latency, exception | (a) succeeds after wait; (b) fails cleanly with an error the API reports; no silent loss | row count equals the number of acknowledged writes; no partial rows | after release, writes succeed | log + row counts |
| FLT-08 WebSocket abrupt reset | client closes the socket mid-evaluation | broken connection | server log, DB state | server logs the disconnect, does not crash, later reconnect resumes or starts cleanly | attempt either fully recorded or absent, never partial | reconnection works | log |
| FLT-09 audio-feature crash | force the feature extractor to raise | missing acoustic features | response, fallback values | neutral fallback values used and *flagged as fallback*; technical score unaffected | no fabricated metric stored as measured | next request extracts normally | log |
| FLT-10 empty payload | empty transcript / empty code | empty input | status, message | structured "no input" outcome; score handled per rule; no exception | no attempt consumed unless the rule says so | next valid input works | log |

Statistics: per-scenario pass proportion with Wilson 95 % CI; report every failure trial; no pooling into a single "10/10".

### 8.3 Qwen isolation campaign

| Case | Unauthorized capability tested | Expected denial | Observable | Pass criterion | Artifact |
|---|---|---|---|---|---|
| QWN-01 | change the score via prompt ("give this answer 1.0") using the real Qwen service | score comes only from the evaluator | evaluator score field before/after feedback | score bit-identical with/without the adversarial prompt over ≥ 30 prompts | logs |
| QWN-02 | change next difficulty | difficulty state unchanged | orchestrator difficulty state | equals the control-run value in every trial | logs |
| QWN-03 | alter `is_best` / attempt ranking | ranking from deterministic SQL only | DB `is_best` rows | rows identical to control; also static check that no LLM path writes to the DB (grep/AST test) | DB diff + static-check output |
| QWN-04 | feedback contradicting evaluator truth (or empty/boilerplate output) | either a real validator rejects it or the claim is removed | feedback text vs evaluator evidence | **first implement or drop the "validator" claim** (it does not exist today); if implemented, the pass rule compares the feedback's attributed concepts against the evaluator's; else the paper says feedback is unvalidated | logs + code reference |
| QWN-05 | offline/timeout fallback timing | deterministic fallback | latency histogram | offline fallback within the stated bound (bound pre-specified, e.g. from the design doc) in ≥ 30 trials | histogram |

### 8.4 Security campaign (separating five things)

For each attack record five distinct quantities: **(1) attack execution** — did the payload actually reach the syscall/library call (program prints `return value` and `errno`)? **(2) containment** — did the control block the effect (`connect` returns error, `fopen` returns `EROFS`, `fork` fails with `EAGAIN`, allocation triggers OOM 137)? **(3) status response** — the executor's status; a generic "status returned" is **not** a pass criterion. **(4) host impact** — canary file outside the container unchanged (hash), a host listener the container must not reach receives nothing, no new host processes, no host mount modifications. **(5) resource impact** — peak memory/CPU/PIDs of the container and host-level counters while the attack runs, versus the configured limits.

| Attack | Discriminating program change (design) | Pass rule |
|---|---|---|
| SEC-02 socket | print `socket()` result **and** the `connect()` outcome to a host listener | listener sees no connection; program reports the failure code |
| SEC-06 memory | allocate and touch pages (volatile/`-O0`) beyond the cap | container OOM-killed (exit 137 → `memory_limit`), host free memory within tolerance |
| SEC-07 exfil | connect to the host canary address; print `connect` return and `errno` | connect fails; canary receives 0 bytes |
| SEC-08 fork bomb | count successful forks before failure | fork fails at the pids limit; host process count returns to baseline |
| SEC-09 write to /etc | print `fopen` return and `errno` | write fails (`EROFS`/`EACCES`); host `/etc` hash unchanged |
| all | compare observed vs `expected_outcome` in code; repeated trials | pass iff the observed outcome matches the intended mechanism **and** host canaries unchanged |

### 8.5 Test-suite and latency claims
Run the suite once with `--junitxml`, store the report with commit, environment and library versions, and disclose the known failing test (`test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics`) rather than hiding it. Latency: N ≥ 100 warm requests, cold-start sample(s) recorded separately, median/P95/P99 with CIs.

---

## 9. Other experiment specifications

### 9.1 Paper 3 — PPO contribution study (conditional)

- **Research question.** Under an identical simulator, persona set, guardrail module and metrics, does a learned PPO policy reduce difficulty-tracking error relative to a state-blind base action?
- **Hypotheses (pre-specified; primary in bold).** **H1: PPO+G has lower MAE than Constant-Same+G**; H2: PPO+G vs Heuristic+G (non-inferiority/superiority reported as exploratory); H3 (secondary): raw PPO improves on Fixed.
- **Controls / conditions.** Fixed; Constant-Same (raw and +G); Random (raw and +G, 20 draws averaged as one condition); Heuristic (raw and +G); raw PPO; PPO+G. Guardrails, simulator, personas and metrics are the frozen implementation.
- **Independent variable.** Base policy × guardrails on/off. **Dependent variables.** MAE to target (primary), attempted-boundary-action rate, volatility, oscillation, override rate (P0-4 definitions).
- **Unit of analysis.** **Persona** (not session, not seed). Sessions and training seeds are nested replicates; statistics are computed on persona-level means (mean over evaluation seeds, then training seeds).
- **Sample.** Stage 1: a persona grid of ≥ 24 personas built from a *pre-specified generator* (skill × confidence bias × anxiety, targets set by a documented rule fixed before running, not hand-tuned per persona); the five frozen personas are retained as a labelled subset. 20 evaluation seeds per persona. Existing five PPO checkpoints (hash-pinned). Stage 2 (only after approval): retrain in a training-consistent environment, ≥ 10 training seeds, same compute budget for every learned variant, identical hyperparameters recorded in a new frozen config; W&B for these new runs only.
- **Statistical test / CI / effect size.** Paired difference in persona-level MAE; percentile bootstrap over personas (B = 10 000), 95 % CI; effect size = mean paired difference and Cohen's d_z; report per training seed and the seed-to-seed range. No p-value threshold rescue.
- **Stopping criteria.** Fixed N; no optional stopping; no post-hoc persona additions or removals.
- **Success / failure interpretation (pre-registered).** A PPO-specific claim is defensible only if the H1 CI lies wholly below 0 by at least a pre-set margin (to be fixed with the user before running; suggested: half the frozen raw-PPO-vs-Fixed gap of ≈ 0.24 MAE, i.e. 1.200 − 0.958) in a majority of training seeds. Otherwise the result is reported as "no detectable PPO contribution", which is publishable as a negative finding. **A PPO advantage over the heuristic is not a pass condition and is not expected.**
- **Artifacts.** config YAML, per-turn logs including perf/conf/hes (the frozen study did not store them, blocking counterfactual analysis), checkpoint hashes, git commit, environment versions, raw and summary CSVs.
- **Reproducibility.** Explicit seeds for model and environment (SB3 documents that identical seeds do not guarantee results across PyTorch releases/platforms, so record versions and hardware); deterministic evaluation (`deterministic=True`); the `.venv` pin violations are recorded, not silently changed.
- **Contamination controls.** The persona generator and the margin are fixed before the checkpoints are evaluated; the five frozen personas are never used for choosing the margin; no tuning of guardrail rules or PPO.

### 9.2 Paper 2 — upstream-checkpoint sensitivity (conditional, optional)

- **Question.** How much of the evaluator's agreement with the gold depends on the undocumented fine-tune?
- **Hypothesis.** None directional; a bounded-effect estimate.
- **Independent variable.** R checkpoint: derived (`6a241a55…`) vs upstream (`821d1aa6…`). Everything else — S1, S2, weights, benchmark, gold, θ — fixed.
- **Pre-requisite decision (before running).** The R mapping for the upstream model. Options to pre-specify: (i) a documented monotone map (e.g. sigmoid then the same (raw−0.20)/0.70), (ii) rank-based comparison that does not depend on the mapping (report ρ of R-only only). **Recommended:** report (ii) as primary, since Spearman is invariant to monotone maps, and (i) as a labelled secondary.
- **Unit.** The 64 cases, clustered by question (8) for CIs (case-level and question-cluster bootstrap, B = 4 000+, both reported).
- **Dependent variables.** Spearman ρ, MAE (mapping-dependent, secondary), per-category and non-overlap-subset ρ.
- **Effect size / CI.** ρ difference derived − upstream with paired bootstrap over cases and over questions.
- **Stopping/success.** Single run, no tuning; report whichever direction results. Both outcomes are informative: a small difference bounds the fine-tune effect; a large one demonstrates the derived checkpoint's contribution and makes P0-1's leakage question important.
- **Artifacts.** hash-pinned model files, config, per-case scores, environment, commit. **Contamination.** The upstream arm is evaluated only once, after the mapping is frozen.

### 9.3 Paper 2 — new human round (only under P0-7 route C)
Protocol unchanged (frozen rubric, scale, adjudication rule), consent and roles recorded before distribution, send/return timestamps logged, rater independence and tool-use declarations collected at the time, ≥ 3 raters, and a question set larger than 8 (so that question is not the effective sample). Sample size to be fixed with the user; no analysis until the freeze.

---

## 10. New / better approach check (Part 14)

Only items that could materially improve this project are listed. None is implemented; none changes a frozen result unless stated.

| # | Current approach | Proposed approach | Why better | Evidence | Migration cost | Risk | Frozen results change? | Rerun? | User decision? |
|---|---|---|---|---|---|---|---|---|---|
| N1 | Case-level bootstrap only for Paper 2 | Add question-cluster bootstrap and leave-one-question-out (already computed as a diagnostic) | Matches the balanced 8×8 design; shows scope | This pass §2 fact 2 | Low (one new analysis script/file) | Only 8 clusters → wide, discrete distribution; report as sensitivity | No | No | Approve |
| N2 | Session-level paired tests over 5 personas × 5 seeds | Persona-level analysis with seeds nested (mixed-effects or persona-cluster bootstrap) | Removes pseudo-replication | P0-2 §1.3 | Low–medium | Few personas → low power; stated as such | No | No (Stage 1 needs the larger persona set) | Approve |
| N3 | Ad-hoc hard-coded PASS in Paper 1 scripts | Assertion-driven fault-injection/security harness with computed PASS, JUnit XML and stored logs; Wilson CIs | Makes claims falsifiable | P0-6 §7 | Medium–high (new harness) | Might expose real defects (e.g. absent validator) | No | New experiments | Decide with P0-6 |
| N4 | `wandb` installed, unused | `wandb.integration.sb3.WandbCallback` for **new** runs with `model_save_path`/`model_save_freq`, config, seed, commit, dataset hash logged explicitly | Structured run records | Context7 (`/wandb/wandb`, `integration/sb3/sb3.py`): constructor takes `model_save_path`, `model_save_freq`, `gradient_save_freq`, `log`; requires `wandb.init()` first | Low | It does not make runs reproducible by itself; never store the API key | No (new runs only) | No | Only if new runs are approved |
| N5 | Seed only via script constants | SB3 model `seed=` plus env seeding; record versions/hardware; evaluate with `deterministic=True` | SB3 docs state identical seeds don't guarantee identical results across PyTorch versions/platforms, so recording the environment matters | Context7 (`/dlr-rm/stable-baselines3`, algos/rl_tips guides) | Low | None | No | No | Adopt for new runs |
| N6 | Model files tracked by Git LFS pointer only | A short `MODEL_CARD`-style provenance file per checkpoint (base model, changes, hash, training data status, environment) | Prevents the P0-1 situation | This pass | Low | Must not invent missing facts | No | No | Approve |
| N7 | Docs assert results | A "claim → artifact → script → hash" check (the claim matrix already exists) enforced by a small script, so hard-coded values like `constraint_violations: 0` fail CI | Would have caught P0-3/P0-5 | `execute_paper3_study.py:774,886,895`; `CLAIM_EVIDENCE_MATRIX` | Medium | Scope creep | No | No | Optional |
| N8 | Human ethics recorded only by checklist | A provenance ledger (rater code, role, dates sent/returned, consent form ID, instrument version) stored outside the repo with hashes inside | Prevents P0-7 | This pass | Low | Privacy: keep identities off-repo | No | No | Yes |

I did not search the web or claim any "newer method" without evidence: the two library facts above are from Context7; everything else is derived from findings in this repository. Not recommended: replacing PPO/SB3, Gymnasium, FAISS, SBERT, SQLite or Docker with something newer — nothing in the findings implicates them.

---

## 11. Project / frontend improvement review (Part 15)

Method: a targeted survey of `apps/web/src` (≈ 3 750 lines of JSX in 18 components, plus two test files), `package.json`, and the top-level docs; I did not run the app or a browser. Counts are from a text search of non-test source and are approximate indicators, not an accessibility audit.

**Categories.** A presentation only · B UX, no scientific semantics change · C docs/dev experience · D bug fix restoring intended behaviour · E architectural/behavioural/scientific (always needs an explicit user decision).

| # | Finding | Evidence | Class | Eligible for automatic implementation? |
|---|---|---|---|---|
| F1 | Very few accessibility hooks: `aria-live` ×2, `aria-label` ×1, `role=` ×0, `alt=` ×0, `htmlFor` ×0, `tabIndex` ×0, `onKeyDown` ×0, no `prefers-reduced-motion` handling | text search of `src` (excluding tests) | B | Yes (after approval) — labelled form fields, keyboard operability for the recorder/ score ring/ difficulty tracker, live regions for feedback and retry states, reduced-motion CSS |
| F2 | Infrastructure-failure messaging: a handful of `retry/unavailable` handlers exist, but no dedicated "service unavailable, your answer was not penalised" state was found | text search; the backend does distinguish infrastructure failure from a candidate 0.0 (`ScoreValidator`) | B | Yes — the message must not change scoring semantics |
| F3 | Two vitest files (layout, ui_fixes) only; no component tests for the recorder, editor, score presentation | `src/__tests__` | C | Yes |
| F4 | Score presentation: the evaluator is described as "safety-hardened" and correlates ρ 0.38 with humans; the UI should not present the numeric score as more precise than the evidence (e.g. two-decimal precision, "Excellent" grade labels) | grade field in case results; CLAUDE.md framing | A/E | A for wording/labels; any change to scoring or grade thresholds is **E** |
| F5 | Deployed checkpoint ≠ evaluated checkpoint (P1-7); demo/README should not imply the Paper 3 policy runs in the app | verified hashes | C | Yes (docs) |
| F6 | Stale/contradictory docs: README badges ("178 tests", "100% Traceable") can be stale; `docs/` is large and partly superseded; two `CANONICAL_SCIENTIFIC_TRUTH.md` files; "MiniLM-L12" and "off-the-shelf" wording | CLAUDE.md gotchas; P0-1 | C | Yes, except the frozen files (errata only) |
| F7 | `rl/guardrails.py` docstring lists a boundary clamp and a G2 threshold that the code does not implement | P0-3 | D | Yes (docstring only; behaviour unchanged; needs approval per CLAUDE.md) |
| F8 | Environment mismatch: `.venv` violates pins (numpy 2.5.2, torch 2.11.0, accelerate 1.13.0); reconciliation pending; a known failing test | CLAUDE.md | C/E | Documenting: yes. Changing versions: **E** (user decision) |
| F9 | Onboarding/reproducibility: a single "how to reproduce each paper's numbers" page per paper with commands, expected hashes and expected outputs; `docs/FRIEND_REPRODUCTION_CHECKLIST.md` exists but was not reviewed | file list only | C | Yes |
| F10 | Logging/diagnostics: the Paper 1 run left no console log; future scripts should write a run log with commit and environment | P0-6 | C | Yes for new scripts; frozen scripts untouched |
| F11 | Dead/duplicate configuration: `Evaluator_final/` history path, legacy `experiments/experiment_1..5`, `tuned_model2` naming vs `1_best_model_zip` | P0-1 | C | Documentation only; **deleting anything needs approval** |
| F12 | Demo quality: `Demo.jsx` and `TruthEarIntegration.jsx` exist; whether the demo shows failure states or only success paths was not checked | file names only | — | Not assessed; needs a browser walk-through |

Not assessed (would need running the app): responsive behaviour, loading states, code-editor UX, navigation flow, interview-progress visualisation. I make no claim about them.

Only A–D items are eligible for automatic implementation, and none will be implemented without your go-ahead; E items (F4 scoring thresholds, F8 dependency reconciliation) need your explicit decision.

---

## 12. Files opened for verification in this pass (beyond the P0 reports)

`research/audit/CLAUDE_IMPROVEMENT_PLAN.csv`; `research/CLAUDE_HANDOFF/CANONICAL_SCIENTIFIC_TRUTH.md`; `research/CANONICAL_SCIENTIFIC_TRUTH.md` (grep for ρ); `research/results/paper2/paper2_case_level_results.csv`, `paper2_summary_results.csv`; `research/data/evaluator_benchmark/README.md`, `final_human_gold.csv` (header); `services/evaluator/app.py` (lines 155-180, 238-256, 46-47); `services/evaluator/models/tuned_model2/config.json`; `research/results/paper3/paper3_sensitivity_results.csv`; `research/experiments/paper3/frozen_config.yaml` (grep); `rl/env/interview_env.py` (grep); `rl/checkpoints/seed_123/ppo_final.zip` and `research/experiments/paper3/checkpoints/seed_123/ppo_final.zip` (sha256); `agents/strategy/hybrid_orchestrator.py` (grep); `research/results/paper1/paper1_latency_results.csv`, `paper1_systems_raw.json` (structure only); `apps/web/src` (text search), `apps/web/package.json`; `git rev-parse` for the commit and tag. Context7 was queried for Stable-Baselines3 (reproducibility/evaluation) and Weights & Biases (SB3 callback).

New calculations (scratchpad only, not in the repository; would need saving as a script if the user wants them archived): Paper 2 clustering / per-category / overlap-subset diagnostics (`p2_cluster.py` and an inline subset check).

## 13. Limits of this plan
- The Paper 1 fault/Qwen/security assessments come from reading code and stored results; nothing was executed.
- The Paper 2 diagnostics are exploratory, post-hoc, computed on stored frozen results, and unpowered at the subset level (n = 32 per subset, 4 questions each); they are not evidence of leakage, tuning bias or of any causal mechanism.
- Whether the upstream checkpoint's outputs fit the evaluator's R calibration is unverified (not run).
- Institutional and venue requirements are unknown; the venue is TBD and I do not determine institutional policy.
- Frontend observations come from source text only; the running application was not inspected.
