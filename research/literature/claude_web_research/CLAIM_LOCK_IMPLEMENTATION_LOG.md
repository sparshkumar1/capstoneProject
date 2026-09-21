# Three-paper claim-lock implementation log (2026-09-21)

Records the exact before/after text of every manuscript-preparation and literature-positioning edit made for the locked three-paper positioning. No frozen result, canonical claim matrix, X1/O7 file, preregistration, raw data, evidence artifact, checkpoint or application code was edited. No new literature search was run. Nothing was committed or pushed. Evidence links stay in the edited files (claim ids and artifact paths).

## research/evidence/final/manuscript/paper1/FINAL_TITLE_OPTIONS.md (rewrite)

BEFORE:

```text
# Paper 1 - title options (working; none final; no "secure"/"fault-tolerant"/"trustworthy")
1. Failure-Aware Orchestration of an LLM-Assisted Technical Interview System: A Fault-Injection and Containment Evaluation
2. Testing the Boundaries of an AI Interview-Practice System: Sandbox Containment, Fault Injection and Invariance of Technical Scores to LLM Feedback
3. What Broke and What Held: A Controlled Evaluation of Failure Handling, Code-Sandbox Containment and Score Authority in an LLM-Assisted Assessment Pipeline
Review-approved framing: a scoped systems/dependability evaluation of tested containment and failure-aware behaviours under a specified harness and environment. Titles must not imply formal security, universal isolation, general fault tolerance, or guaranteed score authority (option 3 mentions "Score Authority" and would need rewording to stay within the invariance result actually tested).
```

AFTER:

```text
# Paper 1 - title (LOCKED positioning 2026-09-21; venue TBD; still a working title until the authors confirm)
RECOMMENDED: Scoped Evaluation of Containment, Authority Boundaries, and Failure Handling in an LLM-Assisted Technical-Assessment System
Type: systems / empirical dependability evaluation. The title must not imply formal security, universal isolation, general fault tolerance, or guaranteed score authority (words to avoid: secure, fault-tolerant, trustworthy, proven, robust).
Retired options (superseded by the locked title; do not use): (1) "Failure-Aware Orchestration of an LLM-Assisted Technical Interview System: A Fault-Injection and Containment Evaluation" (presents orchestration as the object of contribution); (2) "Testing the Boundaries of an AI Interview-Practice System: Sandbox Containment, Fault Injection and Invariance of Technical Scores to LLM Feedback" (broader than the fixed-turn invariance result); (3) "What Broke and What Held: ... Failure Handling, Code-Sandbox Containment and Score Authority ..." (implied guaranteed score authority).
Source of the framing: the locked three-paper positioning of 2026-09-21; the narrowed wording follows research/evidence/final/PAPER1_FINAL_CLAIM_MATRIX.md and the Antigravity verdict METHODOLOGICALLY SOUND ONLY AFTER CLAIM NARROWING.
```

## research/evidence/final/manuscript/paper1/FINAL_CONTRIBUTIONS.md (rewrite)

BEFORE:

```text
# Paper 1 - permitted contribution statements (scoped; exact wording follows the claim matrix; narrowed after the independent Antigravity methodology review)
Framing: a scoped systems/dependability evaluation of tested containment and failure-aware behaviours under a specified harness and environment; not a formal-security proof or a universal fault-tolerance demonstration.
1. A claim-scoped fault-injection campaign over the enumerated request-path dependencies of an LLM-assisted assessment orchestrator, with a no-fault control and oracle-perturbation controls per scenario, that found two defects on the baseline build (an evaluator outage recorded as a 0.0 score; a compiler timeout leaving a running container); the defects were repaired on the repaired build and both builds' results are reported side by side. The results concern the tested scenarios only (FLT-05 = missing Docker CLI, not an unreachable daemon; FLT-08/09 not executed; NaN/Inf/negative evaluator outputs still become 0.0).
2. A containment campaign for the C code sandbox in which nine attack programs run against the shipped configuration and against weakened/permissive controls that show each oracle can fail, in one environment, with the layer-by-layer facts that qualify the result: SEC-01 was blocked by the literal pre-flight filter and ptrace returned 0 in the container when the filter was bypassed (pre-flight filtering and container isolation reported separately); socket() succeeds but connect() fails without a network; executor status strings such as wrong_answer did not discriminate for SEC-02/07/08/09, so host/runtime observables were necessary.
3. A fixed-turn invariance experiment for score/difficulty/best-answer observables against Qwen narrative-feedback text with a mutation control and a static AST guard, reported with its actual valid-sample count against the registered minimum (72/72 valid on the repaired build; 16 of 72 on the baseline build), with the follow-up-question generation channel documented as an untested dependency.
4. A dated record of application defects found by the campaigns, their repair and re-test (same-agent regression check), the outcome of an independent methodology review (sound only after claim narrowing) and how it constrained the wording, and the limitations that remain (four HIGH limitations stated explicitly).
Not contributions: formal security; a secure or universally isolated sandbox; fault tolerance as a general property; that all faults are handled or all attacks contained; that Qwen can never influence future scoring; formal authority separation; cross-platform generality; novelty of the phenomena; any claim about users.
```

AFTER:

```text
# Paper 1 - research question and permitted contribution statements (LOCKED 2026-09-21; replaces the earlier contribution list)
Type: systems / empirical dependability evaluation of tested behaviours under a specified harness and environment. Not a formal-security proof; not a universal fault-tolerance demonstration; no user study.
Evidence source: research/evidence/final/PAPER1_FINAL_CLAIM_MATRIX.md (claim ids in brackets) and the X1-A/B-I/C artifacts it cites. Literature context: research/literature/claude_web_research/ (Paper 1 sections; P1_SANDBOX_METHODOLOGY_COMPARISON.md); no novelty claim.

## Locked research question
"Which containment, authority-boundary, and failure-handling properties of an LLM-assisted technical-assessment pipeline can be demonstrated through controlled tests under a specified execution environment?"

## Locked contributions (use this wording)
1. Scoped containment [P1-C1, P1-C1a, P1-C2, P1-C4]: "On one Windows 11 + WSL2 + Docker Desktop environment, nine specified attack programs met the prespecified containment and host-unchanged criteria in 5/5 repeated runs under the shipped configuration, while corresponding weakened/permissive controls produced the expected breaches where applicable."
2. Tested failure handling [P1-F1, P1-F2]: "The repaired build detected the tested evaluator-outage scenario as an infrastructure failure without assigning a scored result in 5/5 repetitions, and the tested compiler-timeout scenario was cleaned up in 5/5 repetitions."
3. Fixed-turn Qwen authority observation [P1-B1, P1-B3]: "Under the fixed-turn X1-B-I test, with the evaluator held fixed, the tested Qwen narrative-feedback channel did not alter the compared technical observables across 72/72 valid adversarial pairs; mutation and static controls demonstrated sensitivity to an injected authority-leakage path."
4. Containment-oracle observation [P1-C3]: "For four tested attacks, executor status strings were identical in contained and breached configurations, demonstrating that host/runtime observables were necessary for the tested containment oracle."

## Secondary / descriptive only (not headline contributions)
Numeric score clamping [P1-F5]; Qwen outage/slow fallback [P1-F3]; Docker CLI, database lock and empty-input behaviour [P1-F4]; socket()/connect() observation [P1-C4]; latency observation (X1-D; the shipped 6 s client timeout versus about 19-30 s local generation is a limitation [P1-L1], not a latency result).

## Supporting record (context, not a contribution)
Build A defects found by the campaigns (an evaluator outage recorded as a 0.0 score; a compiler timeout leaving a running container), their repair on build B and the same-agent regression re-test (a regression check, not an independent replication); the independent methodology review verdict and how it constrained the wording. Build A invariance produced only 16 of 72 valid pairs (registered minimum 30 not met); report both builds.

## Not claimed
Formal security; universal sandbox isolation; a secure sandbox; universal fault tolerance; all attacks contained; all failures handled; prompt-injection-proof behaviour; that Qwen can never influence scoring; cross-platform isolation; sub-second end-to-end performance; novelty of the underlying phenomena.

## Mandatory limitations that travel with these contributions
The four HIGH limitations and the further disclosures are in FINAL_LIMITATIONS.md and must appear in the manuscript.

Cross-paper ownership (locked): Paper 1 owns containment, authority boundary, tested failure handling and operational behaviour; Paper 2 owns evaluator agreement, evaluator diagnostics, error patterns and robustness; Paper 3 owns learned-policy versus simpler-policy behaviour under shared guardrails. One paper's contribution is not reused as another paper's novelty.
```

## research/evidence/final/manuscript/paper1/FINAL_ABSTRACT_FACTS.md (prepend)

BEFORE:

```text
(top of file unchanged; block inserted above)
```

AFTER:

