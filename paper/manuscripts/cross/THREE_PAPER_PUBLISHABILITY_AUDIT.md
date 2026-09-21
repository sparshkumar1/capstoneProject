# Three-paper publishability audit (hostile-review simulation, 2026-09-21)

No acceptance prediction or probability is given. Readiness classes: READY FOR SUBMISSION / READY AFTER AUTHOR CONFIRMATION / REQUIRES VENUE VERIFICATION / REQUIRES NEW RESEARCH / NOT CURRENTLY DEFENSIBLE.

## P1 — ICETC 2026
- **Contribution:** a scoped, property-by-property evidence account for one LLM-assisted assessment pipeline, with independent oracles, weakened controls and layer attribution; plus the observations that executor status did not identify containment for five attacks and that the ptrace outcome came from an application filter.
- **Strongest evidence:** nine fixed programs 5/5 with seven permissive controls breached 5/5; two baseline defects absent after repair; 72/72 valid pairs with 14 observables equal and a mutation control 72/72.
- **Strongest weakness:** one application, one machine, author-written attacks and oracles, and the same agent designed, ran, repaired and re-tested (regression, not replication).
- **Major objections:** narrow scope (what transfers?); non-independent tests; weak education fit (no learner outcome; an assessment-integrity argument only).
- **Moderate:** artifact not public; git identifiers unresolvable by reviewers; FLT-08/09 unexecuted; follow-up channel untested.
- **Minor:** mostly preprint references (labelled); small figure labels.
- **Evidence still required:** none obtainable without new experiments; independent replication would strengthen it and is not planned.
- **Venue fit:** ICETC has AI-in-education and cybersecurity/digital-ethics tracks; fit is the authors' argument, unconfirmed by the venue.
- **Overlap:** none in evidence or text with P3; one reference shared with held P2.
- **Minimum change for defensibility:** confirm the git-identifier decision, add or decline one sentence separating methodology from application test, resolve the AI-disclosure question with the organisers.
- **Classification: READY AFTER AUTHOR CONFIRMATION** (venue rules on AI disclosure and prior submission still to be verified).

## P3 — HCII 2027 AIS
- **Contribution:** a matched-policy comparison with the constraint layer held fixed, an equivalence result under a pre-specified rule, and guardrail accounting that separates activations, action changes and no-ops.
- **Strongest evidence:** primary Δ −0.0350, interval [−0.0818, +0.0021] inside ±0.12; all seven sensitivity estimates equivalent; stored replay counts (563 / 99 / 464; 41 of 125 sessions).
- **Strongest weakness:** simulation-only with authored simulator, personas and targets; the ±0.12 margin is author-selected with no external justification; Constant-Same at the centre of the target range is a strong reference, so equivalence is partly a property of the setup.
- **Major objections:** no real learners; margin choice; PPO trained for 24,576 steps against one default candidate with a training/evaluation mismatch and a runtime state mismatch; no IRT/CAT/Elo baseline; five seeds.
- **Moderate:** a reviewer may see a null result of limited interest; relevance to AIS is methodological (what evidence an adaptive decision needs).
- **Minor:** dense terminology (three divergence definitions).
- **Evidence still required:** for any learner-facing claim, real-candidate data (not part of P3); none is claimed.
- **Venue fit:** AIS covers adaptive tools/models and evaluation; proposal-first process.
- **Overlap:** none with P1; the system paper must not reuse P3's simulation as user evidence.
- **Minimum change for defensibility:** keep the claims at equivalence within a stated margin; keep the limitations prominent; supply the Declarations.
- **Classification:** proposal (762 words) **READY AFTER AUTHOR CONFIRMATION** (metadata and the form's fields); full paper **REQUIRES VENUE VERIFICATION** (Springer/HCII template, page count, AI policy) and author confirmation.

## System paper
- **Contribution (only if the study is done):** integrated implementation plus a controlled human-outcome evaluation with independent blinded ratings.
- **Strongest evidence now:** none about people. Component evidence exists (P1 sandbox behaviour, exploratory evaluator agreement, P3 simulation).
- **Strongest weakness:** no user study, no runtime baselines, hesitation not wired into the live state, no video, ethics undetermined, evaluator not validated as an outcome measure.
- **Major objections:** "a system description, not research"; no evidence of effect; circularity if the evaluator scores its own outcomes; adaptive component not shown to matter (P3 suggests equivalence with a constant policy).
- **Evidence still required:** approved protocol, participants, arms, held-out questions, independent raters, analysis.
- **Venue fit:** ICALT 2027 is plausible from track names (APTeL, AISLE, TeASSESS), five pages including references, double-blind, 15 Jan 2027; feasibility of a complete study by then is not established. AIED 2027: no CFP yet.
- **Overlap:** high by description with P1/P3; must cite them once public and add no reused prose.
- **Minimum change:** none possible without new research.
- **Classification: REQUIRES NEW RESEARCH** (plus ethics determination and venue verification).

## P2 (held; not one of the final three)
Not audited again in this pass. Classification for submission today: **NOT CURRENTLY DEFENSIBLE** (rater provenance, consent and ethics records incomplete; cross-encoder provenance incomplete). Conditions to revive it are in the publication map.
