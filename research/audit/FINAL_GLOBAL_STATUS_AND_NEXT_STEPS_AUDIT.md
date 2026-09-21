# PREPAIred - final global status, gap and publication-readiness audit (2026-09-20, read-only)

**Method and limits.** Read-only inspection of the repository (registry, protocols, manifests, tags, audits, code, docs, stored results), the Codex audit and the Claude validation, the O7 specification, and official conference pages. Nothing was run, changed, tagged, sent or submitted; this file is the only file created. **This audit is not independent in the strict sense:** it is written by the same Claude executor that wrote the plan, the validation and the O7 specification. I tried to challenge those documents, and several corrections below are against my own earlier statements, but ChatGPT should cross-check this audit. Verification status of external facts: ICETC, ICTCS and ICMETE official pages were read in this pass; ATIS, HCII and the ICMLSC/SmartCom pages were read earlier on the same date and not re-fetched; ACM SAC AIED track page, IEEE MLNLP and IEEE AIEI official pages remain **unreadable/unverified** (TLS errors).

## 1. Executive verdict

1. **Paper 3 is the only paper with a complete, frozen, protocol-tagged confirmatory result, but it is a null/equivalence result in a self-authored simulator.** It is *not yet* manuscript-assembly ready: no literature or novelty positioning exists anywhere in the repository (Zotero holds no references), the tagged protocol has had no methodology review, and claim wording and the evidence package are unbuilt. O7 is a useful robustness check, not the gate the current table implies.
2. **Paper 1 is NOT READY.** Its containment, LLM-isolation and fault-handling claims are withdrawn or design-only, and the experiments that would restore them (X1-A/B/C) are not built. A claim implied by its frozen framing, "sub-second latency", is supported only for the evaluator step, not end-to-end.
3. **Paper 2 is NOT READY, and the current table is too optimistic about it.** X2-C is not a formality: the exploratory evidence already shows a length-only baseline matching the derived CrossEncoder, and the external human/ethics gate has not been started.
4. **The demo is "ready after a structured verification", not "after one clean rehearsal".** The last recorded end-to-end verification is 2026-08-17; since then the system changed (persistent history and retries, follow-up evaluation, UI fixes, and on 2026-09-19 the definition of RL observation dimension 4). Live microphone input has never been verified.
5. **Two planning errors of mine are corrected here.** (i) "ICTCS 2026" and "ICMETE 2026" were reported as unidentifiable; the repository identifies them (`research/audit/paper_overlap_matrix.md`, `research/archive/old_audits/publication_readiness.md`) and official pages now confirm them (Section 12). (ii) An archived audit records a university venue standard (conference age >= 10 years, Scopus/EI indexing) that I never checked against the portfolio; it may exclude some venues (Section 13).
6. **Project-level answer:** we are closer to **B. running more science** than to packaging or writing, because two of three papers cannot be written honestly without new experiments or human data; only Paper 3 is in the packaging stage.

## 2. Validation of the current status table and the global statements

| Area | Current hypothesis | Verdict | Repository-grounded reason |
|---|---|---|---|
| PREPAIred core system | Frozen / mature; do not redesign | **PARTIALLY CONFIRMED** | "Do not redesign" stands. "Frozen" is a policy, not a single recorded product state: only `sut/X1/build-A` (`3904749`) and `v1.0-paper3-complete` (`b7cad49`) exist. The SUT changed on 2026-09-19 inside the Paper-3 freeze commit (`build_rl_observation` dimension 4: `last_time_norm` -> turn progress), one regression test fails because of it (triage: `PHASE_NEXT_RESEARCH_PLAN.md` 5.6), the runtime `.venv` violates its pins, and an untested dead constant (`RESTRICTED_C_HEADERS`) exists in the static filter. "Mature" is not evidenced beyond unit tests. |
| Demo | Essentially ready; one clean rehearsal | **PARTIALLY CONFIRMED / slightly TOO OPTIMISTIC** | See Section 3: verification evidence is 2026-08-17 (archived docs); ~10 SUT commits since; microphone path never hardware-verified; README front page carries superseded claims. A checklist verification is needed, not one run. |
| Paper 3 | Closest to paper-ready; O7 + audit + packaging | **PARTIALLY CONFIRMED (closest: yes; remaining list: incomplete and mis-ordered)** | Missing: literature/novelty (none exists), ChatGPT review of `prereg/X3-A/v1` (pending), claim-wording constraints, evidence package. O7 is SHOULD, not MUST: the Codex audit found no defect that changes the registered result. Drafting of non-numeric sections need not wait for O7. |
| Paper 1 | Needs substantial evidence: X1-C -> X1-B -> X1-A | **CONFIRMED (need) / PARTIALLY CONFIRMED (order and scope)** | Order is defensible, but X1-B's static check has no Qwen dependency and can run with X1-C; X1-A must be scoped by the claims the paper keeps; an end-to-end latency statement and, if kept, an audio-to-score "insulation" static check are missing from the plan. |
| Paper 2 | Not paper-ready; human/institutional gate -> X2-C | **CONFIRMED (not ready) / TOO OPTIMISTIC (path)** | X2-C is externally gated, unstarted, needs authors and raters, needs D-X2-TAU, and may return an adverse result (length baseline). No literature exists. |
| Research infrastructure | Needs hardening: `run_manifest_v2` + protections | **PARTIALLY CONFIRMED / TOO BROAD** | Only a minimal v2 is required before the next confirmatory run (Section 7). Most other items are experiment-specific or documentation. |
| Independent review | Core harness audit done; O7 script needs audit | **TOO OPTIMISTIC** | Codex audited six files once. The *methodology/protocol* review (ChatGPT) of `prereg/X3-A/v1`, `prereg/X2-B`, `prereg/X1-D`, the corrected X1 designs, the O7 spec and the Paper-3 claims has not happened at all. Every new harness (v2, X1-C/B/A, O7 script) also needs its own review. |
| Manuscript writing | Not yet for all; start Paper 3 after O7 | **PARTIALLY CONFIRMED** | The real prerequisites for Paper 3 are literature, ChatGPT review and the evidence package; O7 only feeds one robustness row. |
| Conference submission | Paper-dependent; deadlines must not override evidence | **CONFIRMED**, with updates | ICTCS and ICMETE identified; ICETC 10 Oct is unrealistic for Paper 1; the university venue rule is unchecked (Sections 12-13). |