```text
LOCKED FRAMING (2026-09-21): type = systems / empirical dependability evaluation. Research question: "Which containment, authority-boundary, and failure-handling properties of an LLM-assisted technical-assessment pipeline can be demonstrated through controlled tests under a specified execution environment?" Use the four locked contribution sentences in FINAL_CONTRIBUTIONS.md for the abstract; the facts below are their evidence base. Keep the four HIGH limitations in the abstract's scope statement. Not claimed: formal security, universal isolation, universal fault tolerance, prompt-injection-proofness, that Qwen can never influence scoring, cross-platform isolation, sub-second end-to-end performance.
```

## research/evidence/final/manuscript/paper1/FINAL_LIMITATIONS.md (replace)

BEFORE:

```text
# Paper 1 - limitations and threats to validity to state in the paper
```

AFTER:

```text
# Paper 1 - limitations and threats to validity to state in the paper
LOCKED CHECKLIST (2026-09-21). Mandatory HIGH limitations (all four, in the paper body and the abstract scope): (1) NaN/Inf/negative evaluator outputs can become 0.0; (2) follow-up-generated concepts can flow into evaluator expected concepts and were not tested by X1-B-I; (3) SEC-01 relied on literal ptrace pre-flight filtering rather than demonstrated intrinsic container-level ptrace isolation; (4) local CPU Qwen generation exceeded the shipped 6-second timeout. Also disclose: one Windows 11 + WSL2 + Docker Desktop environment; the five repetitions are deterministic repeatability checks, not samples; SUT-derived bounds and the resulting circularity; the SEC-09 canary-reset flaw; FLT-08 (WebSocket) and FLT-09 (audio) unexecuted. Details follow.
```

## research/evidence/final/manuscript/paper1/FINAL_SECTION_OUTLINE.md (replace)

BEFORE:

```text
1 Introduction (LLM-assisted assessment pipelines; why failure behaviour and score authority matter; scope)
```

AFTER:

```text
1 Introduction (LLM-assisted assessment pipelines; the locked research question: "Which containment, authority-boundary, and failure-handling properties of an LLM-assisted technical-assessment pipeline can be demonstrated through controlled tests under a specified execution environment?"; scope: systems / empirical dependability evaluation, one environment, tested properties only; not a formal-security or universal fault-tolerance claim)
```

## research/evidence/final/manuscript/paper1/FINAL_SECTION_OUTLINE.md (replace)

BEFORE:

```text
sandbox and grader-hijack work from the first-pass matrix after verification; no novelty claim)
```

AFTER:

```text
sandbox and grader-hijack work from the first-pass matrix after verification; sandbox-evaluation methodology comparison in research/literature/claude_web_research/P1_SANDBOX_METHODOLOGY_COMPARISON.md; no novelty claim)
```

## research/evidence/final/manuscript/paper2/FINAL_TITLE_OPTIONS.md (rewrite)

BEFORE:

```text
# Paper 2 - title options (working; exploratory/diagnostic framing; never "validated")
1. How Well Does an Evidence-Grounded Scorer Agree with Human Judges on Technical Interview Answers? An Exploratory Diagnostic Study
2. Concise, Paraphrased and Verbose Answers: Measurement-Validity Diagnostics of a Composite Technical-Answer Scorer
3. When a Length Baseline Rivals a Learned Scorer: An Exploratory Evaluation on a Small Constructed Benchmark
Avoid: "validated", "human-equivalent", "outperforms", "expert raters", "confirmatory".
```

AFTER:

```text
# Paper 2 - title (LOCKED positioning 2026-09-21; exploratory measurement framing; never "validated")
RECOMMENDED: Exploratory Measurement of an Evidence-Grounded Technical-Answer Evaluator
Type: exploratory measurement / diagnostic evaluator study. The contribution is the empirical measurement and diagnostic study, not the S1/S2/R formula.
Retired options (superseded; do not use): (1) "How Well Does an Evidence-Grounded Scorer Agree with Human Judges on Technical Interview Answers? An Exploratory Diagnostic Study"; (2) "Concise, Paraphrased and Verbose Answers: Measurement-Validity Diagnostics of a Composite Technical-Answer Scorer" ("measurement validity" invites a validity claim the data do not support); (3) "When a Length Baseline Rivals a Learned Scorer: An Exploratory Evaluation on a Small Constructed Benchmark" (headline built on one baseline comparison).
Avoid in any title or heading: "validated", "accurate grader", "human-level", "reliable", "fair", "bias-free", "superior", "novel hybrid", "expert raters", "confirmatory".
Source: the locked three-paper positioning of 2026-09-21; numbers in research/evidence/final/PAPER2_FINAL_CLAIM_MATRIX.md.
```

## research/evidence/final/manuscript/paper2/FINAL_CONTRIBUTIONS.md (rewrite)

BEFORE:

```text
# Paper 2 - permitted contribution statements
1. An exploratory agreement analysis of a deployed composite technical-answer scorer against three human raters, with question-clustered intervals and leave-one-question/rater-out sensitivity.
2. A documented finding that a length-only baseline and simpler components are competitive with (or above) the composite on this benchmark, and that the safety-hardened composite carries a measured agreement cost.
3. A diagnostic account of systematic under-scoring of concise-correct and paraphrased answers and over-scoring of verbose-wrong answers, consistent with behaviour known for automated scorers (Kabra 2020; Powers 2002).
4. A blocked-confirmatory-round record and a precision-planning simulation (synthetic, unregistered) for a future study.
Not contributions: validation, superiority, novelty of the phenomena, a general evaluator-quality claim.
```

AFTER:

```text
# Paper 2 - research question and permitted contribution statements (LOCKED 2026-09-21; replaces the earlier list)
Type: exploratory measurement / diagnostic evaluator study. The contribution is the empirical measurement and diagnostic study, NOT the S1/S2/R formula. S1/S2/R is the system under evaluation, not a novel algorithm. Evidence: research/evidence/final/PAPER2_FINAL_CLAIM_MATRIX.md; literature context: research/literature/claude_web_research/P2_2026_BIAS_PASS.md and CLAIM_CHANGE_QUEUE.md.

## Locked research question
"How does a composite technical-answer evaluator agree with human consensus and simpler component baselines, and which answer types and perturbations reveal systematic evaluator errors?"

## Locked emphasis (in this order)
1. Exploratory agreement measurement [P2-A1..A6]: N=64 author-constructed answers, 8 question clusters, Spearman rho = 0.3812, p = 0.0018863 (case-level test; answers not independent within a question), case-bootstrap 95% CI [0.1575, 0.5774]; question-aware intervals are wider (two-level [0.1529, 0.6490]). Human-human: ICC(2,1) 0.9528, ICC(2,k) 0.9838, Krippendorff alpha 0.9523 (raters not independently documented; reliability is not validity).
2. Component diagnostics [P2-B1..B5]: R-only 0.4832, S1+R 0.4884, full composite 0.3812. The full composite is not shown superior; frame it as safety-hardened with a measured agreement cost. Composite minus R-only -0.102 [-0.2849, 0.1174] includes zero.
3. Systematic answer-type error analysis [P2-R1]: concise-correct and paraphrased answers are under-scored (as are all correct/partial categories; verbose-wrong is over-scored). Frame this as a technical-interview-domain measurement of an established surface-form/evaluator-bias family, not as the discovery of evaluator bias.
4. Metamorphic/adversarial robustness diagnostics [P2-R2, P2-R3]: 19/21 metamorphic relations; 11/13 adversarial attacks contained against author-set ceilings (author-set, tiny N).

## Supporting record (not a contribution)
The blocked confirmatory round and the synthetic, unregistered precision-planning simulation for a future study.

## Not claimed
A validated evaluator; an accurate grader; human-level grading; reliable automated grading; fairness; bias-freedom; a superior composite; a novel hybrid scoring algorithm; an externally validated benchmark; expert or independent-committee raters; the discovery of evaluator bias.

## Mandatory limitations that travel with these contributions
Author-constructed N=64; 8 question clusters; possible construction/length artifact; pilot overlap; incomplete provenance/ethics records; incomplete CrossEncoder training provenance; systematic concise/paraphrase under-scoring; exploratory, not confirmatory (details in FINAL_LIMITATIONS.md).

Cross-paper ownership (locked): Paper 1 owns containment, authority boundary, tested failure handling and operational behaviour; Paper 2 owns evaluator agreement, evaluator diagnostics, error patterns and robustness; Paper 3 owns learned-policy versus simpler-policy behaviour under shared guardrails. One paper's contribution is not reused as another paper's novelty.
```

## research/evidence/final/manuscript/paper2/FINAL_ABSTRACT_FACTS.md (prepend)

BEFORE:

```text
(top of file unchanged; block inserted above)
```

AFTER:

