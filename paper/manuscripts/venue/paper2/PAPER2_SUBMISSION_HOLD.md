# PAPER 2 — SUBMISSION HOLD (2026-09-21; maintained, not changed)

**HOLD — manuscript scientifically complete as exploratory study, venue submission not currently cleared.**

This file consolidates the hold. It adds no evidence and invents no record. Detail lives in `PAPER2_SUBMISSION_GATE.md` and `PAPER2_VENUE_GATE.md`; the manuscript is `../../paper2/manuscript.md` (exploratory framing kept).

## Why the hold stands
| Gap | What the repository shows | Consequence |
|---|---|---|
| Ethics review / consent | ethics checklist unsigned; no consent record (`research/audit/P0_7_HUMAN_ETHICS_FORENSIC.md`) | IEEE-co-published venues ask for an IRB/ethics statement or a truthful explanation, and a consent statement or explanation; no defensible statement exists |
| Rater and adjudicator provenance and independence | not documented (number and identity of the adjudicator, independence, blinding beyond the sheet content, timing) | the manuscript says so; it cannot claim blinded, independent or expert raters |
| Cross-encoder provenance | partially fine-tuned derivative, training data unrecoverable (16.28% of parameters differ from the upstream model) | stated as a limitation; cannot be fixed without new work |
| Benchmark | 64 author-constructed answers to 8 questions; length-patterned categories | exploratory only |

Not attempted and not to be attempted without new documented work: creating or back-filling ethics approval, consent, rater independence, blinding, provenance or CrossEncoder training data.

## Harmless maintenance done or confirmed in this pass
- "Human reference score" wording, the 54 mean-of-three / 10 adjudicated split, three named intervals, the labelled nominal p-value and the composite-versus-R-only statement are in place (`paper2/claim_ledger_v2.md`).
- Paper 2's science did not change in the earlier phase; the cross-paper scan found 0 duplicate sentences against Papers 1 and 3 and one intentionally shared reference (arXiv:2606.03090).
- No venue-specific version of Paper 2 was created.

## The 19 reviewer objections (from `audit_v2/P2_INDEPENDENT_HIGH_RISK_AUDIT.md`)
Answered 4: #9, #10, #14, #17. Partly answered 8: #1, #2, #4, #12, #13, #15, #18, #19. Unresolved 7: #3, #5, #6, #7, #8, #11, #16 (each rests on records or data the repository does not contain).

## What would lift the hold (author decision D-6)
Either locate and add documented provenance and ethics records that already exist outside the repository, or run a new documented human-rating round under a proper protocol (new science; not authorised by this task). Until then the manuscript can be kept as an exploratory report; no submission is planned.

## Master-pass note (2026-09-21)
Exact title: "Exploratory Measurement of an Evidence-Grounded Technical-Answer Evaluator". The author block (Dr. Uma D, Professor; Naveen S Khadd; Sparsh Kumar; Athreya Shashidhara; Manasa S A; Dept. of CSE, PES University) was added to `paper2/manuscript.md` for cross-paper consistency only; no venue, blind status or submission format is chosen. The prose pass changed only the discussion scaffolding and two table cross-references; no result, table value or limitation changed. Status remains HOLD; no submission package was prepared.


## Final publication set note (2026-09-21)
The user's final publication plan is P1, P3 and a new end-to-end system paper. This paper (P2) is **not** one of the final three: it stays on HOLD/archived. Its evidence is preserved and none of its claims are merged into another paper. Conditions to revive: documented raters and independence, an institutional ethics determination, cross-encoder provenance, and an independent contribution beyond the exploratory measurement. See `cross/FINAL_PUBLICATION_MAP.md`.
