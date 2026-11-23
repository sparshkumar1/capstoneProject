# Springer/IEEE-Draft Paper Content Analysis

**Source document:** `Details/Coordination_Specialization_and_Bounded_Authority_in_Adaptive_Technical Interview_Systems_A_Replay_Based_Decomposition_Study (1).pdf` (20 pages, Springer `llncs`-style single-column, "Anonymous Author(s)" / "Anonymous Institution", 25 references).

**Related repo artifacts (same paper lineage):**
- `main.pdf` (repo root) — earlier/compiled version of the same paper.
- `ADCOM2027_Track2_Final/main.tex` — a reconstructed LaTeX source for `main.pdf` (no original `.tex` ever existed in the repo), plus `ADCOM2027_Track2_Final/README.md`, `Research_Audit.md`, `Experiment_Decisions.md`.
- `capstonePapers/*.pdf` — ~10 prior PDF-only revisions of the same paper lineage (`v8`, `v13`, `v13.1`, several "Merged_Final" / "Publish_Grade" variants), none with source files.

## 0. Headline finding — read this before anything else below

**The system this paper describes and evaluates does not exist in the `capstoneProject` repository**, and this was already established by a prior audit in this same repo (`ADCOM2027_Track2_Final/Research_Audit.md`, dated 2026-10-06), which I have now independently re-verified.

The paper's subject is a **bounded-authority multi-agent coordination layer**: a "Strategy Agent" and "Coaching Agent" that send typed proposals to an arbitration/admission mechanism (confidence threshold τ=0.6, schema validation, forbidden-key scanning, state-version checks, concept grounding) sitting between the evaluator and a frozen PPO policy, inside the existing `InterviewOrchestrator` hub. It reports:
- 160 deterministic replay sessions (8 clusters × 20 question-order permutations)
- a cluster-bootstrap 95% CI on level-change difference: −2.67 [−4.50, −0.24]
- a split-vs-unified implementation check: 1,280/1,280 matched decisions
- fault injection: adversarial-valid proposals bypass guardrails in 38/40 sessions without arbitration vs 0/40 with it
- a circuit breaker opening in 29/40 full-path crash sessions
- a lexical grounding probe: 57/57 unsupported paraphrased credit accepted
- a frozen PPO checkpoint (seed 123, nominal 100,000 steps, SHA-256 `2ab8d514…`)

**None of this is in the actual codebase.** Independently re-checked in this session:
- `grep`-ing the whole repo for `StrategyAgent`, `CoachingAgent`, `arbitration`, `forbidden_key`, `circuit breaker` turns up nothing except `agents/strategy/hybrid_orchestrator.py` — the single-policy PPO wrapper already documented in `CLAUDE.md` (6-D state, `Discrete(3)` actions Easier/Same/Harder, heuristic fallback). There is no second agent and no arbitration module anywhere.
- None of the distinctive numeric fingerprints (`1,280/1,280`, `57/57`, `38/40`, `−2.67`, `8 replay clusters`) appear anywhere else in the repository, including `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` — the project's sole authority on verified metrics.
- `research/confirmatory/` contains `X1`, `X1-D`, `X2-B`, `X2C`, `X3-A` (mapping to Papers 1–3). No `XA`/`XB`/`XC`/`XD` experiment directories exist anywhere.
- The deployed PPO checkpoint SHA-256 this paper cites (`2ab8d514…`) **is** the real runtime checkpoint hash (`rl/checkpoints/seed_123/ppo_final.zip`), and the evaluator formula in §3 (`0.15·S1 + 0.35·S2_eff + 0.50·R`, `S2_eff` dampened ×0.6 when `R≤0.30`) **does** match `services/evaluator/app.py` exactly. So the paper is not pure fiction — it is grounded in the real single-agent system's real components, but a second coordination/arbitration layer has been invented and wrapped around them, along with an entire replay/fault-injection/ablation experimental apparatus that was never built or run.
- `ADCOM2027_Track2_Final/README.md` documents that a prior session was explicitly instructed by the user (2026-10-06, different session) to "treat `main.pdf` and its contents... as baseline source material to develop further, **without comparing it against or rescoping it to the current `capstoneProject` codebase**" — i.e., to keep developing this paper's prose/figures/tables while *not* reconciling its central claims against the real repo. That session added an abstract rewrite, a new summary table, and redrawn figures, reusing the paper's existing (unverified) numbers.