```text
LOCKED FRAMING (2026-09-21): type = exploratory measurement / diagnostic evaluator study; the contribution is the measurement and diagnostic study, not the S1/S2/R formula (the scorer is the system under evaluation). Research question: "How does a composite technical-answer evaluator agree with human consensus and simpler component baselines, and which answer types and perturbations reveal systematic evaluator errors?" Canonical result: N=64, Spearman rho 0.3812, p 0.0018863 (case-level), 95% CI [0.1575, 0.5774]; ICC(2,1) 0.9528, ICC(2,k) 0.9838, Krippendorff alpha 0.9523; R-only 0.4832, S1+R 0.4884, full composite 0.3812 (no composite superiority). Concise-correct/paraphrase under-scoring is a technical-interview-domain measurement of an established surface-form/evaluator-bias family.
```

## research/evidence/final/manuscript/paper2/FINAL_LIMITATIONS.md (replace)

BEFORE:

```text
# Paper 2 - limitations to state in the paper
```

AFTER:

```text
# Paper 2 - limitations to state in the paper
LOCKED MANDATORY LIST (2026-09-21): author-constructed N=64; 8 question clusters; possible construction/length artifact (the answer categories are length-structured, so length-only baselines are confounded); pilot overlap (questions overlapping the earlier pilot gave rho 0.7092 versus 0.4249 for the others, point estimates only, not a held-out validation [P2-A6]); incomplete provenance and ethics records for the raters; incomplete CrossEncoder training provenance (R is a partially fine-tuned derivative, so overlap with the benchmark cannot be excluded [P2-D2]); systematic under-scoring of concise-correct and paraphrased answers [P2-R1]; exploratory, not confirmatory. Details follow.
```

## research/evidence/final/manuscript/paper2/FINAL_SECTION_OUTLINE.md (replace)

BEFORE:

```text
1 Introduction (measurement validity of technical-answer scoring; scope: exploratory)
```

AFTER:

```text
1 Introduction (measurement of a technical-answer evaluator against human consensus; the locked research question: "How does a composite technical-answer evaluator agree with human consensus and simpler component baselines, and which answer types and perturbations reveal systematic evaluator errors?"; scope: exploratory measurement, not validation)
```

## research/evidence/final/manuscript/paper2/FINAL_SECTION_OUTLINE.md (replace)

BEFORE:

```text
first-pass ASAG/LLM-judge items after verification)
```

AFTER:

```text
first-pass ASAG/LLM-judge items after verification; 2025-2026 surface-form, verbosity and paraphrase-sensitivity sources in research/literature/claude_web_research/P2_2026_BIAS_PASS.md; position the concise/paraphrase finding as a domain measurement of an established bias family; no novelty claim for the evaluator formulation)
```

## research/evidence/final/manuscript/paper2/FINAL_SECTION_OUTLINE.md (replace)

BEFORE:

```text
3 The scorer (formula, components, provenance of R incl. fine-tuned derivative status)
```

AFTER:

```text
3 The evaluator under evaluation (formula and components as the system under test, not a proposed algorithm; provenance of R incl. fine-tuned derivative status)
```

## research/evidence/final/manuscript/paper2/FINAL_REFERENCES.md (append)

BEFORE:

```text
(end of file unchanged; block appended)
```

AFTER:

```text
Newer verified sources on surface-form, verbosity and paraphrase sensitivity of automatic graders, with their verification status, are recorded in research/literature/claude_web_research/BIBLIOGRAPHY.md and P2_2026_BIAS_PASS.md; cite them from there, not from this list.
```

## research/evidence/final/manuscript/paper3/FINAL_TITLE_OPTIONS.md (rewrite)

BEFORE:

```text
# Paper 3 - title options (working; none is final; no superiority wording)
1. Does the Learned Policy Matter? A Controlled Decomposition of a Guardrailed Adaptive-Difficulty Controller in Simulated Technical Interviews
2. Equivalence of a PPO Difficulty Controller and a Constant-Action Control under Rule-Based Guardrails: A Persona-Level Simulation Study
3. Separating Policy from Guardrail: A Negative-Equivalence Evaluation of Reinforcement-Learned Difficulty Control in Simulation
Avoid: "outperforms", "state-of-the-art", "intelligent interviewer that learns", "shield".
```

AFTER:

```text
# Paper 3 - title (LOCKED positioning 2026-09-21; no superiority wording)
RECOMMENDED: A Controlled Equivalence Study of Learned and Constant Difficulty Policies in Simulated Technical Interviews
Type: controlled policy decomposition / equivalence evaluation, in simulation only.
Retired options (superseded; do not use): (1) "Does the Learned Policy Matter? A Controlled Decomposition of a Guardrailed Adaptive-Difficulty Controller in Simulated Technical Interviews"; (2) "Equivalence of a PPO Difficulty Controller and a Constant-Action Control under Rule-Based Guardrails: A Persona-Level Simulation Study"; (3) "Separating Policy from Guardrail: A Negative-Equivalence Evaluation of Reinforcement-Learned Difficulty Control in Simulation".
Avoid: "outperforms", "state-of-the-art", "novel", "first", "intelligent interviewer that learns", "shield", "safe RL", any wording that presents PPO, RL for mock interviews, a simulator or a benchmark as the contribution.
Source: the locked three-paper positioning of 2026-09-21; research/literature/claude_web_research/P3_FINAL_NOVELTY_POSITION.md and KADAM_VERIFICATION.md; result in research/evidence/final/PAPER3_FINAL_CLAIM_MATRIX.md.
```

## research/evidence/final/manuscript/paper3/FINAL_CONTRIBUTIONS.md (rewrite)

BEFORE:

```text
# Paper 3 - permitted contribution statements
1. A persona-level, multi-seed simulation comparison that includes a state-blind constant-action control under the same constraint layer, so the learned policy's contribution can be separated from the guardrails'.
2. A registered equivalence classification (+/-0.12) with a pre-specified superiority margin, plus registered secondary sensitivity analyses that leave the classification unchanged.
3. Descriptive accounting of guardrail activations versus actual overrides and of volatility, showing tracking-MAE equivalence alongside higher PPO volatility.
4. An explicit list of what the simulator cannot support (oracle-aligned reward, authored personas, hypothetical seed population).
Not contributions: a better controller, a validated interview-adaptation method, a formal safety mechanism, any "first"/novelty claim.
```

AFTER:

```text
# Paper 3 - research question and permitted contribution statements (LOCKED 2026-09-21; replaces the earlier list)
Type: controlled policy decomposition / equivalence evaluation, simulation only. Evidence: research/evidence/final/PAPER3_FINAL_CLAIM_MATRIX.md (P3-M1..M6, P3-F1..F5) and the frozen X3-A / O7 artifacts it cites. The frozen result is not modified by this document.

## Locked research question
"Under an identical rule-based guardrail layer, what does a learned PPO difficulty controller add beyond a simpler state-blind Constant-Same policy in simulated technical-interview trajectories?"

## Locked primary result and interpretation
PPO+guardrail versus Constant-Same+same guardrails [P3-M1]: Delta MAE = -0.0350, 95% CI [-0.0818, +0.0021], preregistered equivalence margin +/-0.12 MAE (two-way cluster bootstrap over 40 personas x 5 training seeds, B=10,000; the persona is the statistical unit).
Interpretation (use this wording): "Under the registered simulator and shared guardrail layer, the learned PPO controller was statistically equivalent in tracking error to the state-blind Constant-Same comparator under the preregistered +/-0.12 MAE margin."
Secondary result [P3-M3]: the learned policy exhibited higher trajectory volatility than the matched Constant-Same comparator (+0.14877 [0.0666, 0.25445]).

## Permitted contribution statements
1. A controlled decomposition: a persona-level, multi-seed simulation comparison in which the learned policy and a state-blind constant action run under the same application-level rule-based guardrail layer, so the learned policy's contribution can be separated from the guardrails'.
2. A preregistered equivalence evaluation of that comparison (registered +/-0.12 margin; superiority margin -0.20 not met), with registered secondary sensitivity analyses that leave the classification unchanged [P3-M2].
3. Descriptive intervention accounting (guardrail activations 563/1250 turns versus action overrides 99/1250) and volatility reported next to the tracking result [P3-F3, P3-M3].
4. An explicit list of what the simulator cannot support.

## Terminology (locked)
Always "application-level rule-based guardrail". Never "formal shield", "safe-RL shield", "formally verified shield" or "safety guarantee". The layer has no formal safety specification (research/literature/claude_web_research/P3_FINAL_NOVELTY_POSITION.md section 4).

## Literature position (locked)
Kadam et al. (2026, Simulation Modelling Practice and Theory 151, 103316) already establishes adaptive mock-interview tutoring with simulation, an IRT-based learner model, a finite-horizon MDP, a rule-based heuristic, DQN, PPO, PETS and MBPO (verified parts only; its body is unread, see KADAM_VERIFICATION.md). The contribution is therefore the controlled decomposition/equivalence question, not the broad application of PPO. This paper does not compare against Kadam's simulator or policies.

## Not claimed
That PPO for adaptive interviews is novel; that RL for mock interviews is novel; a new adaptive-interview simulator; a new RL interview benchmark; PPO superiority; guardrail novelty; real-learner benefit; real-interview deployment benefit; "no effect" (equivalence is not "no effect").

## Mandatory limitations that travel with these contributions
See FINAL_LIMITATIONS.md (locked list).

Cross-paper ownership (locked): Paper 1 owns containment, authority boundary, tested failure handling and operational behaviour; Paper 2 owns evaluator agreement, evaluator diagnostics, error patterns and robustness; Paper 3 owns learned-policy versus simpler-policy behaviour under shared guardrails. One paper's contribution is not reused as another paper's novelty.
```

