# PREPAIred — Alternative Paper Positioning (analysis artifact)

Date: 2026-09-20. Phase 0 of the 5-hour block. **Analysis/recommendation only.** No protocol, experiment, registry row or frozen artifact was changed because of it. Where a framing would require changing a preregistered experiment, the consequence is recorded (§14), not applied.

Evidence vocabulary: **[LIT-FT]** literature read in full text this session; **[LIT-AB]** abstract/landing page; **[LIT-SN]** search-level or metadata only (not to be cited from this file); **[REG]** stored PREPAIred result in `research/claims/CLAIM_REGISTRY.csv`; **[PLAN]** planned, not run. Literature references use IDs from `LITERATURE_NOVELTY_MASTER_MATRIX.md` (P1-xx, P2-xx, P3-xx) and the second-pass IDs in `SECOND_PASS_CLAIM_AUDIT.md` (SP-xx). "Not identified in the searches conducted" never means "does not exist".

---

## 1. Current positioning (baseline, not assumed optimal)

| Paper | Baseline framing | Evidence that exists today | Evidence that does not exist |
|---|---|---|---|
| 1 | Dependability/containment of an integrated AI technical-assessment system | X1-D: 226 tests (1 failure, root-cause triage recorded), warm evaluator latency (median 236 ms, P95 615 ms, N=100), SQLite write latency; P1-C001 (n=20; P99 26.4 s cold-scale outlier), P1-C002 (synthetic concurrency), P1-C003 (nine attack outcomes, four discriminate) [REG] | Sandbox effectiveness (P1-C009 is DESIGN-ONLY); LLM-channel invariance; fault propagation; X1-A/B/C **not run** and **no registered X1-A/B/C protocol tag exists** (tags present: prereg/X1-D/v1, X2-B v1/v2, X3-A/v1) |
| 2 | Validity and robustness of technical-answer evaluation | Composite ρ 0.3812 (case CI [0.1575, 0.5774]; two-level [0.1529, 0.6490]); R-only 0.4832, S1+R 0.4884, S1 0.2070, S2 0.3021, S1+S2 0.2894, S2+R 0.4171; rater ICC(2,1) 0.9528; 54 mean-of-three + 10 adjudicated; metamorphic 19/21; adversarial 11/13 vs author-set ceilings; **X2B-C003 (exploratory): length-only Spearman 0.4897 [0.2186, 0.708] vs derived CrossEncoder 0.4825; AUROC 0.8864 vs 0.7821**; residual-vs-length ρ −0.3077 (X2A-C007) [REG] | Any confirmatory benchmark (X2-C not run; institutional/ethics gate open); real learner data |
| 3 | Controlled comparison of learned adaptive difficulty control against simpler policies | X3-A registered: PPO+G − Constant-Same+G = −0.0350 [−0.0818, +0.0021], Equivalent within ±0.12 (40 personas × 5 training seeds); PPO more volatile (0.14877 [0.0666, 0.25445]); PPO uses its observation (zeroing +0.370); PPO+G better than heuristic+G (−0.464) [REG] | Any real-candidate evidence; O7 robustness (specified, **not run**) |

**Reading of the evidence for this document.** The evidence is strongest where results are negative or diagnostic (equivalence to a constant action; a length baseline that matches or beats the learned CrossEncoder on the old benchmark; a composite that correlates below R-only). It is weakest where the baseline framing needs a positive dependability result (Paper 1).

---

## 2. Alternative portfolio A — systems-centered

