# Final literature audit (2026-09-21)

Recommendations only. See README for evidence labels and `UNRESOLVED_GAPS.md` for limits. Reference numbers are BIBLIOGRAPHY.md entries.

## PAPER 1 (dependable / trustworthy systems engineering)
**A. Research question.** How does a specific LLM-assisted interview-preparation pipeline behave under nine attack programs, injected evaluator and compiler faults, and LLM-authored feedback text, under a predefined harness on one environment?
**B. Search coverage.** Sandbox escape, comparative sandboxes, AI-agent sandbox surveys, assessment-sandbox test suites, fault injection in LLM systems, authority separation, grader prompt injection, Docker documentation. Preprint-heavy; not saturated for peer-reviewed sources.
**C. Core literature.** [1]-[14] plus CARRY items.
**D. Strongest direct precedent.** SandboxEval [6] (test programs against an AI-assessment environment; abstract only).
**E. Strongest methodological precedent.** MAS-FIRE [7] and ReliabilityBench [8] (fault injection with reported degradation); CaMeL [11] for authority separation.
**F. Strongest recent precedent.** SandboxEscapeBench [1] (ICML 2026 listing) and the comparative sandbox study [2].
**G. Strongest novelty threat.** [1] and [2] make any broad "secure sandbox / secure interview system" framing untenable; [6] occupies "attack programs against an assessment sandbox"; [3] collides on the term "fault-tolerant sandboxing".
**H. Current defensible contribution.** A scoped dependability evaluation of one configuration: a containment harness with weakened controls and host observables, two defect-and-repair regression checks, and an invariance test of one LLM-to-score channel; plus the methodological lesson that status strings are not sufficient oracles. The mandatory framing answer: literature does not support a stronger framing than the default (dependable/trustworthy systems engineering with scoped empirical evaluation); it strengthens the case for narrowness.
**I. Claims to narrow.** P1-C1 (fixed, non-adaptive programs; one machine), P1-F1, P1-B1 (channel and fixed-turn scope), P1-C3.
**J. Claims to remove.** Any architecture-as-novelty statement; "fault-tolerant sandbox" as a label; any "secure"/"contained" statement without the tested scope.
**K. Missing evidence.** Adaptive-attacker evaluation; the follow-up generation channel; independent replication; other platforms.
**L. Suggested related-work structure.** See PAPER1_RELATED_WORK_MAP.md (A-F).

Answers to the Paper 1 novelty questions (scope: searched literature):
1. Docker/container security for AI code agents: yes, evaluated ([1], [2], [6]).
2. Multiple attack programs with controls: test suites exist ([6]); controls in the weakened-configuration sense: not confirmed in the parts read.
3. Static preflight + runtime containment + host observables together: not found as a combined design in the searched sources; [5] identifies filters and isolation being studied separately as a gap. Not a claim of first.
4. Evaluator outage plus compiler-timeout cleanup in an assessment pipeline: not found (search-negative).
5. Separating deterministic grading from LLM feedback: established pattern ([9], [11]); engineering practice.
6. Prompt injection aimed at an evaluator: heavily studied ([12], [13]); the PrepAIred test differs (LLM does not score).
7. Real contribution: combination of evaluation harness, empirical diagnostic and failure-aware integration; the architecture is not the contribution.
8. Engineering practice: hardening flags, fail-closed on outage, cleanup on timeout, token caps, authority separation.

## PAPER 2 (evaluator validity / measurement)
**A. Research question.** How does an evidence-grounded composite scorer relate to human ratings on technical interview answers, and where does it err systematically?
**B. Search coverage.** LLM-judge bias (incl. EACL 2026), ASAG quality-conditioned error, gaming/adversarial studies, metamorphic testing, agreement synthesis, measurement framework. Not saturated on technical-domain ASAG and psychometric invariance.
**C. Core literature.** [15]-[25] plus CARRY.
**D. Strongest direct precedent.** Schleifer et al. [17] (automated short-answer scoring with quality-dependent error and human comparison).
**E. Strongest methodological precedent.** Williamson et al. [25] (evaluation framework); Cho et al. [18] (metamorphic relations).
**F. Strongest recent precedent.** Moon et al. EACL 2026 [15]; Norman et al. [16].
**G. Strongest novelty threat.** The bias finding: surface-form and length sensitivity of automatic evaluators is established ([15], [20], [21]); gaming studies of graders exist ([22]-[24]).
**H. Current defensible contribution.** An exploratory, diagnostic measurement study of one composite scorer in a technical-interview setting: reliability-gated human comparison, cluster-aware intervals, and category-level error analysis. Answer to the mandatory direct-comparison question: the observed bias is best described as **a new measurement of an established phenomenon family in technical-interview answers**, not a novel phenomenon; primarily a measurement study, not a scoring formulation. The weak agreement (rho 0.3812) constrains the framing to exploratory/diagnostic; the LLM-human synthesis [19] shows agreement varies widely by context but concerns essays and LLM scorers and cannot justify the value.
**I. Claims to narrow.** P2-B (concise/paraphrase/verbose), P2-M (metamorphic-style), P2-C1 (exploratory).
**J. Claims to remove.** Composite formulation as novelty; reliability gate as contribution.
**K. Missing evidence.** Independent rater provenance; larger unconstructed benchmark (X2 planned); simple-baseline comparisons beyond the reported ablation; subgroup impact and generalisability per [25].
**L. Suggested structure.** See PAPER2_RELATED_WORK_MAP.md.

