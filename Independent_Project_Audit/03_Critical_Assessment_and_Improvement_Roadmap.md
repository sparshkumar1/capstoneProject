# 03 — Critical Assessment and Improvement Roadmap

*Independent audit document. This is the most consequential document in the audit: it gives a direct, unhedged judgment of quality (Part 6 of the audit brief) and a prioritized, executable roadmap (Part 7). Every judgment below is traceable to a specific finding in `01_Complete_Project_Summary.md`, `02_Testing_and_Evaluation_Summary.md`, or the underlying `_research/` files.*

---

## 6.1 Overall Project Quality

**Is the implementation genuinely good?** Yes, for the application layer. The FastAPI/React application, the Docker sandbox, the SQLite persistence layer, the audio pipeline, and the fail-closed error handling (never fabricate a score, never run untrusted code if Docker is down) are real, coherent, and reasonably well-engineered for a student capstone. The degrade-gracefully pattern throughout `interview_orchestrator.py` (every sub-agent import guarded, non-RL fallback always available) is a sound design choice for a system with many optional AI dependencies.

**Is the architecture sound?** Mostly. Two concrete architectural weaknesses were found: (1) the admin dashboard reads from an in-memory dict instead of the persisted database, so it silently diverges from ground truth across restarts; (2) the evaluator's Flask HTTP API appears to be dead weight — a whole microservice process is started by the launcher but never called over HTTP by the component that's supposed to use it.

**Are important modules implemented correctly?** The scoring formula, the guardrail logic, and the sandbox hardening are all implemented exactly as documented — verified by direct code reading, not assumed. The RL environment is a correctly-specified Gym environment. Where "correctly implemented" and "actually effective" diverge is the RL policy itself (see 6.1 continued below and §6.3): it is correctly *implemented*, but its real-world value is a separate, unresolved question.

**Is the system coherent end to end?** Yes — a candidate's answer genuinely flows from voice/code input through real scoring, real difficulty adaptation, and real persistence, without a hidden mock substituting for any of those stages in the production path.

**Hidden weaknesses found that are not visible from a surface read:**
- `EVALUATOR_MOCK_MODE` is documented everywhere (CI, docker-compose, test docstrings, `CLAUDE.md` itself) as the standard way to run tests quickly, but **no code anywhere reads it**. Every test run — "mocked" or not — loads the real SBERT/FAISS/CrossEncoder models. This is not a correctness bug (the real models work), but it means a documented performance/determinism lever doesn't actually exist, and any assumption that CI runs "fast, mocked" tests is false.
- The deployed PPO checkpoint (`rl/checkpoints/seed_123/ppo_final.zip`) is a **different file by SHA-256** from the checkpoint that produced the frozen Paper-3 result tables, despite sharing a seed number. Nothing in the testing package or the deployed system flags this when a reader might reasonably assume "the checkpoint I'm running is the one the paper reports on."

**Unnecessary or poorly justified components:** the Flask evaluator HTTP API (likely unused in production) and the duplicate, stale inline guardrail fallback inside `interview_env.py` (which still encodes the *old*, pre-fix G5 boundary and would silently reintroduce the just-closed safety gap if the normal import path ever broke).

**Strongest parts:** the fail-closed error handling; the hardened, genuinely tested Docker sandbox; the Gym-compliant RL environment with real step-level logging; the project's own internal scientific-truth audit apparatus (unusually rigorous — it finds and withdraws its own overstated claims, which is a sign of a team that takes evidence seriously).

**Weakest parts:** the gap between what the RL/evaluator research claims imply ("PPO improves difficulty tracking," "the evaluator is validated against human judgment") and what the project's own frozen evidence actually shows (PPO's contribution is statistically indistinguishable from a trivial baseline under the guardrail shield; the evaluator-human correlation is weak, ρ=0.38, on a small constructed sample); and the currency of the project's public-facing documentation (root `README.md` is confirmed stale on both its test-count badge and its headline human-validation figure).

---

## 6.2 Testing Quality

Covered in detail in document 02. Summary judgment: **the testing package is genuinely meaningful, not padded.** The new `T-N` scripts exercise real production code, not mocks, and their claims trace cleanly to stored logs. Coverage is honestly scoped — three categories are explicitly documentation-only, and the package says so rather than inflating a "test count." The main residual testing-quality issues are process-level (the guardrail-fix approval has no independent artifact) and organizational (a scripts folder with no test scripts in it), not evidentiary fabrication.