| Statement | Verdict | Reason |
|---|---|---|
| A. The core product is frozen and should not change | **YES WITH CAVEAT** | Correct as policy; the caveat is that its definition is not one recorded state, and X1 defects would follow the defect policy (build B), which is a product change by another route. |
| B. The product is demo-ready | **YES WITH CAVEAT** | Ready after verification (Section 3), not verified since 2026-08-17. |
| C. We are mainly doing evidence/research-support work | **YES WITH CAVEAT** | Also: literature, provenance/ethics (external), documentation hygiene, demo verification. |
| D. No additional product feature is needed for the three papers | **YES WITH CAVEAT** | True if claims are narrowed to what is measured. Not true if Paper 1 wants "fault-tolerant" or "secure" wording and X1 finds failures. |
| E. The remaining work is mostly paper-supporting evidence | **YES WITH CAVEAT** | Plus literature (nothing exists), authorship and AI-tool disclosure, and stale-document cleanup. |
| F. The three-paper split is scientifically defensible | **YES WITH CAVEAT** | Questions are distinct, but Papers 1 and 2 both describe the evaluator, Papers 1 and 3 both describe the guardrail/PPO controller, and the overlap matrix predates the withdrawals (Section 9). |
| G. No major scientific redesign is currently required | **YES WITH CAVEAT (redesign) / NO (claim reframing)** | No redesign of the evaluator or PPO is warranted, but Paper 2 needs its claims reframed (length baseline; composite below R-only) and Paper 3's headline is a null result requiring careful framing. |

## 3. Demo readiness audit

**Verdict: READY AFTER ONE STRUCTURED VERIFICATION.** Not "READY NOW" (no verification since 2026-08-17); not "NOT READY" (every path exists and the test suite passes except one known failure).

| Flow step | Implemented? | Evidence / concern |
|---|---|---|
| Startup | Yes | `launch.py` starts evaluator (5000), Qwen service (8001, optional), backend (8000), frontend dev server (5173); flags `--no-qwen`, `--no-frontend`, `--backend-only`. Docker daemon was up (29.7.2) and `prepaired-c-sandbox:latest` (238 MB) present on 2026-09-20. `apps/web/dist` built 2026-09-19. |
| Session initialisation, question generation | Yes | Question bank under `data/questions`; LLM follow-ups via the Qwen service. |
| Candidate answer (text and voice) | Yes / **voice not hardware-verified** | Frontend records via the browser; STT is faster-whisper/WhisperX (installed). The archived gates list "live microphone: NOT VERIFIED (hardware)". |
| Code execution | Yes | Docker C sandbox; requires the daemon and image. |
| Technical evaluation | Yes | Evaluator loads SBERT, FAISS and the CrossEncoder (cold first request ~3.8 s, warm median ~236 ms: `X1D-C002`). |
| Audio / feedback path | Yes | Qwen 2.5 1.5B GGUF (Q4_K_M, present in `models/gguf`, `llama-cpp-python` 0.3.35 installed); the feedback agent times out at 6 s and falls back to `non_llm_structured_recovery`. If the GGUF path failed, the Transformers fallback measured 154-193 s per turn (archived benchmark), i.e. unusable. |
| Adaptive decision | Yes | Runtime PPO is `rl/checkpoints/seed_123` (one of the five Paper-3 checkpoints) with guardrails. Its dimension 4 is now turn progress, whereas training used response time (`rl_state_alignment.md`): **demo adaptivity is not what X3-A evaluates.** |
| Follow-up / retry, persistence / history | Yes | Persistent learning history and retries added 2026-09-08; SQLite `data/prepaired.db` (single file). |
| Final result | Yes | Report generation exists; not re-verified end to end since August. |

**Known blockers and fragilities.** (1) One failing unit test (dimension-4 semantics); it does not stop the demo but it is a stale-expectation signal that the runtime observation changed after the last recorded end-to-end run. (2) Verification evidence is stale (>= 10 SUT commits since). (3) Qwen dependency: model file present, but a cold-load or CPU contention could exceed the 6 s timeout and silently switch to the non-LLM path (correct behaviour, different feedback quality). (4) Docker Desktop must be running. (5) Microphone and browser permission (secure-context requirement; `localhost` is fine). (6) No documented manual recovery procedure was found. (7) Frontend tests (7) were last recorded in August.

**To rehearse.** A scripted full session on the demo machine: cold start; one verbal answer with the real microphone; one coding answer that passes and one that fails/compile-errors; a forced timeout; a follow-up and a retry; history view; final report; Qwen-off (`--no-qwen`) and Docker-off recovery; restart persistence; time each step. Re-run the frontend tests and the backend suite once (read-only observation of failures).

**Never claim in the demo.** "Secure" or "contained" (only design configuration exists; `P1-C006/C008` withdrawn); "fault-tolerant"; "PPO improves difficulty tracking or learning" (`P3-C011` withdrawn; X3-A: equivalent to a constant Same action under the same shield in simulation); "validated against expert raters" or any of 0.6975/0.74 (superseded; current rho 0.3812 on 64 author-constructed answers, exploratory); "reasoning verification" (a length-only baseline matches R on the old benchmark); "off-the-shelf CrossEncoder"; "accent/demographic fairness" or "100% insulation of speech from scoring" (`P1-C010` withdrawn; no demographic data); "video/MediaPipe/multimodal video"; "sub-second" for anything other than the warm evaluator; "improves interview outcomes" (no human outcome data).

**Kept separate.** *Demo correctness* = the flow works. *Research validity* = the registry-backed evidence above. *Production readiness* = **not claimed and not present** (dev servers, single-writer SQLite, no authentication or privacy review was found in this pass, unlocked environment, public documentation stale). None implies another.

## 4. Paper 3 - final gap audit

**A. Publication-grade now.** X3-A primary: pre-registered, tagged before execution (`prereg/X3-A/v1`), gate G-HARNESS 9/9, frozen and hashed, key hashes verified by Codex, point estimate independently recomputed (T2): PPO+G minus Constant-Same+G tracking MAE = -0.0350, 95% CI [-0.0818, +0.0021], class Equivalent within +/-0.12 (`X3A-C001`). X3-0 replay/accounting (G-REPRO 32/32): 563 activations vs 99 overrides vs 136/232 attempted boundary actions; volatility 0.186 (not 0.088). Codex confirmed key alignment and found no hard-coded outcome or result-dependent selection.

**B. Exploratory / descriptive.** Volatility contrast (+0.149), state-zero/shuffle controls, controller/oracle/heuristic comparisons (target authored; controller exploits it), rule ablations (no independent reference for ablation branches), persona-type/skill strata, the shield-on-grid finding (`X3A-C003`). All labelled descriptive by the protocol.

