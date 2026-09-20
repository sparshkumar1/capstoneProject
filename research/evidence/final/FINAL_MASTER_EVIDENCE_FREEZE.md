# PREPAIred — Master evidence freeze, claim audit and manuscript-preparation package (2026-09-20)

Scope: consolidates the state after the O7 run, the X1-A/B/C campaigns and the Paper 2 gate review. It supersedes nothing (the older packages stay as history); numbers below are read from stored artifacts, hashes are in `FINAL_HASH_MANIFEST.json` (built by `build_manifest.py`), tag → commit map is in that manifest. **No manuscript prose is written here.** The canonical truth file was **not edited** (see §9: proposed additions await approval).

## 1. Evidence lineage (categories are never pooled)
| Cat. | Meaning | Items |
|---|---|---|
| A | frozen / pre-existing | Paper 1 frozen items (X1D-C001…C003, P1-C001/C002/C003), old 64-case benchmark and X2-B, X3-A registered chain, Paper 3 frozen study |
| B | newly generated confirmatory | **none** (X2-C human round blocked) |
| C | exploratory | old 64-case Paper 2 results; X2-B length/BM25 baselines; X1-B exploratory count of LLM-sourced adversarial arms |
| D | registered primary | X3-A (X3A-C001); X1-A, X1-C, X1-B-I are registered *protocols* executed once each (registered by the executing agent; **independent methodology review pending**) |
| E | secondary sensitivity | X3-A-O7 (A, B, C) |
| F | engineering validation | X1-A/B/C campaigns, application-repair test suites |
| G | human-study evidence | old 3-rater gold (provenance/ethics incomplete); nothing new |
| H | simulation evidence | all Paper 3 evidence; the X2-C precision simulation (synthetic, preparation only) |

## 2. Tag → state
`release/app-repair/v1` (980747f) application; `prereg/X3-A-O7/v1` (5217542) + `freeze/X3-A-O7/v1` (4bcb969) O7; `prereg/X1-C/v1` (21a4c9c) + `freeze/X1-C/v1`; `prereg/X1-A/v1` (80ac604) + `freeze/X1-A/v1` (68a0bf5); `prereg/X1-B/v1` (c7ab585, superseded, never completed) → `prereg/X1-B/v2` (424894f) + `freeze/X1-B/v2` (2768f49). Nothing pushed.

## 3. Paper 3 — claim audit (see also `PAPER3_FINAL_EVIDENCE.md`)
| Claim (permissible wording) | Evidence / artifact | Method, N, uncertainty | Limitation |
|---|---|---|---|
| Under identical guardrails, PPO's persona-level tracking MAE was equivalent to Constant-Same within the registered ±0.12 margin (Δ −0.0350, 95% CI [−0.0818, +0.0021]) | `x3a_decision.json`; X3A-C001 | two-way cluster bootstrap, 40 personas × 5 training seeds, B = 10,000 | simulation only; five checkpoints; equivalence ≠ zero effect |
| The classification was unchanged under three pre-specified secondary analyses | `research/analysis/x3a_o7/results/*`; `O7_INTERPRETATION.md` | R0 exact (0.0); A [−0.0673, −0.0052]; B [−0.0758, +0.0057]; C five points −0.0463…−0.0234, all Equivalent | A and two leave-one-out intervals exclude zero on the PPO-favourable side; B is 5 aggregates, df 4; O7 does not replace X3A-C001 |
| PPO+G is more volatile/oscillatory than Constant-Same+G | X3A-C002 | volatility +0.149 [0.067, 0.254] | simulation only |
| PPO uses its observation | X3A-C004 | zeroed +0.370, partner +0.254 | as above |
| Superiority not met | O7 | no upper limit < −0.20 in any of 8 intervals | — |
Removed / not permitted: PPO superiority or improved tracking; lower volatility; "shield"; real-user or deployment claims; "no effect"; "novel/first".
Ten-question check (strong statements): (1) directly supported yes for the equivalence wording; (2) population = 40-persona grid, five checkpoints; (3) confirmatory-for-this-protocol; (4) simpler explanation: the persona target is an authored rule, so MAE measures agreement with that rule; (5) O7 A's interval excluding zero does not change the class but must be disclosed; (6) system behaviour vs generalisation: simulation only; (7) causality not claimed; (10) RL benefit not claimed.

