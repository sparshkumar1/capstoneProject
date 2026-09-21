# Claude web-research literature and novelty package (2026-09-21)

Status: **literature/novelty planning artifact only.** Recommendations for later independent review. Nothing here changes a claim, a result, a frozen artifact, or the scientific source of truth. No final paper is drafted.

## What this run was
A Claude-only web investigation using the WebSearch and WebFetch tools of the current Claude Code session, plus the built-in browser pane for one paywalled page (ScienceDirect landing page). No Semantic Scholar API, OpenAlex, Crossref, Gemini API, grounding API, Deep Research API, paid API or other external agent was used. `research/literature/free_pipeline/` was not modified, extended or used.

## How to read the evidence labels (important)
| Label | Meaning |
|---|---|
| **V-TEXT** | Body text was read directly by me (page text via browser, or a downloaded PDF converted to text). |
| **V-PAGE** | The official/arXiv/ACL landing page was opened and its abstract/metadata were extracted by the fetch tool. The tool summarises pages with a small model, so any quotation returned by it must be re-checked against the source before it is printed in a manuscript. |
| **V-SNIP** | Only a search-result snippet or list entry was seen (title/URL/one-line summary). Not evidence of content. |
| **CARRY** | Record carried from the earlier first/second-pass files (`LITERATURE_NOVELTY_MASTER_MATRIX.md`, `SECOND_PASS_CLAIM_AUDIT.md`); not re-opened in this run. |

Nothing labelled V-SNIP or CARRY may be cited from this workspace without a fresh read.

## Honest coverage statement
- 39 web searches and 33 page/PDF fetch attempts were run (about 25 fetches returned usable content; the rest were blocked by publishers or returned redirects). Serious sources newly opened: about 25 (Paper 1: 12, Paper 2: 10, Paper 3: 9, some shared).
- The target of 30-60 initial candidates per paper is **not** met as new items: candidate files list new items plus clearly labelled CARRY items. A search that found nothing is not evidence that nothing exists.
- The mandatory Paper 3 comparison paper (Kadam et al., 2026) is **paywalled**. I read the full abstract, highlights, introduction, the list of contributions, section snippets and the discussion/limitations snippets, but **not** the methods, tables or results. All statements about its state definition, reward, seeds and numbers are therefore *not verified* and must be checked with a full copy before any comparison is written.
- Forward citation chasing was possible only through search-result listings; no citing-paper database was used. Backward chasing was done for the Paper 3 target only (its 42-item reference list was visible in part).
- Saturation: see `UNRESOLVED_GAPS.md`. Paper 1 and Paper 3 show reasonable saturation on their headline threats; Paper 2 is less saturated on ASAG-with-technical-answers.

## Gap-closure pass (2026-09-21)
A second pass added `KADAM_VERIFICATION.md`, `P3_FINAL_NOVELTY_POSITION.md`, `P3_RL_EDUCATION_REVIEWS.md`, `P3_ADAPTIVE_ASSESSMENT_PRIOR_ART.md`, `P1_SANDBOX_METHODOLOGY_COMPARISON.md`, `P2_2026_BIAS_PASS.md` and `QUOTE_AUDIT.md`, and updated the CORE, NOVELTY_MATRIX, PROVENANCE, CLAIM_CHANGE_QUEUE, UNRESOLVED_GAPS, FINAL_LITERATURE_AUDIT, BIBLIOGRAPHY, map and README files. The Kadam et al. full text was still not accessible (paywall; no workaround used). Full texts of several Paper 1 and Paper 3 sources were downloaded as public PDFs (curl, no API) and converted for exact quote matching. Coverage in the section below is the first pass; the gap-closure counts are in `PROVENANCE.md`.

## Final closure pass (2026-09-21)
Added `P3_FINAL_NOVELTY_POSITION.md` and `P3_RL_EDUCATION_REVIEWS.md`; rewrote `KADAM_VERIFICATION.md` (Table A verified elements, Table B full field status); appended entries to BIBLIOGRAPHY ([58]-[60]), QUOTE_AUDIT (section 5), CLAIM_CHANGE_QUEUE (Q3-08 to Q3-11), NOVELTY_MATRIX, UNRESOLVED_GAPS, PROVENANCE and FINAL_LITERATURE_AUDIT. Literature search stopped by instruction. Nothing outside this directory was modified.

## Files
`KADAM_VERIFICATION.md`, `P3_ADAPTIVE_ASSESSMENT_PRIOR_ART.md`, `P1_SANDBOX_METHODOLOGY_COMPARISON.md`, `P2_2026_BIAS_PASS.md`, `QUOTE_AUDIT.md`, `CANDIDATES_PAPER{1,2,3}.md`, `CORE_PAPER{1,2,3}.md`, `NOVELTY_MATRIX.md`, `PAPER{1,2,3}_RELATED_WORK_MAP.md`, `PAPER{1,2,3}_CITATION_MAP.md`, `BIBLIOGRAPHY.md`, `PROVENANCE.md`, `UNRESOLVED_GAPS.md`, `CLAIM_CHANGE_QUEUE.md`, `FINAL_LITERATURE_AUDIT.md`.

## Wording rules applied
The words "first", "novel", "unprecedented", "no prior work", "state of the art", "best", "superior" are not used to describe PrepAIred. "To our knowledge, within the searched literature" is used only where the search was broad enough for that scope, and the scope is stated.

## Claim-lock implementation (2026-09-21)
`CLAIM_LOCK_IMPLEMENTATION_LOG.md` records the exact before/after text of the edits made to the manuscript-preparation and literature-positioning documents for the locked three-paper positioning. `CLAIM_CHANGE_QUEUE.md` (QL-01 to QL-05) lists proposals for the canonical documents that were deliberately not edited.
