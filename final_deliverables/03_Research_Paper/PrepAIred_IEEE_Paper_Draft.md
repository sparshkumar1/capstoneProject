**SUPERSEDED (2026-11-13):** per explicit user decision, `final_deliverables/05_IEEE_Paper/Final_IEEE_Paper_Source.tex`
(+ its compiled `Final_IEEE_Paper_Anonymous.docx`/`.pdf`) is the canonical IEEE paper for submission. This document is
kept only as a preserved earlier draft, not for further editing or submission. It also contains at least one known,
uncorrected factual error relative to the project's own current evidence — see `FINAL_SOURCE_OF_TRUTH_AND_RECONCILIATION.md`,
Finding 2 (this draft's Abstract/§III claims Qwen performs "partial-credit adjustment" on the score and implies
LLM-generated hints; both are disproved by Chapter 10 §10.9 of the university report and
`Independent_Project_Audit/06_Final_Evaluation_Phase_Addendum.md` §6.5). Do not cite or quote this draft as current.

**Format note:** this content is drafted for direct transfer into the official IEEE conference two-column template (`Conference-template-A4.doc`, per the PPT guideline's supplied link — not pandoc/LaTeX-generated in this pass, as no DOCX/LaTeX authoring tool was available in this session). Section numbering and content below follow standard IEEE conference-paper structure and are ready to paste into that template's sections.

---

# Testing-Driven Verification of a Guardrail-Constrained Adaptive-Difficulty Policy in a Deployed Technical-Interview System

**Authors:** Sparsh Kumar, Naveen S Khadd, Manasa S A, Athreya Shashidhara
**Affiliation:** Department of Computer Science and Engineering, PES University, Bengaluru, India

## Abstract

Adaptive technical-interview preparation systems increasingly pair a learned reinforcement-learning (RL) policy with a deterministic safety layer intended to prevent pedagogically unsound decisions, but the safety layer itself is rarely subjected to systematic, boundary-level testing once deployed. We report a project-specific testing programme applied to a deployed adaptive-difficulty system (PrepAIred), combining this project's own existing frozen evidence — that a post-inference guardrail layer, not the trained Proximal Policy Optimisation (PPO) policy, accounts for essentially all of the measured tracking-accuracy improvement over a fixed-difficulty baseline — with new, independently executed verification of that guardrail layer against the live production checkpoint. Direct testing of the real, deployed policy against ten constructed candidate-state scenarios surfaced a below-average-scoring candidate for whom the raw policy proposed a difficulty escalation; systematic boundary testing of the guardrail layer's five documented rules confirmed this was not an isolated anomaly but a genuine, reproducible coverage gap in the interval perf ∈ [0.30, 0.40), where no guardrail intervenes. We diagnosed the gap to a single unaligned threshold between two adjacent rules, applied a minimal, single-condition fix, and verified it closes the gap (13/13 boundary cases pass) with zero regressions across a 283-test automated suite (264/283, 93.3%, passing both before and after the fix). We additionally report a full-stack reconciliation between this project's prior documentation and its verified implementation, which surfaced eight factual discrepancies — including an incorrect claim that question selection uses semantic vector retrieval (it is rule-based) and an incorrect PPO training step count — each corrected with direct evidence. We make no claim about real-candidate learning outcomes, pedagogical efficacy, or the superiority of this architecture over alternatives; our contribution is a demonstrated testing methodology and its concrete yield: one verified, non-trivial safety-layer defect found and fixed in a live system that passed its existing test suite throughout.

**Index Terms:** adaptive testing, reinforcement learning, safety guardrails, software testing, technical interview systems, defect discovery

## I. Introduction

Technical interviews remain a high-stakes, difficult-to-practise evaluation format, and existing preparation platforms largely present fixed-difficulty question pools with no individualised adaptation [1]. Systems that do adapt difficulty increasingly combine a learned policy (commonly reinforcement learning) with a deterministic safety or guardrail layer that overrides the policy where its recommendation would be pedagogically unsound — a pattern also seen in automated-scoring systems that pair a generative or learned component with rule-based validation [2], [3]. A natural but under-examined question follows: once such a guardrail layer is deployed, is it actually tested at the level of its individual rule boundaries, against the real policy it is meant to constrain, rather than only exercised incidentally through end-to-end functional tests?

This paper reports the result of asking that question of a real, deployed system: PrepAIred, an adaptive technical-interview preparation platform combining a frozen PPO policy, a six-rule deterministic guardrail layer, and a rubric-anchored multi-component semantic evaluator. This project's own prior, already-frozen research evidence had already established an important and somewhat counter-intuitive finding — that the guardrail layer, not the trained policy, accounts for essentially all of the measured improvement in difficulty-tracking accuracy over a fixed-difficulty baseline, a finding significant enough that this project's internal evidence record explicitly withdraws the simpler claim that "PPO improves tracking." If the guardrail layer is this system's primary behaviour-shaping mechanism, its own correctness deserves direct, independent, boundary-level verification — which, prior to this work, had not been performed against the live production checkpoint.

**Contributions.** (1) A systematic, boundary-targeted testing methodology for a deployed RL-plus-guardrail adaptive system, exercising the real production policy checkpoint and the real guardrail function directly, rather than only through higher-level functional tests. (2) The empirical discovery and minimal, verified correction of a genuine guardrail coverage gap — perf ∈ [0.30, 0.40) was unguarded against policy-proposed difficulty escalation — found not by code reading alone but by constructing and running adversarial boundary cases against the live checkpoint. (3) A disciplined reconciliation between this project's prior documentation and its verified implementation, correcting eight specific factual discrepancies with direct evidence, including the retraction of an unverified headline accuracy figure and an incorrect architectural claim about semantic question retrieval.

**What this paper does not claim.** We make no claim about real-candidate learning outcomes or pedagogical efficacy (no human-subject evaluation was conducted); we do not claim the discovered gap was ever exploited by a real candidate in production, only that it was reachable and unguarded; we do not claim superiority over alternative adaptive-difficulty architectures; and a separate research-paper draft describing a multi-agent "bounded-authority coordination" extension to this system, supplied alongside this project's materials, was found on inspection not to correspond to anything in the deployed codebase and is excluded from this paper's evidentiary claims entirely (§VI).

## II. Related Work

**Automated scoring decomposition and validation.** AutoSCORE [2] decomposes essay scoring across specialist agents coordinated by a validating "chairman" agent that applies rubric-aligned veto and capping rules, outperforming monolithic LLM scoring. PrepAIred's evaluator follows a structurally similar pattern (three scoring components combined through a fixed formula, with a deterministic post-hoc `ScoreValidator` applying capping/penalty rules) — this paper's contribution is orthogonal to that architecture's correctness, focusing instead on the separate guardrail layer governing *difficulty adaptation*, not answer scoring.

**LLM scoring reliability.** Independent empirical work [4], [5] finds LLM-based scoring reliable but prompt- and domain-dependent, with correlation to human judgment varying by task. This motivates architectures, including PrepAIred's, that use a learned/generative component only as a secondary, scope-limited signal rather than the sole evaluator.

**Multi-agent coordination evaluation.** MultiAgentBench [6] establishes milestone-based evaluation methodology for measuring multi-agent coordination quality, not just task completion — a methodological principle this paper's own testing design follows at a smaller scale (measuring whether the guardrail-and-policy coordination behaves correctly at specific, constructed boundary conditions, not only whether an end-to-end session completes).

**Grounded verification against hallucination.** Argos [7] demonstrates that grounding a reward or verification signal in independently checkable evidence, rather than trusting a learned component's own output, reduces hallucination-driven errors in agentic RL. The same principle motivates this paper's broader system design (a deterministic evaluator as the primary scoring path, a learned LLM only as a secondary adjustment) and, at the testing level, motivates verifying the guardrail layer against directly observable, constructed states rather than trusting either the policy's own behaviour or prior documentation describing it.

**Gap this paper addresses.** None of the surveyed work evaluates a *deployed* RL-plus-guardrail adaptive-difficulty system through direct, boundary-targeted testing of the guardrail layer against the live policy checkpoint, nor reports a genuine defect found and fixed through that process. This paper reports exactly that case study.

## III. System Architecture

PrepAIred is a single-controller, hub-and-spoke architecture (Fig. 1, described in prose as no diagramming tool was available for this draft): a central orchestrator owns all session state; a semantic evaluator (Sentence-BERT similarity + FAISS concept-coverage + a fine-tuned CrossEncoder reasoning score, combined 0.15/0.35/0.50 with a keyword-stuffing defense dampening concept coverage when reasoning quality is low) scores verbal/code answers; a frozen PPO policy (`Discrete(3)` = {Easier, Same, Harder}, 6-dimensional observation: performance, rolling-average performance, audio confidence, hesitation, session progress, normalised difficulty) proposes a difficulty action; a six-rule deterministic guardrail layer evaluated in strict priority order may override that proposal; a question selector retrieves the next question via nearest-difficulty matching and topic rotation — **not** via semantic/vector retrieval, correcting a claim in this project's own prior internal documentation; and a locally hosted LLM is invoked selectively for partial-credit adjustment and hint/follow-up generation when the primary deterministic score is low. This is a single-agent, single-policy system: there is no second decision-making agent and no inter-agent arbitration protocol anywhere in the deployed codebase (§VI).

## IV. Methodology

### A. Policy Inference Sanity Check

We loaded the real, frozen, deployed PPO checkpoint via the actual production inference wrapper (not a reimplementation) and constructed ten candidate-state scenarios spanning strong, weak, boundary, "nervous-expert" (high performance with high hesitation), difficulty-floor, difficulty-ceiling, declining-trend, and improving-trend profiles. Each scenario was passed through the real `suggest()` method and the resulting action, new difficulty, and action source (policy vs. heuristic fallback) were recorded.

### B. Guardrail Boundary Verification

We called the real guardrail function directly (no mocking) with eleven constructed states spanning each of the five documented rules' trigger boundaries, plus states adjacent to those boundaries to test for gaps between adjacent rules' conditions. This tests the guardrail layer's actual coded behaviour against its own documented specification, independent of whether the policy itself behaves as expected.

### C. Diagnosis-and-Fix Protocol

Where testing surfaced a defect, we applied the following discipline, consistent with this project's broader experiment-governance policy: diagnose root cause before proposing a fix; apply the minimal, single-purpose change that closes the specific gap found, without altering unrelated behaviour; re-verify the targeted fix with boundary cases bracketing the change; and rerun the full existing automated test suite to confirm zero regressions before considering the fix complete.

### D. Full-Stack Documentation Reconciliation

Independent of the RL/guardrail testing above, we performed a systematic line-by-line reconciliation between this project's existing descriptive documentation and the actual source code for every architecturally significant claim (service frameworks, data-flow mechanisms, training hyperparameters, action-space definitions), using direct code inspection as the sole arbiter, and flagging — rather than silently correcting — any claim for which no supporting stored artifact could be located.

## V. Results

### A. Policy Inference

All ten constructed scenarios produced a valid `Discrete(3)` action and a difficulty remaining within the valid [1,5] range; all ten were served by the real policy (not the heuristic fallback), confirming the deployed checkpoint loads and functions correctly in the current environment. One scenario — a below-average performance score (0.35) with moderate audio confidence and hesitation — produced a raw "Harder" action from the policy.

### B. Guardrail Coverage Gap: Discovery

Testing the guardrail layer directly against the scenario above, and against boundary-adjacent constructed states, confirmed that **no guardrail among the five documented rules intervenes for performance scores in the half-open interval [0.30, 0.40)** when the policy proposes escalation and confidence/hesitation are moderate. The two lowest-performance rules require `perf < 0.30`; the partial-understanding rule originally required `perf > 0.40`. The interval between these two thresholds is simply unguarded by construction — a boundary-alignment oversight across two independently reasonable-looking rules, not a defect within either rule considered alone.

### C. Fix and Verification

We widened the partial-understanding rule's lower bound from `perf > 0.40` to `perf >= 0.30`, a single-condition change. Re-running the boundary-verification suite (now thirteen cases, including the original gap case and two new cases exactly at and just below the new boundary) gave **13/13 passing, zero mismatches**. A full regression run of the existing 283-test automated suite gave **264 passed, 19 failed, 0 collection errors — identical to the pre-fix result**, confirming the change introduced no regressions. All 19 remaining failures trace to a single external environment dependency (an unavailable container-execution daemon in the test environment, affecting only sandboxed code-execution tests) and one pre-existing, already-documented, deliberately unaltered issue unrelated to this fix.

### D. Supporting System-Level Evidence

Table I summarises supporting verification performed alongside the guardrail investigation, establishing that the finding above was not an isolated, unrepresentative probe of an otherwise-unverified system.

**Table I. Supporting verification summary**

| Area | Method | Result |
|---|---|---|
| Evaluator API contract | Direct test-client calls, valid/invalid/malformed input | 7/7 pass |
| Evaluator adversarial input | 10 constructed adversarial/edge-case texts | 10/10 handled without crash, scores in-range |
| Database referential integrity | Direct inspection of the live, populated database | 0/52 and 0/26 orphaned foreign keys |
| Sandbox isolation configuration | Direct code inspection of container-invocation flags | All claimed isolation flags confirmed present |
| Evaluator latency | 30 warm in-process calls | Median 896 ms, p95 986 ms (this host; not a cross-environment comparison) |
| Frontend | Existing automated UI test suite | 28/28 pass |

### E. Documentation Reconciliation Findings

The reconciliation process (§IV-D) found eight discrepancies between this project's prior documentation and the verified implementation, the two most architecturally significant being: (1) question selection was documented as retrieving from a semantic vector index, but the deployed code contains no embedding or vector-search dependency whatsoever — it is a deterministic difficulty-match-and-topic-rotation algorithm; and (2) the deployed policy's documented training provenance (step count, random-seed set) did not match this project's own existing frozen research-evidence record for the same checkpoint lineage, and the documented figure traced to no locatable stored artifact. All eight findings, with full evidentiary detail, are catalogued in the accompanying project report (not reproduced in full here for space).

## VI. Discussion and Limitations

**On the guardrail finding's significance.** This project's own prior, independently-frozen research evidence already established that the guardrail layer — not the learned policy — is the primary mechanism responsible for this system's measured improvement over a non-adaptive baseline. The present work's contribution is complementary and, we argue, necessary: a safety layer identified as the system's primary behaviour-shaping mechanism cannot be assumed correct merely because it is deterministic and rule-based; this case study shows a real, reproducible gap existed in exactly that layer, reachable by the real deployed policy's own output, undetected by the system's pre-existing end-to-end test suite (which exercises typical, not adversarially-constructed, scenarios).

**Threats to validity.** The guardrail gap was found via ten hand-constructed scenarios, not an exhaustive or randomised search of the six-dimensional state space; other, undiscovered gaps may remain. The fix was verified against the existing automated suite and targeted boundary cases, not against a held-out, independently-constructed validation set. No claim is made that this fix is optimal among possible corrections, only that it closes the specific identified gap with no observed regression. No human-candidate data informed this study; all evidence is either direct code/configuration inspection or execution against constructed, synthetic inputs.

**Excluded scope.** A separate research-paper draft, supplied alongside this project's materials, describes a bounded-authority multi-agent coordination layer (a second "Strategy" and "Coaching" agent arbitrating proposals against the policy) and reports a four-campaign replay/fault-injection/ablation experimental study against that layer. Direct inspection in this work confirmed **this layer, and every specific numerical result in that draft, do not exist anywhere in the deployed codebase** — no second decision-making agent, no arbitration module, and no matching stored artifact for any of its reported figures. That draft's statistical methodology (cluster-bootstrap confidence intervals, pre-registered-prediction discipline) is methodologically sound and informed this paper's own verification discipline (§IV), but its results are not real evidence about this deployed system and are explicitly excluded from this paper's claims.

## VII. Conclusion and Future Work

Systematic, boundary-targeted testing of a deployed adaptive-difficulty system's guardrail layer — the component this project's own prior evidence identifies as its primary behaviour-shaping mechanism — found and enabled the correction of a genuine, previously undetected safety-coverage gap, with the fix verified to introduce zero regressions across the system's existing 283-test automated suite. This demonstrates both the value of boundary-level testing applied directly to deployed rule systems (not only to the learned components they constrain) and a concrete, reproducible instance of such testing yielding a real improvement, rather than only confirming existing behaviour. Future work includes an exhaustive or randomised search of the full six-dimensional state space for further guardrail gaps, execution-level (not only configuration-level) verification of the sandboxed code-execution isolation layer once a container-execution daemon is available in the test environment, and — as a separate, explicitly preregistered effort distinct from this paper — a decision on whether to actually build the multi-agent coordination layer described in the excluded research-paper draft (§VI), which would make its experimental framing genuinely applicable to this system.

## References

[1] [Suitable interview-platform landscape citation — carried from project literature review, Chapter 3 of the accompanying project report]

[2] Y. Wang et al., "AutoSCORE: Enhancing Automated Scoring with Multi-Agent Large Language Models via Structured Component Recognition," arXiv:2509.21910, 2025.

[3] D. Mendonça, Quintal, and Mendonça, "Evaluating LLMs for Automated Scoring in Formative Assessments," *Applied Sciences*, 2025, doi: 10.3390/app15052787.

[4] A. Karjus et al., "Machine-Assisted Grading of Nationwide School-Leaving Essay Exams with LLMs and Statistical NLP," arXiv:2601.16314, 2026.

[5] [reserved — see note below]

[6] K. Zhu, H. Du et al., "MultiAgentBench: Evaluating the Collaboration and Competition of LLM agents," in *Proc. 63rd Annual Meeting of the Association for Computational Linguistics (ACL)*, vol. 1, pp. 8580–8622, 2025.

[7] Microsoft Research, "Argos: Multimodal Reinforcement Learning with Agentic Verifier for AI Agents," Microsoft Research publication, 2026.

[8] J. Schulman, F. Wolski, P. Dhariwal, A. Radford, and O. Klimov, "Proximal policy optimization algorithms," arXiv:1707.06347, 2017.

[9] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence embeddings using Siamese BERT-networks," in *Proc. EMNLP*, 2019.

[10] J. Johnson, M. Douze, and H. Jégou, "Billion-scale similarity search with GPUs," *IEEE Transactions on Big Data*, vol. 7, no. 3, pp. 535–547, 2019.

**Note on references [1] and [5]:** [1] needs a verified "existing partial solutions" citation (e.g. a platform landscape/survey source) not yet selected — see the project report's Chapter 3 §3.1 for the status of that search. [5] is reserved for the Mendonça/Karjus pairing's second reliability citation if a reviewer requests additional support; currently folded into [3]/[4]. **Both should be resolved before final submission**, consistent with this paper's own stated citation-integrity discipline.