---

## 6.3 Results Quality — Project-by-Project

### Paper 1 (systems/latency/security)
**Good but limited.** Real, measured latency and concurrency numbers exist, with an honest correction (the 1960.8ms mean is a single cold-start-outlier artifact; the median 404.6ms is the representative figure). Security testing is honestly downgraded from an earlier "9/9 contained" framing to "4/9 outcomes actually discriminate" — this is exactly the kind of self-correction that strengthens credibility rather than weakening it, *provided it is the version actually cited going forward*.

### Paper 2 (evaluator vs. human judgment)
**Preliminary, and the project's own framing is correct.** ρ=0.3812 (3 raters, 64 constructed answers to 8 questions), CI [0.158, 0.577] — a moderate-to-weak correlation with a wide interval, on researcher-constructed (not naturally elicited) answers. The CrossEncoder responsible for 50% of the composite's weight has an incomplete, partially-contradicted provenance. A trivial length-only baseline matches or exceeds the derived CrossEncoder's correlation with the human gold labels — a genuinely unflattering finding the project registered rather than suppressed. **This evidence does not support a strong claim of evaluator validity and should not be presented as more than exploratory/initial** — which is exactly how `CLAUDE.md` already frames it. The risk is not the research record; it is that downstream documents (notably the root README) do not yet reflect this framing.

### Paper 3 (PPO difficulty controller)
**This is the most important weak result in the project, and it must be stated plainly: the project's own confirmatory evidence finds no detectable value from the learned PPO policy over a trivial constant action, once the guardrail safety layer is in place.** Specifically:
- The primary baseline table shows a rule-based Heuristic (MAE 0.473) beating every PPO variant (0.666–0.804), including PPO+Guardrails (0.673–0.687).
- A pre-registered confirmatory test on a held-out 40-persona grid (`X3A-C001`) reports a 95% CI of [−0.0818, 0.0021] for PPO's contribution over a constant action under the shield — statistically indistinguishable from zero, and PPO is *more* volatile than the constant baseline under the same shield.
- This audit's own independent read of the policy's univariate sensitivity sweep corroborates the pattern from a different angle: the raw policy outputs "Same" across the entire range of performance, confidence, hesitation, and progress when each is varied in isolation.
- The reward function used to train the policy is ~60–90% weighted toward imitating a hand-coded rule oracle, not toward the tracking metric the policy is actually evaluated on — a plausible causal explanation for why training "succeeds" (reward stabilizes, action distribution shifts consistently across 5 seeds) without that translating into measurable superiority on the evaluation metric.

This is **not** a case of weak methodology — the multi-seed training, matched baseline comparison, bootstrap CIs, and pre-registered confirmatory test are all methodologically sound, arguably more rigorous than most capstone RL work. The result itself is simply unfavorable to the "PPO adds value" hypothesis, and the project's own canonical-truth document already says so. **The improvement needed here is not more RL engineering — it is honest reframing of what the system's contribution actually is** (a safety-shield-plus-heuristic system that happens to include a PPO component whose marginal value is not established), in every downstream document that still implies otherwise.

### Testing-phase original findings (guardrail gap, launch.py crash)
**Strong and convincing**, within their narrow, disclosed scope — these are small, real, well-evidenced, regression-tested engineering fixes with before/after proof via log diffing, not research claims.

---

## 6.4 Academic and IEEE Suitability

The project's own evidence, read honestly, supports a **defensible but modest** technical contribution: a working, safety-shielded adaptive-difficulty interview system, with a composite (non-LLM) answer evaluator, whose principal *methodologically interesting* finding is a **negative/equivalence result** — a pre-registered confirmatory test showing the learned RL component does not demonstrably outperform a trivial constant policy once a safety shield is in place. This is a legitimate, publishable finding (null/equivalence results are valuable, and the project's `PHASE0_DECISION_LOCK.md`/`X3A-C001` apparatus is unusually careful about how to report it correctly) — but it is a **different and more modest** claim than "we built an RL system that improves interview difficulty adaptation," which is the claim implied by several still-live documents (the old root canonical-truth file, `PAPER3_FINAL_FREEZE.md`'s still-displayed "eliminates 100% of violations" language, and the root README's framing).