Answers to the Paper 2 novelty questions (scope: searched literature):
1. Semantic similarity + concept coverage + reasoning verification combined: components are standard (CARRY Mohler 2011, SemEval-2013); the exact combination not found; do not claim novelty.
2. CrossEncoder/NLI for short-answer grading: established framing (SemEval-2013 entailment; CARRY transformer ASAG).
3. Keyword stuffing: studied ([22]-[24]).
4. Concise vs verbose bias: verbosity/length bias studied ([20], [21], [16] finds small effects for some judges); concise-correct under-scoring of a similarity composite not found named.
5. Metamorphic testing for grading: metamorphic testing of LLMs and agents exists ([18], [8]); grader-specific suite not found; adversarial grader studies exist.
6. Inter-rater reliability as a gate: standard ([25]).
7. Primary novelty: evaluation protocol/diagnostic measurement, not scoring formulation.
8. Weak correlation constrains framing: yes (exploratory only).

## PAPER 3 (guardrailed adaptive-difficulty RL as decomposition/equivalence)
**A. Research question.** How much of a guardrailed adaptive-difficulty controller's behaviour is attributable to a learned PPO policy versus the constraint layer, in simulation?
**B. Search coverage.** Mandatory target opened (paywalled); PPO tutoring papers; RL CAT; shielding; RL statistics; equivalence testing. Not saturated on knowledge tracing/curriculum RL/bandit CAT and Elo/IRT versus RL.
**C. Core literature.** [26]-[37] plus CARRY.
**D. Strongest direct precedent.** Kadam et al. 2026 [26].
**E. Strongest methodological precedent.** Lakens [35], Agarwal et al. [34].
**F. Strongest recent precedent.** [26] (published online Jul 2026).
**G. Strongest novelty threat.** [26] for the application space and PPO/heuristic/simulator/IRT elements; Che et al. [28] for the "PPO collapses to a constant action" observation.
**H. Current defensible contribution.** A controlled decomposition and preregistered equivalence result of guardrailed PPO versus a state-blind constant action, with guard-layer intervention accounting and persona-level statistics (within the parts read of [26]). Answers to the mandatory questions: (1) [26] occupies most of the application-level problem definition; (2) yes, PPO; (3) yes, a rule-based heuristic; (4) yes, simulated learners; (5) yes, IRT-based; (6) state representation differs in description but this is not a defensible novelty by itself (their state was not fully verified); (7) our action space is narrower (difficulty only) not more novel; (8) the guardrail is an application-level intervention, not new as a concept; (9) the controlled decomposition/equivalence result is the residual contribution; (10) yes, a reviewer would likely see an incremental PPO application if framed around PPO or the interview setting.
**I. Claims to narrow.** Guardrail wording (never "shield"); equivalence claim must be simulation-only; heuristic comparison descriptive.
**J. Claims to remove.** PPO-for-adaptive-interview-difficulty as a contribution; simulator/benchmark contribution.
**K. Missing evidence.** Elo/IRT baseline; full read of [26]; real users.
**L. Suggested structure.** See PAPER3_RELATED_WORK_MAP.md. Alternative framing (proposal only): "controlled decomposition / negative result".

## CROSS-PAPER ASSESSMENT
- Distinctness: three papers remain distinct in object (system dependability; evaluator measurement; controller decomposition) and in evidence. Shared themes: LLM as untrusted or biased component; simulation/harness limits; preprint-heavy 2026 literature.
- Overlap risk: Paper 1 and Paper 2 both touch the LLM-in-assessment threat (prompt injection / evaluator robustness); citing the same grader-attack papers in both is fine, but the Paper 1 and Paper 2 test designs must not be presented as the same test. Paper 3 shares the adaptive interview setting with Kadam et al. and is the most exposed.
- Derivative risk: Paper 3 is the most derivative if framed as PPO application; Paper 2 is derivative if framed as a new scoring formulation; Paper 1 is safest if framed narrowly.
- No merge recommended.
- Reframing prompted by literature: Paper 3 (decomposition/negative result); Paper 2 (measurement study); Paper 1 (scoped dependability).

## FINAL CLAIM-SAFETY AUDIT
Every novelty phrase in this package was checked. Not used to describe PrepAIred: first, only, unprecedented, no prior work, state of the art, best, superior. "Novel" appears only in a source's own wording, as the label of a claim under evaluation (NOVELTY_MATRIX P2-N), or in the two field names ("What remains novel", "no longer novel") that the task specification requires in CORE_PAPER3.md, each qualified by the searched scope. "To our knowledge / not found by the searched queries" appears only with the scope stated, and every such statement is scope-limited in NOVELTY_MATRIX.md, CORE files and UNRESOLVED_GAPS.md. Where sources are preprints or abstract-only, the label is shown. Items rated "High confidence" in NOVELTY_MATRIX rely on abstract-level reading; they are not full-text verified.

