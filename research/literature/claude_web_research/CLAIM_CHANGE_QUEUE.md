# Claim change queue (proposals only; for later human/independent review)

Date 2026-09-21. **Nothing in this queue has been applied.** `PAPER1_FINAL_CLAIM_MATRIX.md`, Paper 2 evidence, Paper 3 preregistered conclusions and all frozen evidence are unchanged. Each item lists the exact current claim, the strongest supporting and challenging prior art with the specific evidence seen, the reason, and proposed wording. Evidence strengths follow README labels; several items rest on abstract-level evidence and require a full read before acceptance.

## Paper 1

**Q1-01 NARROW - P1-C1 containment of nine attack programs.**
- Current claim (matrix wording): on one Docker Desktop (WSL2) machine, for nine specified attack programs under the predefined harness and controls, the shipped configuration met the containment/host-unchanged criteria in 5/5 repetitions per attack, and weakened controls produced the expected breaches where applicable.
- Supporting: Rabin et al. 2025 (arXiv:2504.00018): manually crafted test cases against an AI-assessment environment show the test-suite approach is accepted practice (abstract only).
- Challenging: Marchand et al. 2026 (arXiv:2603.02277, ICML 2026 listing): nested-container escape CTF where LLMs exploit added vulnerabilities; threat model is an adaptive motivated agent (abstract only). Andronchik and Lokhmakov 2026 (arXiv:2606.08433): engine classes separate on every architectural axis; OCI containers are one class (abstract only).
- Reason: nine fixed programs cover a small fixed slice; recent work evaluates adaptive attackers and engine-level differences. The existing scoping already handles most of this.
- Proposed additional wording: add "fixed, non-adaptive attack programs" and "we do not evaluate adaptive or model-driven attackers" to the claim and limitations.

**Q1-02 REFRAME - authority separation as contribution.**
- Current claim: the deterministic evaluator scores; the LLM only writes narrative feedback and follow-ups (architecture as part of the contribution).
- Supporting: CaMeL (arXiv:2503.18813): separating control/data flow gave provable security on 77% of AgentDojo tasks vs 84% undefended (abstract).
- Challenging: Bhattarai and Vu (arXiv:2602.09947): the principle "deterministic, architectural enforcement" is already argued as necessary (abstract; conceptual). Grader-injection papers (arXiv:2606.03090, arXiv:2601.21360) show why an LLM should not grade.
- Reason: the pattern is known; only the empirical test of one channel is PrepAIred's.
- Proposed wording: "The system follows an established authority-separation pattern [CaMeL; Bhattarai and Vu]; we report an empirical invariance check of one LLM-to-score channel."

**Q1-03 NARROW - P1-B1 Qwen invariance.**
- Current claim: under the fixed-turn X1-B-I test the narrative-feedback channel did not alter the measured observables (72/72 valid pairs).
- Supporting: CaMeL's premise that untrusted LLM output can be quarantined from privileged decisions.
- Challenging: Li et al. 2026 and Sahoo et al. 2026 show LLM-mediated grading paths are highly vulnerable, which makes the untested Qwen follow-up-to-expected-concepts path (HIGH-2) the salient omission a reviewer will raise.
- Proposed wording: add a sentence that grader-injection literature concerns LLM-as-grader, while PrepAIred tests LLM-as-feedback-writer; state HIGH-2 explicitly.

**Q1-04 REMOVE - "fault-tolerant sandbox" as a label.**
- Current use: descriptive phrase for failure-aware handling (if used anywhere in drafts).
- Challenging: Yan 2025 (arXiv:2512.12806) uses "Fault-Tolerant Sandboxing for AI Coding Agents" for policy interception plus transactional rollback, reporting 100% interception and rollback (abstract).
- Reason: term collision with a different fault model; avoid implied equivalence.
- Proposed wording: "failure-aware handling of two injected faults (evaluator outage, compiler timeout)."

