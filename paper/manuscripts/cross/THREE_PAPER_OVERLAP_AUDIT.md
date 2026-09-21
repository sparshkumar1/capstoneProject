# Three-paper overlap audit — P1, P3 and the system paper (2026-09-21)

Text-level results come from `cross/ORIGINALITY_OVERLAP_AUDIT.md` (repository-level screen; not an external plagiarism check; no "100 %" claim). The system paper has no results text, only a short pre-research draft, so its text overlap was **not measured with the scanner**; its prose is new and it reuses no paragraph from P1 or P3. P2 (held) is included where it matters.

| Dimension | P1 (ICETC 2026) | P3 (HCII 2027 AIS) | System paper (planned) |
|---|---|---|---|
| Title | Scoped Evaluation of Containment, Authority Boundaries, and Failure Handling in an LLM-Assisted Technical-Assessment System | A Controlled Equivalence Study of Learned and Constant Difficulty Policies in Simulated Technical Interviews | Provisional; not locked |
| Research question | Which containment, authority-boundary and failure-handling properties of the pipeline can be demonstrated under controlled tests? | Under an identical application-level rule-based guardrail, what does a PPO controller add beyond a state-blind Constant-Same policy in simulation? | Proposed only: does an adaptive condition change blinded-rated held-out performance, usability and reliability relative to a non-adaptive condition (`system_paper/SYSTEM_PAPER_RQ.md`) |
| Contribution | Property-by-property evidence account for one pipeline, with oracles, weakened controls and layer attribution | Matched-policy comparison with pre-specified equivalence rule; guardrail accounting (activations, overrides, no-ops) | Integrated system description and, only after new work, a human-outcome evaluation |
| Dataset / simulator | Nine fixed C attack programs, fault scenarios, fixed-turn transcripts; one environment | Authored simulator, 40 authored personas × 5 PPO seeds; five-persona replay | Real participants and held-out questions (not collected) |
| Experiments | X1-C, X1-A, X1-B-I | X3-A, X3-0 replay, sensitivity analyses | none run |
| Metrics | k/5 counts, host-side observables, 72/72 pairs | tracking MAE difference, intervals, activation counts | not fixed (proposed: blinded rubric score change) |
| Figures | 1 (containment matrix, re-plotted from stored runs) | 3 (equivalence forest, guardrail accounting, divergence/volatility) | none (architecture figure only after design; implemented components only) |
| Tables | 4 | 4 | none |
| Text overlap | none with the legacy paper or the archived drafts (0 duplicate sentences, 0 shared 8-grams); with P3: one 11-word generic disclosure phrase kept by design; with P2: the grader-injection sentence was reworded | as left: none with the legacy paper; the proposal and the full paper overlap by design (same study) | not measured; the pre-research draft is new text |
| Reused evidence | X1 results only | X3 results only | must not reuse either as evidence of effect on people; may describe them as prior work, cited once public |
| Reused references | none shared with P3 (lists inspected: sandbox/LLM-grader/fault-injection sources versus RL-in-education/equivalence-testing sources); P1 shares arXiv:2606.03090 with the held P2 | none shared with P1 | to be assembled; must not copy P1/P3 lists to enlarge the bibliography |

## Boundaries that must hold
- P1 answers what the pipeline's tests can show; nothing in P1 is evidence that the system helps learners.
- P3 is simulation only; nothing in P3 is evidence of real-user effect. Its equivalence result gives no reason to expect PPO to beat a constant policy for people.
- The system paper's user results, if they ever exist, cannot change frozen P1 or P3 results.
- The held P2 evaluator numbers (Spearman 0.3812 on 64 constructed answers) may appear in the system paper only as an exploratory prior measurement with the P2 caveats (54 mean-of-three plus 10 adjudicated; incomplete rater provenance), never as validation.

## Publication-order and prior-publication risks
- P1 (ICETC decision 10 Nov 2026) and P3 (HCII proposal 9 Oct 2026, decision 20 Nov 2026) are independent studies. If one is under review when another is submitted, the later venue's related-submission and disclosure rules apply; ICALT's rule is not stated on its page and ICETC's was not found. Ask before submitting.
- P1's backup (CSEDU 2027) prohibits simultaneous submission; P3's alternative (SAC AIED) must not be submitted concurrently with HCII. Neither backup is selected.
- The system paper describes the same implementation as P1 and P3; describe the shared parts briefly, cite the companion papers once public, and do not reuse their sentences.
- Do not describe any paper as "published" before the venue accepts and publishes it.

## Residual risk
The scanner cannot see the wider literature; run an external similarity check at submission time.