## 4. Paper 1 — claim audit
| Claim (permissible wording) | Evidence / artifact | Method, N | Uncertainty / limitation |
|---|---|---|---|
| In this harness, on one Docker Desktop (WSL2) machine, the shipped sandbox configuration met pre-specified containment and host-unchanged criteria for nine attack programs in 5/5 runs each, while single-change permissive controls breached in 5/5 (where applicable) | `results/x1c/*`, `X1C_RESULT_NOTE.md` | 90 runs; computed criteria; benign and cross-oracle negative controls | not "secure"/"isolated"; nine programs only; no kernel/runtime escape testing; static pre-flight blocks only `ptrace(`; `socket()` succeeds under `--net=none` (connect fails); `ptrace(TRACEME)` returned 0 with pre-flight bypassed; canary dir not reset between SEC-09 permissive reps; status strings cannot discriminate (four attacks `wrong_answer` in both configs) |
| For the executed fault classes, Qwen outage/slow, Docker outage, invalid-score range, short DB lock and empty input met their criteria | `results/x1a/*`, `X1A_RESULT_NOTE.md` | 60 repetitions, per-scenario counts | FLT-01 latency 4.84–4.90 s vs SLA 5.0 s; in-process injection; Qwen stubbed |
| **Two defects were found**: an evaluator outage is recorded as a 0.0 candidate score with no infrastructure flag (FLT-03, 0/5), and a compile timeout leaves a running container (FLT-06, 0/5); FLT-07b met behaviour but exceeded the registered timing bound in 1/5 | same | | not fixed; NaN/Inf/−3 invalid scores and empty transcripts are also silently recorded as 0.0 |
| "Fault-tolerant" | **not permitted** (protocol §5) | | use "failure-aware/failure-characterised" |
| In a fixed-evaluator harness with real Qwen, no compared score/difficulty/best-answer observable differed in any of 72 adversarial-vs-benign pairs; only 16 pairs had LLM-sourced feedback in both arms (registered minimum 30 not met) | `results/x1b/*`, `X1B_RESULT_NOTE.md` | 72 pairs; exact equality; static guard 0 flags; mutants detected | under-powered; follow-up channel (LLM text and target concepts become the evaluated question) is a documented dependency; service silently falls back to a template ~55% of the time while reporting `llm_status: available`; shipped 6 s client timeout < 13–21 s generation |
| Frozen items: 226-test suite at build A with one known failure; warm evaluator latency (in-process) median 236 ms [221, 252], P95 615 ms; SQLite single-writer save 12.7 ms; synthetic-DB concurrency without lock errors to 25 threads | X1D-C001…C003, P1-C002 (category A) | | not end-to-end latency; the current suite at the repaired build is a different run (last recorded 274 passed, 1 known failure, not a registered claim) |
Not permitted: secure, isolated, "zero violations", escape-proof, formal shield, "the LLM cannot alter scoring/difficulty", sub-second end-to-end latency, prompt-injection-proof, that Docker grading or interview-practice systems are new. Observed in X1-B (not a registered latency claim): a real-LLM turn took about 20 s on this CPU.

## 5. Paper 2 — claim audit
| Claim (permissible wording) | Evidence / artifact | Method, N | Limitation |
|---|---|---|---|
| On an exploratory, author-constructed 64-answer benchmark (8 questions, 3 raters), agreement between the composite and rater consensus was ρ = 0.3812 (case-bootstrap 95% CI [0.1575, 0.5774]) | old benchmark artifacts (category A/C) | Spearman, case bootstrap | rater provenance/ethics records incomplete; exploratory; 8 questions |
| The full composite was below R-only (0.4832) and S1+R (0.4884) in the seven-way ablation; a length-only baseline (0.4897, X2-B, exploratory) matched or exceeded the learned cross-encoder | ablation results; X2B-C003 | | exploratory |
| Concise-correct and paraphrase answers were substantially under-scored | frozen diagnostic categories | | author-constructed categories |
| Rater reliability on the old set ICC(2,1) 0.9528 | old human-agreement results | | same provenance limits |
**No confirmatory evidence exists; none was collected.** Not permitted: validated/accurate/reliable evaluator; improves over R-only; robust to attacks; length-bias free; "off-the-shelf" CrossEncoder; expert/independent/committee raters; ρ 0.6975 as current; fairness or real-learner claims; calling any of this confirmatory.

## 6. Threats to validity (cross-paper)
Single machine, unlocked SUT environment (`.venv` violates pins); all X1 protocols were written and executed by the same agent that built the harness (independent methodology review pending); X1-B and X1-A used in-process fixtures and a stubbed evaluator/Qwen; simulation-only RL evidence with authored persona targets; Paper 2's benchmark is author-constructed with 8 questions and incomplete rater records; two SUT defects unfixed; no formal threat model; literature gaps unresolved. One tracked file (`.env.example`) was modified throughout and is not part of any evidence.