| Field | Content |
|---|---|
| Paper 1 | *Architecture and dependability of a local, LLM-assisted technical-assessment system* — RQ: which failure modes remain contained, and how does the pipeline behave when components fail? |
| Paper 2 | *The technical-evaluation subsystem* — RQ: how does the composite (SBERT + FAISS + CrossEncoder) score constructed answers, and where does it fail? |
| Paper 3 | *Adaptive policy subsystem* — RQ: does a learned PPO controller with guardrails track a target difficulty in simulation? |
| Contribution types | P1 systems + diagnostic; P2 empirical/diagnostic; P3 empirical/negative-equivalence |
| Closest prior work | P1: APAC/Docker grader (SP-01), Conversate/PolyInterview as interview-practice systems; P2: Mohler 2011, Ormerod 2023 (ensemble); P3: Axak 2025 (PPO tutor, simulation) |
| Exact difference | P1: measurement of containment/invariance (if X1 run); P2: composite is safety-hardened and scores below R-only; P3: state-blind null under same guardrails |
| Evidence today | P1 X1-D and partial P1-C001–003; P2 X2A/X2B; P3 X3-A |
| New evidence required | P1: X1-A/B/C; P2: none for exploratory framing, X2-C for confirmatory; P3: O7 (robustness only) |
| Experiments made unnecessary | None |
| Claims abandoned | "Subsystem improves scoring" (P2); "adaptive control benefit" (P3) |
| Cross-paper overlap | **High**: same system described three times; each paper is a subsystem view |
| Coherence | Coherent as a system story; each paper depends on the system description |
| Main reviewer attack | P2: "a length-only baseline matches the learned component on your benchmark (X2B-C003)"; P1: "an integration paper without a user study"; P3: "PPO adds nothing beyond the constraint layer" |
| Compatibility | **Potentially compatible but needs evidence** (P1); **clearly compatible** with current evidence for P3 only as an equivalence/negative result; P2 compatible only as a diagnostic, not as a subsystem-quality claim |

## 3. Alternative portfolio B — measurement/evaluation-centered