**C. Still required.** Literature review and novelty positioning; ChatGPT review of `prereg/X3-A/v1`; wording constraints from the registry; the Paper-3 evidence package; an honest treatment of the null result; the reward/oracle-coupling, training/evaluation-mismatch and dimension-4 limitations (the last two are recorded in the audits but not in the earlier Paper-3 limitation list before this audit round); a statement about non-reproducible training (unseeded candidate).

**D. Supportable.** The pre-registered equivalence (for these checkpoints, this persona generator, this simulator); PPO+G is more volatile than Constant-Same+G; the shield's tracking benefit seen on five personas does not generalise to the 40-persona grid; PPO uses its observation; counting definitions; the frozen-study replication.

**E. Not supportable.** PPO improves tracking; guardrails eliminate boundary violations; PPO lowers volatility; anything about learners, engagement or outcomes; a method-level claim that adaptive learned controllers cannot beat a constant under a shield; any statement about the deployed runtime policy (dimension-4 divergence; runtime uses seed 123 only); "multimodal" or "speech robustness" (simulated confidence/hesitation only; the old title and overlap-matrix table include such wording).

**Exactly what must happen before Paper 3 is honestly manuscript-ready.**
- **MUST:** (1) ChatGPT methodology review of `prereg/X3-A/v1` and the claim map; (2) literature/novelty positioning with verified sources (Zotero is empty); (3) claim-wording constraints applied from the registry (allowed/forbidden lists); (4) the Paper-3 evidence package (tables/figures generated from stored results with source hashes); (5) limitations and threats section content assembled (coupling, mismatch, dimension 4, five seeds, authored persona grid, delta = 0.12); (6) venue-specific requirements for the chosen venue; (7) an explicit statement of the Codex findings that touch X3-A (O5 provenance nuance, O8/O10 as non-defects for the frozen result).
- **SHOULD:** O7 (approved specification; Codex review of the R0 code first); the offline recomputation of MAE/volatility from the stored action strings (an independent check that needs no rerun); a descriptive delta-sensitivity table.
- **OPTIONAL / NOT NEEDED:** X3-B; retraining; a second simulator or persona generator; further ablations.
- **X3-B is still unnecessary.** It would be needed only to support a *method-level* claim about training recipes, which the paper should not make; its prerequisite (D-N2) is open and it would touch training-environment definitions that are reserved.

**Framing risk.** The contribution is a well-controlled negative/decomposition result. That is publishable in principle, but reviewers may ask why a simulator-only null result about a component is a contribution; the answer must rest on the pre-registered design and the decomposition method, not on PPO.

## 5. Paper 1 - final gap audit

**A. Usable now.** X1-D (`X1D-C001..C003`): 226 tests, 225 passed, 1 failed (disclosed); warm evaluator latency median 236 ms, P95 615 ms, P99 804 ms, cold first request 3.8 s, single-writer SQLite median 12.7 ms; stored concurrency table (`P1-C002`, narrowed) and stored latency (`P1-C001`, narrowed); the sandbox configuration as **design only** (`P1-C009`); the architecture description and threat model as design mapping.
**B. Correctly withdrawn.** `P1-C004` (10/10 faults; a literal), `P1-C005` (Qwen 5/5; no output inspected), `P1-C006` (9/9 contained; five attacks non-discriminating), `P1-C007` (213 passed), `P1-C008` ("secure"), `P1-C010` (100% acoustic insulation). The withdrawals are sound; I found nothing that should be restored without new evidence.
**C. Needs X1-C.** Any statement that attacks were contained, that the static filter versus the container each did something, and that the host was unchanged.
**D. Needs X1-B.** "LLM output has no authority over score, difficulty or ranking"; the audio-to-score insulation claim if kept (a static path check, no Qwen needed).
**E. Needs X1-A.** "Failure-aware behaviour verified" or "fault-tolerant" for the enumerated classes.
**F. Order.** X1-C -> X1-B -> X1-A is defensible on tractability; refine: run the X1-B *static* check together with X1-C (no service dependency), then the dynamic invariance test once Qwen is confirmed, then X1-A restricted to the fault classes the paper actually claims.
**G. Experiments that may be unnecessary.** X1-B-S (behavioural stress) unless a claim uses it; X1-A scenarios for claims that will not be made (for example WebSocket reset, feature-extractor crash); attack additions beyond those that map to a claimed control (compile bomb, `/dev/zero` include) unless a defect appears.
**H. Missing controls, oracles, repetitions.** Present in the design: four-layer oracle separation, predefined weakened configurations, canaries, mutation controls, 5 repetitions. Gaps to add: record the Docker/WSL2 kernel, image digest, default seccomp profile and gcc version (the shipped flags do not disable seccomp, which is unrecorded); a *no-op/benign program* negative control; an orphan-container check after the compile step's host-side timeout; an end-to-end latency measurement or narrowed wording; a defect log across builds A/B; an environment record (the SUT `.venv` is unlocked with pin conflicts).

**Verified specifics.** The static filter (`sandbox_policy.py`) blocks only `ptrace(` and sources over 64 KB; `RESTRICTED_C_HEADERS` is defined and never used; the executor derives `status` partly from string heuristics; shipped flags include `--net=none`, `--cap-drop=ALL`, `--read-only`, `--pids-limit=32`, `--memory=128m`, a `:ro` input mount. The frozen overlap matrix lists Paper 1's core question as isolating failure modes and removing LLMs from the scoring path "while maintaining sub-second latency"; measured sub-second latency exists for the warm evaluator only, and the LLM feedback step alone was measured at 1.8-2.9 s (GGUF, archived).

**Minimum scientifically sufficient Paper-1 campaign.**
- **MUST RUN:** X1-C (nine attacks made discriminating; layers 1-4; predefined weakened-configuration controls; benign control; 5 repetitions); X1-B-I (fixed-answer invariance, >= 30 pairs, real Qwen, static check, LLM-wired mutant); X1-A restricted to the fault classes claimed, each with a no-fault control and a mutant.
- **SHOULD RUN:** an end-to-end per-turn latency measurement (or narrow the wording to evaluator latency); the audio-to-score static path check if the insulation claim is kept.
- **NOT NEEDED:** further attack programs, fuzzing, load testing, cross-platform/host-kernel escape tests, re-running X1-D, fixing the failing test for a green suite, a second sandbox.

**Can Paper 1 be written before all X1 experiments are complete?** Not as a manuscript that a systems or security reviewer would accept: the paper's central claims are exactly the untested ones. What can be prepared without overclaiming: the architecture and design description labelled as design, the threat-model table labelled as a design mapping, the X1-D test and latency sections with their scope, the related-work section, and the limitations skeleton. Result sections for containment, isolation and fault handling must wait for X1-C, X1-B and X1-A; a design-plus-X1-D paper would invite "no evaluation of the claims".