## 7. Publication-readiness assessment (evidence sufficiency for writing/submission; no acceptance promised)
| | Paper 1 (systems/dependability) | Paper 2 (evaluator validity) | Paper 3 (adaptive-difficulty PPO, simulation) |
|---|---|---|---|
| Research question | Which containment/authority-separation/fault-handling properties of the pipeline can be shown by tests able to fail? | How well does the composite agree with blinded humans, vs simple baselines, and which answers does it mis-score? | What does a learned PPO controller add beyond a constraint layer, versus matched simpler policies, in simulation? |
| Main contribution | Failure-aware evaluation with negative/permissive controls; documented defects | Diagnostic/negative measurement result on an exploratory benchmark | Negative-equivalence, matched-control decomposition |
| Strongest evidence | X1-C (9 attacks, controls, computed criteria); X1-A defect findings | Ablation (composite not best); under-scoring of concise answers; wide-interval agreement | X3-A registered result + O7 unchanged classification |
| Weakest evidence | X1-B (16/30 valid pairs); protocols self-registered, unreviewed | No confirmatory round; provenance/ethics incomplete; 8 questions | Simulation only; authored target; one training recipe, 5 seeds |
| Remaining evidence | independent protocol review; decisions on FLT-03/FLT-06 fixes (then full reruns); B2 if a "no LLM authority" claim is wanted; literature checks | institutional route → protocol registration → new benchmark and blind raters | equivalence-margin justification; optional X3-B only via new preregistration |
| Blockers | decisions on defects; review | institutional/ethics determination; user confirmation of precision target | none for writing |
| Claims supportable | §4 rows | §5 rows | §3 rows |
| Not supportable | secure, fault-tolerant, LLM-proof, new | validated, better than baselines, confirmatory | PPO superiority, deployment, shield |
| **Readiness** | **WRITING READY WITH LIMITATIONS** (as a failure-characterisation paper; conditional on independent review of the X1 protocols) | **NOT READY** as a validation or confirmatory paper; only an explicitly exploratory diagnostic note is supportable | **WRITING READY WITH LIMITATIONS** |

## 8. Manuscript-preparation package (facts only; no prose)
**Title candidates** (from the claim map; not decisions): P1 "Testing containment and authority separation in an LLM-assisted technical-assessment prototype" / failure-characterisation framing; P2 "What a composite technical-answer evaluator measures: agreement, length dependence and under-scored concise answers"; P3 "What a learned difficulty controller adds beyond a constraint layer: a persona-level matched-control evaluation in simulation".
**Abstract facts** — P1: 9 attacks × {shipped, permissive control} × 5 reps, 9/9 contained in this harness, controls breached; 8 fault classes, 2 defects; 72 injection pairs, 16 LLM-sourced, invariants equal. P2: ρ 0.3812 [0.1575, 0.5774], N = 64/8 questions; ablation R-only 0.4832, S1+R 0.4884 > composite; length-only 0.4897 (exploratory). P3: Δ −0.0350 [−0.0818, +0.0021], margin ±0.12, Equivalent; O7 unchanged in A/B/C; PPO volatility +0.149.
**Contribution lists** — P1: controlled test design with oracle validation; SUT defect catalogue; channel enumeration. P2: diagnostic measurement results with negative findings. P3: matched-control decomposition with equivalence framing.
**Section outlines / tables / figures**: P1 — threat model (design mapping), oracle definition table, per-attack outcome table (X1C note §per-attack), per-scenario fault table, invariance table, defect list; figures: architecture with authority boundaries, containment outcome matrix. P2 — benchmark construction table, ablation table, category under-scoring plot, length-vs-score scatter. P3 — condition table (26 conditions; Section 2 of the Paper 3 package), registered-contrast forest plot, O7 interval figure (8 intervals vs ±0.12/−0.20 margins), seed-level Δs.
**Reproducibility checklist**: commits/tags above; locked environment for O7/X3-A; X1 environment record in `results/x1c/environment_and_verdicts.json`; hashes in the manifest; the Qwen model file SHA-256 `6a1a2eb6…9407e`; harness commands in each `RUN_RECORD.json`.
**Reference gaps requiring literature review**: P1 — graceful-degradation and authority-separation literature; container-escape/seccomp measurement studies; SandboxEval comparison; LLM-as-scorer attack papers already listed (verify each). P2 — non-LLM evaluator/measurement-validity literature; ASAG clustering; paraphrase testing; technical-interview benchmarks. P3 — CAT/IRT and adaptive-control literature; RL evaluation methodology with matched controls; equivalence-margin justification; persona-simulator validity. **No "first/novel/state-of-the-art" wording is licensed by the current literature files.**

## 9. Proposed additions to the canonical truth file (NOT applied; require user approval and a changelog entry)
O7 official result (R0 exact; A/B/C values as above; run record hash); X1-C, X1-A, X1-B result summaries with the defect list; Paper 2 gate status ("no confirmatory data; blocked"); the clarification that X1 protocols were self-registered and await independent review.

## 10. Repository state
See `FINAL_HASH_MANIFEST.json` (`head`, `tags`, `files_sha256`). Nothing pushed. Untracked, deliberately uncommitted: `.env.example` (modified), `.serena/`, `CLAUDE.md`, `docs/PROJECT_STATE.md`, `paper/`, `requirements/tracking.txt`, the older `research/audit/*` reports, `research/evidence/PAPER*_PACKAGE.md`, `research/literature/`, `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`.