**Q1-05 RETAIN with citation - SEC-01 filter dependence.**
- Supporting: Docker documentation states the default seccomp profile blocks ptrace only before kernel 4.8 (tool-extracted from the official page; re-check). Rashidi 2026 (arXiv:2607.05743): policy-enforcement failures and the lack of joint filter/isolation testing (abstract; figures unverified).
- Reason: makes the HIGH-3 limitation better grounded.
- Proposed wording: see NOVELTY_MATRIX P1-C2.

## Paper 2

**Q2-01 NARROW - concise/paraphrase/verbose under-scoring as a finding.**
- Current claim: concise-correct and paraphrased answers were under-scored; verbose-correct answers affected.
- Supporting: Moon et al., EACL 2026 Findings (doi 10.18653/v1/2026.findings-eacl.70): all tested LLM judges show positive and negative surface-form biases; Zheng et al. NeurIPS 2023: verbosity and position bias named.
- Challenging: Norman et al. 2026 (arXiv:2606.19544): verbosity bias below 0.011 for 21 modern judges under single pairwise rubrics (abstract), i.e. the phenomenon is not uniform; Schleifer et al. BEA 2026: error concentrates in mid-range answers (abstract). Neither names concise-correct under-scoring of a similarity-based composite.
- Reason: the family is established; the technical-interview and similarity-composite measurement is the part I did not find elsewhere within the searched scope.
- Proposed wording: "We measure a known class of surface-form sensitivity in a technical-interview setting."

**Q2-02 REMOVE - scoring formulation as novelty.**
- Current claim (if any draft implies it): the S1/S2/R composite is a contribution.
- Challenging: Mohler et al. 2011, Sung et al. 2019 (CARRY, not re-opened) combine similarity features/transformers for ASAG; SemEval-2013 framed grading with textual entailment (CARRY).
- Proposed wording: present the composite as the system under evaluation.

**Q2-03 NARROW - metamorphic/adversarial testing.**
- Supporting: Cho et al. 2025 (arXiv:2511.02108): 191 MRs collected, 36 implemented (abstract). Gupta 2026: action metamorphic relations.
- Challenging: Filighera et al. AIED 2020, Yarmohammadtoosky et al. 2025 (arXiv:2505.00061), J. Educ. Meas. 2025 (doi 10.1111/jedm.12427): adversarial/gaming studies of graders already exist.
- Proposed wording: "metamorphic-style perturbation tests of a technical-answer scorer".

**Q2-04 RETAIN with framing - exploratory agreement.**
- Supporting/context: Li et al. 2025 synthesis (arXiv:2512.14561): agreement is highly context-dependent (essay scoring, LLMs).
- Reason: weak agreement (rho 0.3812) requires an explicit exploratory frame; the synthesis is not a comparable benchmark and must not be used to excuse the value.

## Paper 3

**Q3-01 REMOVE - PPO-for-adaptive-difficulty as contribution; REFRAME the paper.**
- Current claim: guardrailed PPO controller for adaptive interview difficulty.
- Challenging: Kadam et al., SMPT 2026 (doi 10.1016/j.simpat.2026.103316): RL policy benchmark (PPO, DQN, PETS, MBPO, heuristic) for adaptive mock-interview tutoring with IRT-based simulated learners; "The novelty of the work lies in the integrated benchmarking setup" (page text read; methods/results not read). Axak et al. 2025 (CEUR-4048): PPO vs DQN vs rule-based tutor, single seed, 50,000 timesteps (text read).
- Supporting a different framing: Che et al. 2025 (Sci. Rep.): PPO tutor chose "repeat" 99.9% of the time and a constant heuristic matched its reward (abstract/PMC page; numbers as extracted).
- Reason: the application space and PPO use are occupied; the control comparison and equivalence test are the residual contribution.
- Proposed framing (for review): "Controlled decomposition of a guardrailed adaptive-difficulty controller: learned policy versus constraint layer, in simulation."