**Claims that can be defended as-is:** the engineering (sandbox hardening, fail-closed evaluator, orchestrator robustness); the evaluator formula's internal correctness; the RL environment's correctness; the multi-seed training methodology; the project's own self-audit discipline.

**Claims that must be weakened or reframed before submission:** "PPO improves difficulty tracking" (already withdrawn by the project's own canonical-truth document — this withdrawal must propagate to every paper draft, not just the audit trail); "the evaluator correlates with human judgment" (true but weak — must retain the ρ=0.38/CI framing, not a stronger historical number); "guardrails eliminate 100% of out-of-bounds transitions" (still asserted in the frozen `PAPER3_FINAL_FREEZE.md` banner document, contradicted by the current canonical-truth position — any paper drawing on the frozen file's language must use the corrected framing instead); "the CrossEncoder" should never be called off-the-shelf.

**Reproducibility:** strong for the engineering/testing claims (scripts, logs, hashes all check out); adequate for the RL/evaluator research claims (seeds, configs, and raw CSVs are stored and hash-verified) but undermined by the unresolved deployed-vs-evaluated checkpoint hash mismatch and the `.venv` pin-vs-installed-version drift, neither of which has been resolved.

**Do not predict acceptance.** This audit makes no claim about any venue's decision; it only assesses whether the evidence supports the claims being made, which is a different question.

---

## 6.5 Results That Are Not Good Enough — Direct Treatment

### Weak result 1: "PPO improves difficulty tracking"
1. **What's weak:** the claim that the learned policy adds adaptive value is not supported — a trivial constant action under the same guardrails matches it.
2. **Why:** the reward function trains the policy to imitate a hand-coded oracle, not to optimize the tracking metric it is evaluated on; the guardrail shield does nearly all of the measurable work.
3. **Where the problem sits:** methodology/experiment design (the training objective and evaluation objective are misaligned), not a bug and not insufficient data (5 seeds, matched baselines, bootstrap CIs are all adequate).
4. **Realistically improvable?** Only partially, within capstone scope. Retraining with a reward directly tied to the tracking metric is the correct fix but constitutes a new experiment requiring pre-registration and explicit approval per the project's own governance rules — not something to do silently.
5. **Recommended change:** either (a) register and run a new experiment with an outcome-aligned reward (not an imitation-of-oracle reward), and report it as a new, separate result, or (b) accept the null result and reframe the contribution as "a safety-shielded adaptive system; the learned component's marginal value under the shield is an open question answered negatively in this study," which is the scientifically honest and already partially-written position.
6. **Experiment to repeat:** a reward-function ablation (outcome-weighted vs. imitation-weighted) trained and evaluated under the identical 5-seed/25-session/40-persona-grid protocol already used for `X3A-C001`, so the new result is directly comparable.
7. **What would count as meaningful improvement:** a confirmatory CI for PPO's contribution over the constant-action-plus-guardrails baseline that excludes zero, in the favorable direction, on a held-out grid — the same bar the project already set for itself.
8. **Risks:** retraining risks violating the project's own frozen-artifact and pre-registration rules if done without the described registration step; it also risks simply reproducing the same null result with a different reward, which is itself useful information but should be anticipated, not treated as a surprise.
9. **Verification:** repeat the exact `X3A-C001` confirmatory protocol against the new policy; only trust a result that comes from that pre-registered, held-out procedure, not from re-examining the training-time metrics.

