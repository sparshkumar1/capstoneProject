# IEEE Paper Scope Decision

**Date:** 2026-11-12 · **Decided by:** user, in response to the Phase-1 critical finding recorded in `Springer_Paper_Content_Analysis.md` §0–1.

## Decision

**Rescope the IEEE paper to the real system.** The Strategy/Coaching bounded-authority multi-agent layer and its XA–XD replay/fault-injection/ablation experiments, as described in `Details/Coordination_Specialization_and_Bounded_Authority_in_Adaptive_Technical Interview_Systems_A_Replay_Based_Decomposition_Study (1).pdf`, are **not used as evidence** in the IEEE paper, because they do not exist in the `capstoneProject` codebase (independently re-verified in this session; consistent with the prior `ADCOM2027_Track2_Final/Research_Audit.md` finding of 2026-10-06).

## What this means for Task 3

The IEEE paper will instead be built around:
- The real, single-policy system: `agents/orchestrator/interview_orchestrator.py` (hub), `agents/strategy/hybrid_orchestrator.py` (frozen SB3 PPO wrapper), `rl/guardrails.py` (the real guardrail/safety layer), `services/evaluator/app.py` (the real three-component evaluator).
- Genuinely frozen, already-audited evidence: Paper 1 (systems/fault-injection), Paper 2 (evaluator-vs-human, ρ=0.3812 composite / 0.4832 R-only), Paper 3 (PPO-vs-guardrail attribution: guardrails — not PPO — account for essentially all of the tracking-MAE improvement over Fixed; "PPO improves tracking" is an explicitly withdrawn claim). All figures per `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`.
- **Reused from the Springer draft** (methodology/framing only, not its numbers): the cluster-bootstrap statistical approach, Clopper-Pearson intervals for bounded proportions, pre-registered-prediction discipline, and the "coordination vs. specialization vs. arbitration vs. bounded authority" analytical frame — applied to the real guardrail layer's real ablation finding, which has the same shape ("the safety/arbitration mechanism, not the learned policy, drives the observed behavior change") but is true.
- Reformatted into the **official IEEE two-column conference template** (`Conference-template-A4.doc`, per the PPT template's slide 13 instruction), not the Springer `llncs` single-column style of the original draft.

## What this does NOT mean

- It does not mean building the Strategy/Coaching layer for real (that was "Option B" — rescope — not "Option A" — build it; building it remains a possible *future* direction but is out of scope for this submission per the user's choice).
- It does not mean discarding the Springer draft entirely — its prose structure, RQ-framing discipline, and statistical rigor are genuinely reusable; only its Results section and architecture claims are excluded.
- `main.pdf`, `ADCOM2027_Track2_Final/*`, and `capstonePapers/*` are left untouched in the repository (no deletions) — they remain available if the user later chooses to pursue "Option A: build it" as separate future work.

## Next step this unblocks

`Academic_Requirement_Traceability_Matrix.md` items I1/I2/P13 (IEEE template migration, evidence-traceability requirement, PPT slide 13's "IEEE draft status") can now proceed once Task 1 (testing) produces real results to cite for the "Results and Discussion" section.