## 6. Paper 2 - final gap audit

**What the old benchmark can support.** It supports a **pilot / exploratory / negative-findings paper** or background evidence; it cannot support a full validation paper. Evidence: 64 author-constructed answers to 8 questions (8 effective clusters); composite rho 0.3812 with two-level CI [0.153, 0.649]; three raters with very high reliability on constructed contrast items (ICC(2,1) 0.953) that says nothing about natural answers; rater provenance/ethics records incomplete (the annotation ethics checklist is an unfilled template, status "HUMAN ADMINISTRATIVE CHECK REQUIRED"); length-only baseline rho 0.4897 / AUROC 0.886 versus derived CE 0.4825 / 0.782; composite below R-only (-0.102, interval includes zero); composite bias -0.134 with concise-correct answers under-scored; exploratory false-accept analysis does not favour the composite; the derived CE agrees better than the upstream model (0.4825 vs 0.1454) with unrecoverable training provenance; question overlap with the pilot (0.709 vs 0.425); metamorphic 19/21 and adversarial 11/13 against author-set ceilings.

1. **Is X2-C genuinely necessary?** For any validity or generalisation claim, yes. It resolves: replication on unseen questions (circularity and tuning overlap), whether R adds evidence beyond surface features (length-controlled strata), the leakage suspicion behind the derived-versus-upstream gap, and human-provenance repair.
2. **Could Paper 2 be submitted honestly before X2-C?** Yes, only as an explicitly exploratory/pilot/negative-findings paper, and only if the human-rating provenance can be stated truthfully for the venue (many venues require an ethics statement that the project cannot currently supply).
3. **Claim restriction.** "On 64 constructed answers to 8 questions, a composite evaluator shows moderate rank agreement, comparable to a length baseline; the composite is not better than R alone; a fine-tuned derivative outperforms its public upstream on this set; provenance is incomplete." No validity, no expert-agreement, no safety-hardening claim.
4. **Would submitting before X2-C materially weaken the paper?** Yes: no confirmatory result, an adverse baseline finding, and an evaluator contribution that reviewers will read as unvalidated. It would also expose the provenance gap.
5. **Minimum confirmatory benchmark.** Question-disjoint and temporally separated items; independently authored, evaluator-unaware, no score-based filtering; >= 3 fully crossed blind raters; a 2x2 length design (correct/incorrect x concise/verbose) plus correct and technically wrong paraphrases; a natural stratum only where institutionally permitted; a precision-simulation-based question count (working range 20-30 questions x 8 answers is an estimate, not a decision); threshold-free primary endpoints (D-X2-TAU); provenance ledger and institutional determination beforehand.

**Not "more data" for its own sake:** each element above resolves one named uncertainty (circularity, surface-feature dependence, leakage, provenance, calibration).

## 7. Research infrastructure audit

| Item | Class | Comment |
|---|---|---|
| `run_manifest_v2.py` (new file) | **REQUIRED BEFORE ANY NEW CONFIRMATORY RUN** (minimal) | The v1 tool has validated write-once and provenance weaknesses. Time-box to a single small file; Codex re-audit. |
| Atomic run creation (exclusive sentinel before preflight, `exist_ok=False`, exclusive create/atomic rename) | REQUIRED BEFORE ANY NEW CONFIRMATORY RUN | Core of the v2 tool. |
| `aborted` status in `finally` | REQUIRED BEFORE ANY NEW CONFIRMATORY RUN | Few lines. |
| In-tool protocol/tag verification (no caller-trusted dict) | REQUIRED BEFORE ANY NEW CONFIRMATORY RUN | Prevents misattribution. |
| Mandatory declared inputs and models; full digests | REQUIRED BEFORE ANY NEW CONFIRMATORY RUN | Prevents the X1-D and X2-B gaps. |
| SUT binding (tag + scoped tracked-diff hash + untracked inventory under harness/SUT/input paths) | REQUIRED ONLY FOR SPECIFIC EXPERIMENT (X1-A/B/C) | X3-B and X2-C do not run the SUT. |
| Completed-run linkage (`require_completed_run`) | REQUIRED BEFORE ANY NEW CONFIRMATORY *ANALYSIS* | Small helper. |
| Key-set assertions | REQUIRED ONLY FOR SPECIFIC EXPERIMENT (any new paired aggregation, including O7) | Frozen X3-A verified aligned. |
| Self-test separation | REQUIRED ONLY FOR SPECIFIC EXPERIMENT (an X2-B-on-X2-C harness) | Not needed for X1. |
| Mutation-coverage matrix | REQUIRED ONLY FOR SPECIFIC EXPERIMENT (each X1 protocol) | A protocol content item, not a tool. |
| `try/finally` around monkeypatches (O4), coarse environment hash (O6) | DOCUMENTATION ONLY / NICE TO HAVE | No false-pass route. |
| Wheel-hash lock of the SUT environment | NICE TO HAVE | Record `pip freeze` hash instead; the SUT environment cannot be re-locked without a decision. |
| Editing v1 or rewriting the X3-A/X2-B/X1-D harnesses | NOT NEEDED | Frozen; hash-bound. |
| A generic experiment framework | NOT NEEDED | Endless-engineering risk. |

**Do not block O7 on v2:** O7 is a single-launch, stored-data analysis; record v1's limitation instead.

## 8. O7 final check

**Complete and sound as specified:** REG kept as the primary preregistered estimand and never replaced; A/B/C defined with estimand, unit, statistic, CI construction and factor treatment; the analysis set is closed; R0 is coded independently, from the recovered draw order (persona indices then seed indices via `rng.integers(0, n, n)`; `D[np.ix_(pi, si)].mean()`; `numpy.percentile` linear; persona string-sort and numeric seed order; 6-decimal CSV parsing), in the locked environment (Python 3.12.7, numpy 2.5.2, scipy 1.17.1, hashes asserted), with exact/1e-12 acceptance, hard stop and no Monte Carlo tolerance; evaluation seeds averaged and never resampled; margins and classification rule unchanged; B labelled a conditional seed-level sensitivity interval (df = 4, normality untestable); the five-checkpoint limitation stated; the reporting table defined. The distance-to-boundary arithmetic is correctly demoted to a descriptive remark.