**Q3-02 NARROW - guardrail wording.**
- Current claim: guardrail layer with full intervention accounting.
- Challenging: Alshiekh et al. AAAI 2018 (shield defined against a temporal-logic safety specification; search summary), guard-layer/action-masking literature (V-SNIP), Olukola and Rahimi 2026 (constrained tutoring RL).
- Proposed wording: "application-level post-policy rule, not a formal shield; we distinguish activations from actual interventions".

**Q3-03 RETAIN - equivalence classification, with the precedent disclosed.**
- Supporting: Lakens 2017 (TOST; equivalence bounds); Agarwal 2021 (interval estimates with few runs).
- Challenging: Che et al. 2025 reports a collapsed policy near a constant heuristic without an equivalence test.
- Proposed wording: cite Che et al. as an observational precedent; claim only the preregistered, guardrail-matched equivalence test.

**Q3-04 RECORD - missing Elo/IRT comparator.**
- Supporting evidence for its relevance: Pelanek 2016 (Elo in adaptive educational systems); Deep CAT 2026 and BRM 2024 (RL vs information-based selection); Kadam 2026 uses IRT in the simulator.
- Action: list as a limitation. Any new run requires a registered protocol; not proposed here.

## Cross-cutting
**Q-X1 Full read of Kadam et al. before any Paper 3 comparison text is written** (state dimension, reward terms, number of seeds, results, heuristic definition). Required by the evidence gap noted in `CORE_PAPER3.md`.

# Gap-closure pass additions (2026-09-21) - proposals only, nothing applied

Errata to earlier queue items: Q1-05 quote is now verified against the Docker page (use the full sentence); Q2-03 counts (191 / 36) are arXiv v1 numbers and differ in a later listing (38 / 550K); Q3-03 and Q3-01 wording for Che et al. is verified (mean 6.563 vs Heuristic Repeat 6.564; random 5.231; the 5.213 figure belongs to the no-signals ablation; 99.9% action share); the comparative-study wording "rather than proposing an overall ranking" and the SandboxEval "preliminary working paper" note were wrong or unverifiable and are withdrawn.

**Q1-06. P1-C3, status strings as insufficient oracles**
CURRENT CLAIM: executor status strings did not discriminate SEC-02/07/08/09; host-side observables were required.
EVIDENCE: within the frozen X1-C evidence (not re-examined here).
LITERATURE CHALLENGE: RedCode uses deterministic environment-state scripts because traces and judgements can be unreliable; Abdelnabi et al. treat independent verification and canaries as core benchmark hygiene; SandboxEval uses in-payload status plus proxy operations, which is the practice being criticised.
RECOMMENDED ACTION: RETAIN as an observation in this harness; do not present as a new methodological principle.
SAFE ALTERNATIVE WORDING: "Consistent with prior benchmark practice [54], [55], executor status strings did not discriminate SEC-02/07/08/09 in our harness; host-side observables were needed."
CONFIDENCE: medium.
SOURCE(S): [54] RedCode (V-TEXT), [55] Abdelnabi et al. (V-TEXT), [6] SandboxEval (V-TEXT).

**Q1-07. P1-C1 method wording**
CURRENT CLAIM: nine attack programs contained under a predefined harness with weakened controls, host-side observables and 5/5 repetitions.
EVIDENCE: frozen X1-C evidence (not re-examined).
LITERATURE CHALLENGE: SandboxEscapeBench uses a host-side secret, deliberately weakened configurations, reference-solution positive controls and 5 trials per pair; RedCode checks post-run state deterministically.
RECOMMENDED ACTION: NARROW: describe the harness elements as established practice applied to a shipped configuration; claim only the measurement.
SAFE ALTERNATIVE WORDING: "Following practice in container-escape and code-agent benchmarks [1], [54], we ran nine fixed attack programs against the shipped configuration and against weakened controls, judged by host-side observables; we do not evaluate adaptive attackers."
CONFIDENCE: medium-high.
SOURCE(S): [1] SandboxEscapeBench (V-TEXT), [54] RedCode (V-TEXT), [6] SandboxEval (V-TEXT).