## research/evidence/final/manuscript/paper3/FINAL_ABSTRACT_FACTS.md (replace)

BEFORE:

```text
- Question: does a learned (PPO) difficulty controller add tracking benefit once rule-based guardrails are present? Simulation only.
```

AFTER:

```text
- LOCKED FRAMING (2026-09-21): controlled policy decomposition / equivalence evaluation, simulation only. Research question: "Under an identical rule-based guardrail layer, what does a learned PPO difficulty controller add beyond a simpler state-blind Constant-Same policy in simulated technical-interview trajectories?" Locked interpretation: "Under the registered simulator and shared guardrail layer, the learned PPO controller was statistically equivalent in tracking error to the state-blind Constant-Same comparator under the preregistered +/-0.12 MAE margin." Say "application-level rule-based guardrail" (never "shield").
- Literature position: adaptive mock-interview tutoring with simulation, IRT, a finite-horizon MDP and DQN/PPO/PETS/MBPO plus a heuristic is prior art (Kadam et al. 2026). Do not present RL, PPO, the simulator or a benchmark as the contribution.
```

## research/evidence/final/manuscript/paper3/FINAL_ABSTRACT_FACTS.md (replace)

BEFORE:

```text
PPO+G below heuristic+G and proportional+G, indistinguishable from oracle-rule+G.
```

AFTER:

```text
on the 40-persona grid PPO+G has lower MAE than heuristic+G and proportional+G (authored comparators) and is indistinguishable from oracle-rule+G; in the frozen five-persona study the heuristic scored lower MAE (0.473) than PPO+G (0.677) - report both and do not merge them.
```

## research/evidence/final/manuscript/paper3/FINAL_LIMITATIONS.md (replace)

BEFORE:

```text
# Paper 3 - limitations to state in the paper
```

AFTER:

```text
# Paper 3 - limitations to state in the paper
LOCKED MANDATORY LIST (2026-09-21), each stated in the manuscript: (1) simulation only, no human learners; (2) authored simulator (personas and their target rule are author-written); (3) reward/oracle coupling: the reward contains oracle-alignment components and the coupling was not re-audited; (4) five training seeds, a hypothetical population (df = 4 in the seed-level analysis); (5) unseeded training-candidate issue: checkpoints were trained against one default candidate with unseeded noise and are not regenerable; (6) training/evaluation mismatch: 39 of 40 grid personas were unseen in training and the policies were trained with the guardrails in the loop; (7) runtime state divergence: the deployed demo policy differs from the X3-A training state definition, so no claim is made about the deployed application; (8) author-chosen +/-0.12 equivalence margin, with no literature justification found; (9) no Elo/IRT (or CAT/knowledge-tracing) baseline; (10) the heuristic is strong: it scored lower MAE (0.473) than PPO+G (0.677) in the frozen five-persona study, although PPO+G has lower MAE than heuristic+G on the 40-persona grid (report both); (11) frequent Same action: a learned policy that often proposes Same is close to the state-blind comparator by construction (the stored summaries reviewed do not give the Same-action share; quantify it from the frozen sessions before writing a number); (12) limited session-level policy divergence: of 25 differing action paths only 5 differ in MAE, and 41 of 125 five-persona sessions had at least one guardrail override [P3-F3, P3-F4]. Details follow.
```

## research/evidence/final/manuscript/paper3/FINAL_LIMITATIONS.md (replace)

BEFORE:

```text
The guardrail is a rule-based constraint layer, not a formal shield.
```

AFTER:

```text
The guardrail is an application-level rule-based guardrail (a rule-based constraint layer), not a formal shield and not a safety guarantee.
```

## research/evidence/final/manuscript/paper3/FINAL_RESULTS_TABLES.md (replace)

BEFORE:

```text
shield on/off for Constant-Same 1.104 vs 1.000
```

AFTER:

```text
guardrail on/off for Constant-Same 1.104 vs 1.000 (the frozen artifact and registry may label this contrast 'shield'; the manuscript says 'application-level rule-based guardrail')
```

## research/evidence/final/manuscript/paper3/FINAL_SECTION_OUTLINE.md (replace)

BEFORE:

```text
1 Introduction (adaptive difficulty; why separate policy from guardrail; scope: simulation)
```

AFTER:

```text
1 Introduction (adaptive difficulty; why separate policy from guardrail; the locked research question: "Under an identical rule-based guardrail layer, what does a learned PPO difficulty controller add beyond a simpler state-blind Constant-Same policy in simulated technical-interview trajectories?"; scope: simulation only; the contribution is the controlled decomposition/equivalence question, not RL, PPO, a simulator or a benchmark for mock interviews)
```

## research/evidence/final/manuscript/paper3/FINAL_SECTION_OUTLINE.md (replace)

BEFORE:

```text
2 Related work (RL evaluation methodology:
```

AFTER:

```text
2 Related work (adaptive mock-interview tutoring: Kadam 2026 as direct prior art - establishes simulation-based benchmarking with an IRT learner model, finite-horizon MDP, heuristic, DQN, PPO, PETS and MBPO; state that this paper does not compare against their simulator or policies and that their body was not read; RL-in-education reviews: Riedmann 2025, Doroudi 2019 (simulation-only limitation; inconsistent baselines and testing); constraint layers in tutoring RL: Olukola and Rahimi 2026 (MC-CPO, context not competitor); RL evaluation methodology:
```

## research/evidence/final/manuscript/paper3/FINAL_SECTION_OUTLINE.md (replace)

BEFORE:

```text
6 Discussion (what equivalence means; MAE blindness to path shape; guardrail vs shield)
```

AFTER:

```text
6 Discussion (what equivalence means; MAE blindness to path shape; terminology: application-level rule-based guardrail, not a formal shield)
```

## research/evidence/final/manuscript/paper3/FINAL_REFERENCES.md (append)

BEFORE:

```text
(end of file unchanged; block appended)
```

AFTER:

```text
LOCKED ADDITIONS (2026-09-21; verification status in research/literature/claude_web_research/BIBLIOGRAPHY.md and QUOTE_AUDIT.md, which stay authoritative): Kadam et al. 2026, Simulation Modelling Practice and Theory 151, 103316 (abstract, introduction and contribution text accessible; body, formulas, hyperparameters and numbers unread - cite only the verified elements in KADAM_VERIFICATION.md); Riedmann, Schaper and Lugrin 2025, IJAIED 35, 2669-2723 (full page text read); Doroudi, Aleven and Brunskill 2019, IJAIED 29(4), 568-620 (author version read); Olukola and Rahimi 2026, arXiv:2604.04251 (preprint, full text read; context only). Alshiekh 2018 is cited only to contrast terminology; its definition was not reopened (QUOTE_AUDIT 3.13 stays UNVERIFIED). The unlocatable "Kaur 2024" item is UNVERIFIED and must not be cited.
```

## research/evidence/final/FINAL_PUBLICATION_READINESS.md (replace)

BEFORE:

```text
- **Research question:** In an LLM-assisted interview-practice pipeline, how does the system behave under enumerated dependency faults and attack programs, and do LLM-authored texts influence the recorded technical score observables?
```

AFTER:

```text
- **Research question (locked 2026-09-21):** Which containment, authority-boundary, and failure-handling properties of an LLM-assisted technical-assessment pipeline can be demonstrated through controlled tests under a specified execution environment?
```

## research/evidence/final/FINAL_PUBLICATION_READINESS.md (replace)

BEFORE:

```text
- **Research question:** How well does an evidence-grounded composite scorer agree with human raters on technical interview answers, and where does it fail?
```

AFTER:

```text
- **Research question (locked 2026-09-21):** How does a composite technical-answer evaluator agree with human consensus and simpler component baselines, and which answer types and perturbations reveal systematic evaluator errors?
```

## research/evidence/final/FINAL_PUBLICATION_READINESS.md (replace)

BEFORE:

