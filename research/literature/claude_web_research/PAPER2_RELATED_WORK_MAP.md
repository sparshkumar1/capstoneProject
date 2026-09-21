# Paper 2 related-work map (planning only)

| Subsection | Strongest sources | What each contributes | How our work differs | Suggested placement | Do NOT claim |
|---|---|---|---|---|---|
| A. Automatic short-answer grading | CARRY: Mohler 2011, SemEval-2013 Task 7, Sung 2019, Camus 2020, surveys; [17] Schleifer 2026; CARRY Ferreira Mello 2025 | Task history; transformer and LLM graders; mid-range degradation | Technical interview answers; similarity-composite scorer; exploratory human comparison | II-A | Superiority over other graders; human-level grading |
| B. Semantic/embedding/NLI/cross-encoder scoring | CARRY: SBERT, SemEval-2013 (entailment framing) | Standard components | The specific S1/S2/R weighting and provenance-limited CrossEncoder | II-B | That the composite formulation is new; upstream CrossEncoder training data (unknown) |
| C. Bias and surface-form sensitivity of automatic evaluators | [15] EACL 2026 code-judge biases; [20] MT-Bench; [21] CALM; [16] Reliability without Validity; CARRY LC-AlpacaEval | Named biases; evidence that verbosity effects can be small for some modern judges | Concise/paraphrase/verbose diagnostic on technical answers | II-C | That length/surface bias is new; that our bias generalises beyond this scorer |
| D. Gaming and adversarial robustness of graders | [22], [23], [24]; CARRY Filighera 2024, Raina 2024 | Attacks and defences for graders | Concept-stuffing and perturbation tests on this scorer | II-D | New attack class |
| E. Metamorphic and behavioural testing | [18] LLM metamorphic testing; [8] ReliabilityBench; CARRY CheckList | Methodology and relations catalogue | Applied to a technical-answer scorer | II-E | New testing method |
| F. Measurement validity and agreement | [25] Williamson 2012; [19] agreement synthesis; [16] | Agreement, association with independent measures, generalizability | Human-human ICC gate; cluster-bootstrap CI; weak model-human rho | II-F / Section III | Validity beyond the exploratory benchmark; excuse for weak rho using a non-comparable range |

Gaps: read ASAG-in-technical-domain literature (programming/CS ASAG, CARRY P2-23/24); verify Baldwin authors and text; check whether a quotable defintion of "measurement invariance" applies before using the term (not searched in depth).

## Gap-closure additions (2026-09-21)
- Bias and robustness subsection: score-range bias [48] and position bias [49] as adjacent, non-applicable dimensions for a pointwise scorer; verbosity and style effects vary by judge [16], [50]; synonym and semantic-alignment effects in short-answer graders [53], [52]; hybrid symbolic + LLM graders [51]; shared-task context [57].
- Keep the framing exploratory and diagnostic; no formulation novelty.