| Field | Content |
|---|---|
| Paper 1 | *An evaluation protocol for containment and authority separation in AI assessment systems* — RQ: can a test design with predefined weakened-configuration controls and a multi-layer oracle distinguish a contained from an uncontained sandbox, and can LLM-facing channels alter authoritative decisions? |
| Paper 2 | *Measurement validity of technical-answer evaluators* — RQ: how do agreement, length dependence and under-scoring of concise-correct/paraphrase answers affect what a composite evaluator measures? |
| Paper 3 | *Evaluating learned adaptive policies against matched null policies* — RQ: what does the learned component add beyond a constraint layer? |
| Contribution types | P1 methodological/diagnostic; P2 diagnostic/negative; P3 methodological/negative |
| Closest prior work | P1: SandboxEval (SP-02; reports an unsandboxed-laptop comparison, see claim audit), grader-hijacking papers (SP-03…SP-05); P2: Condor & Pardos 2024 (agreement ≠ reliability), Dubois 2024/Zheng 2023 (length bias, LLM judges), Riordan et al. 2017 (strong non-neural baseline; SN); P3: Riedmann 2025 (non-adaptive controls recommended; 14 of 89 studies used them), Olukola 2026 (constraint ablations) |
| Exact difference | P1: predefined single-flag weakened controls with the same oracle (not identified in SandboxEval's text as a design element, but an unsandboxed comparison is reported there); P2: length dependence and concise-correct under-scoring reported for a **non-LLM** composite against a length-only baseline; P3: **state-blind constant action under identical guardrails** |
| Evidence today | P2 and P3 have stored evidence (X2A/X2B, X3-A); P1 needs X1-C/B |
| New evidence required | P1: X1-C/B; P2: X2-C for confirmatory statements; P3: O7 (robustness) |
| Experiments made unnecessary | X1-A could be scoped down or deferred (fault campaign is not central) |
| Claims abandoned | Architecture-centric P2 contribution; "composite best" ; any PPO benefit claim |
| Cross-paper overlap | **Moderate**: shared system, but each paper's contribution is a *measurement design*, which differs across papers |
| Coherence | Coherent theme: "what do the measurements of an AI assessment prototype actually establish?" |
| Main reviewer attack | P1: "a test design without a positive system result"; P2: "benchmark authored by the team makes length a construction artifact"; P3: "a negative result on a simulator" |
| Compatibility | **Clearly compatible with current evidence for P2 and P3**; **potentially compatible but needs evidence for P1** |

## 4. Alternative portfolio C — trustworthy/responsible-AI-centered

**Literature basis first.** Reviews of AI in education organise trustworthiness into multi-dimensional requirement sets (e.g. human agency and oversight, technical robustness and safety, privacy and data governance, transparency, fairness, well-being, accountability; PRISMA reviews 2024–2025) [LIT-SN: master matrix §2; not read]. PREPAIred's stored evidence touches only technical robustness/safety (partially), some transparency (provenance), and nothing on privacy governance, fairness, human oversight, accountability or well-being; rater provenance/ethics records are incomplete. **The label "trustworthy AI" is therefore not supported by the evidence and is not used as a claim.** A neutral lens of *selected technical reliability properties* (authority separation, failure containment, validity, robustness, constrained adaptation) is used below.

| Field | Content |
|---|---|
| Paper 1 | *Authority separation and failure containment in an LLM-assisted assessment pipeline* |
| Paper 2 | *Validity and robustness of the scoring component* |
| Paper 3 | *Constrained adaptation: what a rule-based guardrail layer contributes* |
| Contribution types | P1 systems/diagnostic; P2 diagnostic; P3 analytical/negative |
| Closest prior work | P1: CaMeL (architectural separation, preprint), instruction hierarchy, grader-hijacking (SP-03…05); P2: adversarial ASAG (Filighera), LLM-judge bias; P3: Alshiekh 2018, Carr 2023, Könighofer 2025 (formal shields); Olukola 2026 (constraints for educational RL, preprints) |
| Exact difference | Same as portfolio B for the measured parts; the umbrella adds no new evidence |
| Evidence today / required | As B; plus **privacy, fairness, oversight, ethics evidence is absent** |
| Claims abandoned | Any "trustworthy", "responsible", "safe", "fair" label |
| Cross-paper overlap | Moderate–high (shared vocabulary) |
| Coherence | Coherent only as a lens; weak as a claim |
| Main reviewer attack | "Trustworthy AI without privacy, fairness or oversight evaluation is a label, not a contribution" |
| Compatibility | **Incompatible with current evidence as a "trustworthy AI" umbrella**; the technical-reliability lens is **potentially compatible** but adds no evidence |

## 5. Alternative portfolio D — adaptive-assessment-centered ("reliable execution / scoring / adaptation")

| Field | Content |
|---|---|
| Paper 1 | *Reliable execution* — containment and dependable operation of the assessment pipeline |
| Paper 2 | *Reliable scoring* — validity of the evaluator |
| Paper 3 | *Reliable adaptation* — controller behaviour |
| Contribution types | as A/B |
| Closest prior work | Adaptive assessment literature (CAT: BOBCAT, MAB-CAT 2026, CodeGENCAT preprint; Elo for programming, Vesin 2022) [LIT-AB/SN]; ASAG; sandboxing |
| Exact difference | The umbrella claims a *reliable* adaptive technical assessment |
| Evidence | P1 reliability of execution: unmeasured; P2 reliability of scoring: ρ 0.3812 with a length-only baseline at or above the learned components on the old benchmark; P3 adaptation: equivalent to a constant action |
| Claims abandoned | Any "reliable" outcome claim |
| Overlap | High: three papers in one system narrative |
| Coherence | High as narrative; **contradicted by the results** if "reliable" is an achievement |
| Reviewer attack | "Your own results show scoring and adaptation are not reliable" |
| Compatibility | **Incompatible with current evidence as an achievement claim** ("reliable adaptive technical assessment"). **Potentially compatible** as a research *question* ("empirical evaluation of whether reliability properties hold in a prototype adaptive technical-assessment system"), reporting negative results |

## 6. Alternative portfolio E — empirical-methodology-centered

| Field | Content |
|---|---|
| Paper 1 | *System stress testing*: containment/invariance/fault propagation with controls |
| Paper 2 | *Evaluator validity testing*: agreement, length baseline, metamorphic and adversarial checks, concise-correct/paraphrase under-scoring |
| Paper 3 | *Policy/control decomposition*: separating learned-policy benefit from constraint-layer benefit |
| Contribution types | P1 methodological; P2 diagnostic/benchmark (with X2-C); P3 analytical/negative |
| Closest prior work | As B; plus Riedmann 2025 on statistical reporting practice in educational RL (54 of 89 studies without statistical analysis) |
| Exact difference | Decomposition designs with matched controls are the contribution type; none is a mechanism |
| Evidence today | P2, P3 as B |
| Required | P1: X1-C/B; P2: X2-C for benchmark claims |
| Experiments made unnecessary | X1-A optional |
| Abandoned | Architecture claims; any performance claim |
| Overlap | Low–moderate (each paper tests a different property) |
| Coherence | High and honest |
| Reviewer attack | "Methodological papers on a small prototype: generality?" |
| Compatibility | **Clearly compatible** for P2 and P3; **potentially compatible** for P1 |

## 7. Additional candidate portfolios

**F. Two-paper consolidation (measurement + system).** Paper A = P2 + P3 diagnostics reframed as "what a composite evaluator and a learned controller add beyond simple baselines in a prototype interview-preparation system"; Paper B = P1. Reduces overlap and salami risk; loses three-venue flexibility; P3 and P2 would then share one system description. *Compatibility: potentially compatible; needs a venue-length feasibility check (not done).*

**G. Research-process paper (reproducibility and audit).** Contribution: a preregistration/hash/manifest chain for ML-system research, and what an independent audit found (six blocking harness issues, disclosed and versioned). Closest prior work: **not searched in this block** (reproducibility/preregistration in ML/SE literature — matrix §15). *Compatibility: potentially compatible; literature open.* It must not be started before that search.

**H. P2 reframed as a length-confound diagnostic.** *"Length dependence and under-scoring of concise-correct answers in a composite technical-answer evaluator"* — supported by X2B-C003 and X2A-C007 (exploratory), with X2-C as the confirmatory follow-up. Closest prior work: Dubois 2024, Zheng 2023, Ye 2025 (LLM judges); Riordan et al. 2017 (SN; non-neural baselines); ASAG length features (SN). *Compatibility: clearly compatible with current evidence as exploratory; confirmatory needs X2-C.*

---

## 8. Candidate umbrella research themes

| Theme | Literature support found | Effect on independent contributions | Verdict |
|---|---|---|---|
| "Reliable adaptive technical assessment" (achievement) | Adaptive assessment, ASAG and sandboxing literatures exist separately; no work found that studies all three together (**not identified in the searches conducted**) | Weakens P2/P3 (their results are negative/equivalent) | **Not supported as a claim** |
| "Empirical evaluation of reliability properties of an adaptive technical-assessment prototype" | Same; the framing is a question, not a claim | Neutral to slightly strengthening for negative results | **Supported as a question**; adds no evidence |
| "Matched-control evaluation of AI-assessment components" (portfolio E/B) | Non-adaptive controls recommended in RL-education review (Riedmann 2025: only 14 of 89 studies); SandboxEval reports an unsandboxed comparison | Strengthens each paper's methodological identity | **Supported as a design theme**; does not establish novelty |
| "Trustworthy AI in education" | Multi-dimensional requirement reviews | Unsupported by evidence (privacy/fairness/oversight absent) | **Not supported** |

**Does the umbrella strengthen or weaken each paper?** A shared theme raises overlap risk (same system, same vocabulary) unless each paper is scoped by *what is measured*. Only the measurement-design themes preserve independent contributions.

## 9. Evidence compatibility matrix

| Portfolio | Paper 1 | Paper 2 | Paper 3 |
|---|---|---|---|
| A systems | potentially compatible, needs X1 | compatible only as diagnostic | compatible as equivalence result |
| B measurement | potentially compatible, needs X1-C/B | clearly compatible | clearly compatible |
| C trustworthy | incompatible as label | incompatible as label | incompatible as label |
| D reliable-adaptive | incompatible as achievement | incompatible as achievement | incompatible as achievement |
| E empirical-methodology | potentially compatible, needs X1-C/B | clearly compatible | clearly compatible |
| F two-paper | potentially compatible | clearly compatible (merged) | clearly compatible (merged) |
| G process paper | literature open | — | — |
| H length-confound P2 | — | clearly compatible (exploratory); X2-C for confirmatory | — |

## 10. Cross-paper overlap analysis

| Overlap | Portfolios where it is high | Mitigation available without changing protocols |
|---|---|---|
| Same system described in all three | A, D, C | Scope by measured property (B/E); one shared system description cited across papers |
| Prompt-injection/adversarial vocabulary across P1 and P2 | A, C | Use "channel invariance" (P1) vs "score-ceiling containment" (P2) |
| Simulation-only caveat across P1 and P3 | A, D | P3 owns the simulation caveat; P1 makes no RL efficacy claim |
| Evaluator formula appears in P1 and P2 | A | P1 cites P2's scope; P2 owns evaluator validity |
| Persona/simulator description | — | P3 only |

## 11. Reviewer attack analysis

| Attack | Paper | Applies under | Response available from stored evidence |
|---|---|---|---|
| Length-only baseline matches the learned component | 2 | A, D (architecture-centric); less under B/E/H | X2B-C003 must be reported, not hidden; X2-C is the test |
| Benchmark authored by the study team; length may be a construction artifact | 2 | all | Acknowledge; X2-C independent-authoring design |
| PPO is equivalent to a constant action under the same guardrails | 3 | A, D | Reported as the result under B/E |
| Guardrails are hand-written, not a shield | 3 | C | Use "rule-based guardrail / constraint layer" |
| Sandbox effectiveness unmeasured | 1 | A, C, D | Only resolved by X1-C |
| LLM-grader hijacking literature | 1 | C | Distinguish LLM-as-scorer from LLM-as-feedback (SP-03…05) |
| "Trustworthy" without privacy/fairness/oversight | all | C | Do not use the label |
| Simulator not validated against real candidates | 3 | all | Limitation; no repair possible in this block |

## 12. Positioning decisions that can already be locked (evidence-supported, no protocol change)

1. Do **not** use "trustworthy AI", "reliable adaptive technical assessment" (as achievement), "shield" (formal), "novel/first" in any framing.
2. Paper 3 is framed around *decomposition of learned-policy benefit from constraint-layer benefit*, reporting equivalence and higher volatility as findings; "rule-based guardrail/constraint layer" terminology.
3. Paper 2 cannot be framed as an architecture-improvement paper: composite < R-only < (old-benchmark) length-only baseline on the exploratory benchmark; concise-correct/paraphrase under-scoring is central.
4. Paper 1 cannot make containment or invariance claims before X1-C/X1-B; current P1 evidence supports only a scoped systems/diagnostic statement.
5. Each paper is scoped by *measured property*; no paper re-describes another's results.

## 13. Positioning decisions that must remain open

1. Whether Paper 1 is a systems paper (A) or a measurement-protocol paper (B/E) — depends on X1-C/B outcomes and on SandboxEval's full protocol (read: partially; see claim audit).
2. Whether P2 and P3 merge (portfolio F).
3. Whether a research-process paper (G) exists — literature not searched.
4. Whether Paper 2's confirmatory path (X2-C) is feasible under the institutional/ethics gate.
5. Venue selection (not decided by deadline; not addressed here).

## 14. Consequences for experiments (recorded; nothing modified)

| If framing… | Consequence |
|---|---|
| B/E for Paper 1 | X1-C and X1-B become the core; X1-A can be scoped to retained claims or deferred. **Requires registering X1-C/B protocols first** (none registered) |
| B/E/H for Paper 2 | The X2-C design must include a length-only baseline and strata (short/long × correct/wrong, paraphrase) — already in the requested X2-C requirements |
| E for Paper 3 | O7 is robustness evidence of the registered primary result; no new PPO/simulator experiment is needed |
| Any | No change to X3-A, X2-B, X1-D |

## 15. Final evidence-based positioning recommendation

This is an assessment of compatibility, not a ranking. **The framings that the stored evidence supports today are the measurement/evaluation-centered and empirical-methodology-centered portfolios (B, E), with H as a sharper Paper 2 identity.** Their common umbrella is a *design theme* — matched controls and decomposition — not a claim of reliability or trustworthiness. The systems-centered portfolio (A) remains viable for Paper 1 only if X1 evidence is produced; the trustworthy-AI (C) and reliable-adaptive (D) umbrellas are incompatible with current evidence as claims and are viable at most as research questions. Multiple framings remain open for Paper 1 (§13); that uncertainty is preserved. Prior work closest to each element is in §§2–7 and `SECOND_PASS_CLAIM_AUDIT.md`; no publication-novelty claim is made.
