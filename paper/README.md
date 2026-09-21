# Final Paper Workspace (IEEE format)

**Target publication format:** IEEE
**Target venue:** TBD (not yet chosen)

This directory is the working location for the final IEEE-style paper. It is separate from implementation code and
separate from the frozen Paper 1/2/3 packages.

## Do not touch
`research/papers/paper1_systems`, `paper2_evaluator`, `paper3_rl`, `research/papers/archived`, and everything listed
in `research/CLAUDE_HANDOFF/PAPER3_FINAL_FREEZE.md` are frozen/audited. Read from them; never edit them here.
`docs/paper_draft_ieee.md` and `docs/IEEE-Access-Submission-Checklist.txt` are pre-existing historical documents,
not the venue source of truth.

## Requirements
- IEEE-compatible LaTeX/document structure, IEEE reference conventions, IEEE-style figures, tables and equations.
- Once the venue is chosen, that venue's official IEEE template and submission rules are the source of truth.
  Do not invent page limits, margins, author rules or submission requirements before then.
- Every reference comes from Zotero or a verified real source. No invented citations.
- Every reported number traces to stored experiment evidence (result files + config + seed + commit + W&B run where one exists).
  Facts about the existing system come from `research/CANONICAL_SCIENTIFIC_TRUTH.md`.
- The paper must be reproducible from stored results/configuration. Figures and tables are generated from those results, not typed in.
- Mark every claim as measured / hypothesis / interpretation / assumption / literature-supported.

## Layout (planned)
```
paper/
    README.md        (this file)
    figures/         generated figures only, each traceable to a results file
    tables/          generated tables only, each traceable to a results file
    main.tex         (deferred: created from the official venue template once the venue is chosen)
    references.bib   (deferred: exported from Zotero, not hand-written)
```
