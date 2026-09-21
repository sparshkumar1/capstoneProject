# ORIGINALITY / OVERLAP AUDIT (master pass, 2026-09-21)

**Scope and limits.** This is a repository-level text-overlap screen, run with `audit_v2/originality_scan.py` (re-runnable; it excludes bibliographies, tables and HTML comments). It compares the current manuscripts with the legacy PrepAIred paper and with each other. It does not query any external plagiarism service or the wider literature, so it supports "no substantial overlap found" within the repository and nothing stronger. Nothing here should be described as "100% plagiarism-free".

**Texts compared.** Current: P1 (blinded source), P2, P3 full manuscript, P3 proposal. Legacy (reference only): `research/papers/archived/superseded_manuscripts/final_prepaired_ieee_paper.pdf` (text extracted in reading order), `IEEE_TLT_MANUSCRIPT.md`, `paper_draft_ieee_access.md`, `paper_draft_ieee_toE.md`. Repository preparation notes: 39 documents under `research/evidence/final/manuscript/` and `research/papers/` (non-archived).

## Results
| Comparison | Duplicate sentences | Shared 8-word sequences | Longest shared run | Treatment |
|---|---|---|---|---|
| P1 vs each legacy text | 0 | 0 | 0 | none needed |
| P2 vs each legacy text | 0 | 0 | 0 | none needed |
| P3 and P3 proposal vs each legacy text | 0 | 0 | 0 | none needed |
| At 5-word granularity, current vs legacy | 0 | P2: 9 and P3: 4 five-word matches | 7 words | all are the author-name block or a section heading ("Limitations and threats to validity") |
| P1 vs P2 | 0 | 5 | 12 words: a sentence about grader-injection studies | P1's wording was changed to "evaluations of LLM graders report that instructions injected into a submission can change the grade"; the residual overlap is the shared citation topic [12]/[16] |
| P1 vs P3 | 1 sentence before the pass | 4 | 11 words | P3's reproducibility sentence was rewritten; a generic disclosure phrase ("is not publicly released in this draft") remains in both by design |
| P2 vs P3 | 0 | 8 at 5 words; none at 8 | 11 words: the author-metadata note | the same metadata note appears in both headers; unavoidable boilerplate |
| Proposal vs full P3 | 0 | 31 | — | expected: same study; the proposal was written separately from the full paper |
| Current manuscripts vs the project's own preparation notes | — | coverage of 8-word sequences: P1 1.3%, P2 0.2%, P3 0.8%, proposal 0.0% | — | these notes state the same frozen facts (counts, definitions); overlap is technical, not prose |

## Findings
- **No substantial overlap found** between any current manuscript and the legacy paper or its archived drafts. The only text shared with the legacy PDF is the author block, which is supplied metadata, and one generic heading.
- **Cross-paper overlap is limited to** technically necessary language (the shared grader-injection citation, the reproducibility and availability disclosures, the author-metadata note). No paragraph, caption or table is duplicated.
- Copied-looking section openings and conclusions were checked by opening-word counts; the most repeated two-word sentence opening is "These are" (five times, in P2), which is unremarkable.
- References are excluded from the screen. The one reference shared by P1 and P2 (arXiv:2606.03090) is deliberate and scientifically relevant to both.
- Numbers, counts and definitions are identical wherever they must be; that overlap is expected and correct.

## Residual risks (not resolvable here)
- The screen cannot see published literature outside the repository. Paraphrase closeness to external sources (for example the abstracts of cited works) was not tested beyond the earlier quote audit (`research/literature/claude_web_research/QUOTE_AUDIT.md`).
- Related-work sentences summarise cited papers; each is written as a summary with the citation, but an external similarity check at submission time would be the appropriate final step.