### Weak result 2: Evaluator–human correlation (ρ=0.38)
1. **What's weak:** a moderate-to-weak correlation with a wide CI, on a small, researcher-constructed sample.
2. **Why:** small N (64 cases, 8 questions, 3 raters), constructed (not naturally elicited) answers, and a length-only baseline performing comparably to the derived CrossEncoder on the same benchmark.
3. **Where the problem sits:** dataset (size and construction method) and possibly model (CrossEncoder provenance gap), not an implementation bug — the pipeline is implemented exactly as specified.
4. **Realistically improvable?** Yes — the project has already drafted a plan for this (`research/audit/X2_PROTOCOL_DRAFT.md`), with a locked decision that there will be no second human round beyond this planned confirmatory study.
5. **Recommended change:** execute the planned X2-C confirmatory study with naturally elicited (not constructed) answers, more raters, and more questions, as already specified.
6. **Experiment to repeat:** the X2-C protocol exactly as drafted, pre-registered per the project's own rules.
7. **Meaningful improvement:** a materially tighter CI and a point estimate that remains interpretable (even if still moderate) on a methodologically stronger sample; separately, a length-bias probe (holding concept content fixed while varying verbosity) to close a currently complete blind spot.
8. **Risks:** a new study could produce an even weaker correlation — this must be reported regardless of direction, consistent with the project's stated decision not to run a third round.
9. **Verification:** the new ρ and CI must be computed by the same pre-registered recompute pipeline (hash-checked CSV, stored script) used for the current figure, not hand-calculated.

### Weak result (process, not scientific): README/documentation currency
1. **What's weak:** the project's most visible document (`README.md`) states the superseded ρ=0.6975 pilot as the current headline result and describes the already-completed 64-case study as "pending"; its test-count badge (178) does not match a direct recount (298 collected).
2. **Why it matters:** this is the first thing any external reader — including an IEEE reviewer who happens to check the repository — will see, and it directly contradicts the project's own corrected position.
3. **Evidence:** `README.md` lines ~42-55, 117-127; direct `pytest --collect-only` recount in this audit (298 vs. 178).
4. **Fix:** a direct text edit — no experiment required. This is the single highest-value, lowest-cost item in this entire roadmap.
5. **Verification:** re-read the file after editing and confirm the cited figures match `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` and a fresh test run exactly.

---

## 7. Prioritized Improvement Roadmap

### P0 — Must fix before final submission

