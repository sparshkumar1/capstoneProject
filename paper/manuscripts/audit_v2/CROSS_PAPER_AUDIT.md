# CROSS-PAPER AUDIT (2026-09-21, audit-v2 pass)

Method: `audit_v2/overlap_scan.py` on the v2 manuscript bodies (comments and reference lists removed; tables excluded from sentence/8-gram scans), plus manual comparison. The previous overlap report (`cross/CROSS_PAPER_OVERLAP_REPORT.md`) reported 0 shared references as a *virtue*; the brief for this pass reverses that: shared foundational literature should be cited when scientifically relevant. That has been applied (see Rule 2).

## 1. Automated results (v2)
| Pair | Duplicate sentences | Shared 8-grams | Content of the overlap |
|---|---|---|---|
| P1–P2 | 0 | 6 | anonymity notice; the sentence "studies of LLM-based grading report that injected instructions can change grades" (deliberately shared, see Rule 2) |
| P1–P3 | 1 | 5 | "Artifact availability is not independent reproduction, which has not been performed." (generic reproducibility disclosure) and the anonymity notice |
| P2–P3 | 0 | 11 | anonymity notice only |
Reference lists: P1 14, P2 16, P3 14. Shared: arXiv:2606.03090 (P1 [12] = P2 [16]). No other shared entry.

## 2. Rule-by-rule
| Rule | Finding | Action |
|---|---|---|
| 1. Do not describe the architecture in detail three times | P1 Section III carries the only full component list (one paragraph + configuration list). P2 Section III describes only the evaluator formula and cross-encoder (needed to interpret the measurement). P3 Section III describes only the simulator, policies and guardrail. No paragraph duplicates another. | none |
| 2. Do not force zero shared references | The injected-instruction/LLM-grader literature is relevant to both P1 (authority boundary) and P2 (injected-instruction probes). It was cited only in P1. | Added P1 [12] as P2 [16] with a limiting sentence in P2's related work (the probes concern a similarity scorer, not an LLM grader). No other shared reference is scientifically necessary: P3's statistical references (uncertainty over runs, equivalence tests) are not needed by P1, and P2's clustered-bootstrap and ICC references are not needed by P3 (P3's own two-way cluster bootstrap is cited to its registered method, not to [13] of P2; adding Field & Welsh to P3 would cite a one-way clustered-data result for a two-way design without a verified justification). |
| 3. Distinct identities stated | P1 containment/authority/failure handling; P2 evaluator measurement, human-reference agreement, diagnostic errors; P3 learned vs constant policy, equivalence, behavioural accounting. Each abstract and RQ states only its own. | none |
| 4. Shared properties justified per paper | (a) The evaluator appears in P1 as a component whose output is fixed to a stub (justification: isolates the feedback path); in P2 as the system under measurement. (b) The rule-based guardrail appears only in P3. (c) The repository/registration-status statement appears in P1 and P3 with the same qualifier (local, unpushed tags). (d) Same-agent/AI-assistance: disclosed in P1 in the body; for P2 and P3 the decision is pending (see `AI_DISCLOSURE_AUDIT.md`). | none needed beyond D-4 |
| 5. Repeated sentences/tables/captions/contribution language | One duplicated generic sentence (P1–P3); no repeated tables or captions; contribution paragraphs use the same list-of-four pattern but different content. | Sentence variant left; it is a required disclosure in both. |

## 3. Terminology consistency
| Term | P1 | P2 | P3 | Consistent? |
|---|---|---|---|---|
| baseline / repaired SUT | used | n/a | n/a | yes |
| human reference score | n/a | used (21×); "three-rater" once, defined | n/a | yes |
| "registered" / "pre-specified" | "pre-specified"; "not a preregistered inferential study" | "protocol … registered before the ratings" (confirmatory requirement, future) | "pre-specified"; defined once; "repository-registered" once | yes |
| exploratory vs confirmatory | descriptive engineering evaluation | exploratory (12×) | pre-specified primary; secondary descriptive | yes |
| guardrail (never "shield" except prior-work sentence) | n/a | n/a | 56× | yes |
| "independent reproduction" | disclosed as not performed | same | same | yes |

## 4. Contradictions
None found among the three manuscripts. One inconsistency between a *frozen* note and frozen data (SEC-05 status; see P1-F1) is disclosed and not edited.

## 5. Shared system properties and why each is relevant
| Property | Papers | Relevance |
|---|---|---|
| Local unpushed tags as "registration" | P1, P3 | qualifies how "pre-specified" is meant |
| Evaluator | P1 (fixed-stub), P2 (system under test) | different roles; P1 reports no evaluator accuracy, P2 no containment |
| Python environment violates declared pins | P1, P2 | reproducibility limitation (P3 uses a separate locked environment) |
| Author-constructed instruments | P1 (attack programs), P2 (benchmark), P3 (simulator) | construct-validity limitation in each |

## 6. Verdict
Distinct papers, no duplicated claim, no repeated evidence. **GREEN** for cross-paper integrity; remaining cross items are decisions (AI-use disclosure for all three; whether to cross-cite once any paper is public).