## GAP-CLOSURE PASS RESULT (2026-09-21)
Details: KADAM_VERIFICATION.md, P3_ADAPTIVE_ASSESSMENT_PRIOR_ART.md, P1_SANDBOX_METHODOLOGY_COMPARISON.md, P2_2026_BIAS_PASS.md, QUOTE_AUDIT.md, UNRESOLVED_GAPS.md (status section), CLAIM_CHANGE_QUEUE.md (added items).

[Superseded by the FINAL CLOSURE section at the end of this file.] **Status: Paper 1 LITERATURE SUFFICIENT FOR CLAIM REVIEW. Paper 2 LITERATURE SUFFICIENT FOR CLAIM REVIEW (not for manuscript writing). Paper 3 MATERIAL LITERATURE GAP REMAINS (Kadam et al. full text).**

Paper 1. Strongest direct precedent: SandboxEval [6] (now read in full). Strongest methodological precedent: SandboxEscapeBench [1] for host-side oracle, controls and repetition, with RedCode [54] for deterministic state checks. Strongest recent precedent: [1] and the comparative study [2]. Strongest novelty threat: [1] against any broad or method-novelty framing; the term collision with [3]. Novelty conclusion: unchanged in direction; method elements are established practice. Most threatened claim: P1-C3. Uncertainty: Part 2 of [2] not found; adaptive attackers, the follow-up generation channel and other platforms untested.
Paper 2. Strongest direct precedent: Schleifer et al. [17]. Strongest methodological precedent: Williamson et al. [25] (snippet-level) and Cho et al. [18]. Strongest recent precedent: Moon et al. [15]. Strongest novelty threat: established surface-form and perturbation sensitivity ([15], [53], [52], [20]). Novelty conclusion: unchanged. Most threatened claim: P2-B. Uncertainty: technical-domain ASAG and measurement invariance not saturated; several new sources are abstract-level.
Paper 3. Strongest direct precedent: Kadam et al. [26]. Strongest methodological precedent: Lakens [35] and Agarwal et al. [34] for design; Tang [38], Wang [37], Li [30] for RL item selection. Strongest recent precedent: [26]. Strongest novelty threat: [26] for the application, PPO, heuristic, simulator and IRT; Che [28], Schmucker [41] and Jiang [42] for the "learned policy is not better than a simple one" observation. Novelty conclusion: unchanged in direction, with lower confidence on observational novelty. Kadam verification: partial (landing-page text only). Remaining unverified: state, reward, seeds, heuristic, results, constant baseline, guardrail, PPO configuration, and other fields listed in KADAM_VERIFICATION.md.
Safest current Paper 3 framing (proposal only): a controlled decomposition and preregistered equivalence result of a guardrailed PPO controller versus a state-blind constant action, in simulation, with prior benchmark and observational work disclosed.

## FINAL CLOSURE (2026-09-21): literature review frozen for claim review
Details: KADAM_VERIFICATION.md, P3_FINAL_NOVELTY_POSITION.md, P3_RL_EDUCATION_REVIEWS.md, QUOTE_AUDIT.md section 5, CLAIM_CHANGE_QUEUE.md (Q3-08 to Q3-11). Broad literature search stopped by instruction. This does not mean every bibliographic detail is verified; it means the literature is sufficient to lock the high-level novelty position and proceed to independent claim review.

**PAPER 1: LITERATURE SUFFICIENT FOR CLAIM REVIEW**
**PAPER 2: LITERATURE SUFFICIENT FOR CLAIM REVIEW**
**PAPER 3: LITERATURE SUFFICIENT FOR CLAIM REVIEW, WITH EXACT KADAM IMPLEMENTATION/NUMERICAL DETAILS STILL UNVERIFIED**

Paper 1 and Paper 2 conclusions are preserved unchanged from the gap-closure pass (no new search; no factual error found).
Paper 3. Kadam et al. establishes prior art for adaptive mock-interview tutoring, simulation-based evaluation, IRT-based simulated learners, RL policy comparison, PPO in that application, heuristic comparison and benchmark-style evaluation. The contribution must not be framed as introducing RL, PPO, a simulator or a benchmark for mock interviews. Remaining defensible distinction (proposal only): a controlled decomposition and preregistered equivalence evaluation of a guardrailed learned difficulty policy against a state-blind constant action in a simulated technical-interview setting. The guardrail is not a formal shield. No materially new direct competitor was found in the focused final gap check (scope-limited). Kadam fields still unverified: state dimension, IRT formula, horizon and budget, reward, hyperparameters, seed count, numbers, any constant or random baseline, any post-policy guardrail.

## Claim-lock implementation (2026-09-21)
The locked three-paper positioning was applied to manuscript-preparation and literature-positioning documents only (see CLAIM_LOCK_IMPLEMENTATION_LOG.md). The literature status lines in the FINAL CLOSURE section are unchanged. No new literature search was run. Canonical claim matrices, evidence packages, audit and freeze files were not edited; proposed changes to them are QL-01 to QL-05 in CLAIM_CHANGE_QUEUE.md.