**Remaining flaws or gaps (minor).**
1. **Independence is procedural** (the executor read the frozen code); the spec correctly requires an independent review, but the review scope is not yet written down (below).
2. **Tag naming and script hashing are not specified** (for example `prereg/X3-A-O7/v1`); trivial to add.
3. **Execution dependency wording** prefers `run_manifest_v2`, which does not exist; state explicitly that O7 does not wait for it (v1 with recorded limitations).
4. **Page-limit realism:** the reporting table (main text plus supplement) may exceed some venues' limits; allow the table to move to a supplement without changing the wording rule.
5. **The exact 1e-12 comparison is itself strong evidence** that draw order, indexing and environment match (accidental agreement is not plausible), so no additional sensitivity control for R0 is needed.

**Codex review of the R0 implementation (exact scope).** Confirm: (a) no import, call or copy of `x3a_analyze.py`, `x3a_lib.py`, `x3a_run.py`; (b) the declared draw order and index conventions are implemented exactly and only once; (c) CSV parsing (`float()` of 6-decimal strings), cell means over 20 evaluation seeds in file order, persona string-sort, numeric seed order, seedless Constant-Same broadcast; (d) `numpy.percentile` default method; (e) version and hash assertions run first and hard-stop; (f) registered target values are read only after R0 is computed and compared with `<= 1e-12`; (g) A, B, C are unreachable unless the R0 record shows pass; (h) a fresh `default_rng(42)` per analysis, C's 4-column subsets in ascending seed order; (i) B uses `t(0.975, df=4)` on the five seed aggregates; (j) the classification function reimplemented from the protocol thresholds; (k) key-set and duplicate assertions precede any statistic; (l) outputs are write-once; (m) no analysis beyond A/B/C exists. **Before O7 can run:** ChatGPT's final confirmation of the spec (including the added tag/hash wording), the O7 script written, the Codex review above, the tag and the run manifest. Nothing else is needed.

## 9. Three-paper separation audit

Boundaries to hold: Paper 1 = system dependability and containment; Paper 2 = evaluator validity; Paper 3 = adaptive-policy decomposition in simulation. **Claims that currently cross boundaries:**
1. **`README.md` (public front page)** mixes superseded Paper-2 and Paper-3 results: PPO "statistically significant positive difficulty adaptation" (withdrawn) and rho 0.6975 "with blinded human expert educator ratings" (superseded pilot), plus "178 tests" and "100% Traceable" badges. 29 markdown files mention the superseded rho values 0.6975/0.74/0.9152/0.8358 (README, `research/README.md`, `research/CLAUDE_RESEARCH_INDEX.md`, `docs/paper_draft_ieee.md`, the booklet, older stage reports; a few, such as `CLAUDE.md`, mention them only as labelled-superseded).
2. **Frozen overlap matrix** lists Paper 3 tables such as "6D State Ablation & Speech Robustness" and the title "Guardrailed *Multimodal* Reinforcement Learning": X3-A uses simulated confidence/hesitation, so speech robustness and multimodality are unsupported (Paper 3 evidence is simulation-only).
3. **Speech audit** (`speech_claim_audit.md`, marked "COMPLETE & FROZEN") states acoustic features "cannot mathematically alter" technical scores as a guarantee, while the registry withdrew `P1-C010` (100% insulation) as unmeasured. Either restore the claim through an X1-B-style static path check or keep it as design-only wording; it must not appear as a Paper-1 measured claim or a Paper-3 speech-robustness claim.
4. **Demo behaviour** (runtime adaptive difficulty using seed 123 and a different dimension 4) is not X3-A evidence and must not be used as Paper-3 support.
5. **Paper 1 sub-second latency vs Paper 2 evaluator:** latency of the evaluator is a systems fact; it says nothing about scoring validity; Paper 2's evaluator validity says nothing about containment. Paper 1 must describe the evaluator only as a component.
6. **Paper 2's "safety-hardened composite / adversarial robustness"** is an evaluator-level property (author-set ceilings, exploratory), not system security.

Rules to keep: Paper-2 human alignment does not validate the RL policy; Paper-3 simulation does not establish human benefit; Paper-1 sandbox results do not establish general security; evaluator validity does not establish adaptive learning effectiveness; nothing observed in the demo counts as evidence.

## 10. Hostile reviewer audit (only open attacks; closed ones omitted)

**Paper 1**
| Reviewer | Attack | Severity | Evidence now | Missing | Fixable / new experiment? | Wording alone? |
|---|---|---|---|---|---|---|
| A systems | "Fault tolerance was never tested; your oracle can't fail" | High | Withdrawn claims; mocked-failure tests only | X1-A with mutants | Yes / yes | No |
| A systems | "Sub-second latency but LLM feedback takes seconds; N=100, one machine" | Medium | X1-D warm evaluator latency; archived Qwen timing | End-to-end timing | Yes / small measurement | Partly (narrow to the evaluator) |
| A systems | "Unlocked environment, pin conflicts, one failing test" | Medium | Disclosed | Environment record for new runs | Yes / no | Yes with records |
| B security | "Five of nine attacks cannot distinguish blocked from harmless; static filter bypassable; Docker shares the host kernel (WSL2 VM)" | High | `P1-C003`; dead `RESTRICTED_C_HEADERS` | X1-C layers 1-4 with weakened controls | Yes / yes | No |
| B security | "No threat model against a malicious LLM or prompt injection" | Medium | Design mapping | X1-B | Yes / yes | Partly |
| E HCI/AIED | "No educational or user evidence for a technical-interview assessment system" | Medium | None | Not obtainable without users | No | Yes (scope statement) |

**Paper 2**
| Reviewer | Attack | Severity | Evidence now | Missing | Fixable / new experiment? | Wording alone? |
|---|---|---|---|---|---|---|
| C NLP/evaluation | "Your model learned length" | **Critical** | `X2B-C003` supports the attack | X2-C length-controlled strata | Only via X2-C | No |
| C NLP/evaluation | "Eight developer-built questions; circular tuning overlap" | High | `X2A-C001/C006` | X2-C | Only via X2-C | No |
| C NLP/evaluation | "Undocumented fine-tune; contamination" | High | `X2B-C001/C002` | Trainer records; stratified X2-C | External / X2-C | Partly |
| C NLP/evaluation | "Why ship a composite that is worse than R alone; 'safety-hardened' unsupported" | High | `X2A-C003/C008/C009` | X2-C H3 with rule fixed first | Yes / X2-C | Partly (drop the claim) |
| C NLP/evaluation | "Ethics approval and rater independence?" | High | Withdrawn `P2-C011`; checklist unfilled | Institutional determination and ledger | External | No |
| D ML | "Not usable as a grade: bias -0.134, no threshold" | Medium | `X2A-C007` | D-X2-TAU rule | Yes / no | Yes (limitation) |

