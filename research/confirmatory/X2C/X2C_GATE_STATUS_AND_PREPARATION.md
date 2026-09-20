# Paper 2 — X2-C confirmatory round: gate status and preparation (2026-09-20)

## 1. Gate decision: **NO HUMAN DATA COLLECTED — BLOCKED**
The confirmatory round needs a valid institutional/venue/ethics route before any author or rater is asked to do anything. Evidence searched in the repository (2026-09-20):
- `research/audit/P0_P1_USER_DECISIONS.md` (P0-7) and `SPRINT_DECISIONS_AND_BLOCKERS.md` (B-2, D-HUMAN): institutional determination, consent, rater provenance and compensation records **do not exist**; the ethics enquiry drafts were **not sent**; no route (A/B/C/D) has been chosen.
- `research/annotation/ETHICS_CHECKLIST.md` is recorded as unsigned; no consent records for the old raters exist.
No wording here asserts approval, consent, independence or qualifications, and none may be added. **Nothing was authored, sent, simulated as if human, or collected.** The old 64-case study remains **exploratory/initial evidence** and must not be called confirmatory.

**Exact blocker and minimal decision needed (user + institution):** (1) an institutional/venue determination (exempt / approved / not human-subjects) recorded before authoring or rating; (2) consent text and compensation/credit rules; (3) confirmation of the precision target (draft suggestion 0.12 half-width) and of the threshold-free primary outcome (`PAPER2_X2C_PROTOCOL_PACKAGE.md` §11); (4) a decision on the CrossEncoder provenance wording. Until then the round cannot be registered.

## 2. What was prepared (all without human data)
| Item | File | State |
|---|---|---|
| Protocol package (question-disjoint, temporal separation, strata, blinding, provenance ledger, baselines, threshold-free primary outcome) | `research/evidence/PAPER2_X2C_PROTOCOL_PACKAGE.md` | existing draft, unchanged, not registered |
| Precision simulation (script + labelled draft results) | `research/confirmatory/X2C/precision_simulation.py`, `precision_simulation_results.json` | run on synthetic data calibrated to the OLD benchmark variance components (see section 5); **not registered; does not fix N** |
| Rater instructions | outline in package §5; the frozen rubric/scale are `research/annotation/HUMAN_RATING_PROTOCOL.md` (unchanged; not rewritten here) | outline only |
| Sampling design | package §2 (six strata, length crossed with correctness, question-disjoint, temporally separated, references before answers) | design only; Q and K to be chosen from the simulation after the precision target is confirmed |
| Analysis script | not written (specification in package §8; the draw order must be declared in the protocol text before any run — lesson from O7) | pending |

## 3. Statements that stay valid without new data
Old benchmark: ρ = 0.3812 [0.1575, 0.5774] (case bootstrap), 3 raters, 64 constructed answers to 8 questions; ICC(2,1) 0.9528; ablation shows R-only 0.4832 and S1+R 0.4884 above the full composite 0.3812; concise-correct and paraphrase answers substantially under-scored; X2-B exploratory: length-only ρ 0.4897. These are exploratory numbers from the old benchmark with incomplete rater provenance; the composite is **not** shown to be better than simpler baselines, and the evidence does not support "validated".

## 4. What Paper 2 can be without the confirmatory round
A measurement-validity / negative-and-diagnostic paper on an exploratory benchmark: agreement estimate with wide interval, documented systematic under-scoring, an ablation in which the composite is not best, and a safety-hardened composite framed as a design choice with a measured accuracy cost. Claims of general evaluator quality, validation, or superiority over baselines are not supportable.

## 5. Precision simulation result (draft; synthetic data; not registered; does not fix N)
`precision_simulation.py` (B_sim = 100, B_boot = 300, seed 20260920; calibrated to the old benchmark's gold variance components; rater noise ignored, so widths are slightly optimistic; **coverage was not simulated**; the calibration found **no between-question variance in the old gold** (question-level SD 0.0, within-question SD 0.378, because the old design gave every question the same answer-type mix), so the simulated widths assume essentially no question clustering and are **optimistic** if the new benchmark's questions differ in difficulty; Monte Carlo error of each mean half-width is roughly ±0.005). Mean half-width of the two-level cluster-bootstrap 95% interval for pooled Spearman ρ, by number of questions Q and answers per question K (target half-width 0.12 is the draft's suggestion, **not confirmed by the user**):

| true agreement (Pearson) | Q=24, K=10 (240 answers) | Q=30, K=10 (300) | Q=40, K=8 (320) | Q=40, K=10 (400) |
|---|---|---|---|---|
| 0.2 | 0.167 | 0.147 | 0.144 | 0.128 |
| 0.4 | 0.150 | 0.132 | 0.128 | 0.117 |
| 0.6 | 0.119 | 0.109 | 0.102 | 0.093 |

Reading: reaching a 0.12 half-width needs about 30–40 questions × 8–10 answers if the true agreement is 0.4–0.6, and more than 400 answers if it is as low as 0.2. This informs the choice of Q and K once the user confirms the precision target; it is not a success threshold and it does not decide anything about the evaluator.
