# ICCCT 2027 (Goa) Submission Package

## Decision

**Chosen venue: ICCCT 2027** (9th International Conference on Communication & Computational Technologies, Goa,
organized by NFSU Goa / Soft Computing Research Society), **not** ICICC-2027. Reasoning, from the prior review
(see the shared Claude Doc report, "PrepAIred: ADCOM 2027 / ICCCT 2027 / ICICC-2027 Submission Review"):

- ICCCT's Track 1 ("Intelligent Systems: Concepts & Algorithms") explicitly names ML/DL/RL — a direct, specific
  match for this paper's PPO/guardrail and evaluator content. ICICC has no RL/ML-named track; the closest fit
  ("Innovative Computing") is a generic catch-all.
- ICCCT's actual submission requirements (page limit, template family, review type) were directly confirmable from
  the organizer's own "Conference Rules and Guidelines" page; ICICC's were not (its site did not return readable
  text to automated fetch, and its CFP brochure did not extract as text), which made it impossible to build a
  properly verified reformat for ICICC within this session.
- The deadline (21 Nov 2026) is tighter than ICICC's (25 Nov), but the decision was **not** made on deadline
  proximity alone. Both venues sit in the same modest, Scopus-indexed-series tier; ICCCT was chosen on confirmed
  track fit and confirmed submission mechanics, not on which clock runs out first.

This is a submission to **ICCCT only**. Do not also submit this same manuscript to ICICC-2027 concurrently — the
same manuscript under review at two venues at once is itself a duplicate-submission problem, independent of the
ADCOM question (see the report's Section 13).

## Anonymity and page limit (re-verified 2026-11-16, second pass)

- **Fully anonymous.** Re-fetched ICCCT's own "Conference Rules and Guidelines" page directly: it specifies "blind
  peer review by at least two expert reviewers" and states no explicit author-anonymization requirement — but the
  paper is anonymized anyway (`Anonymous Author(s)` / `Anonymous Institution`, no email addresses, no identifying
  text anywhere in `main.tex`, verified by a repo-wide text search for every team/guide name and "PES University").
  This matches the original IEEE paper's own double-blind convention and errs toward the safer, standard-for-review
  practice even though ICCCT doesn't strictly require it.
- **Page limit re-confirmed, verbatim, from the same official page on a second direct fetch:** *"The manuscript
  must be 10 to 12 pages formatted strictly using the Springer conference template."* No extra-page-charge
  threshold was stated on this page (an earlier research pass had inferred one from a sibling SCRS conference's
  page, not from ICCCT 2027's own page — that inference is now superseded; treat it as unconfirmed for this venue).
- **The paper now compiles to exactly 12 pages** — within the confirmed range. Getting there (down from an earlier
  13-page draft) required real trims, not formatting tricks: tightened prose in the Introduction, Related Work,
  Discussion and Conclusion (shortened, not removed — every cut kept its underlying claim and citations), smaller
  figure display widths, and a trimmed note on raw-PPO/heuristic volatility moved into a table footnote. No content
  claim, number, or citation was dropped to make the page count; no font size or margin was altered from the
  template's defaults (`llncs`'s own `\small`/`\footnotesize` for the bibliography was tried and found to have no
  effect — `llncs` already fixes that size internally — so it was reverted rather than left in as dead code).
- Visually spot-checked page 1 (confirms full anonymity) and page 12 (confirms all 15 references render completely,
  nothing orphaned onto a 13th page) after the final compile.

## What this package is

- `main.tex` / `main.pdf` — the paper, reformatted from `final_deliverables/05_IEEE_Paper/review_v2/`'s IEEE
  conference paper into Springer's `llncs` proceedings class (the same Springer LaTeX class already used and
  proven to compile in this repository, at `ADCOM2027_Track2_Final/main.tex`), single-column, per ICCCT's
  confirmed "Springer conference template" requirement, anonymized.
- `references.bib` — the same 15 references from the original paper, unchanged and unaugmented.
- `fig1_architecture.png`, `fig2_evaluator_scatter.png`, `fig3_equivalence.png` — the same three figures reused
  from the original paper, pixel-identical; only their display width changed (twice — once for the initial
  single-column reformat, once more to help the content fit 12 pages).

**Source of truth for every number in this paper:** `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`. Nothing
numeric was invented; the added Table 4 (per-seed MAE/volatility) and the guardrail intervention-accounting
paragraph in Sect. 5.3 use figures already stored there that were not in the original IEEE version due to its
5-page limit.

## What changed relative to `review_v2` (the original IEEE paper)

1. **Reformatted IEEE → Springer `llncs`**: two-column → single-column; Roman-numeral sections → Springer's plain
   Arabic numbering; IEEE bracketed references → `splncs04` numbered style (same 15 references).
2. **Anonymized** (see above).
3. **Restored and added content**, all from already-stored, already-verified evidence, no new experiment: a new
   Table 4 (per-seed tracking MAE and volatility, showing guardrailed PPO is ~2.4× more volatile than the raw
   policy); a guardrail-intervention-accounting paragraph (563/1250 rule activations, only 99/1250 turns with a
   different final action); a one-sentence statistical-unit-of-analysis clarification; a short AI-tool-use
   declaration.
4. **Nothing was removed** from the original paper's evidentiary content.

## Open items requiring your action before submission

1. **Template provenance**: ICCCT's guidelines say only "Springer conference template," not a specific series
   template file; this package uses `llncs` as a faithful stand-in (no downloadable template link was found on any
   reachable page). If you obtain the official template from CMT or `iccct@scrs.in`, port the content into it —
   the content itself doesn't need to change.
2. **Registration fee and whether AI-tool disclosure is formally required** were not stated on any page this
   session could reach — confirm with `iccct@scrs.in` if it matters to you.
3. **Submit via CMT**: `https://cmt3.research.microsoft.com/iccct2027`, deadline 21 Nov 2026.

## Build

```
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Compiled clean with MiKTeX: no LaTeX errors, no undefined references/citations, exactly 12 pages, visually
spot-checked.