```text
- **Research question:** Does a learned PPO difficulty controller add tracking benefit over a state-blind constant action once the same guardrails are applied, in simulation?
```

AFTER:

```text
- **Research question (locked 2026-09-21):** Under an identical rule-based guardrail layer, what does a learned PPO difficulty controller add beyond a simpler state-blind Constant-Same policy in simulated technical-interview trajectories?
```

## research/literature/FINAL_RESEARCH_POSITIONING.md (replace)

BEFORE:

```text
P3 owns the simulator and persona-level policy comparison.
```

AFTER:

```text
P3 owns the learned-policy versus simpler-policy comparison under shared guardrails (the simulator is authored infrastructure, not a contribution; corrected 2026-09-21 by the locked positioning).
```

## research/literature/FINAL_RESEARCH_POSITIONING.md (replace)

BEFORE:

```text
No instance of the same control-under-same-constraint design was found (absence is not proof).
```

AFTER:

```text
No instance of the same control-under-same-constraint design was found in the sources read (absence is not proof; the body of Kadam 2026 was not readable, see the locked section below).
```

## research/literature/FINAL_RESEARCH_POSITIONING.md (prepend)

BEFORE:

```text
(top of file unchanged; block inserted above)
```

AFTER:

```text
> **LOCKED POSITIONING (2026-09-21) - read the section "Locked three-paper positioning" at the end of this file first. Where earlier text in this file conflicts with that section, the locked section governs.**
```

## research/literature/FINAL_RESEARCH_POSITIONING.md (append)

BEFORE:

```text
(end of file unchanged; block appended)
```

AFTER:

```text

## Locked three-paper positioning (2026-09-21)
Sources: research/literature/claude_web_research/ (FINAL_LITERATURE_AUDIT.md, P3_FINAL_NOVELTY_POSITION.md, KADAM_VERIFICATION.md, P2_2026_BIAS_PASS.md, QUOTE_AUDIT.md). No new literature search was run for this update. No sentence here says PrepAIred is first, novel or state of the art.

**Paper 1 - systems / empirical dependability evaluation.** RQ: "Which containment, authority-boundary, and failure-handling properties of an LLM-assisted technical-assessment pipeline can be demonstrated through controlled tests under a specified execution environment?" Title: "Scoped Evaluation of Containment, Authority Boundaries, and Failure Handling in an LLM-Assisted Technical-Assessment System". Contributions: scoped containment; tested failure handling; fixed-turn Qwen authority observation; containment-oracle observation (locked wording in manuscript/paper1/FINAL_CONTRIBUTIONS.md). Not claimed: formal security, universal isolation, secure sandbox, universal fault tolerance, prompt-injection-proofness, that Qwen can never influence scoring, cross-platform isolation, sub-second end-to-end performance.

**Paper 2 - exploratory measurement / diagnostic evaluator study.** RQ: "How does a composite technical-answer evaluator agree with human consensus and simpler component baselines, and which answer types and perturbations reveal systematic evaluator errors?" Title: "Exploratory Measurement of an Evidence-Grounded Technical-Answer Evaluator". The contribution is the measurement/diagnostic study, not the S1/S2/R formula (the system under evaluation). Concise-correct/paraphrase under-scoring is a domain measurement of an established surface-form/evaluator-bias family, not the discovery of evaluator bias. The composite is not shown superior (R-only 0.4832, S1+R 0.4884, composite 0.3812).

**Paper 3 - controlled policy decomposition / equivalence evaluation.** RQ: "Under an identical rule-based guardrail layer, what does a learned PPO difficulty controller add beyond a simpler state-blind Constant-Same policy in simulated technical-interview trajectories?" Title: "A Controlled Equivalence Study of Learned and Constant Difficulty Policies in Simulated Technical Interviews". Kadam et al. 2026 already establishes adaptive mock-interview tutoring with simulation, IRT, a finite-horizon MDP, a rule-based heuristic, DQN, PPO, PETS and MBPO (verified parts only; body unread), so the contribution is the controlled decomposition/equivalence question, not the broad application of PPO. Guardrail terminology: "application-level rule-based guardrail" only. Result unchanged: Delta MAE -0.0350, 95% CI [-0.0818, +0.0021], margin +/-0.12.

**Cross-paper lock.** Cross-paper ownership (locked): Paper 1 owns containment, authority boundary, tested failure handling and operational behaviour; Paper 2 owns evaluator agreement, evaluator diagnostics, error patterns and robustness; Paper 3 owns learned-policy versus simpler-policy behaviour under shared guardrails. One paper's contribution is not reused as another paper's novelty.
```

## research/evidence/final/FINAL_PUBLICATION_READINESS.md (replace)

BEFORE:

```text
- **Contribution (permitted):** a claim-scoped fault-injection campaign and a containment campaign with controls, two defects found and repaired with old-vs-new evidence on two builds, and a documented and partly tested invariance property; not a security or fault-tolerance result.
```

AFTER:

```text
- **Contribution (permitted; locked 2026-09-21, wording in manuscript/paper1/FINAL_CONTRIBUTIONS.md):** scoped containment of nine attack programs with controls (one environment, 5/5 repeated runs); tested failure handling on the repaired build (evaluator outage, compiler timeout); a fixed-turn Qwen authority observation (72/72 valid adversarial pairs, with mutation and static controls); a containment-oracle observation (executor status strings did not discriminate for four attacks). The two build-A defects and their repair are supporting record. Not a security or fault-tolerance result.
```

## research/evidence/final/FINAL_PUBLICATION_READINESS.md (replace)

BEFORE:

```text
- **Contribution (permitted):** exploratory agreement, question-cluster intervals, sensitivity analyses, baseline comparison (length-only competitive, composite below simpler components), and category diagnostics (all correct/partial categories under-scored, verbose-wrong over-scored).
```

AFTER:

```text
- **Contribution (permitted; locked 2026-09-21, wording in manuscript/paper2/FINAL_CONTRIBUTIONS.md):** the empirical measurement and diagnostic study, not the S1/S2/R formula: exploratory agreement, question-cluster intervals, sensitivity analyses, component diagnostics (composite not superior; length-only competitive), category diagnostics (all correct/partial categories under-scored, verbose-wrong over-scored; an established surface-form/evaluator-bias family measured in the technical-interview domain) and metamorphic/adversarial robustness diagnostics.
```

## research/evidence/final/FINAL_PUBLICATION_READINESS.md (replace)

BEFORE:

```text
- **Contribution (permitted):** registered equivalence result (Δ −0.0350 [−0.0818, +0.0021], margin ±0.12; superiority not met), unchanged under three registered sensitivity analyses, with higher PPO volatility and full guardrail accounting.
```

AFTER:

```text
- **Contribution (permitted; locked 2026-09-21, wording in manuscript/paper3/FINAL_CONTRIBUTIONS.md):** a controlled decomposition and preregistered equivalence evaluation (Δ −0.0350 [−0.0818, +0.0021], margin ±0.12; superiority not met), unchanged under three registered sensitivity analyses, with higher PPO volatility and full application-level guardrail accounting. Not RL, PPO, a simulator or a benchmark for mock interviews (Kadam et al. 2026 is prior art for the application and its simulation-based comparison).
```

## research/literature/claude_web_research/CLAIM_CHANGE_QUEUE.md (append)

BEFORE:

```text
(end of file unchanged; block appended)
```

AFTER:

```text

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
```

## research/literature/claude_web_research/FINAL_LITERATURE_AUDIT.md (append)

BEFORE:

```text
(end of file unchanged; block appended)
```

AFTER:

```text

## Claim-lock implementation (2026-09-21)
The locked three-paper positioning was applied to manuscript-preparation and literature-positioning documents only (see CLAIM_LOCK_IMPLEMENTATION_LOG.md). The literature status lines in the FINAL CLOSURE section are unchanged. No new literature search was run. Canonical claim matrices, evidence packages, audit and freeze files were not edited; proposed changes to them are QL-01 to QL-05 in CLAIM_CHANGE_QUEUE.md.
```

## research/literature/claude_web_research/README.md (append)

BEFORE:

```text
(end of file unchanged; block appended)
```

AFTER:

```text

## Claim-lock implementation (2026-09-21)
`CLAIM_LOCK_IMPLEMENTATION_LOG.md` records the exact before/after text of the edits made to the manuscript-preparation and literature-positioning documents for the locked three-paper positioning. `CLAIM_CHANGE_QUEUE.md` (QL-01 to QL-05) lists proposals for the canonical documents that were deliberately not edited.
```

# Cleanup pass (2026-09-21, second pass): stale-framing removal in claim and evidence documents

Wording only. No number, evidence table, hash, protocol, experiment id or registered conclusion was changed. Every edit below matched exactly once. Pre-edit copies are kept in the session scratchpad only.

