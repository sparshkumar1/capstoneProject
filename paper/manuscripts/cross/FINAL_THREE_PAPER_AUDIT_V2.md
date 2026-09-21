# FINAL THREE-PAPER AUDIT V2 (2026-09-21)

Independent audit pass over the first drafts. Individual audits: `audit_v2/P1_INDEPENDENT_AUDIT.md`, `P2_INDEPENDENT_HIGH_RISK_AUDIT.md`, `P3_INDEPENDENT_AUDIT.md`, `CROSS_PAPER_AUDIT.md`, `REFERENCE_AUDIT.md`, `STATISTICS_LANGUAGE_AUDIT.md`, `CLAIM_LANGUAGE_AUDIT.md`, `FIGURE_DECISION.md`, `VENUE_GATE_AUDIT.md`, `AI_DISCLOSURE_AUDIT.md`. No frozen file, code, checkpoint, result or protocol was modified; no experiment, build, commit, push, tag or submission occurred.

## Paper 1
- **RQ:** Which containment, authority-boundary and failure-handling properties of an LLM-assisted technical-assessment pipeline can be demonstrated through controlled tests under a specified execution environment?
- **Strongest evidence:** nine fixed attack programs met prespecified criteria in 5/5 runs under the shipped configuration; seven permissive controls breached in 5/5; benign 10/10; two baseline defects (FLT-03, FLT-06) absent on the repaired SUT in 5/5; 14 observables identical across 72/72 valid matched pairs (fixed-turn, repaired SUT).
- **Strongest limitation:** one Windows/WSL2/Docker environment; author-written attacks and oracles; the same AI agent designed, ran, repaired and re-tested; SEC-01 depended on a literal pre-flight filter; follow-up channel untested.
- **Strongest reviewer attack:** "Your ptrace result is a preflight filter, not Docker security." Answered by the paper's own statement; survives as a stated limitation.
- **New finding of this audit:** SEC-05 status also identical in shipped and permissive runs (frozen note's parenthetical is inaccurate; not edited; decision D-1).
- **Final safe contribution:** scoped empirical evidence, attributed per property, oracle and layer, in one environment; not a security or fault-tolerance guarantee.

## Paper 2
- **RQ:** How does a composite technical-answer evaluator agree with human reference scores and simpler component baselines, and which answer types and perturbations reveal systematic evaluator errors? (wording changed from "human consensus"; decision D-2)
- **Strongest evidence:** Spearman 0.3812 with three named intervals; R-only .4832 and S1+R .4884 above the composite with intervals for differences including zero; word count .4897 (AUROC .8864); mean bias −0.134 with 38/64 under-scored; category means with n.
- **Strongest limitation:** author-constructed benchmark (64 answers, 8 questions) with undocumented rater independence, blinding, provenance and ethics; length-patterned categories; cross-encoder provenance unrecoverable.
- **Strongest reviewer attack:** "You have no ethics/consent/provenance records." Survives; it blocks submission to IEEE-co-published venues.
- **Submission gate:** **HOLD** (`venue/paper2/PAPER2_SUBMISSION_GATE.md`).
- **Final safe contribution:** exploratory measurement and diagnostic evidence for one evaluator on one constructed benchmark; not validation.

## Paper 3
- **RQ:** Under an identical rule-based guardrail layer, what does a learned PPO difficulty controller add beyond a simpler state-blind Constant-Same policy in simulated technical-interview trajectories?
- **Strongest evidence:** Δ −0.0350 [−0.0818, +0.0021] inside the pre-specified ±0.12 margin; superiority not met; all seven sensitivity estimates Equivalent; guardrail activated on 563/1250 (45.0%), changed the action on 99 (7.9%), 464 no-op, 41/125 sessions with an override; divergence 50/25/5 of 125; guarded PPO more volatile.
- **Strongest limitation:** simulation only with authored simulator, personas, targets and an author-selected margin; a reward with an oracle-alignment term; five checkpoints trained against one simulated candidate; training/evaluation and runtime mismatches; no real candidates, no learning outcome, no Elo/IRT/CAT baseline.
- **Strongest reviewer attack:** "±0.12 is arbitrary." Survives as a stated limitation with no external justification offered.
- **Final safe contribution:** controlled decomposition and equivalence evidence with behavioural accounting, in simulation.

## Cross-paper
- **Overlap:** 0 duplicate sentences across P1–P2 and P2–P3; 1 generic disclosure sentence duplicated P1–P3; 6–11 shared 8-grams per pair (anonymity notice, the deliberately shared injected-instruction sentence, reproducibility disclosures).
- **Shared system description:** one full description in P1 Section III; P2 and P3 describe only their own component; no repeated paragraph.
- **Shared citations that should exist:** arXiv:2606.03090 (P1 [12], P2 [16]) — added. No other shared reference is scientifically required.
- **Duplicated evidence:** none. **Contradictory language:** none among manuscripts; one frozen-note-versus-data inconsistency (SEC-05) recorded, not edited.
- **Venue fit:** P1 ICETC (primary, port prepared) / ATIS (memo); P2 HOLD; P3 HCII AIS (proposal drafted, not submitted) / SAC AIED (conditional).

## Final acceptance gate — per-paper checklist ("ready for submission" is **not** declared for any paper)
| Gate item | P1 | P2 | P3 |
|---|---|---|---|
| claim ledger complete | ✅ (v1 + v2) | ✅ | ✅ |
| all quantitative claims traceable | ✅ (numeric check 0 unmatched) | ✅ | ✅ |
| key interpretations manually audited | ✅ | ✅ | ✅ |
| no unsupported causal / superiority language | ✅ | ✅ | ✅ |
| no false preregistration language | ✅ | ✅ | ✅ |
| no false ethics statement | ✅ (none needed) | ✅ (none made) | ✅ (none needed) |
| no false rater description | n/a | ✅ | n/a |
| no hidden negative results | ✅ | ✅ | ✅ |
| all relevant limitations visible | ✅ | ✅ | ✅ |
| figures traceable | ✅ (1) | ✅ (3) | ✅ (3) |
| captions accurate | ✅ (author to re-read) | ✅ | ✅ |
| references verified (existence/metadata) | ✅ | ✅ | ✅ (one number removed) |
| venue rules checked | ICETC ✅ (blind status ❓) | ✅ gate | HCII ✅; SAC partly |
| AI disclosure requirement checked | ✅ policy; ⬜ text | ✅ policy; ⬜ text | ✅ policy; ⬜ text |
| page budget checked | ⬜ estimate only | ⬜ | ⬜ estimate (fits 10–20) |
| anonymization checked where relevant | ❓ ICETC | n/a | n/a (single-blind) |
| no frozen science modified | ✅ | ✅ | ✅ |
| no experiments rerun | ✅ | ✅ | ✅ |
| `git diff --check` clean | ✅ | ✅ | ✅ |
| **Paper 2: ethics/provenance passed through the venue gate** | — | ❌ **HOLD** | — |

## Author decisions outstanding
D-1 whether to state five instead of four status-indistinguishable attacks (both wordings are safe) · D-2 accept the P2 RQ wording change · D-4 AI-use disclosure facts (all papers) · D-5 whether to disclose repository file-time facts about the ratings in P2 (currently the manuscript says timing is not documented) · D-6 pursue P2 provenance/ethics records or hold · D-7 keep the descriptive (D) figures (list in `FINAL_MANUSCRIPT_AUDIT.md` §4) · D-8 HCII proposal submission by 9 Oct · D-9 confirm the ICETC date and blind status with the organizers.

## Verdicts (GREEN = may proceed to template conversion; YELLOW = one more correction decision; RED = cannot be submitted under current evidence)
- **Paper 1: YELLOW** (decision D-1, then GREEN).
- **Paper 2: RED** for submission; the exploratory manuscript is stable but venue submission is not cleared.
- **Paper 3: GREEN** for template conversion (HCII proposal review first).
No acceptance probability is predicted.