**Paper 3**
| Reviewer | Attack | Severity | Evidence now | Missing | Fixable / new experiment? | Wording alone? |
|---|---|---|---|---|---|---|
| D ML/RL | "The learned policy is redundant; contribution is a null in your own simulator" | High | `X3A-C001` (accepted) | Framing and novelty positioning | Framing / no | Yes |
| D ML/RL | "Target is your reward: authored target, oracle coupling; the controller exploits it" | High | `P3-C023`, `X3A-C005` | Nothing new | No | Yes |
| D ML/RL | "Trained on one unseeded candidate with the shield in the loop; evaluated off-distribution; runtime dimension 4 differs" | High | `P3-C017..C019`, `rl_state_alignment.md` | X3-B (not recommended) | No | Yes (state scope: these checkpoints) |
| D ML/RL | "Five seeds; 40 factorial personas are not a population; is the CI valid?" | Medium | `X3A-C001`, Codex O7 lead | O7 robustness | Yes / stored-data only | Partly |
| D ML/RL | "Why delta = 0.12?" | Medium | Pre-registered | Descriptive sensitivity | Optional | Yes |
| E HCI/AIED | "Simulation only; no human benefit" | Medium | Scope statement | None obtainable | No | Yes |
| A systems | "Authors wrote simulator, harness and analysis; no independent review" | Medium | Codex audit; ChatGPT review pending | ChatGPT review | Yes / no | Partly |

## 11. Publication-readiness audit

| Paper | Evidence level (now) |
|---|---|
| Paper 3 | **EARLY DRAFT READY** (evidence exists and is frozen; not manuscript-assembly ready) |
| Paper 1 | **NOT READY** |
| Paper 2 | **NOT READY** (a scoped exploratory note would be EARLY DRAFT READY only after a scope decision and provenance repair) |

| Paper | MUST HAVE BEFORE MANUSCRIPT | MUST HAVE BEFORE SUBMISSION | OPTIONAL STRENGTHENING |
|---|---|---|---|
| 3 | ChatGPT review of `prereg/X3-A/v1`; literature/novelty with verified sources; evidence package; claim-wording constraints; limitations content | Venue requirements and format; authorship/AI-disclosure statements; artifact/code-data release decision; internal claim audit; O7 result if run | O7; delta-sensitivity; action-string recomputation; figures polish |
| 1 | X1-C and X1-B (and X1-A for any fault claim) executed and frozen; reviewed protocols; `run_manifest_v2`; literature; evidence package; environment record | As Paper 3; defect log across builds; disclosure of the failing test | End-to-end latency; X1-B-S; audio-to-score static check |
| 2 | Institutional determination; provenance ledger; D-X2-TAU; X2-C executed and frozen; literature; evidence package | As above plus ethics statements the venue requires | Second-run robustness; extra strata |

## 12. Conference and deadline check (2026-09-20)

| Venue | Official status | Deadline / open? | Scope evidence | Fit and evidence realism | Flags |
|---|---|---|---|---|---|
| **ICETC 2026** (18th, Porto, 14-17 Dec) | Read; no notices after 31 Aug 2026 | **10 Oct 2026, open (20 days)**. The 30 Aug date was superseded by the official 31 Aug notice; not a conflict. Extended twice already | Official CFP: Track 2 AI in Education (adaptive learning, AI in Assessment & Feedback, Ethical AI), Track 4, Track 7 (security of learning platforms, privacy, digital ethics), Track 10 (assessment); multimodal not listed; double-blind; >= 5 two-column pages (EasyChair) | Topically coherent for Paper 1 and Paper 2; **not realistic for Paper 1 by 10 Oct**: unreviewed protocols, no v2, X1-A/B/C unbuilt | Do not plan on another extension |
| **ATIS 2026** (16th, Bengaluru, 14-15 Dec) | Read earlier | **7 Nov 2026 (48 days)** | Track 3 AI, Data Security and Cybersecurity; Springer CCIS, <= 12 pages; double-blind | Realistic first candidate for Paper 1 only if X1-C and X1-B (and a scoped X1-A) freeze by about 25 Oct; fit is partial (containment/dependability, not a pure security paper) | At risk; go/no-go by mid-October |
| **HCI International 2027** (Berlin, 25-30 Jul 2027) | Read earlier | **Proposal (800 words) 9 Oct 2026 (19 days)**; notification 20 Nov; final 29 Jan 2027; registration 12 Feb 2027 | AIS scope: adaptive instructional systems, learner modeling and assessment, evaluation | Best fit for Paper 3; the proposal is short and the full paper follows in January, leaving time for gates. The proposal is manuscript prose and needs Sparsh's go-ahead | HCI audience expects users; frame as component-level decomposition without a learner claim; one registration per submission |
| **ACM SAC 2027 - AIED** (Gwangju, 5-9 Apr 2027) | Main page read; AIED is track 2; track page **unreadable** | 2 Oct 2026 (12 days), track date **unverified** | AIED track exists | Not realistic: needs a complete audited paper in 12 days | Track deadline/length unverified; open-access fees (unverified here) |
| **IEEE AIEI 2027** (Bangalore, 21-23 Jan 2027) | IEEE Systems Council listing only; conference site **unreadable**; second domain `aiei2027.org` seen | 30 Sep 2026 (10 days), **unverified** at the source | "AI Engineering and Innovations" (education is one listed sector) | Not realistic; generic scope | Verify against the IEEE record; possible first edition (age rule) |
| **ICTCS 2026** = 11th Intl. Conf. on **ICT for Competitive Strategies**, Ahmedabad, 16-19 Dec 2026 (`ictcs.in`) | **Read this pass; identity resolved from repository docs** | "September 10 and September 30, 2026" for regular tracks (ambiguous: first/second call?); **open until 30 Sep if the later date is final (10 days)** | Tracks: ICT for Infrastructure and Computation; ICT for Engineering Applications (includes NLP and HCI); ICT for e-Governance. No education track. Springer LNNS, Scopus/EI | Was the repository's old Paper-2 target. Not realistic for Paper 2 (no confirmatory evidence; no ethics record); fit partial (NLP topic) | Page limit and review type not on the page read |
| **ICMETE 2026** = 10th Intl. Conf. on **Micro-electronics and Telecommunication Engineering**, SRM Ghaziabad, 3-4 Dec 2026 (`icmete.in`) | **Read this pass; identity resolved** | **Deadline not on the page read; the repository's "20 Oct" appears to be the ICMETE 2025 extended deadline**: UNVERIFIED for 2026 | Microelectronics/telecommunication | **Poor fit for all three papers** | Drop unless the user supplies a reason |
| **SmartCom 2027** (11th, Goa, 27-30 Jan 2027) | Read earlier | Regular 12 Oct 2026 (22 days) | Eight generic ICT tracks | Not needed; not realistic for Papers 1-2 | Site text stale |
| **ICMLSC 2027** (11th, Tokyo, 29-31 Jan 2027) | Read earlier | 30 Sep 2026 (10 days) | ML and soft computing | Not realistic; not pursued | |
| **IEEE MLNLP 2026** (9th, Xiamen, 26-28 Dec 2026) | Official site **unreadable** | 20 Nov 2026 **unverified** | ML + NLP (secondary sources) | Fits Paper 2 only after X2-C | Name collisions; ninth edition (age rule) |