## 1. Direct conflict with this session's governing instructions

Both `CLAUDE.md` ("Never invent results, citations, datasets or metrics, and never present a hypothesis as measured") and the user's own pasted master prompt for *this* session ("Never fabricate results... Never claim that PPO learned successfully merely because the training script executed... Never describe a planned component as implemented") are incompatible with using this paper's Results section as real evidence in an IEEE submission. The 2026-10-06 instruction that authorized developing it anyway was given in a different session under different framing ("this is accepted as genuinely-not-yet-built work" — i.e., explicitly *not* claimed as real at the time). Carrying it forward into an actual IEEE paper submission without disclosure would cross from "unbuilt future work" into "fabricated results," which is exactly what this session's master prompt repeatedly forbids.

**This is the one decision in Phase 1 that I am not making unilaterally — see the chat message for the options.**

## 2. What is genuinely reusable from this paper regardless of which option is chosen

- **Statistical methodology is sound and transferable**: cluster bootstrap over dependent sessions (Field & Welsh 2007), Clopper-Pearson exact intervals for bounded proportions, leave-one-cluster-out sensitivity analysis, pre-registered predictions with contradicted/supported status tracking (Table 8 pattern). This rigor is worth reusing on *real* data once it exists.
- **The "coordination vs. specialization vs. arbitration vs. bounded authority" conceptual decomposition** (Table 1, four separable mechanisms with their own comparison) is a genuinely good analytical frame, reusable for a paper about the real single-policy system's guardrail layer (`rl/guardrails.py`), which already has a real, frozen ablation result (Paper 3: guardrails — not PPO — account for essentially all of the tracking-MAE improvement over Fixed; "PPO improves tracking" is explicitly withdrawn in canonical truth). That finding is structurally the same shape as this paper's "arbitration is the control point, not specialization" conclusion — just about a mechanism that's real.
- **Fault-injection design pattern** (crash/timeout/malformed/stale/NaN/forbidden-key/adversarial-valid proposal, each crossed with "remove one safeguard") is a reusable template for a real test on `rl/guardrails.py` and the real orchestrator's error handling, once Task 1 testing is underway — this would produce genuinely new, defensible evidence.
- **Limitations section discipline** (Table 11: limitation → effect on claims → planned future work) is good practice to replicate in whatever paper is ultimately written.

## 3. What must NOT be reused as-is

- Any specific number from Results (§6), Tables 5–10, or the abstract's headline figures — none trace to a stored artifact.
- The architecture description implying a second agent layer exists "inside the orchestrator between the evaluator and the commit" (Fig. 1b) — this is not built.
- The "500,000 steps" / specific seed sets referenced for PPO training in this lineage should also be cross-checked against `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §D.1 before reuse anywhere (frozen study: 24,576 timesteps/seed, seeds 42/123/456/789/999 — not 500,000 steps or seeds 42/123/777, which is what the *other* reference document, the capstone report, separately and also-incorrectly claims — see `Previous_Project_Report_Analysis.md`).

## 4. IEEE formatting note

This draft uses Springer `llncs` single-column style. The PPT template (`PPT_Guideline_Analysis.md`) explicitly requires the **official IEEE conference template** (two-column, `Conference-template-A4.doc` per the IEEE link stated on PPT slide 13). Whichever paper is ultimately submitted as "the IEEE paper" must be reformatted into that two-column IEEE conference layout — a Springer-to-IEEE template migration, not just a content decision.
