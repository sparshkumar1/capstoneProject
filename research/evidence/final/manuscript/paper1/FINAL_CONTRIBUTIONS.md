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