**Q1-08. "Secure interview system" framing (mandatory Paper 1 check)**
CURRENT CLAIM: dependable/trustworthy systems-engineering framing.
LITERATURE CHALLENGE: SandboxEscapeBench recommends treating plain Docker isolation as insufficient by default; the comparative study finds engine class matters; the assurance-framework preprint bounds deployment claims by the weakest link.
RECOMMENDED ACTION: RETAIN the dependability framing; REMOVE any unqualified "secure"; keep threat model and scope in the claim sentence.
SAFE ALTERNATIVE WORDING: "a scoped dependability evaluation of one deployment configuration under a stated threat model".
CONFIDENCE: high.
SOURCE(S): [1], [2], [4].

**Q2-05. P2-B, hybrid/paraphrase framing**
CURRENT CLAIM: concise-correct and paraphrased answers are under-scored; the composite is a hybrid evaluator.
EVIDENCE: frozen Paper 2 evidence (not re-examined).
LITERATURE CHALLENGE: meaning-preserving variation changes automatic scores in LLM graders (synonym sensitivity, abstract level [53]), in code judges [15], and response difficulty tracks weaker semantic alignment [52]; hybrid symbolic + LLM graders exist [51]; verbosity effects vary by judge [16], [50].
RECOMMENDED ACTION: NARROW the finding to a measurement in technical interview answers; REMOVE the hybrid formulation as a contribution.
SAFE ALTERNATIVE WORDING: "We measure, for a similarity-based composite scorer, a known class of surface-form sensitivity in technical interview answers: concise-correct and paraphrased answers were under-scored."
CONFIDENCE: medium.
SOURCE(S): [15], [16], [50], [51], [52], [53] (several abstract-level).

**Q3-05. P3-C1, observational novelty**
CURRENT CLAIM: under identical guardrails PPO is statistically equivalent within +/-0.12 MAE to a state-blind constant action, in simulation.
EVIDENCE: preregistered result (not re-examined).
LITERATURE CHALLENGE: Che et al. (PPO 99.9% one action; constant heuristic equal mean reward); Schmucker et al. (uniform policies close to contextual policies at scale); Jiang et al. (RL and heuristics "similar results"). None uses identical guardrails or a preregistered equivalence margin as far as read.
RECOMMENDED ACTION: RETAIN as the core, disclose the three observational precedents, lower the confidence of any statement that the pattern is new.
SAFE ALTERNATIVE WORDING: "Prior work reports learned tutoring policies that match simple or uniform policies [28], [41], [42]; we test this under identical constraints with a preregistered equivalence margin."
CONFIDENCE: medium.
SOURCE(S): [28] (V-TEXT), [41] (V-TEXT), [42] (V-TEXT abstract).

**Q3-06. Kadam comparison text**
CURRENT CLAIM: none in the papers yet; the comparison text is pending.
LITERATURE CHALLENGE: Kadam et al. [26] is the direct precedent; its methods and results were not accessible (KADAM_VERIFICATION.md).
RECOMMENDED ACTION: write no sentence about what [26] lacks; use only verified statements; obtain the full text first.
SAFE ALTERNATIVE WORDING: as in KADAM_VERIFICATION.md, "SAFE FRAMING".
CONFIDENCE: high for the restriction; comparison itself not established.
SOURCE(S): [26] (V-TEXT for landing-page parts only).

