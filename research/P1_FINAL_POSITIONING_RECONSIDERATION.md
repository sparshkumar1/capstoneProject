# P1 — final positioning reconsideration (independent audit, 2026-09-21)

**Status: REASONING ONLY.** Nothing was modified, run, committed, pushed or tagged; this is the only file created. Every fact below comes from reading repository files or stored results in this pass; nothing was executed. Where a claim rests on a document that the repository itself marks superseded, it is labelled as such. The two earlier files (`research/FINAL_P1_SCIENTIFIC_POSITIONING.md`, `research/P1_REPAIR_AND_FOLLOWUP_PROTOCOL.md`) are treated as hypotheses. No venue, fee, deadline or acceptance question is discussed.

**What was read in this pass (beyond the two earlier files):** `docs/ARCHITECTURE.md` (design principles), `docs/FALLBACK_REMOVAL.md`, `docs/PROJECT_STATE.md`, `README.md` (top), the archived `docs/STAGE22_1_FINAL_LIVE_SYSTEM_CHECK.md`, module headers of `services/storage/best_answer.py`, `agents/timing/timer.py`, `agents/validation/score_validator.py`, the Qwen feedback validator in `services/qwen/app.py`, the outage and follow-up tests in `tests/integration/test_multiagent_responsibility_and_failures.py` (working tree and the `release/app-repair/v1` version), the size of every component (line counts), `launch.py`, the P1 manuscript layers, `system_paper/SYSTEM_PAPER_{IMPLEMENTATION_STATE,RESEARCH_DECISION}.md`, `cross/FINAL_PUBLICATION_MAP.md`, `research/literature/{FINAL_RESEARCH_POSITIONING,LITERATURE_NOVELTY_MASTER_MATRIX}.md`.

---

## 1. What the team actually built

**Scale (line counts and file counts, read from the tree; not a quality measure).** About 10,000 lines of production Python (`agents/` 5,655, `services/` 2,457, `apps/backend` 1,215, `rl/` 720), about 5,000 lines of React/JavaScript in 37 files (`apps/web/src`), about 3,900 lines of scripts, 24 test files with 264 test functions (7,347 lines), five Dockerfiles, a `docker-compose.yml`, and a single launcher (`launch.py`) that starts the evaluator (port 5000), model service (8001), backend (8000) and front end (5173). 59 commits between 2026-04-13 and 2026-09-20. A full-suite result is recorded in `X1_OLD_VS_NEW_SUMMARY.md` (283 passed, one known failure, run before the X1 campaigns); it was not re-run here.