## research/evidence/final/PAPER1_FINAL_CLAIM_MATRIX.md (replace)

BEFORE:

```text
**Frame.** Failure-aware orchestration of an LLM-assisted technical-interview system, with a controlled containment campaign for the code sandbox and an invariance test of score observables against LLM-authored text.
```

AFTER:

```text
**Frame (locked 2026-09-21; wording only, no result changed).** A scoped systems / empirical dependability evaluation of the containment, authority-boundary and failure-handling properties of an LLM-assisted technical-assessment pipeline that can be demonstrated through controlled tests under one specified execution environment (title: "Scoped Evaluation of Containment, Authority Boundaries, and Failure Handling in an LLM-Assisted Technical-Assessment System"). The evidence comprises a controlled containment campaign for the code sandbox, tested failure handling on the repaired build, and a fixed-turn observation of score observables against LLM-authored text. "Failure-aware orchestration" is not the contribution.
```

## research/evidence/final/PAPER1_FINAL_CLAIM_MATRIX.md (replace)

BEFORE:

```text
tested containment and failure-aware behaviours under a specified harness and environment, not a formal-security proof
```

AFTER:

```text
tested containment, authority-boundary and failure-handling behaviours under a specified harness and environment (restated here in the locked vocabulary: "failure-handling" replaces the earlier "failure-aware"), not a formal-security proof
```

## research/evidence/final/PAPER1_FINAL_CLAIM_MATRIX.md (replace)

BEFORE:

```text
## Paper 1 must never claim
```

AFTER:

```text
## Paper 1 must never claim
Also never: "secure system"; "fault-tolerant platform"; "universally contained"; "prompt-injection-proof"; "Qwen cannot affect scoring"; "failure-aware orchestration" as the research contribution.
```

## research/evidence/final/PAPER2_FINAL_CLAIM_MATRIX.md (replace)

BEFORE:

```text
**Frame.** Exploratory diagnostic / measurement-validity study of an evidence-grounded technical-answer scorer on a small author-constructed benchmark.
```

AFTER:

```text
**Frame (locked 2026-09-21; wording only, no result changed).** Exploratory measurement / diagnostic evaluator study ("Exploratory Measurement of an Evidence-Grounded Technical-Answer Evaluator"): how a composite technical-answer evaluator agrees with three-rater human consensus and with simpler component baselines, and which answer types and perturbations reveal systematic evaluator errors, on a small author-constructed benchmark. The contribution is the measurement and diagnostic study, not the S1/S2/R formula (S1/S2/R is the system under evaluation, not a novel algorithm). It is not a measurement-validity or validation study.
```

## research/evidence/final/PAPER2_FINAL_CLAIM_MATRIX.md (replace)

BEFORE:

```text
three raters; final human gold frozen.
```

AFTER:

```text
three-rater human consensus (rater blinding and independence are not documented in stored provenance); the final human-consensus file is frozen.
```

## research/evidence/final/PAPER2_FINAL_CLAIM_MATRIX.md (replace)

BEFORE:

```text
| Case bootstrap treats answers as independent; exploratory. |
```

AFTER:

```text
| Case bootstrap treats answers as independent; exploratory. The stored Spearman p (0.0018863; `research/results/paper2/paper2_summary_results.csv`) is a case-level, nominal p-value under independent-case assumptions; it is not primary robustness evidence and not a claim of confirmatory significance. For inferential robustness use the question-aware intervals (P2-A2). |
```

## research/evidence/final/PAPER2_FINAL_CLAIM_MATRIX.md (replace)

BEFORE:

```text
"independent raters"; ethics approval;
```

AFTER:

```text
"independent raters"; "blinded" raters or "blinded consensus" (no blinding record is stored); "expert panel"; "gold-standard human labels" as a quality claim (`final_human_gold.csv` is a file identifier only); ethics approval;
```

## research/evidence/final/PAPER3_FINAL_CLAIM_MATRIX.md (replace)

BEFORE:

```text
**Frame.** Controlled decomposition / negative-equivalence study of a guardrailed adaptive-difficulty controller, **in simulation only**. Not: PPO superiority, state-of-the-art adaptive interviewing, or evidence that RL improves interviewing.
```

AFTER:

```text
**Frame (locked 2026-09-21; wording only, no result changed).** Controlled policy decomposition / equivalence evaluation, **in simulation only** ("A Controlled Equivalence Study of Learned and Constant Difficulty Policies in Simulated Technical Interviews"): under an identical application-level rule-based guardrail layer, what a learned PPO difficulty controller adds beyond a simpler state-blind Constant-Same policy in simulated technical-interview trajectories. Not: PPO superiority, state-of-the-art adaptive interviewing, evidence that RL improves interviewing, or a new application, RL method, simulator or benchmark. **Prior art:** adaptive mock-interview tutoring with simulation, an IRT-based learner model, a finite-horizon MDP and a heuristic/DQN/PPO/PETS/MBPO comparison is established by Kadam et al. 2026 (only its Table A elements were verified; the body was not read); the contribution is the controlled decomposition and preregistered equivalence evaluation (registration tags are local and unpushed). **Terminology:** always "application-level rule-based guardrail"; never a formal, safe-RL or verified shield and never a safety guarantee. Registered artifacts, registry ids and the registered interpretation string still use the word "shield" for this layer; those strings are quoted verbatim only where cited and are read as "application-level rule-based guardrail".
```

## research/evidence/final/PAPER3_FINAL_CLAIM_MATRIX.md (replace)

BEFORE:

```text
Under the same shield PPO is more volatile
```

AFTER:

```text
Under the same application-level rule-based guardrail PPO is more volatile
```

## research/evidence/final/PAPER3_FINAL_CLAIM_MATRIX.md (replace)

BEFORE:

```text
The shield did not improve tracking of constant Same on the 40-persona grid
```

AFTER:

```text
The application-level rule-based guardrail did not improve tracking of constant Same on the 40-persona grid
```

## research/evidence/final/PAPER3_FINAL_CLAIM_MATRIX.md (replace)

BEFORE:

```text
the guardrail is a rule-based constraint layer, **not a formal shield**.
```

AFTER:

```text
the guardrail is an application-level rule-based guardrail (a rule-based constraint layer) with no formal safety specification and no safety guarantee.
```

## research/evidence/final/PAPER3_FINAL_CLAIM_MATRIX.md (replace)

BEFORE:

```text
| Activations ≠ overrides; only a minority of sessions differ from a state-blind constant action. |
```

AFTER:

```text
| Activations ≠ overrides. In the same frozen replay, of 125 PPO+G sessions the final-action sequence differs from Constant-Same+G in 50, the executed difficulty path (after clipping to [1, 5]) in 25, and the session MAE in 5 (`x3_0c_followup.json`; `X3_0C_FOLLOWUP.md`; P3-C009, P3-C023). |
```

## research/evidence/final/PAPER3_FINAL_CLAIM_MATRIX.md (replace)

BEFORE:

```text
(of 25 differing paths only 5 differ in MAE). [P3-C009, C023]
```

AFTER:

```text
(of the 25 of 125 PPO+G sessions whose executed difficulty path differs from Constant-Same+G, only 5 differ in session MAE; final-action sequences differ in 50 of 125). [P3-C009, C023]
```

## research/evidence/final/PAPER3_FINAL_CLAIM_MATRIX.md (replace)

BEFORE:

```text
the frozen-evidence tags are local and unpushed.
```

AFTER:

```text
the frozen-evidence tags are local and unpushed. Action mix: the training-time Same share of the stochastic policy (last logging window) was 0.5069–0.5345 across the five training seeds (24,576 timesteps each; `research/analysis/phase1/x3_0/x3_0a_training_action_shares.csv`; `X3_0A_REPORT.md` item 7); the evaluation-time Same share of the X3-A trajectories is not stored in any summary and is not reported.
```

## research/evidence/PAPER3_EVIDENCE_PACKAGE.md (replace)

BEFORE:

```text
# Paper 3 — Evidence Package (simulation-only; frozen X3-A chain)
```

AFTER:

```text
# Paper 3 — Evidence Package (simulation-only; frozen X3-A chain)

**Wording alignment (2026-09-21; no number, table, hash or registered conclusion changed).** Framing: controlled policy decomposition / equivalence evaluation of PPO plus an application-level rule-based guardrail versus Constant-Same plus the same guardrail, in simulation; Kadam et al. 2026 is prior art for the application and its simulation-based policy comparison. The word "shield" survives only inside verbatim registered strings and artifact labels and is read as "application-level rule-based guardrail". Status note: §3 below ("O7 NOT RUN") is a superseded status from 2026-09-20; O7 was subsequently run and frozen (see `research/evidence/final/PAPER3_FINAL_EVIDENCE.md`); §3 is left as written for history.
```

## research/evidence/PAPER3_EVIDENCE_PACKAGE.md (replace)