**Q3-07. RL/IRT/CAT positioning**
CURRENT CLAIM: none stated; the machinery is used, not claimed.
LITERATURE CHALLENGE: RL and bandit item selection with IRT and simulated examinees is established ([37], [38], [30], [39]); a candidate-window filter around a learned selector appears in [38].
RECOMMENDED ACTION: state the missing Elo/IRT baseline as a limitation (already Q3-04); avoid any claim about RL-based selection per se.
SAFE ALTERNATIVE WORDING: "RL for question or item selection under IRT-style simulators is established [30], [37], [38]; our contribution is the control comparison."
CONFIDENCE: medium-high.
SOURCE(S): [30], [37], [38], [39] (abstract level).

**Q-X2. Rechecks before any manuscript use**
All items listed as UNVERIFIED in QUOTE_AUDIT.md must be reopened; Kadam's methods and results must be read; Part 2 of the comparative sandbox study was not found.

## Final-closure additions (2026-09-21): Paper 3 (proposals only; nothing applied)
Format follows the final-closure instruction. The earlier item Q3-06 is partly superseded by Q3-10.

**Q3-08. Wording implying PPO or adaptive mock-interview RL is itself the contribution**
CURRENT CLAIM: Paper 3 is framed around a guardrailed adaptive-difficulty PPO controller for technical interviews (any wording that presents PPO, RL for mock-interview difficulty, the simulator or a benchmark as the contribution).
LITERATURE EVIDENCE: Kadam et al. (2026) benchmark a rule-based heuristic, DQN, PPO, PETS and MBPO for adaptive mock-interview tutoring with IRT-based simulated learners, under a shared simulator, state, reward and seed protocol, and state their own novelty as the "integrated benchmarking setup rather than in proposing a new generic reinforcement learning algorithm" (verified from the accessible page). The RL-in-education reviews (Riedmann et al. 2025; Doroudi et al. 2019) show PPO-family methods and simulation-based evaluation are ordinary in the field.
NOVELTY THREAT: High for any PPO, application, simulator, heuristic-comparison or benchmark framing.
PROPOSED SAFE CLAIM: "controlled decomposition and preregistered equivalence evaluation of a guardrailed learned difficulty policy against a state-blind constant action in a simulated technical-interview setting." Do not describe the paper as introducing RL, PPO, a simulator or a benchmark for mock interviews.
SOURCE: Kadam et al. [26] (accessible page text); Riedmann et al. [36]; Doroudi et al. [45]; P3_FINAL_NOVELTY_POSITION.md.
CONFIDENCE: high that the broad framing is unsafe; medium that the narrow framing is unoccupied (Kadam body unread).

**Q3-09. Guardrail terminology and guard-layer novelty**
CURRENT CLAIM: an application-level guardrail with intervention accounting.
LITERATURE EVIDENCE: Olukola and Rahimi (arXiv:2604.04251, full text) compare post-hoc filtering with structural constraints in tutoring RL over 10 seeds; Kadam et al. build constraints (budgets, curriculum blueprint) into the MDP. The formal "shield" definition (Alshiekh et al.) was not reopened.
NOVELTY THREAT: medium. A guard or filter layer, and its comparison with learned behaviour, is not a new idea; a formal-shield label would over-claim.
PROPOSED SAFE CLAIM: "an application-level guardrail (a rule applied to the policy's action, with intervention counts); it is not a formal shield and carries no verified safety guarantee." Present intervention accounting as reporting practice, not as a mechanism.
SOURCE: Olukola and Rahimi [58] (V-TEXT); Kadam et al. [26]; QUOTE_AUDIT 3.13 (Alshiekh, UNVERIFIED).
CONFIDENCE: medium-high.

**Q3-10. Kadam comparison text (supersedes the restriction in Q3-06 in part)**
CURRENT CLAIM: no comparison text written yet.
LITERATURE EVIDENCE: the elements in Table A of KADAM_VERIFICATION.md are verified from the accessible source; state dimension, IRT formula, horizon and budget, reward, hyperparameters, seed count, numbers, any constant or random baseline and any post-policy guardrail are not.
NOVELTY THREAT: high for the application space; unresolved for the control comparison.
PROPOSED SAFE CLAIM: "Kadam et al. [26] benchmark a rule-based heuristic, DQN, PPO, PETS and MBPO for adaptive mock-interview tutoring with IRT-based simulated learners. We propose neither a new benchmark nor a new algorithm; we test whether, under identical guardrails, a learned PPO difficulty policy differs from a state-blind constant action." Add no sentence stating what [26] lacks, and no numerical comparison.
SOURCE: KADAM_VERIFICATION.md.
CONFIDENCE: high for the restriction.