**Portfolio re-check.** Paper 3 -> HCII AIS primary: **realistic and the best fit**, gated by review and by Sparsh's approval of proposal text. SAC AIED and AIEI as Paper-3 secondaries: **not realistic on their dates and unverified**; keep only as later-cycle options. Paper 1 -> ICETC primary: **too optimistic** (see Section 1); ATIS is the honest first target; ICETC only if a later cycle or another extension appears. Paper 2 -> hold: confirmed; ICTCS 30 Sep is not a candidate. Deadlines do not change experimental standards; nothing in this section ranks venues by acceptance probability.

## 13. "What are we forgetting?"

| Item | Class | Finding |
|---|---|---|
| Literature review, related work, novelty positioning | **MUST** (all three papers) | No related-work, literature or novelty file exists under `research/`; the Zotero library holds no references. Nothing in the repository establishes what is new relative to prior work. |
| Citation/source verification | **MUST** | References only from Zotero or verified sources; currently none. |
| University venue standard (conference age >= 10 years, Scopus/EI, peer-reviewed proceedings) | **MUST (ask Sparsh whether it still applies)** | Recorded in an archived 2026-09-17 audit; unchecked against the portfolio. ICETC (18th, IEEE), ATIS (16th), ICTCS (11th), SmartCom (11th), ICMLSC (11th), HCII (29th), SAC (42nd) meet the age condition; IEEE MLNLP (9th) does not; AIEI edition unknown; ICMETE is the 10th. |
| Authorship, contributor roles, acknowledgements | **MUST** | Not specified; the ethics template mentions co-authorship for raters. |
| AI-tool use disclosure (Claude, Codex, ChatGPT in analysis and writing) | **MUST (per venue)** | Springer, IEEE and ACM require disclosure statements; not addressed anywhere. |
| Ethics and consent for Paper 2 human data; data-protection statement | **MUST** | Checklist is an unfilled template; no institution identified. |
| Demo user data (voice audio, transcripts in SQLite) and privacy statement | **SHOULD** | `privacy_data_flow.md` exists; no consent flow for demo users. |
| Cross-paper overlap and dual-submission rules | **MUST** | Overlap matrix predates the withdrawals; HCII/ICETC/ATIS rules on simultaneous submission and prior publication unchecked; the old monolithic `docs/paper_draft_ieee.md` mixes all three papers. |
| Stale documentation (29 files with superseded numbers; README badges) | **MUST before public release, demo use and artifact statements** | D-F1; documentation only. |
| Code/data release strategy, licences, model redistribution, repository visibility | **MUST (decision)** | Remote `origin` is a GitHub repository; branch is ahead of origin; question bank, human ratings (rater identifiers), derived CrossEncoder (upstream licence) and a 5.8 GB Qwen directory need a release decision. |
| Figures and tables from stored results only | **MUST** | `paper/figures` and `paper/tables` are empty. |
| Statistical reporting conventions (CIs, effect sizes, multiplicity statement) | **SHOULD** | Largely present in the registry. |
| Limitations and threats-to-validity content | **MUST** | Exists in the registry and readiness review; needs assembling. |
| Supplementary material and appendix | **SHOULD** | |
| Claim registry completeness after O7, Codex, X1 | **SHOULD** | Update after each new result. |
| Experiment logs, hashes, tags for evidence packages | **SHOULD** | Present for executed experiments; add freeze tags per package. |
| Model provenance (CrossEncoder trainer records; Qwen file hashes) | **MUST for Paper 2 and X1-B; SHOULD elsewhere** | Trainer request drafted, not sent. |
| Venue templates, page limits, per-page fees, registration and travel | **SHOULD (after venue choice)** | ICETC: >= 5 pages, USD 70 per extra page; ATIS: CCIS 12 pages; HCII: registration per submission. |
| Presentation/slides/demo video | **OPTIONAL** (later) | Only after acceptance; do not build now. |
| Demo rehearsal and claims sheet | **MUST for the demo** | Section 3. |

## 14. Scope-creep audit (drop or defer)

New product features (video/MediaPipe, replacing Qwen with Mistral, ChromaDB, company/domain transfer learning: listed as open decisions in `docs/PROJECT_STATE.md`; **drop**: they change the frozen system and support no planned claim); a new LLM; PPO tuning, reward changes, retraining, W&B training runs (**drop**: the results are frozen and X3-B is unnecessary); extra baselines; a second human benchmark (**drop**: one round is a locked decision); additional persona generators or a second simulator (**defer**: only if a reviewer demands); unnecessary ablations; X1-B-S and extra attack programs not tied to a claim (**defer**); a fix of the failing test for a green suite or a build B (**defer** pending the triage decision); a generic experiment framework and environment re-locking of the SUT (**drop**); ten target venues (**narrow to three or four**); redundant agent reviews (Antigravity, Gemini, NotebookLM) (**drop for now**); a demo video or slides (**defer**); reconciling `.venv` pins (**defer**, document only).

## 15. Dependency graph (shortest defensible)