BEFORE:

```text
| Registered interpretation | "no detectable PPO contribution beyond the shield in these checkpoints (equivalence within ±0.12 MAE)" |
```

AFTER:

```text
| Registered interpretation (verbatim string in `x3a_decision.json`, which uses the word "shield" for the guardrail layer) | "no detectable PPO contribution beyond the shield in these checkpoints (equivalence within ±0.12 MAE)"; manuscript reading: no detectable PPO contribution beyond the application-level rule-based guardrail in these checkpoints (equivalence within ±0.12 MAE) |
```

## research/evidence/PAPER3_EVIDENCE_PACKAGE.md (replace)

BEFORE:

```text
shield vs no shield on Constant-Same: MAE 1.104 vs 1.000
```

AFTER:

```text
guardrail on vs off on Constant-Same (labelled "shield" in the registered artifacts): MAE 1.104 vs 1.000
```

## research/evidence/PAPER3_EVIDENCE_PACKAGE.md (replace)

BEFORE:

```text
| The shield did not improve constant-Same tracking on the grid |
```

AFTER:

```text
| The application-level rule-based guardrail did not improve constant-Same tracking on the grid |
```

## research/evidence/PAPER3_EVIDENCE_PACKAGE.md (replace)

BEFORE:

```text
"PPO's contribution beyond the shield" concerns these checkpoints only.
```

AFTER:

```text
PPO's contribution beyond the application-level rule-based guardrail concerns these checkpoints only.
```

## research/evidence/PAPER3_EVIDENCE_PACKAGE.md (replace)

BEFORE:

```text
7. Tracking MAE ignores path shape (P3-C023) and equal MAE does not mean equal behaviour.
```

AFTER:

```text
7. Tracking MAE ignores path shape (P3-C023) and equal MAE does not mean equal behaviour.
8. **Action mix and session-level divergence (exact frozen values only).** Training-time Same share 0.5069–0.5345 per training seed (stochastic policy, last logging window; `x3_0a_training_action_shares.csv`; `X3_0A_REPORT.md` item 7). Five-persona frozen replay, 125 PPO+G sessions: final-action sequence differs from Constant-Same+G in 50, executed difficulty path in 25, session MAE in 5; sessions with at least one guardrail override 41 of 125 (`x3_0c_followup.json`; `x3_0c_replay_summary.csv`; P3-C009, P3-C023). The evaluation-time Same share and the session-level divergence on the 40-persona grid are not stored in any summary and are not reported.
```

## research/evidence/PAPER3_EVIDENCE_PACKAGE.md (replace)

BEFORE:

```text
guardrails are a formal "shield" or provide safety guarantees;
```

AFTER:

```text
the guardrail is described as a formal, safe-RL or verified mechanism, or as providing safety guarantees; PPO, RL for mock interviews, the simulator or a benchmark presented as the contribution;
```

## research/evidence/final/FINAL_MASTER_EVIDENCE_FREEZE.md (replace)

BEFORE:

```text
# PREPAIred — Master evidence freeze, claim audit and manuscript-preparation package (2026-09-20)
```

AFTER:

```text
# PREPAIred — Master evidence freeze, claim audit and manuscript-preparation package (2026-09-20)

**Wording alignment (2026-09-21; wording only; no number, table, hash, protocol or registered conclusion changed).** The research-question, contribution, title-candidate and contribution-list rows below now follow the locked three-paper positioning (`manuscript/paper{1,2,3}/FINAL_CONTRIBUTIONS.md`). Status statements dated 2026-09-20 elsewhere in this file (e.g. "independent methodology review pending", the two X1 defects "not fixed", the 16 LLM-sourced pairs of build A) were superseded by later records (build B; the Antigravity review; `PAPER1_FINAL_CLAIM_MATRIX.md`) and are left as written for history.
```

## research/evidence/final/FINAL_MASTER_EVIDENCE_FREEZE.md (replace)

BEFORE:

```text
lower volatility; "shield"; real-user or deployment claims;
```

AFTER:

```text
lower volatility; any formal-safety or safety-guarantee wording for the application-level rule-based guardrail; a new application, simulator or benchmark; real-user or deployment claims;
```

## research/evidence/final/FINAL_MASTER_EVIDENCE_FREEZE.md (replace)

BEFORE:

```text
use "failure-aware/failure-characterised" |
```

AFTER:

```text
use "tested failure handling under the specified harness and environment" |
```

## research/evidence/final/FINAL_MASTER_EVIDENCE_FREEZE.md (replace)

BEFORE:

```text
escape-proof, formal shield, "the LLM cannot alter
```

AFTER:

```text
escape-proof, formal security or verified isolation, "the LLM cannot alter
```

## research/evidence/final/FINAL_MASTER_EVIDENCE_FREEZE.md (replace)

BEFORE:

```text
| | Paper 1 (systems/dependability) | Paper 2 (evaluator validity) | Paper 3 (adaptive-difficulty PPO, simulation) |
```

AFTER:

```text
| | Paper 1 (systems / empirical dependability evaluation) | Paper 2 (exploratory evaluator measurement / diagnostics) | Paper 3 (learned vs constant difficulty policy, controlled equivalence, simulation) |
```

## research/evidence/final/FINAL_MASTER_EVIDENCE_FREEZE.md (replace)

BEFORE:

```text
| Research question | Which containment/authority-separation/fault-handling properties of the pipeline can be shown by tests able to fail? | How well does the composite agree with blinded humans, vs simple baselines, and which answers does it mis-score? | What does a learned PPO controller add beyond a constraint layer, versus matched simpler policies, in simulation? |
```

AFTER:

```text
| Research question (locked) | Which containment, authority-boundary, and failure-handling properties of an LLM-assisted technical-assessment pipeline can be demonstrated through controlled tests under a specified execution environment? | How does a composite technical-answer evaluator agree with human consensus and simpler component baselines, and which answer types and perturbations reveal systematic evaluator errors? | Under an identical rule-based guardrail layer, what does a learned PPO difficulty controller add beyond a simpler state-blind Constant-Same policy in simulated technical-interview trajectories? |
```

## research/evidence/final/FINAL_MASTER_EVIDENCE_FREEZE.md (replace)

BEFORE:

```text
| Main contribution | Failure-aware evaluation with negative/permissive controls; documented defects | Diagnostic/negative measurement result on an exploratory benchmark | Negative-equivalence, matched-control decomposition |
```

AFTER:

```text
| Main contribution (locked) | Scoped containment (nine attacks, one environment), tested failure handling on the repaired build, a fixed-turn Qwen authority observation, and a containment-oracle observation, with negative/permissive controls; the build-A defects and their repair are supporting record | Exploratory measurement and diagnostic study (agreement with three-rater consensus, component baselines, answer-type and perturbation error patterns), not the S1/S2/R formula | Controlled decomposition and preregistered equivalence evaluation of PPO plus application-level guardrail versus Constant-Same plus the same guardrail (Kadam et al. 2026 is prior art for the application and simulation) |
```

## research/evidence/final/FINAL_MASTER_EVIDENCE_FREEZE.md (replace)

BEFORE:

```text
→ new benchmark and blind raters |
```

AFTER:

```text
→ new benchmark and a documented rater process (blinding, if used, to be specified in the protocol) |
```

## research/evidence/final/FINAL_MASTER_EVIDENCE_FREEZE.md (replace)

BEFORE:

```text
| PPO superiority, deployment, shield |
```

AFTER:

```text
| PPO superiority, deployment, formal-safety or safety-guarantee wording for the guardrail, a new simulator/benchmark/application |
```

## research/evidence/final/FINAL_MASTER_EVIDENCE_FREEZE.md (replace)

BEFORE:

```text
(as a failure-characterisation paper; conditional on independent review of the X1 protocols)
```

AFTER:

```text
(as a scoped systems / empirical dependability evaluation; the earlier condition "independent review of the X1 protocols" was met by the Antigravity review, verdict: sound only after claim narrowing)
```

## research/evidence/final/FINAL_MASTER_EVIDENCE_FREEZE.md (replace)

BEFORE:

```text
**Title candidates** (from the claim map; not decisions): P1 "Testing containment and authority separation in an LLM-assisted technical-assessment prototype" / failure-characterisation framing; P2 "What a composite technical-answer evaluator measures: agreement, length dependence and under-scored concise answers"; P3 "What a learned difficulty controller adds beyond a constraint layer: a persona-level matched-control evaluation in simulation".
```

AFTER:

```text
**Locked titles (2026-09-21):** P1 "Scoped Evaluation of Containment, Authority Boundaries, and Failure Handling in an LLM-Assisted Technical-Assessment System"; P2 "Exploratory Measurement of an Evidence-Grounded Technical-Answer Evaluator"; P3 "A Controlled Equivalence Study of Learned and Constant Difficulty Policies in Simulated Technical Interviews". The earlier candidates in this row are retired.
```

