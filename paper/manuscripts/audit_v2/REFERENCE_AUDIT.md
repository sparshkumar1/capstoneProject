# REFERENCE AUDIT — index (2026-09-21)

Per-paper tables: `reference_audit_p1.md` (14 entries), `reference_audit_p2.md` (16), `reference_audit_p3.md` (14). Total 44 entries; 43 distinct works (Li et al., arXiv:2606.03090, is deliberately cited by Papers 1 and 2).

## What was verified in this pass
| Check | Method | Result |
|---|---|---|
| Existence, title, author count, submission date of every arXiv entry (24 IDs; 23 distinct plus arXiv:2108.13264) | arXiv API, 2026-09-21 | all exist; titles match |
| DOI, venue, volume, issue, pages of journal/proceedings entries (16 items) | Crossref API | all exist; metadata added to the manuscripts where missing |
| Docker seccomp statement | page read | matches the manuscript's paraphrase |
| Sanz Ausin et al. abstract (qualitative claim) | Semantic Scholar abstract record | supports the qualitative statement only; "N = 84" and "p = 0.046" not confirmable → removed |
| Cho et al. peer-reviewed venue | arXiv `journal_ref` and Crossref | ICSME 2025; citation upgraded from preprint |

## What was **not** done
- No full-text re-reading of any source. Claim-level verification levels come from the earlier `QUOTE_AUDIT.md` (abstract-level or PDF-level per row) and are stated in each table.
- Peer-review status of [6] Zheng et al. (NeurIPS D&B 2023) and of [4] Schleifer et al. (BEA 2026, accepted per arXiv comment) was not independently confirmed.
- No new literature search was run; no reference was added for the sake of count.

## Findings
1. One number in Paper 3 Related Work ("N = 84", "p = 0.046") could not be verified and was removed.
2. Paper 2 [12] is peer-reviewed (ICSME 2025); v1 called it a preprint with unverified venue.
3. Metadata added: DOIs and pages for P1 [8]; P2 [2], [11], [12], [13], [14]; P3 [4], [7], [9], [11].
4. Two title-level-only citations remain (P2 [9], [10]); they support only a general statement.
5. Foundational sharing: P1 [12] = P2 [16].
6. Nine of Paper 1's 14 references are preprints; that is a stated risk, not an error.

## Verdict
References are existing and correctly attributed at the level stated. **GREEN for existence/attribution; YELLOW for final submission** until each venue's reference style is applied and the abstract-level items are read in full if the venue expects it.