| Field | ID P0-1 |
|---|---|
| Priority | **Critical** |
| Current problem | Root `README.md` presents the superseded ρ=0.6975 pilot as the current headline human-validation result and describes the completed 64-case/3-rater study (ρ=0.3812) as "designed and pending"; stale "178 tests"/"100% Traceable" badges |
| Evidence | `README.md` lines ~42-55, 117-127; `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §C; this audit's direct `pytest --collect-only` recount (298 tests) |
| Why it matters | This is the project's highest-traffic document; it actively misinforms a reader in the *more favorable* direction, the opposite of the project's own evidentiary discipline elsewhere |
| Root cause | Documentation not updated when Phase-0 canonical-truth work superseded the old pilot number |
| Proposed solution | Replace the ρ=0.6975 headline with ρ=0.3812 (CI [0.158,0.577], 3 raters, 64 cases) and remove the "pending" framing; update or remove the stale test-count badge |
| Files/modules affected | `README.md` |
| Required experiment | None — documentation correction only |
| Expected benefit | Removes the single clearest instance of the project's public face contradicting its own verified evidence |
| Regression risk | None |
| Validation method | Re-read file; diff cited numbers against `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` |
| Completion criterion | No superseded number appears unflagged in `README.md` |
| Academic value | Prevents a reviewer who checks the repo from immediately finding a contradiction with the paper's own stated evidence |

| Field | ID P0-2 |
|---|---|
| Priority | **Critical** |
| Current problem | Any paper draft or presentation still asserting "PPO improves difficulty tracking" contradicts the project's own confirmatory finding (`X3A-C001`: 95% CI [−0.0818, 0.0021], no detectable PPO contribution over a constant action under the guardrail shield) |
| Evidence | `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` line 77 (P0-2, explicitly "withdrawn"); `research/claims/CLAIM_REGISTRY.csv` row `X3A-C001`; this audit's independent sensitivity-sweep corroboration |
| Why it matters | Presenting a withdrawn claim as current in a submitted paper is a correctness/academic-integrity risk, not merely a style issue |
| Root cause | Multiple paper drafts and the still-frozen `PAPER3_FINAL_FREEZE.md` predate the withdrawal and were never reconciled with it |
| Proposed solution | Audit every paper draft (`paper/manuscripts/paper3/*`, `final_deliverables/03_Research_Paper/*`) for this language and replace with the equivalence/null-result framing already established in canonical truth |
| Files/modules affected | `paper/manuscripts/paper3/manuscript.md`, any RL-related sections of `final_deliverables/02_University_Project_Report/`, presentation deck |
| Required experiment | None — reframing, not new research, unless the project chooses to pursue Roadmap item P1-1 below |
| Expected benefit | Academic claims match the project's own strongest-tier evidence |
| Regression risk | None — this narrows a claim, it does not require new work |
| Validation method | Line-by-line grep of every paper/report draft for "PPO improves"/"outperforms baseline" language, cross-checked against canonical truth |
| Completion criterion | Zero unreconciled instances of the withdrawn claim in any document intended for submission |
| Academic value | Converts a potential credibility risk into the project's most interesting, defensible finding (a well-designed null result) |

| Field | ID P0-3 |
|---|---|
| Priority | **Critical** |
| Current problem | Two independent, non-overlapping "IEEE paper" tracks exist (`paper/manuscripts/paper1-3`, venue-committed to ICETC2026/HCII2027, vs. `final_deliverables/03_Research_Paper`, a narrower guardrail-bug paper from a later session) with no cross-reference between them |
| Evidence | `_research/06_academic_materials_and_paper_readiness.md` §1, §3, §7 (item 2) |
| Why it matters | Submitting conflicting or duplicate work, or being unclear about which paper is "the" deliverable, risks both self-plagiarism/overlap concerns and simple confusion at submission time |
| Root cause | Two separate work sessions produced two separate papers without reconciling scope |
| Proposed solution | Explicit decision (user-level, not automated): which paper is the capstone's primary IEEE deliverable; if both are intended for different venues, document that explicitly and check for content overlap |
| Files/modules affected | `paper/manuscripts/*`, `final_deliverables/03_Research_Paper/*`, `paper/README.md`, `docs/PROJECT_STATE.md` |
| Required experiment | None |
| Expected benefit | Removes ambiguity before any submission deadline |
| Regression risk | None |
| Validation method | A single reconciliation document stating the final decision, referenced from both `paper/README.md` and `docs/PROJECT_STATE.md` |
| Completion criterion | `paper/README.md` and `docs/PROJECT_STATE.md` both reflect the actual, current venue/paper status (currently both still say "venue TBD," which is itself stale) |
| Academic value | Prevents submission-time confusion and duplicate-work risk |

### P1 — High-value improvements

| Field | ID P1-1 |
|---|---|
| Priority | **High** |
| Current problem | The RL reward function is ~60-90% weighted toward imitating a hand-coded oracle rather than the tracking metric used for evaluation — a plausible root cause of the null PPO result |
| Evidence | `rl/env/interview_env.py` lines 340-398 (reward code); `_research/04_rl_ppo_evaluation.md` §6 |
| Why it matters | Determines whether the null result reflects a genuine ceiling (guardrails are sufficient; RL adds nothing achievable) or a fixable training/evaluation misalignment |
| Root cause | Reward and evaluation objectives were not aligned at design time |
| Proposed solution | Design and pre-register a new experiment with an outcome-aligned reward (directly rewarding reduced tracking error, not oracle agreement), trained and evaluated under the same protocol as `X3A-C001` |
| Files/modules affected | New files only — per `CLAUDE.md`, do not modify frozen `rl/env/interview_env.py` reward definitions without approval; implement as a new, separately versioned environment/experiment |
| Required experiment | New pre-registered experiment (X4 or similar), 5 seeds minimum, same baseline comparison design as Paper 3 |
| Expected benefit | Either demonstrates genuine PPO value under a better-aligned objective, or further strengthens the equivalence finding with a second, independent confirmation |
| Regression risk | Consumes significant time; may simply reproduce the null result |
| Validation method | Same confirmatory-grid CI test used for `X3A-C001` |
| Completion criterion | A new, stored, hash-verified result comparable to `X3A-C001` |
| Academic value | Directly strengthens or clarifies the project's central RL finding — the single highest-value remaining research question |

| Field | ID P1-2 |
|---|---|
| Priority | **High** |
| Current problem | CrossEncoder fine-tuning provenance (data, procedure, author) is unrecoverable; a second, discarded checkpoint with different weights exists with no documented selection rationale |
| Evidence | `research/audit/P0_1_CROSSENCODER_FORENSIC.md`; `_research/05_ml_evaluator_evaluation.md` §2 |
| Why it matters | 50% of the evaluator's composite score weight rests on a model whose training data cannot be audited for leakage, bias, or relevance to this specific question set |
| Root cause | No training script, dataset, or documentation was retained alongside the checkpoint |
| Proposed solution | Either locate the original training artifacts (ask whoever produced the checkpoint) and document train/validation overlap against the benchmark questions, or explicitly abandon recovery and run a robustness comparison against the unmodified upstream checkpoint to bound how much the undocumented fine-tune changes behavior |
| Files/modules affected | `services/evaluator/models/tuned_model2/`, new comparison scripts only |
| Required experiment | A new, pre-registered comparison: tuned checkpoint vs. stock `cross-encoder/ms-marco-MiniLM-L-6-v2`, same benchmark questions |
| Expected benefit | Either recovers missing provenance or bounds the uncertainty it introduces |
| Regression risk | None to production (read-only comparison); requires explicit approval per `CLAUDE.md`'s frozen-artifact rules before execution |
| Validation method | Compare correlation/ablation numbers for both checkpoints against the same human gold file |
| Completion criterion | A documented, hash-verified comparison result exists |
| Academic value | Converts an open provenance gap into either a resolved fact or an honestly bounded limitation |

| Field | ID P1-3 |
|---|---|
| Priority | **High** |
| Current problem | No length-bias test exists for the evaluator at all — a classic failure mode for embedding + cross-encoder composites is completely unexamined |
| Evidence | `_research/05_ml_evaluator_evaluation.md` §5 |
| Why it matters | A length-sensitive evaluator would systematically reward verbosity over correctness, undermining the "safety-hardened" framing the project already claims for the evaluator |
| Root cause | No test was ever written to isolate length as a variable |
| Proposed solution | Construct answer sets holding concept content fixed while varying length/verbosity; score through the real `evaluate()` pipeline; measure score variance attributable to length alone |
| Files/modules affected | New test file under `tests/unit/` or `testing_and_evaluation/ml_evaluation/` |
| Required experiment | Not a pre-registered research experiment — a standard engineering test, can be added directly |
| Expected benefit | Either confirms the pipeline is length-robust (strengthens the evaluator's credibility) or surfaces a concrete, fixable bias |
| Regression risk | None |
| Validation method | New test passes/fails against a defined tolerance for score variance across length-only variants |
| Completion criterion | Test exists, runs, and its result (pass or documented failure) is recorded |
| Academic value | Closes a currently complete blind spot directly relevant to the evaluator's core validity claim |

| Field | ID P1-4 |
|---|---|
| Priority | **High** |
| Current problem | The deployed PPO checkpoint (`rl/checkpoints/seed_123/ppo_final.zip`) differs by SHA-256 from the checkpoint that produced the frozen Paper-3 result tables for nominally the same seed |
| Evidence | `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` line 79; independently cross-confirmed in `_research/02_testing_package_audit.md` and `_research/04_rl_ppo_evaluation.md` §3 |
| Why it matters | Any claim that "the deployed system behaves as described in Paper 3" is not strictly supported — the two checkpoints are different files |
| Root cause | Unclear — not established by any artifact; could be a re-save, a different training run promoted later, or a copy error |
| Proposed solution | Determine which checkpoint is correct/intended for deployment; either replace the deployed checkpoint with the evaluated one, or explicitly document the difference and re-run the sanity checks against whichever is kept |
| Files/modules affected | `rl/checkpoints/seed_123/` (deployment location only — do not touch the frozen `research/experiments/paper3/checkpoints/` copy) |
| Required experiment | None — a provenance/deployment reconciliation, not new research |
| Expected benefit | Removes a specific, concrete reproducibility gap |
| Regression risk | Low if handled carefully; replacing a checkpoint requires re-running `T-N02` against the replacement |
| Validation method | SHA-256 comparison before/after; rerun `T-N02_ppo_checkpoint_sanity_check.py` |
| Completion criterion | Deployed and evaluated checkpoints match by hash, or the discrepancy is explicitly documented everywhere it matters |
| Academic value | Closes a reproducibility gap a careful reviewer would likely find |

### P2 — Useful improvements

- **P2-1:** Wire `EVALUATOR_MOCK_MODE` to an actual code path, or remove it from `CLAUDE.md`/CI/docker-compose/test docstrings so documentation matches behavior. *Files: `services/evaluator/app.py`, `.github/workflows/ci.yml`, `docker-compose.yml`, two test file docstrings.* Documentation/code-drift fix, not a correctness fix — real models already run in CI regardless.
- **P2-2:** Wire the admin dashboard (`/api/admin/*`) to read from SQLite instead of the in-memory `SESSIONS` dict, so historical sessions survive a backend restart. *File: `apps/backend/main.py` lines 1184-1247.*
- **P2-3:** Determine whether the evaluator's Flask HTTP API is actually used anywhere (`grep -rn "localhost:5000"`); if not, stop starting it from `launch.py` to reduce redundant process overhead and reviewer confusion about the real request path.
- **P2-4:** Fix the pre-existing docstring/code mismatch in guardrail rule G2 (`rl/guardrails.py`) — the docstring describes an `hes > 0.85 → Easier` branch that the code never implements.
- **P2-5:** Update the stale duplicate guardrail fallback inside `rl/env/interview_env.py` (still encodes the old, pre-fix G5 boundary) so a broken import path doesn't silently reintroduce the just-closed safety gap.
- **P2-6:** Update `docs/PROJECT_STATE.md`'s pointer from the old `CANONICAL_SCIENTIFIC_TRUTH.md` to `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`, and its stale "venue TBD" line.
- **P2-7:** Resolve or explain the `v1.0-paper3-complete` git tag, which is cited repeatedly as the Paper-3 freeze point but does not exist in the current checkout's tag list (the underlying commit does exist and is correct).
- **P2-8:** Add a short, explicit "superseded — see CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md" pointer near (not inside) `research/audit/rho_provenance.md`'s §3 and `research/CLAUDE_RESEARCH_INDEX.md`, since both still carry dead instructions recommending the superseded ρ=0.6975 figure, without touching their frozen bytes.
- **P2-9:** Run the already-identified-but-unresolved ablation-pipeline provenance question (`ablation/results/rl_ablation_missing_input.txt` vs. `rl_ablation_summary.md`) to determine whether the favorable "adaptation ρ=0.871" metric reported there was produced by the same rigor as the audited tracking-MAE pipeline, before it is used to support any "PPO adds value" claim.

### P3 — Optional enhancements

- **P3-1:** Re-verify the two old canonical-truth files' SHA-256 hashes against `SCIENTIFIC_TRUTH_SUPERSESSION.md`'s recorded values (quick, low-stakes confirmation).
- **P3-2:** Re-hash the three Paper-2 result CSVs cited in `CLAIM_REGISTRY.csv` to close the remaining OBSERVATION-tier (not independently re-verified) gaps in this audit.
- **P3-3:** Recompute the ICC/Krippendorff inter-rater reliability statistics from the raw rater files, rather than relying on the registry's citation of an earlier recomputation.
- **P3-4:** Cosmetic: rename or relocate `testing_and_evaluation/scripts/` (document-formatting utilities) so its contents match its name.

---

## Execution Order

1. **P0-1 (README fix)** — immediate, zero dependencies, highest visibility-to-cost ratio.
2. **P0-2 (claim reframing across paper drafts)** and **P0-3 (paper-track reconciliation)** — do together, since reconciling which paper is primary determines which draft needs the reframing applied.
3. **P1-4 (checkpoint hash reconciliation)** before any further RL work, since P1-1 (reward redesign) would otherwise be built on an already-ambiguous checkpoint lineage.
4. **P1-2 (CrossEncoder provenance) and P1-3 (length-bias test)** can run in parallel with each other and with P1-4 — independent of the RL track.
5. **P1-1 (reward-redesign experiment)** last among P1 items — it is the most expensive and requires the pre-registration step `CLAUDE.md` mandates; should not start until P0/P1-4 are settled, since its baseline comparison depends on a resolved checkpoint identity.
6. **P2 items** are independent of each other and of the P0/P1 track; can be done opportunistically.
7. **P3 items** are closeout/completeness tasks with no urgency.