## research/evidence/final/FINAL_MASTER_EVIDENCE_FREEZE.md (replace)

BEFORE:

```text
**Contribution lists** — P1: controlled test design with oracle validation; SUT defect catalogue; channel enumeration. P2: diagnostic measurement results with negative findings. P3: matched-control decomposition with equivalence framing.
```

AFTER:

```text
**Contribution lists (locked)** — P1: scoped containment; tested failure handling; fixed-turn Qwen authority observation; containment-oracle observation (supporting record: defect catalogue and repair; channel enumeration). P2: the exploratory measurement and diagnostic study (agreement, component diagnostics, answer-type error analysis, metamorphic/adversarial diagnostics). P3: controlled decomposition; preregistered equivalence evaluation; intervention accounting plus volatility; explicit limits.
```

## research/evidence/final/FINAL_MASTER_EVIDENCE_FREEZE.md (replace)

BEFORE:

```text
non-LLM evaluator/measurement-validity literature
```

AFTER:

```text
non-LLM evaluator measurement literature
```

## research/evidence/final/FINAL_CLAIM_AUDIT.md (replace)

BEFORE:

```text
- Paper 1: "failure-aware", "met the
```

AFTER:

```text
- Paper 1: "tested containment, authority-boundary and failure-handling properties under the specified harness and environment" (not "failure-aware orchestration" as the contribution), "met the
```

## research/evidence/final/FINAL_CLAIM_AUDIT.md (replace)

BEFORE:

```text
- Paper 2: "exploratory", "diagnostic", "measurement validity"; never "validated", "human-equivalent", "independent experts", "composite superior".
```

AFTER:

```text
- Paper 2: "exploratory", "measurement", "diagnostic", "three-rater human consensus"; never "measurement validity" as a headline, "validated", "human-equivalent", "independent experts", "blinded" raters (no blinding record), "composite superior".
```

## research/evidence/final/FINAL_CLAIM_AUDIT.md (replace)

BEFORE:

```text
"rule-based guardrail (not a shield)"; never "PPO superior"
```

AFTER:

```text
"application-level rule-based guardrail"; never "PPO superior"
```

## research/evidence/final/PAPER3_FINAL_EVIDENCE.md (replace)

BEFORE:

```text
Framing: **controlled decomposition / negative-equivalence result**, not PPO superiority.
```

AFTER:

```text
Framing: **controlled policy decomposition / equivalence evaluation** (locked 2026-09-21), not PPO superiority.
```

## research/evidence/final/PAPER3_FINAL_EVIDENCE.md (replace)

BEFORE:

```text
the guardrail layer is a rule-based constraint layer, **not a formal shield**;
```

AFTER:

```text
the guardrail layer is an application-level rule-based guardrail with no formal safety specification and no safety guarantee;
```

## research/evidence/final/FINAL_PUBLICATION_READINESS.md (replace)

BEFORE:

```text
as an exploratory diagnostic / measurement-validity study:
```

AFTER:

```text
as an exploratory measurement / diagnostic evaluator study:
```

## research/evidence/final/manuscript/paper3/FINAL_LIMITATIONS.md (replace)

BEFORE:

```text
(11) frequent Same action: a learned policy that often proposes Same is close to the state-blind comparator by construction (the stored summaries reviewed do not give the Same-action share; quantify it from the frozen sessions before writing a number); (12) limited session-level policy divergence: of 25 differing action paths only 5 differ in MAE, and 41 of 125 five-persona sessions had at least one guardrail override [P3-F3, P3-F4]. Details follow.
```

AFTER:

```text
(11) action mix (Same is frequent in training, not quantified at evaluation): the training-time Same share of the stochastic policy in the last logging window was 0.5069-0.5345 across the five training seeds (24,576 timesteps each; research/analysis/phase1/x3_0/x3_0a_training_action_shares.csv; X3_0A_REPORT.md item 7), and in the stored probe sweep of the seed-123 checkpoint 8 of 66 probes chose a non-Same action (X3_0A_REPORT.md item 6; one checkpoint at one neutral point, not a general statement); the evaluation-time Same share of the X3-A trajectories is not stored in any summary and is not reported, and a policy that often proposes Same is close to the state-blind comparator by construction; (12) session-level policy divergence, exact counts from the frozen five-persona replay (125 PPO+G sessions = 5 training seeds x 25 sessions): the final-action sequence differs from Constant-Same+G in 50, the executed difficulty path (after clipping to [1, 5]) in 25, and the session MAE in 5; separately, 41 of 125 PPO+G sessions had at least one guardrail override (x3_0c_followup.json; X3_0C_FOLLOWUP.md; P3-C009, P3-C023, P3-F3, P3-F4); session-level divergence on the 40-persona X3-A grid is not stored in any summary and is not reported. Details follow.
```

## research/evidence/final/manuscript/paper3/FINAL_LIMITATIONS.md (replace)

BEFORE:

```text
MAE ignores path shape (of 25 path-differing sessions only 5 differ in MAE).
```

AFTER:

```text
MAE ignores path shape (of the 25 of 125 five-persona PPO+G sessions whose executed difficulty path differs from Constant-Same+G, only 5 differ in session MAE).
```

## research/evidence/final/manuscript/paper3/FINAL_LIMITATIONS.md (replace)

BEFORE:

```text
The guardrail is an application-level rule-based guardrail (a rule-based constraint layer), not a formal shield and not a safety guarantee.
```

AFTER:

```text
The guardrail is an application-level rule-based guardrail (a rule-based constraint layer) with no formal safety specification and no safety guarantee.
```

## research/evidence/final/manuscript/paper3/FINAL_SECTION_OUTLINE.md (replace)

BEFORE:

```text
terminology: application-level rule-based guardrail, not a formal shield)
```

AFTER:

```text
terminology: application-level rule-based guardrail; no formal safety specification, no safety guarantee)
```

## research/evidence/final/manuscript/paper3/FINAL_SECTION_OUTLINE.md (replace)

BEFORE:

```text
8 Conclusion (negative-equivalence; no superiority claim)
```

AFTER:

```text
8 Conclusion (equivalence within the registered margin; no superiority claim)
```

## research/evidence/final/manuscript/paper1/FINAL_SECTION_OUTLINE.md (replace)

BEFORE:

```text
8 Conclusion (scoped to the tested containment and failure-aware behaviours under the specified harness and environment)
```

AFTER:

```text
8 Conclusion (scoped to the tested containment, authority-boundary and failure-handling properties under the specified harness and environment)
```

## research/evidence/final/manuscript/paper2/FINAL_ABSTRACT_FACTS.md (replace)

BEFORE:

```text
p 0.0018863 (case-level), 95% CI [0.1575, 0.5774];
```

AFTER:

```text
95% case-bootstrap CI [0.1575, 0.5774]; the stored p = 0.0018863 is a case-level, nominal p-value under independent-case assumptions (answers cluster within 8 questions; it is not primary robustness evidence and not a claim of confirmatory significance; for inferential robustness use the question-aware two-level cluster interval [0.1529, 0.6490]);
```

## research/evidence/final/manuscript/paper2/FINAL_ABSTRACT_FACTS.md (replace)

BEFORE:

```text
evaluated against three human raters on 64
```

AFTER:

```text
evaluated against three-rater human consensus on 64
```

## research/evidence/final/manuscript/paper2/FINAL_CONTRIBUTIONS.md (replace)

BEFORE:

```text
p = 0.0018863 (case-level test; answers not independent within a question), case-bootstrap 95% CI [0.1575, 0.5774]; question-aware intervals are wider (two-level [0.1529, 0.6490]).
```

AFTER:

```text
case-bootstrap 95% CI [0.1575, 0.5774]; question-aware intervals are wider (two-level cluster bootstrap [0.1529, 0.6490]; this, not the p-value, is the inferential-robustness evidence). The stored p = 0.0018863 is a case-level, nominal p-value under independent-case assumptions (answers cluster within 8 questions); it is not a claim of robust confirmatory significance.
```

## research/evidence/final/manuscript/paper2/FINAL_LIMITATIONS.md (append)

BEFORE:

```text
(end of file unchanged; block appended)
```

AFTER:

```text
Nominal p-value: the stored Spearman p (0.0018863; research/results/paper2/paper2_summary_results.csv) is a case-level, nominal p-value under independent-case assumptions; answers cluster within 8 questions, so it is not primary robustness evidence and is not a claim of confirmatory significance. Report the question-aware two-level cluster interval [0.1529, 0.6490] (X2A-C001) as the inferential-robustness evidence. Rater terminology: write "three-rater human consensus"; no record of rater blinding or independence is stored, so "blinded", "independent", "expert panel" and "committee" are not used.
```
