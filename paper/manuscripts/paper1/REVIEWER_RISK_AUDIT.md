# P1 — reviewer-risk audit (2026-09-21)

Scope: the blinded ICETC manuscript (`venue/ICETC_P1/P1_ICETC_BLINDED.md/.pdf`, built from `venue/icetc2026/ICETC_PORT_MANUSCRIPT.md`) checked against the reviewer-level concerns in the master brief (A–S) and against the evidence trail (`paper1/claim_ledger_v2.md`, `paper1/P1_SEC05_RECONCILIATION.md`, `research/evidence/final/PAPER1_FINAL_CLAIM_MATRIX.md`). Only wording was changed in this pass (one added introduction paragraph and one list item); no number, result or frozen file was changed. This supersedes nothing: the earlier attack audit is `paper1/reviewer_attack_audit.md`.

## Disposition of the brief's concerns
| Item | Requirement | State in the manuscript | Status |
|---|---|---|---|
| A | Contribution framed as an evidence framework, not a new algorithm or a formal framework | Introduction: each concern becomes a named property, a test condition, an oracle independent of the component under test and, where possible, a weakened control; contributions are "scoped empirical evidence of four kinds"; Discussion: "nothing here is a new escape result"; conclusion "scoped observations, not guarantees". The application-test versus methodology distinction is implicit rather than stated in one sentence | Met; one optional sentence could make the distinction explicit (author choice) |
| B | ICETC education/assessment fit without outcome claims | New introduction paragraph: technical-interview practice, formative use, assessment integrity, infrastructure that educational technology relies on; explicit "no learning, grade, usability or outcome measure"; "learning outcomes" in the not-evaluated list | Met in this pass; fit is still the authors' argument, not something ICETC has confirmed |
| C | X1-B-I is not a prompt-injection-resistance test | "The steering effect of the injections was not demonstrated"; the test covers narrative feedback with the evaluator output held fixed; the follow-up channel is untested | Met |
| D | Same agent designed, ran, repaired and re-tested; regression evidence, not replication | Results and Threats: "regression check and not an independent replication"; "One AI coding agent designed, pre-specified, ran, repaired and re-tested"; reruns written after baseline results were seen | Met (kept because it bears on validity) |
| E | SEC-01 ptrace | Literal pre-flight filter; disabled filter → direct call returned 0; "not evidence of kernel-level ptrace containment"; not attributed to Docker | Met |
| F | SEC-05 five attacks, frozen note untouched | Five attacks named (SEC-02, -05, -07, -08, -09); SEC-05 separated by execution time; the frozen note still says four and is not edited (`P1_SEC05_RECONCILIATION.md`) | Met; the frozen-note discrepancy stays visible in the repository record |
| G | X1-C counts, no statistical rate | 9 programs, 5/5, seven controls 5/5, benign 10/10; "k/5 counts runs meeting a criterion and is not a rate" | Met |
| H | SEC-08 oracle not fully independent | Stated in Results and Threats | Met |
| I | SEC-09 flawed canary reset | Stated; only the write-failure observation is relied on | Met |
| J | FLT-07b is not a repair | "one baseline run 0.1 s above the bound; not a repair"; the two substantive defects are FLT-03 and FLT-06 | Met |
| K | FLT-04 is range sanitization | "a range-sanitization observation and not evidence of corruption detection" | Met |
| L | FLT-08 / FLT-09 unexecuted | Stated in Table III and text | Met |
| M | X1-B-I validity and baseline diagnostic | Repaired 72/72 valid, 14 observables equal, mutation control 72/72; baseline 16/72 valid, minimum 30, "diagnostic only" | Met |
| N | Timeout | Shipped 6 s versus 19–30 s local generation; test client raised to 600 s; "no end-user consequence was tested" | Met |
| O | Environment | Windows 11 (10.0.26200), WSL2 kernel 6.6.87.2, Docker Desktop with Docker 29.7.2, 12 CPUs, 8.15 GB, model file name and decoding settings; "No other environment was tested" | Met |
| P | Package-version drift | "The development environment's package versions violate its declared pins" (Threats) | Met |
| Q | No inferential statistics | Stated in the introduction and the threats section; none reported | Met |
| R | Artifact availability | "stored in the project repository, which is not publicly released in this draft"; "not independent reproduction" | Met; no URL |
| S | References | 14 entries, all cited, all resolve; unverified venues and abstract-level readings are labelled in the list (`audit_v2/REFERENCE_AUDIT.md`) | Met; the reference list is mostly 2025–2026 arXiv preprints, see objection 4 |

## Hostile-review simulation
**What is actually new?** Not a method or result about sandboxes in general. The manuscript offers a property-by-property evidence account for one pipeline, including the observation that the executor's own status string did not identify containment for five attacks, and that the ptrace outcome came from an application-level filter.

**Strongest likely criticisms (major)**
1. *One application, one machine, fixed programs.* Nine fixed programs and five deterministic repetitions cannot support claims beyond "these programs, this configuration". The paper already says so; a reviewer may still ask what a reader can transfer. The answer offered is the evidence structure (oracle, control, layer attribution), not the outcome.
2. *Author-written attacks, oracles and controls; same agent designed and re-tested.* The independence limitation is stated. It cannot be removed without an independent re-run.
3. *Education relevance.* ICETC is an education-technology venue and the paper reports no learning, usability or user outcome. The added paragraph argues assessment-integrity relevance only. This may still be judged a weak fit for the track; no evidence exists that would change that.

**Moderate:** the artifact is not public, so nothing can be independently rerun; git tags and short hashes cannot currently be resolved by a reviewer; timings are single-machine; FLT-08 and FLT-09 were not executed; the follow-up-question channel was not tested.

**Minor:** mostly preprint references (labelled); Fig. 1's labels are small; the page count is Word's rendering.

**Which claim is easiest to attack?** "Contained" for the nine programs: it is defined operationally in the paper ("the recorded outcome of a named program under the shipped configuration met prespecified criteria") and bounded by the permissive controls, which is the intended defence.

**Is any result over-interpreted?** Not on the pages read: the 72/72 result is limited to fixed evaluator output, one channel and unseeded generation, and the steering claim is explicitly withheld.

**Overlap with the other papers?** None in evidence or method (P3 is a simulation study; the system paper is planned and unevaluated). The X1 results must not be reused as evidence of system effectiveness (`cross/THREE_PAPER_OVERLAP_AUDIT.md`).

**Minimum changes that would make it more defensible** (all author decisions, none needs new science): confirm whether git identifiers stay in the blinded text; decide whether to state the "evaluation methodology, not an application test" distinction in one sentence; confirm the AI-use disclosure question with ICETC before upload.

## Readiness classification
**READY AFTER AUTHOR CONFIRMATION** (with venue verification outstanding for ICETC's AI-disclosure and prior-submission rules). Not classed "ready for submission" because the author-confirmation items are unresolved.
