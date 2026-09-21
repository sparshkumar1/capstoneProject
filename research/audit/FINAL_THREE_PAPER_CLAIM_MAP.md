# PREPAIred — Final Three-Paper Claim Map (2026-09-20)

Sources: `research/claims/CLAIM_REGISTRY.csv`, `research/literature/SECOND_PASS_CLAIM_AUDIT.md`, `FINAL_RESEARCH_POSITIONING.md`, `research/evidence/PAPER{1,3}_EVIDENCE_PACKAGE.md`, `PAPER2_X2C_PROTOCOL_PACKAGE.md`. No score or ranking is used. "Closest prior work" means what the searches conducted found closest, not that nothing else exists. Working titles/themes are **candidates**, not decisions.

## Paper 1 — systems / dependability (framing open between systems-centered and measurement-design)
| Field | Content |
|---|---|
| 1 Working research question | Which containment and authority-separation properties of an LLM-assisted technical-assessment pipeline can be demonstrated by controlled tests that are able to fail, and how does the pipeline behave when components fail? |
| 2 Candidate title/theme | "Testing containment and authority separation in an LLM-assisted technical-assessment prototype" (theme: evaluation design); alternative systems framing if only X1-D evidence exists |
| 3 Contribution type | Systems + diagnostic (methodological if X1-C/B are run) |
| 4 Closest prior work | SandboxEval (2025 preprint; uncontained comparison, outcome-based tests); APAC (2015; Docker grader); CaMeL (2025 preprint) and Cai 2026 / Li 2026 / Sahoo 2026 (LLM-as-scorer attacks); PolyInterview / Conversate (interview-practice systems) |
| 5 Evidence we have | X1D-C001…C003 (226 tests, 1 known failure; warm evaluator latency; SQLite latency); P1-C001/C002/C003; P1-C009 design-only |
| 6 Evidence we still need | X1-C run with weakened-configuration control; X1-B1/B2 with channel enumeration; X1-A on retained claims; registered protocols; audited `run_manifest_v2`; decision on the known failing test |
| 7 Strongest allowed claim (today) | "The build has a 226-test suite with one known failure; warm evaluator latency (in-process) was median 236 ms; four of nine attack outcomes discriminated; the sandbox configuration's effectiveness has not been measured." |
| 8 Prohibited claim | secure / isolated / contained / fault-tolerant; LLM cannot alter scoring; sub-second end-to-end; prompt-injection-proof; new Docker grader; new interview-practice system; "negative controls are new" |
| 9 Key limitation | No X1-A/B/C evidence; unlocked SUT environment; single machine |
| 10 Cross-paper overlap risk | High for system description (shared); moderate for adversarial vocabulary with Paper 2 |
| 11 Readiness | **Evidence-building** (not manuscript-ready) |

## Paper 2 — validity and robustness of technical-answer evaluation (diagnostic identity)
| Field | Content |
|---|---|
| 1 | How well does a composite technical-answer evaluator agree with blinded human consensus, how does it compare with simple baselines including length, and which answer types does it mis-score? |
| 2 | "What a composite technical-answer evaluator measures: agreement, length dependence and under-scored concise answers" (candidate diagnostic theme) |
| 3 | Diagnostic / negative-result (exploratory now; benchmark contribution only if X2-C is completed) |
| 4 | Mohler 2009/2011; Ormerod 2023; Condor & Pardos 2024; Filighera 2020/2024; Dubois 2024, Zheng 2023, Ye 2025 (LLM judges); Riordan et al. 2017 (search-level) |
| 5 | Composite ρ 0.3812 (case CI [0.1575, 0.5774]; two-level [0.1529, 0.6490]); R-only 0.4832; S1+R 0.4884; composite − R-only −0.102 [−0.2849, 0.1174]; ICC(2,1) 0.9528; metamorphic 19/21; adversarial 11/13 (author-set ceilings); X2B-C003 length-only ρ 0.4897 (exploratory); residual-vs-length ρ −0.3077; under-scoring of concise-correct/paraphrase |
| 6 | X2-C confirmatory benchmark (institutional/ethics gate; independent authoring; ≥3 crossed blind raters; length crossed with correctness); literature on paraphrase testing, clustering in ASAG, technical-interview benchmarks (P2-4…P2-8 open) |
| 7 | "On an exploratory, author-constructed 64-answer benchmark, agreement between the composite and three-rater consensus was ρ = 0.3812 (wide interval), lower than the cross-encoder alone, and a length-only baseline matched or exceeded the learned cross-encoder." |
| 8 | validated/accurate/reliable evaluator; improves over R-only; robust to attacks; length-bias free; off-the-shelf CrossEncoder; expert/independent/committee raters; ρ 0.6975 as current; comparison with Mohler/SemEval scores; fairness; real-learner claims |
| 9 | Author-constructed benchmark (length may be a construction artifact); small N (8 questions); provenance/ethics records incomplete |
| 10 | Moderate: evaluator description shared with Paper 1 |
| 11 | **Evidence-building** (exploratory results exist; confirmatory study not started) |

## Paper 3 — learned adaptive difficulty control vs matched simpler policies (analytical / negative-equivalence identity)
| Field | Content |
|---|---|
| 1 | Under an identical rule-based guardrail layer, what does a learned PPO difficulty controller add over simpler policies, in simulation? |
| 2 | "What a learned difficulty controller adds beyond a constraint layer: a persona-level matched-control evaluation in simulation" (candidate) |
| 3 | Analytical / empirical negative-equivalence result; methodological (matched controls) |
| 4 | Axak 2025 (PPO vs rule-based tutor, single fixed seed in the text read); Ion 2025 (simulated coding interviews; extended abstract); Olukola 2026 (constraint layers; preprints); Carr 2023 / Alshiekh 2018 (shielding; shielded-random reference); Riedmann 2025 (review; non-adaptive controls in 14/89) |
| 5 | X3A-C001…C007; P3-C001…C009, C016…C024 (registered Δ −0.0350 [−0.0818, +0.0021], Equivalent ±0.12; PPO more volatile; PPO uses state; heuristic/controller comparisons; rule ablation) |
| 6 | O7 robustness (specified and implemented; **not run** — independent code review and registration pending); literature on equivalence margins and RL-evaluation methodology; simulator validity (unavailable in this study) |
| 7 | "Under identical guardrails, the learned policy's tracking error was equivalent, within a pre-registered ±0.12 margin, to a state-blind constant action, and its volatility was higher (simulation only)." |
| 8 | PPO improves tracking / is superior / lowers volatility; guardrails eliminate boundary violations or are a formal shield; real-interview or deployment evidence; speech/multimodal robustness; human learning improvement; novel/first |
| 9 | Simulation only; trained against a single default candidate; unseeded candidate noise; guardrails in the training loop; seed population hypothetical; MAE ignores path shape |
| 10 | Low–moderate (simulator and policy owned by Paper 3; system description shared) |
| 11 | **Evidence-building** — the registered primary result is complete; O7 robustness and a literature justification for the equivalence margin are pending. It is the closest of the three to manuscript-ready (the earlier audit's "early draft ready" is not upgraded here) |

## Cross-paper program
The three papers share one prototype but are separated by *measured property*: P1 owns containment/authority separation/latency, P2 owns evaluator agreement and diagnostics, P3 owns the simulated controller comparison. The umbrella "reliable adaptive technical assessment" is **not supported as a claim**; "empirical evaluation of reliability properties of a prototype" is supportable as a research question. Consolidating P2 and P3 into one paper and a separate reproducibility/process paper remain open options (see `ALTERNATIVE_PAPER_POSITIONING.md` §7). No paper is submission-ready.