**Paper 3.** CURRENT (evidence frozen) -> **ChatGPT review** of `prereg/X3-A/v1`, claim map, O7 spec -> GATE (review accepted) -> in parallel: literature/novelty; evidence package; limitations assembly; O7 script -> **Codex R0 review** -> tag -> run O7 (single launch) -> registry rows -> GATE (package frozen) -> [HCII proposal on 9 Oct only after the review gate and Sparsh's go-ahead] -> manuscript assembly -> internal review (ChatGPT claim audit) -> venue requirements check -> submission (HCII final 29 Jan 2027 if the proposal is accepted).

**Paper 1.** CURRENT -> ChatGPT review of corrected X1 designs -> `run_manifest_v2` (minimal) -> Codex re-audit -> GATE -> decision on the failing-test triage -> X1-C construct + mutation dry run -> tag -> run -> freeze (with the X1-B static check) -> GATE -> X1-B invariance (Qwen confirmed) -> tag -> run -> freeze -> X1-A claim-scoped scenarios -> tag -> run -> freeze -> (end-to-end latency) -> evidence package -> literature -> GATE -> manuscript assembly -> internal review -> submission (ATIS 7 Nov only if the gates clear).

**Paper 2.** CURRENT (exploratory only) -> Sparsh sends institutional and trainer enquiries -> **GATE: institutional determination** -> D-X2-TAU decision and precision simulation -> **GATE: authors and raters recruited, consent/ledger ready** -> tag `prereg/X2-C` -> item authoring -> item freeze -> blind rating -> gold freeze -> evaluator run once (and the X2-B arm once) -> analysis as registered -> freeze -> evidence package -> literature -> manuscript assembly -> internal review -> submission (no listed date is compatible). Alternative branch (decision): a scoped exploratory note only after provenance can be stated truthfully.

**Cross-paper parallel plan (no interference).** One batched ChatGPT review session (all tagged protocols, X1 designs, O7 spec, Paper-3 claims); enquiries sent by Sparsh; literature workstream shared by all three; stale-document banners (D-F1) and README correction (documentation only); evidence-package scaffolding; demo verification (independent of research gates); `run_manifest_v2` (only Paper 1 needs it). Papers 1 and 3 do not share files; keep Codex and Claude on separate worktrees.

## 16. Final decision table

| Item | Current status | Evidence | Must do? | Blocker? | Owner | Earliest safe next action |
|---|---|---|---|---|---|---|
| Demo | Verification stale | Docs 2026-08-17; SUT changed since | Yes (if demoing) | For any demo | Sparsh (Claude prepares the checklist) | Structured verification on the demo machine |
| O7 | Spec approved in principle; not run | `X3A_O7_SENSITIVITY_SPEC.md` | Should | No | Sparsh + ChatGPT approve; Claude implements; Codex reviews | ChatGPT confirmation, then script |
| `run_manifest_v2` | Not built | Codex O5/O20/O17 validated | Yes (before new confirmatory runs) | For X1 | Claude; Codex re-audit | Minimal spec (Section 7) after design review |
| X1-C | Not built | Withdrawn claims; design exists | Yes for containment claims | Yes for Paper 1 | Claude builds; ChatGPT reviews | ChatGPT design review |
| X1-B | Not built; design corrected | Fixed-answer invariance | Yes for isolation claims | Yes for that claim | Claude; Qwen availability | Channel enumeration (read-only) |
| X1-A | Not built | Enumeration missing | Yes for fault claims (scoped) | Yes for that claim | Claude | Enumeration table |
| X2-C | Blocked | Ethics/provenance unstarted | Yes for any validity claim | Yes for Paper 2 | Sparsh (external) | Send the enquiries |
| X3-B | Parked | Trigger not fired; D-N2 open | No | No | - | None |
| Paper-3 evidence package | Not built | Registry supports it | Yes | No | Claude | Scaffold after ChatGPT review |
| Paper-1 evidence package | Not built | X1 incomplete | Yes (later) | After X1 | Claude | Scaffold with placeholders |
| Paper-2 evidence package | Not built | Exploratory only | Yes (later) | After X2-C | Claude | Scaffold with placeholders |
| Literature | Not started | No files; Zotero empty | Yes | Yes for manuscripts | Claude/Sparsh with verified sources | Start a source list in Zotero (with Sparsh's approval) |
| Provenance (model, raters) | Requests unsent | `MODEL_PROVENANCE_REQUEST.md` | Yes (Paper 2, X1-B hashes) | Yes for Paper 2 | Sparsh | Send trainer request |
| Ethics | Template unfilled | `ETHICS_CHECKLIST.md` | Yes (Paper 2) | Yes | Sparsh (institution) | Send the institutional enquiry |
| Venue selection | Provisional; identities resolved | Section 12 | Yes | No | Sparsh | Confirm the university venue rule; drop ICMETE |
| Manuscript drafting | Not authorised | - | Later | Gated by reviews | - | None before gates |
| Internal review | Not started | - | Yes | - | ChatGPT, Codex | Batched review session |
| Submission | None | - | Later | - | Sparsh | None |

## 17. Claude's independent recommendation

1. **First:** Sparsh sends the two external enquiries (institutional/ethics and CrossEncoder provenance) and hands ChatGPT one batched review package; both cost little and unblock everything else.
2. **Do not:** chase the 30 Sep-12 Oct dates with Papers 1 or 2; change the product or build a build B for a green test; run X3-B; run O7 before its R0 code is reviewed; submit an exploratory Paper 2 without provenance repair; build a generic experiment framework; treat the demo as evidence.
3. **Biggest scientific risk:** Paper 2's evaluator validity. The exploratory data already show a length-only baseline matching the derived model and the composite below R-only; if X2-C confirms this, Paper 2's core contribution and the evaluator's role in Paper 1 and the demo are weakened.
4. **Biggest execution risk:** the external human/ethics gate: unstarted, unowned lead time, and it cannot be compressed.
5. **Write first:** Paper 3, after ChatGPT review and literature.
6. **Do not rush:** Paper 2 (and Paper 1's claims sections).
7. **Done building the product?** For research purposes yes, with two caveats: the demo verification may reveal defects, and X1 experiments may reveal defects to be handled under the defect policy. The research **instrumentation** (v2, X1 harnesses) is not built.
8. **Done designing experiments?** Paper 3 yes; Paper 1 not yet (corrected designs need review, X1-A enumeration missing); Paper 2 not yet (D-X2-TAU, authoring pathway).
9. **At the evidence-packaging stage?** Only for Paper 3.
10. **What I would change in the current plan:** (a) demote ICETC for Paper 1 (ATIS 7 Nov as the honest first target, or a later cycle); (b) treat O7 as SHOULD and do not block it on v2; (c) add a literature/novelty workstream now; (d) add a demo verification and claims sheet; (e) make the ChatGPT protocol review a single batched, explicit checklist, because it is the largest independent review not yet done; (f) resolve the university venue rule and drop ICMETE; (g) scope X1-A by claims and pair the X1-B static check with X1-C; add an audio-to-score path check or drop the insulation wording; (h) add an end-to-end latency measurement or narrow the wording; (i) decide authorship and AI-tool disclosure early; (j) fix the stale README and the 29 stale files by banner (documentation only) before any public statement; (k) correct my earlier statement that ICTCS/ICMETE were unidentifiable.

**What remains uncertain (not invented):** whether the university venue rule still applies; the intended ICTCS deadline (10 or 30 Sep); ICMETE's 2026 deadline; SAC AIED, IEEE AIEI and IEEE MLNLP official terms; the current live behaviour of the demo (not run); the developer's intent for the dimension-4 change; the repository's release/visibility plan.