**Q3-11. Positioning against the RL-in-education literature**
CURRENT CLAIM: simulation-only evidence; equivalence result.
LITERATURE EVIDENCE: Riedmann et al. list simulation-only evaluation as a limitation and report inconsistent statistical testing (35 of 89 with tests) and frequent random baselines; Doroudi et al. report theory-constrained RL as most successful and (as reported in that review) a simple heuristic approximating an optimal policy in simulation. Schmucker et al., Jiang et al. and Che et al. report learned policies matching simple ones.
NOVELTY THREAT: medium for the observation "a learned policy matches a simple one".
PROPOSED SAFE CLAIM: "Prior work reports learned tutoring policies that match simple policies [28], [41], [42]; we test this under identical guardrails with a preregistered equivalence margin, in simulation only, and make no claim about learners."
SOURCE: [28], [36], [41], [42], [45].
CONFIDENCE: medium.

## Claim-lock implementation (2026-09-21)

**Status of this section.** The locked three-paper positioning was applied to the manuscript-preparation and literature-positioning documents listed in CLAIM_LOCK_IMPLEMENTATION_LOG.md (title options, abstract facts, contributions, limitations, section outlines, references notes, the research-question lines of FINAL_PUBLICATION_READINESS.md and research/literature/FINAL_RESEARCH_POSITIONING.md). The entries below are still PROPOSALS for documents that were NOT edited (canonical claim matrices, evidence packages, audit and freeze files), because those are frozen or canonical and are changed only by an explicit decision.

**QL-01. Paper 3 canonical matrix and evidence package: "shield" wording**
CURRENT CLAIM: PAPER3_FINAL_CLAIM_MATRIX.md P3-M3 "Under the same shield PPO is more volatile ..." and P3-M6 "The shield did not improve tracking ..."; PAPER3_EVIDENCE_PACKAGE.md lines 15, 55, 65 ("no detectable PPO contribution beyond the shield", "The shield did not improve constant-Same tracking", "PPO's contribution beyond the shield").
LITERATURE EVIDENCE: the formal shield notion (Alshiekh et al.) requires a temporal-logic safety specification enforced during learning and execution (definition not reopened; QUOTE_AUDIT 3.13 UNVERIFIED); the guardrail is a hand-written rule layer with no such specification. The same files elsewhere already say "not a formal shield".
NOVELTY THREAT: none to novelty; terminology over-claim risk (safe-RL "shield" implies guarantees).
PROPOSED SAFE CLAIM: replace "shield" by "application-level rule-based guardrail" in P3-M3, P3-M6, the interpretation line "no detectable PPO contribution beyond the application-level rule-based guardrail in these checkpoints (equivalence within +/-0.12 MAE)", and the evidence-package lines above. Artifact keys and registry ids that contain "shield" are left as recorded.
SOURCE: research/literature/claude_web_research/P3_FINAL_NOVELTY_POSITION.md section 4; SECOND_PASS_CLAIM_AUDIT.md E6.
CONFIDENCE: high.

