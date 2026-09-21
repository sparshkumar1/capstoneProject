# P1 PAGE ECONOMY REPORT (2026-09-21)

Target: ≤ 6 printed IEEE two-column pages for ICETC "if possible" (ICETC facts verified 2026-09-21: IEEE format ≥ 5 pages; 70 USD per page beyond 6; see `venue/icetc2026/ICETC_VENUE_FACTS.md`).

## Measured
| Version | Body words (tables, captions, headings included; comments and references excluded) |
|---|---|
| v1 first draft | about 4,340 (earlier overlap report method) |
| v2 `paper1/manuscript.md` | 3,594 |
| ICETC port | 3,503 (includes an ~85-word acknowledgment placeholder) |
Net change v1 → v2: about −17%. (Per-edit word deltas were not measured and are not reported.)

## What changed from v1 to v2 (qualitative)
- Related Work condensed; the separate "brief results" paragraph of the introduction removed (results are in the abstract and Section V).
- Pipeline description condensed and merged with a new threat-model and scope paragraph.
- Table I reduced to three rows; the minor-fault row moved into Table III's note.
- The v1 X1-C table replaced by Fig. 1 (per-run markers) plus a shorter table giving the observation and the deciding observable.
- Timing section reduced to three sentences; discussion paragraphs condensed; limitations kept intact.
- Additions required by the audit: threat model, per-attack oracle statements, baseline/repaired SUT naming, ptrace paragraph, same-agent statement.

## Protected (not cut)
Research question; threat and property definitions; oracle design (Table I); attack/control matrix (Fig. 1, Table II); core results; four material limitations; ptrace paragraph; follow-up-channel sentence; FLT-08/09 visibility; same-agent disclosure.

## Cut as redundant or generic
Repeated architecture prose, repeated motivation, generic technology lists, the separate results summary in the introduction, duplicated statements of the four limitations.

## Estimate and status
Estimated 5.5–6.5 printed pages in the IEEE template (an estimate from a words-per-page model, not a measurement; see `venue/icetc2026/ICETC_PAGE_BUDGET.md`). The ≤ 6-page target is **not confirmed** and cannot be confirmed without converting to the official IEEE template, which has not been done. Optional further cuts that do not remove any limitation are listed there.