**The system.** A local-first, audio-and-text technical-interview practice system for C and data structures. A candidate answers by speech (server-side speech-to-text is authoritative; the browser's preview text is explicitly non-authoritative, `apps/backend/main.py:885-918`) or writes C code in a Monaco editor. An orchestrator (`interview_orchestrator.py`, 2,299 lines) holds session state and drives: question selection with three-level de-duplication; a composite answer evaluator (0.15·S1 + 0.35·S2_eff + 0.50·R, with S2 dampened when R ≤ 0.30); a Docker C sandbox; a local 1.5B language model (llama.cpp GGUF) that writes narrative feedback and follow-up questions, with a deterministic non-LLM recovery path; a timing modifier; a warm-up plus PPO-and-guardrail difficulty controller; SQLite persistence with rule-based best-answer selection; and a report. It is **audio + text, not multimodal** (no video path exists); the README's "multimodal" and its numbers are superseded (`CLAUDE.md`).

| Layer | Existing technology used | What the team designed or integrated | Research significance | Evidence status |
|---|---|---|---|---|
| Web UI, WebSocket lifecycle, report | React, Vite, Monaco, FastAPI | session flow, live feedback display, report | none by itself | no usability data |
| Orchestrator | Python `asyncio` | queue, retry and rollback semantics, follow-up policy, fail-closed outage state, `decision_source`/`llm_status` labels on every decision, attempt persistence | **carries the authority design** (below) | X1-A, X1-B-I, unit and integration tests |
| Answer evaluator | MiniLM, FAISS, a partially fine-tuned CrossEncoder (provenance incomplete) | the composite, the dampening rule, 125 rubrics (100 indexed) | belongs to the held Paper 2 | exploratory only (ρ 0.3812, 64 constructed answers) |
| Model service | Qwen2.5-1.5B GGUF, llama.cpp | prompts, JSON schema, **validators that reject narratives contradicting the evaluator's structured facts or leaking a score** (`services/qwen/app.py:575-597`), template recovery | design of a *non-authoritative* model role | X1-B-I (feedback channel only) |
| Code sandbox | Docker, gcc, Alpine | flag set, pre-flight filter, container naming and cleanup | scoped containment evidence | X1-C, X1-A FLT-06 |
| Speech and confidence | WhisperX/faster-whisper | prosody features, hand-designed confidence blend | none validated | none; only the confidence number reaches adaptation |
| Difficulty control | Stable-Baselines3 PPO | environment, guardrails, warm-up, deployment | Paper 3 | simulation only; deployed checkpoint differs from the evaluated one |
| Storage and best-answer rules | SQLite | pure functions for eligibility and ranking (`best_answer.py`), fail-closed classification | design rule, tested by unit tests | unit tests; persistence not in the X1 campaigns |
| Timing and validation | — | timing modifier with "technical correctness dominance" (`timer.py`), score validator | design rule | unit tests |

### The design idea that the repository states, in its own words
This is what earlier positioning missed. The documentation and code state a coherent design position:
- **Authority dominance:** the neural evaluator "serves as the uncompromised ground truth" and timing "modifies the final score without" replacing it (`ARCHITECTURE.md` principle 2); `timer.py` ("Strict Decoupling: Raw authoritative Stage 1 evaluator scores are preserved verbatim"); `best_answer.py` (recency, feedback text, confidence signals, Qwen output and retry order "can never make an incorrect attempt eligible"); the STT rule that only server transcripts are authoritative.
- **Provenance labels:** every runtime decision records its `decision_source` and `llm_status`/`rl_status` (principle 3).
- **Fail-closed, anti-fabrication:** `FALLBACK_REMOVAL.md` describes an audit (Stages 8–12) that removed mock and heuristic fallbacks presented as intelligence; principle 4 promises degradation "without fabricating data or mislabeling".
- **Containment:** the sandbox is "the authoritative security and isolation boundary" (`sandbox_policy.py`).

P1 tests these commitments. The manuscript calls them "design intentions" in one sentence and does not say where they come from.

**Two facts from the repository that make this more than framing:**
1. The baseline **violated the stated design in three places**, found only by the campaigns: an evaluator outage stored as a 0.0 attempt (FLT-03); feedback labelled `llm_status = available` when the template was served (78 of 144 arms); a compiler timeout leaving a container running. The documentation had already claimed the anti-mislabelling and anti-fabrication audit was done.
2. **The test suite had encoded the defect.** On `release/app-repair/v1` the test named `test_evaluator_failure_produces_structured_failure_without_fabrication` asserted `final_score == 0.0` (docstring: "explicit evaluator_unavailable state with score 0.0"); on build B it asserts a null score, an infrastructure flag and no stored score. A test named `test_followup_agent_cannot_alter_authoritative_evaluator_score` asserts only that an already-recorded 0.65 is unchanged after a follow-up is injected; it does not touch the path through which the follow-up question text becomes the reference for scoring the next answer (see the repair protocol, Part 2). So unit tests, an audit document and design text all asserted properties that hostile-condition testing did not confirm.

### Separation A–G
| | Content | Honest status |
|---|---|---|
| **A. Original system/architecture contribution** | An authority-separated design for an LLM-assisted assessment pipeline (model text non-authoritative, evaluator and validators authoritative, fail-closed states, provenance labels) applied throughout one implemented system | A design *position* with consistent implementation. The pattern itself (separating model output from privileged actions) is established and the manuscript already cites it [11]; the application to this pipeline is the team's. No architectural novelty is claimed |
| **B. Integration/engineering** | Ten-plus components made to run together, locally, on CPU, with a launcher, containers, persistence and a UI | Substantial and real; largely established components |
| **C. Research methodology** | Property → oracle → weakened control → layer attribution; baseline-versus-repaired comparison; pre-tagged protocols | Established practice components applied with discipline; not a new method |
| **D. Empirical findings** | Two defects; status strings non-discriminating for five attacks; filter-attributed ptrace outcome; invariance 72/72 (by construction, see prior audit §9.6); the design-versus-behaviour gap above | Modest, specific, well documented; single system |
| **E. Validation/evaluation** | X1-A, X1-B-I, X1-C on build B; independent methodology review by record only | Scoped to component boundaries; **not an end-to-end evaluation** (below) |
| **F. Demonstration value** | A working integrated system exists, and it is the real orchestrator, executor and model in the tests | Establishes realism of the system under test; not evidence of effectiveness |
| **G. Not scientifically supportable** | multimodal; adaptive-difficulty benefit; validated confidence score; evaluator validity; usability; latency acceptability; "end-to-end evaluated" | see §5 and §8 |

**Integration level of the X1 evidence (this bounds every position).** X1-C ran the real Docker executor. X1-B-I ran the real orchestrator and the real Qwen model with a **fixed evaluator stub**. X1-A ran the real orchestrator with **injected** exceptions and a local model stub. No X1 campaign ran speech, the real evaluator and the model and the sandbox together in one session, and FLT-08/09 (WebSocket, audio) were not run. The repository's integration tests use the evaluator's mock mode (`EVALUATOR_MOCK_MODE=1` in `CLAUDE.md`). The only real full-session record found is a superseded, archived note (2026-08-17: one three-turn verbal-plus-coding-plus-report run; live microphone "not verified").

---

## 2. The three positions compared

### Position A — system / architecture paper
**Scientific contribution it would have:** the authority-separated design and a description of an integrated system.
**What the architecture contributes:** a worked instance of a known separation pattern in an interview-practice setting, with explicit fail-closed and provenance rules.
**What the demonstration contributes:** existence and feasibility of the integration on a workstation.
**Is the evidence sufficient?** No. The repository holds no evidence about the system's purpose: no user data, no usability, no effectiveness, no comparison with an alternative system. Each adaptive or measurement component is weakly evidenced (evaluator ρ 0.3812 exploratory and below simpler components; confidence not validated; PPO equivalent to a constant policy in simulation, `P3`; the deployed checkpoint has no evaluation of its own). An honest system paper must say all of that in its own component table. The one part with research-grade evidence is exactly what P1 already tests.
**Novelty actually present:** the project's own literature pass records the whole combination as "combines previously studied components; the system itself is not a contribution" (`LITERATURE_NOVELTY_MASTER_MATRIX.md` H9; closest work: Conversate, PolyInterview, APAC; Kadam 2026 already reports adaptive mock-interview tutoring). That was a first-pass, partly-read scoping statement, not a proof, but nothing in the repository contradicts it.
**Reviewer would demand:** a user study or at least a comparison; ablations; latency and scalability numbers (documents disagree: README 1.8–2.9 s per task, archived note 155–193 s on CPU, X1 measurement 19–30 s for feedback); validation of the evaluator and the confidence score; a related-work section on interview-practice systems (the current reference list has none).
**Strongest objection:** "an integration of existing components, with no evidence it works for its purpose."
**What A undersells:** the specific design commitments and the fact that they were tested and found partly violated.
**What A oversells:** everything the repository cannot evidence.

### Position B — empirical dependability evaluation (the earlier conclusion)
**Contribution:** experimental evidence on three integrity properties under adverse conditions; defects found and repaired; oracle observations.
**Strength of the campaigns:** contained but real: controls flip outcomes; two genuine defects; the harness demonstrably can fail. Weaknesses are recorded (author-written attacks, same-agent, one environment, SEC-09 flaw, follow-up path untested).
**Importance of the defects:** a silent 0.0 stored as a result is a real integrity defect in an assessment pipeline; the orphan container is a resource-leak defect.
**Does the system become a test instrument?** Yes, and that is the position's specific weakness. Three problems follow. (i) **No population definition:** the abstract speaks of "an LLM-assisted technical-assessment pipeline" but the evidence is one bespoke system; the reader cannot judge representativeness because the system is described in about 270 of 3,990 words (about 7%) and has no figure. (ii) **The three properties appear arbitrary** unless one knows they are the system's own design commitments. (iii) **Generic vocabulary** ("dependability") invites reviewers to expect the breadth of the dependability literature (reliability, availability, recovery) that three narrow properties cannot meet.
**Reviewer objections:** author-controlled evidence, nine programs, one environment, by-construction passes, the untested path.
**Evidence requirements:** as in the earlier audit (SEC-09 supplement, follow-up channel, second-machine run).
**What B undersells:** the system as the source of the hypotheses; the design-versus-behaviour gap; the scale of what was tested; why these properties.

### Position C — system plus scoped empirical evaluation
**Core idea:** present the implemented system and its stated integrity design, then test whether the implementation honours that design in a scoped way.
**Do the two contributions reinforce each other?** Yes, and this is the strongest point in favour of C: the system supplies the *claims* (authority dominance, fail-closed, provenance, containment), the evaluation supplies *evidence about them*, and the repair record shows the two co-evolved (four code changes and four adapted tests after the campaigns). A reader can then ask a precise question: which of the system's stated properties held, which held only after repair, which are untested?
**Does the paper become too broad?** It would, if the system section grew to cover audio, PPO, the evaluator's validity or the UI. The section must be limited to what defines the tested boundaries and must label every other component with its evidence status in one table.
**System as artifact, evaluation as contribution?** Yes: the evaluation carries the scientific content because the evidence is there; the architecture is a secondary, modest contribution and the frame that gives the tests meaning.
**Would reviewers see a system paper with a weak evaluation, or an evaluation paper with unnecessary engineering?** Either, if the boundaries above are not stated. Prevention: (a) state in the first paragraph that the paper evaluates integrity properties only and makes no effectiveness, usability, latency or end-to-end claim; (b) derive the tests explicitly from stated design commitments; (c) cap the system section; (d) report per commitment: held in scope / failed on baseline and repaired / untested (including the follow-up path as a *known exception* to the authority commitment).
**Reviewer objections and answers:** see §7.

---

## 3. Guard against favouring a label

The earlier identity ("dependability") sounded rigorous and was chosen partly for that reason; it is a sound *method* label and an incomplete *object* label. The system paper sounds substantial and would fail for lack of evidence. The choice below rests on one test applied to each: what would a reader be entitled to conclude from the evidence in the repository? For A: almost nothing about the system's purpose. For B: something about three properties, without knowing what system they concern. For C: what the system's designers committed to, and what a scoped test showed about those commitments.

---

## 4. The central questions

**What is the actual intellectual contribution?** A stated design position for LLM-assisted assessment (the model narrates, the evaluator decides, failures are flagged not scored, code runs contained, every decision is labelled) implemented across a working system, and evidence about how far that position held under adverse conditions, including where the documentation, the tests and the behaviour disagreed. The position is an application of established ideas; the intellectual value is in the specific testing of it and the discrepancy findings.

**What is the actual engineering contribution?** An integrated, locally deployable system of roughly 10k lines of production Python and 5k lines of front end, with containerised execution, persistence, fail-closed handling, a launcher and a test suite. Real and substantial; established components; not by itself a research contribution.

**What is the actual empirical/scientific contribution?** The scoped campaigns X1-C, X1-A and X1-B-I: containment of nine programs with controls; two defects found and repaired; five cases where the system's status signal did not identify the outcome; the filter-attributed ptrace result; invariance for one channel; the design-versus-behaviour discrepancies. Modest, honest, single-system.

**Can these form ONE coherent paper?** Yes, in one way: the system is the object and source of hypotheses, the evaluation is the contribution. They cannot form a coherent paper if the system is presented as the contribution (evidence absent) or omitted from view (the tests lose their object). The system's audio, RL and evaluator-validity parts must be present only as status-labelled context.

---

## 5. Working-demonstration test

| Question | Answer |
|---|---|
| What does the demo prove? | that the components run together as one system with real services (author-attested; not run here) and that the tests exercised the real orchestrator, executor and model rather than mocks in their targeted paths |
| What does it not prove? | correctness of scoring, usefulness, usability, acceptable latency, the audio path (X1 did not run it), any end-to-end property, or any property of the demo's specific runs; the repository's only full-session record is superseded and archived |
| Is integration itself a contribution? | An engineering one, and a *precondition* for the research questions (the authority questions exist only in an integrated system) |
| Central or artifact? | **Artifact and object of study**, with a substantial, honest description; not the source of scientific claims |
| Does the current manuscript give it enough weight? | No: about 270 words, no architecture figure, no component-status table, no statement that the tested properties are the system's own design commitments |
| Caution | "Working demo" is not evidence for "end-to-end evaluated". A claim of end-to-end testing would be false for X1. If the demo is meant to carry weight, a scripted, hashed, replayable session record (descriptive, no result claims) would be needed; none exists in the current evidence base (recommendation only) |

---

## 6. Contribution-balance test

| Position | Reviewer impression the evidence supports | Why |
|---|---|---|
| A | **#1: mostly an engineering project with insufficient research** | no evidence about purpose or quality; components mostly established; own literature pass says the combination is not a contribution |
| B | **#2 in part: a research evaluation that ignores the system it evaluates**, plus a residual #1 ("a test of a home-made system") | the system is 7% of the text; the object and its design claims are missing, so representativeness and motivation are unanswerable |
| C | **#3 conditionally: a system contribution supported by a meaningful, scoped evaluation**; degrades to #1 if the system section grows, to #2 if the design claims are not stated | the evidence supports exactly this shape and no larger one; it is not a forced outcome |

---

## 7. Reviewer simulation

**A.**
| Reviewer | Reject because | Already answered by | Unanswered |
|---|---|---|---|
| Systems/SE | integration of known parts, no comparison | none | comparison, scalability, deployment evidence |
| AI/LLM systems | no evidence the LLM, evaluator or controller add value | P3 equivalence (unfavourable), P2 exploratory (weak) | all of it |
| Security/dependability | no threat model, no tests | X1 (but off-topic for A) | unless X1 is added, everything |
| Testing/evaluation | no evaluation | X1 | end-to-end evaluation |

**B.**
| Reviewer | Reject because | Already answered by | Unanswered |
|---|---|---|---|
| Systems/SE | one bespoke system, three narrow properties, same-agent | disclosure, baseline failures, controls | representativeness; why these properties |
| AI/LLM systems | injections aimed at a role the model lacks; the real path untested | static and mutation controls; documented dependency | follow-up channel (protocol part 3) |
| Security/dependability | nine programs, filter not container, author-written | control flips, layer attribution | adaptive attackers, kernel-level, independence |
| Testing | oracle circularity, SEC-09 confound, small suite | most disclosed | SEC-09 repair (protocol part 1) |

**C.**
| Reviewer | Reject because | Already answered by | Unanswered |
|---|---|---|---|
| Systems/SE | "system paper without an effectiveness or scale evaluation" | the paper states up front that it claims integrity only; scoped table of what is not evaluated | if a venue expects effectiveness evidence, this stays unanswered and is a limitation of scope, not a repairable gap |
| AI/LLM systems | "the authority commitment has a known exception you did not test" | documented dependency; repair protocol offers a test or a narrowed claim | the follow-up path until run or narrowed |
| Security/dependability | "not a security evaluation" | the paper says so; scoped criteria | adaptive attackers |
| Testing/evaluation | "same-agent, one environment, author-written" | disclosure; baseline failures; controls; the tests-encoded-the-defect finding | independent execution (protocol step 8) |

---

## 8. Novelty audit

| Kind | Present? | Basis |
|---|---|---|
| Architectural novelty | **No claim.** A consistent application of an established separation pattern [11] and of standard fail-closed practice | the manuscript's own citation; literature matrix H9 |
| Integration novelty | **Not established.** Integrating STT, neural grading, a local LLM, a sandbox and an RL controller in one traceable system is engineering; close prior interview-practice systems exist (as recorded in the literature matrix, partly read) | H9 |
| Methodological novelty | **Not claimed**; established practices combined (fixed programs, host observables, weakened controls, fault injection, mutation control). The literature hypothesis H1 (weakened-configuration controls with a multi-layer oracle "differs from" prior sandbox work) was not fully verified | H1 |
| Evaluation novelty | Minimal | |
| Empirical findings | **Yes, modest and specific** to one system: defects, oracle observations, invariance | X1 record |
| Engineering novelty | Substantial engineering; "novel" is not the right word | §1 |
| Combination | The only honest combined claim: *a system whose stated integrity design was tested, with the design-versus-behaviour discrepancies reported* | §1 facts 1–2 |

The design-versus-behaviour observation deserves care: it is three instances in one system, documented by repository evidence. It supports a lesson ("unit tests and an audit document asserted properties that adverse-condition tests did not confirm"), not a general claim about LLM systems.

---

## 9. Conceptual structure for each identity (no rewrite)

| Section | A: system | B: dependability | C: system + scoped evaluation |
|---|---|---|---|
| Introduction | problem of interview practice; the system | risk that recorded results are wrong | the system's integrity design; what is and is not evaluated |
| Related work | interview and grading systems (absent today) | sandbox, fault injection, grader injection | both, kept short; adds system-level work |
| System | central: all components | supporting paragraph | **bounded**: architecture figure, design commitments as testable claims, one component-status table |
| RQ | how it is built and whether it works | which properties can be demonstrated | which stated commitments hold under adverse conditions |
| Methodology | design and implementation | tests, oracles, controls | as B, derived from the commitments |
| Experiments | user study needed (absent) | X1 | X1 (+ supplements) |
| Results | effectiveness (absent) | per campaign | **per commitment**: held in scope / failed on baseline, repaired / untested |
| Discussion | design lessons | oracle and defect findings | design-versus-behaviour gaps; what the tests cannot show |
| Limitations | large (everything unevaluated) | scoped | scoped plus explicit non-claims |
| Conclusion | the system | scoped observations | scoped observations on the design |

Central versus supporting: in A the system is central and the evidence is missing; in B the tests are central and the object is thin; in C the commitments-and-tests pair is central, the system description supporting.

---

## 10. Multi-venue stability

The stable core must survive changes of emphasis without changing a claim.
- **A** is the least stable: its acceptability depends on evaluation norms that this evidence cannot meet in any community that expects user or effectiveness evidence, and its claims would have to grow with each audience.
- **B** is stable in content but narrow, and its unlabelled object makes each new audience re-ask "what is this system".
- **C** is the most stable: the claims (commitments, tests, findings, limits) do not change; only the emphasis moves (system description versus test evidence versus integrity motivation). Its fixed core is the claim-and-evidence table; its adaptable layers are the amount of system description, the vocabulary and the related-work balance.

Precondition: the system section is capped and the "no effectiveness or end-to-end claim" statement is constant across presentations.

---

## 11. Challenging the assumptions

| # | Assumption | Verdict | Evidence |
|---|---|---|---|
| 1 | "P1 is fundamentally a dependability paper." | **PARTIALLY SUPPORTED** | The methods and outcome types are dependability-style and the manuscript itself says "closer to dependability testing … than to a security evaluation". But the object and the hypotheses come from the system's stated design commitments (`ARCHITECTURE.md`, `best_answer.py`, `FALLBACK_REMOVAL.md`); "dependability" is the right method label and an incomplete identity, and it promises a breadth the three properties do not have |
| 2 | "The system is merely an experimental artifact." | **PARTIALLY SUPPORTED** | Scientifically the system's quality is not what is evidenced, so it is not the contribution. But it is the source of the tested claims, the population the results refer to, and it changed in response to the tests (four code changes; four test files adapted; a test that had asserted the defect). The archived manuscript literally says it "treats the pipeline as the experimental vehicle"; that understates its role |
| 3 | "A working end-to-end system is not important to the paper." | **NOT SUPPORTED as stated; a qualification applies** | The working system is what makes the tests about a real orchestrator, executor and model. What is not supported is any claim that the *end-to-end* system was evaluated: X1 used stubs and injected faults and did not run speech, or the full path together |
| 4 | "The evaluation is necessarily more scientifically important than the system." | **PARTIALLY SUPPORTED** | With the evidence in the repository, only the evaluation is research-grade. "Necessarily" fails: the design commitments give it meaning, and for readers who judge systems the description is required |
| 5 | "The best paper must choose either system OR evaluation." | **NOT SUPPORTED** | The evidence supports a system-as-object, evaluation-as-contribution paper (Position C), provided one of them is explicitly primary |

---

## 12. Decision

**C. SYSTEM + SCOPED EMPIRICAL EVALUATION**, with the evaluation primary and the system secondary.

- **PRIMARY IDENTITY:** a scoped empirical test of the integrity design (authority dominance, containment, fail-closed failure handling) of one implemented LLM-assisted technical-assessment system.
- **SECONDARY CONTRIBUTION:** the system and its stated design commitments, described to the extent needed to define the tests, with the record of design-versus-behaviour discrepancies found and repaired.

This changes the earlier conclusion in emphasis and in structure. "Dependability" stays as the discipline of the methods; it is no longer the identity of the paper. The earlier unifying question (whether a recorded result reflects the candidate's work) stays as the motivation and is now anchored in the system's own stated rule that the evaluator, not model text, decides.

---

## 13. Recommendations only (nothing was changed)

Consequences for what should be tested or produced if this positioning is adopted:
1. **Design-commitment traceability table** (documentation, no experiment): each commitment stated in `ARCHITECTURE.md`, `best_answer.py`, `timer.py`, `FALLBACK_REMOVAL.md` mapped to the X1 result, a unit test, or "untested". It is the natural results structure for C.
2. **Follow-up channel becomes more important**, not less: it is the one documented exception to the authority commitment. Either run the exposure test in `P1_REPAIR_AND_FOLLOWUP_PROTOCOL.md` or state the exception explicitly as an untested dependency; the protocol's outcome tree already covers both.
3. **SEC-09 supplement:** unchanged in priority.
4. **The system description** should not be expanded to cover audio, PPO or evaluator validity; those appear only in a status table with their evidence level.
5. **Related work:** a short system-level paragraph would be needed (interview-practice and automated-assessment systems); the project's literature matrix marks this as an open, unverified category (open question 5), so nothing can be cited from it without verification.
6. **Third paper:** the publication map reserves a separate "end-to-end system" paper with a human pilot. Under C, P1 owns *architecture and integrity evidence* and the third paper owns *human-facing claims* (feasibility, usability, exploratory outcomes) and should cite P1 for the architecture rather than re-describe it. The overlap audit (`cross/THREE_PAPER_OVERLAP_AUDIT.md`) and the publication map would then need a boundary sentence; that is a decision for you and is not made here.
7. **Wording to avoid under C:** "end-to-end evaluation", "multimodal", any effectiveness or latency claim, and any implication that the audio or RL components were tested.

---

### P1 — ACTUAL PROJECT CONTRIBUTION

The team built and integrated a substantial, locally deployable, audio-and-text technical-interview practice system (about 10,000 lines of production Python, about 5,000 lines of front end, ten-plus components, containers, persistence, a launcher and 264 test functions) around an explicit design position: the evaluator and validators are authoritative, model-written text is not, failures are flagged and not scored, code runs contained, and every decision is labelled with its source. The project then tested that position under adverse conditions and repaired what failed. The combination of a coherent system design and a scoped test of it is the project's actual contribution; the system alone is engineering with weakly evidenced components, and the tests alone lose their object.

### P1 — ACTUAL SCIENTIFIC CONTRIBUTION

Scoped empirical evidence, in one system and one environment, about whether the stated integrity design held: containment of nine specified programs with weakened controls; two defects found by fault injection and repaired (an outage stored as a 0.0 result; a timed-out compiler container left running); five cases where the system's own status signal did not identify the outcome; a ptrace result that belongs to an application filter and not to the container; and invariance of 14 score-bearing observables to model-written feedback in 72/72 valid pairs (by construction, with the follow-up channel untested). Plus the documented discrepancy between design text, unit tests and behaviour. It is modest, honest and specific.

### P1 — ACTUAL ENGINEERING CONTRIBUTION

A working end-to-end pipeline and application built from established components: React/Monaco front end, FastAPI backend with WebSocket lifecycle, a 2,299-line orchestrator with retry, rollback, follow-up policy, fail-closed states and provenance labels, a composite evaluator service, a local quantised language model service with validators against the evaluator's facts, a Docker C sandbox with pre-flight filtering and cleanup, SQLite persistence with rule-based best-answer selection, a timing modifier, a PPO-and-guardrail controller and a launcher. The engineering is substantial and real; it is not a novelty claim, and its integrated behaviour was tested only at component boundaries.

### SYSTEM POSITIONING

Presented as the contribution, the system cannot be defended with the evidence in the repository: there are no user data, no effectiveness or usability results, no comparison, weakly evidenced adaptive and measurement components (evaluator ρ 0.3812 exploratory; confidence unvalidated; PPO equivalent to a constant policy in simulation; deployed checkpoint unevaluated), documents that disagree on latency, a superseded README that says "multimodal", and a prior literature pass that records the combination as a combination of studied components. The likely reviewer conclusion is "engineering project with insufficient research". The system is nevertheless essential as the object, the source of the tested claims and the definition of what the results refer to, and it is under-described at about 7% of the current text.

### DEPENDABILITY POSITIONING

Presented as a generic dependability evaluation, the paper keeps its strongest evidence (defects, oracle observations, controls) and the right methods, but it loses its object. The reader cannot tell why these three properties, what system they concern, or whether the system is representative, and the label implies a breadth of reliability and availability evidence that three narrow properties do not provide. The likely reviewer conclusion is "a research evaluation of a home-made system that ignores the system". It is the right method identity and an incomplete paper identity.

### HYBRID POSITIONING

Presented as a system whose stated integrity design is tested, the two contributions reinforce each other: the system supplies the claims, the evaluation supplies evidence about them, and the repair record shows the two co-evolved. The evaluation is the scientific contribution; the system is the described object. It stays coherent only if it states up front that it evaluates integrity properties only, derives every test from a stated design commitment, caps the system section, and reports each commitment as held in scope, failed on the baseline and repaired, or untested (with the follow-up path as a named exception). Without those controls it degrades into either "engineering with weak evaluation" or "evaluation without a system".

### FINAL PRIMARY IDENTITY

A scoped empirical test of the integrity design (authority dominance, containment, fail-closed failure handling) of one implemented LLM-assisted technical-assessment system. (Position C, evaluation primary.)

### SECONDARY CONTRIBUTION

The system and its stated design commitments, described only as far as needed to define the tests, together with the record of design-versus-behaviour discrepancies found and repaired.

### WHY THIS IS THE STRONGEST POSITIONING

It is the only shape the evidence fills. It keeps the research-grade evidence (the X1 campaigns) as the contribution, gives that evidence its object and its reason (the system's own stated commitments), gives the engineering credit without making an unevidenced system claim, and turns a weakness into content: three places where documentation and passing unit tests asserted a property that the tests under adverse conditions did not confirm. Its claims are unchanged under any change of emphasis, so it is the most stable core for repeated presentation, and it stays within what the repository can support: no effectiveness, no end-to-end, no multimodal claim.

### WHAT THE CURRENT POSITIONING UNDERSOLD

The system as the source of the hypotheses: the authority-dominance, provenance and fail-closed commitments are explicit in the architecture text, the best-answer and timing modules and the fallback-removal audit, yet the manuscript calls them "design intentions" in one sentence. The scale and integration of what was built and tested (real orchestrator, real executor, real model in the targeted paths). The design-versus-behaviour finding: a documented anti-fabrication audit, a test suite that had encoded a silent 0.0, and a status label that misreported template output as model output. The reason the three properties were chosen.

### WHAT THE CURRENT POSITIONING OVERSTATED

"Dependability" as the identity, which implies breadth the three properties lack. The generality of "an LLM-assisted technical-assessment pipeline" when the evidence is one bespoke system. The independence of the oracles (SEC-08 and the SEC-09 control). The informativeness of the passing results (invariance 72/72 is by construction; SEC-03/04 have no controls). The earlier audit's statement that follow-up scoring uses model concepts for 25 rubric-less questions (already corrected in the protocol). And the implicit reach of the word "system" in the title relative to what was tested: the campaigns were not end-to-end.

### REQUIRED EVIDENCE CHANGES

No new experiment is required by this repositioning. Recommended, in order of weight:
- Keep the SEC-09 supplement and the follow-up-channel decision from the repair protocol; the follow-up test matters more under this positioning because it concerns the one documented exception to the authority commitment.
- Produce the design-commitment traceability table from existing documents, tests and X1 results (documentation only).
- Add a bounded system description with a component-status table (evidence level per component); label audio, PPO and evaluator validity as untested here.
- Verify and add system-level related work; nothing is citable from the project's first-pass literature matrix until verified.
- If the working demonstration is to carry weight, a scripted, hashed, replayable integrated session record (descriptive) would be needed; none exists in the current evidence base.
- Do not claim end-to-end evaluation, multimodality, effectiveness or latency.

### FINAL RECOMMENDATION

Adopt Position C with the evaluation primary and the system secondary. The paper's identity sentence: *"This paper presents an implemented LLM-assisted technical-assessment system, states the integrity design it is built on, and reports a scoped empirical test of whether that design held under adverse conditions."* Retain "dependability" as the method discipline and as secondary vocabulary, not as the identity. Keep the claims exactly as scoped; expand only the system description, and only to the extent needed to define the tests and the status of every untested component. Treat the boundary with the planned human-pilot system paper as an open decision for you (P1 owns architecture and integrity evidence; the pilot owns human-facing claims and cites P1). Make no change to code, experiments, canonical truth, manuscript, title or research question until you decide; a candidate title and research question in this spirit (for your consideration only) would be, respectively, a title beginning "Testing the Integrity Design of an LLM-Assisted Technical-Assessment System" and a question asking which of the system's stated integrity commitments held under adverse conditions in one specified environment.