**QL-02. Paper 3 canonical matrix frame: add the prior-art statement**
CURRENT CLAIM: "Controlled decomposition / negative-equivalence study of a guardrailed adaptive-difficulty controller, in simulation only. Not: PPO superiority, state-of-the-art adaptive interviewing, or evidence that RL improves interviewing."
LITERATURE EVIDENCE: Kadam et al. 2026 (verified elements only, KADAM_VERIFICATION.md Table A).
NOVELTY THREAT: high if the application, PPO, the simulator or a benchmark were presented as the contribution.
PROPOSED SAFE CLAIM: append "Adaptive mock-interview tutoring with simulation, an IRT-based learner model, a finite-horizon MDP and DQN/PPO/PETS/MBPO plus a heuristic is prior art (Kadam et al. 2026); the contribution is the controlled decomposition and preregistered equivalence evaluation of PPO plus application-level guardrails against Constant-Same plus the same guardrails."
SOURCE: KADAM_VERIFICATION.md; P3_FINAL_NOVELTY_POSITION.md.
CONFIDENCE: medium-high (Kadam body unread).

**QL-03. Paper 1 canonical matrix frame and master-freeze contribution row**
CURRENT CLAIM: PAPER1_FINAL_CLAIM_MATRIX.md frame "Failure-aware orchestration of an LLM-assisted technical-interview system, with a controlled containment campaign ..."; FINAL_MASTER_EVIDENCE_FREEZE.md main-contribution row "Failure-aware evaluation with negative/permissive controls; documented defects"; research/audit/FINAL_THREE_PAPER_CLAIM_MAP.md "P1 owns containment/authority separation/latency".
LITERATURE EVIDENCE: no literature change; the locked framing follows the independent methodology verdict (sound only after claim narrowing).
NOVELTY THREAT: low; "authority separation" and "orchestration" read as architectural or formal-property claims.
PROPOSED SAFE CLAIM: "A scoped systems/dependability evaluation of the containment, authority-boundary and failure-handling properties of an LLM-assisted technical-assessment pipeline that can be demonstrated through controlled tests under one specified execution environment." Ownership: containment, authority boundary, tested failure handling, operational behaviour.
SOURCE: manuscript/paper1/FINAL_CONTRIBUTIONS.md (locked wording).
CONFIDENCE: high.

**QL-04. Paper 2 canonical matrix frame and master-freeze wording**
CURRENT CLAIM: PAPER2_FINAL_CLAIM_MATRIX.md frame "Exploratory diagnostic / measurement-validity study"; FINAL_MASTER_EVIDENCE_FREEZE.md research-question row "agree with blinded humans" and contribution row "Diagnostic/negative measurement result".
LITERATURE EVIDENCE: surface-form, verbosity and paraphrase sensitivity of automatic graders is documented (P2_2026_BIAS_PASS.md).
NOVELTY THREAT: medium for the under-scoring finding presented as a discovery; "measurement-validity" can be read as a validity claim.
PROPOSED SAFE CLAIM: "Exploratory measurement / diagnostic evaluator study; the contribution is the measurement and diagnostic study, not the S1/S2/R formula." Remove "blinded" unless a rater-blinding record is located (provenance and ethics records are incomplete; blinding was not verified in this pass).
SOURCE: manuscript/paper2/FINAL_CONTRIBUTIONS.md (locked wording); PAPER2_FINAL_CLAIM_MATRIX.md section 1.
CONFIDENCE: high for the frame; medium for the "blinded" point (not verified either way).

**QL-05. Cross-paper ownership**
CURRENT CLAIM: research/audit/FINAL_THREE_PAPER_CLAIM_MAP.md "P3 owns the simulated controller comparison".
PROPOSED SAFE CLAIM: "Paper 3 owns learned-policy versus simpler-policy behaviour under shared guardrails; the simulator is authored infrastructure, not a contribution." Paper 1 owns containment, authority boundary, tested failure handling and operational behaviour; Paper 2 owns evaluator agreement, evaluator diagnostics, error patterns and robustness. No paper reuses another's contribution as its novelty.
LITERATURE EVIDENCE: KADAM_VERIFICATION.md (no new simulator or benchmark claim is available).
NOVELTY THREAT: medium for any "new simulator" reading.
SOURCE: locked positioning 2026-09-21.
CONFIDENCE: high.
