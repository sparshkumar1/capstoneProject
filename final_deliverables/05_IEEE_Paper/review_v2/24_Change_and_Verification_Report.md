# 24. Change and Verification Report — Revised IEEE Paper (Specialised Agentic Architecture)

## 1. What was produced, and where

| Deliverable | File |
|---|---|
| 1 — Revised paper (markdown source, editable) | `review_v2/ieee_paper_specialised_architecture_v2.md` |
| 2 — Final IEEE PDF | `review_v2/build/PrepAIred_IEEE_Paper_SpecialisedArchitecture_v2.pdf` |
| 3 — Editable source document (.tex, content-equivalent mirror) | `review_v2/PrepAIred_IEEE_Paper_SpecialisedArchitecture_v2_Source.tex` |
| 4 — Research evidence mapping | `review_v2/23_Research_Evidence_Mapping.md` |
| 5 — This change/verification report | `review_v2/24_Change_and_Verification_Report.md` |
| Build script (new, for reproducibility) | `review_v2/build_revised_ieee_paper.py` |

All five, plus the build script, are **new files in a new subdirectory** (`final_deliverables/05_IEEE_Paper/review_v2/`). The original paper deliverables — `Final_IEEE_Paper_Anonymous.docx`, `Final_IEEE_Paper_Anonymous.pdf`, `Final_IEEE_Paper_Source.tex`, and the three files in `IEEE_Figures/` — were **read, never edited**. The official template (`paper/manuscripts/venue/ICETC_P1/template_official/template.docx`) and its proven builder (`paper/manuscripts/venue/ICETC_P1/build_icetc_docx.py`) were **read and adapted into a new script, never modified in place.**

## 2. Major changes relative to the previous paper

| # | Change | Rationale |
|---|---|---|
| 1 | Title changed from "PrepAIred: Architecture and Evidence-Based Evaluation of a Guardrail-Shielded Adaptive Technical-Interview System" to "PrepAIred: A Specialised Agentic Architecture for Adaptive Multimodal Technical Interview Preparation" | Master task's explicit requirement to centre the specialised/agentic architecture in the title, using one of its own suggested candidate titles verbatim, while avoiding any claim of autonomous peer-to-peer collaboration |
| 2 | Abstract rewritten to lead with the architecture-as-research-asset framing, restructuring (not discarding) the same four evidence findings | Master task §2/§4; all four numeric findings (rho=0.3812, Qwen non-scoring, PPO-vs-guardrail equivalence, guardrail fix) preserved unchanged |
| 3 | §III "System Architecture" (one paragraph in the original) expanded into §III "Specialised Agentic Architecture" with three subsections (Central Orchestration, Component Classification, Why Decomposition Matters) and a new Table I | Master task's explicit requirement that architecture be "one of the most important sections"; the classification table operationalizes the A/B/C/D framework from `17_Architecture_Audit_Report.md` |
| 4 | Related Work reframed around the decomposition/attribution theme, citations and claims unchanged | Master task §9-II; no reference added or removed |
| 5 | §V subsections renamed/reordered to "Component-Attributed..." framing (e.g. "Component-Attributed Difficulty-Control Comparison") and a new §V-F "Architectural Comparison: Status and Design" added, explicitly stating the Configuration-A-vs-B comparison is designed, not executed | Master task §7.C: "If the new single-controller experiment has not been executed... do not invent comparative results... explain that the formal comparative evaluation remains future work" |
| 6 | §VI Discussion rewritten to separate three specific, evidence-backed claims from what the evidence does not support | Master task §13 Discussion requirements; §15 final-checklist item "no unsupported multi-agent claim has been introduced" |
| 7 | Table III and Table IV (system testing + post-deployment verification) merged into one combined Table IV to manage page budget, per-component rows preserved | Master task §11 ("prefer compact tables... combine related subsections") |
| 8 | All four numeric results (evaluator correlation table, RL tracking-MAE table, guardrail boundary finding, system-test pass rate) carried over **unchanged** | Master task §12/§15: "no historical result has been silently changed" |

## 3. Sections retained, rewritten, or newly added

- **Retained with no substantive change:** all four numeric findings and their sources; the evaluator formula (§IV-A); the RL state/action/reward formulation (§IV-B); the Qwen role description (§IV-C); all 15 references.
- **Rewritten for architecture-centred framing, same facts:** Abstract, Introduction, Related Work, Discussion, Conclusion.
- **Newly added:** §III-B (component classification table), §III-C (decomposition-enables-attribution argument), §V-F (explicit not-yet-executed architectural-comparison status).
- **Nothing was removed** from the original paper's evidentiary content; the Limitations subsection's content was folded into §V-F and the Discussion rather than deleted (the "no single-controller comparison exists" limitation is now a dedicated subsection rather than one sentence in a general Limitations paragraph — a strengthening, not a removal, per `IEEE_Page_Limit_Verification.md`'s own stated principle of not padding or cutting evidence to hit a page target).

## 4. Results incorporated (all verified against source, none invented)

Every numeric result in the revised paper is identical to the original paper's corresponding number:
- Evaluator correlation: rho = 0.3812 [0.158, 0.577], and all four component-ablation rows in Table II, unchanged.
- RL tracking MAE: Fixed 1.200, Heuristic 0.473, PPO raw 0.804, PPO+guardrails 0.677, unchanged.
- Guardrail boundary fix: 13/13 boundary cases, zero regressions across 283 tests, unchanged.
- System testing: 264/283 (93.3%), 19 remaining failures, unchanged; the two verification tables' eight rows, unchanged, now in one table.

**No new experimental result was added.** The only new content is architectural framing, the component-classification table (derived from already-completed static-inspection work in `17_Architecture_Audit_Report.md`, not a new experiment), and the explicit "not executed" status of the single-controller comparison.

## 5. References retained or added

All 15 references from the original paper are retained **verbatim**, in the same numeric order. **Zero references were added, removed, or altered.** This was a deliberate choice: this session had no live citation-verification capability (no Zotero/web access invoked for this task), so introducing any new reference would have violated the project's "no invented citations" rule; reusing the already-verified 15-entry list (`IEEE_References_Verification.md`) avoided that risk entirely while still supporting the new framing, since the existing MultiAgentBench, AutoSCORE, and Argos citations already motivate the specialisation/decomposition argument.

## 6. Final page count and IEEE formatting verification

Built via the same authoritative method the project's own prior verification record used (`IEEE_Page_Limit_Verification.md`): the docx was built from the official IEEE Word conference template (`paper/manuscripts/venue/ICETC_P1/template_official/template.docx`) by direct OOXML content replacement, opened in Microsoft Word via COM automation, `Document.Repaginate()` was called to force a full pagination pass, and `Document.ComputeStatistics(wdStatisticPages)` was read directly.

- **First build (full architecture expansion, no trimming): 6 pages**, with page 6 found **nearly empty** (only the Conclusion's opening lines and the first ~8 references) — the same "severe column imbalance" defect this project's own prior build already encountered and fixed once (see `IEEE_Page_Limit_Verification.md`'s own account of an intermediate 6-page build with the same defect).
- **Second build (moderate trim, ~285 words cut from Related Work, §III-C, §III-F, Discussion):** still 6 pages, same defect, confirming the overflow was not primarily driven by running prose.
- **Third build (larger trim, ~440 further words cut from Introduction, §III-A/B, §IV, §V trailing sentences, Conclusion; total ~725 words cut from the first draft): 5 pages**, confirmed by direct visual inspection of all 5 rendered pages (no clipped text, tables, figures, or captions; the final page ends with the reference list and a normal, expected amount of trailing white space, matching this project's own prior documented standard for what counts as acceptable vs. defective).
- **Figures:** all three original figures (architecture diagram, evaluator scatter, equivalence forest plot) reused unchanged at the pixel level; only their embedded display width was adjusted (full-text-width to single-column width, matching the original `.tex`'s actual `0.85\linewidth`, non-starred `figure` environment — i.e. correcting the adapted build script's default to match the original paper's true, already-correct figure sizing, not a new design decision).
- **Tables:** 4 tables (component classification, evaluator correlation, RL tracking MAE, combined system/post-deployment verification), all rendered without column overflow at the font sizes inherited from the official template.
- **No font size, margin, line spacing, or figure size was altered from the template's own defaults to manipulate the page count**, consistent with the project's own prior stated policy.

**Result: the final PDF is confirmed, by Word's own pagination engine, to be exactly 5 pages — within the 6-page maximum, with headroom, and with no near-empty trailing page.**

## 7. Preservation confirmation

| Item | Status |
|---|---|
| `Final_IEEE_Paper_Anonymous.docx` / `.pdf` | **Untouched** |
| `Final_IEEE_Paper_Source.tex` | **Untouched** |
| `IEEE_Figures/*.png` | **Untouched** (read-only reuse) |
| `IEEE_Page_Limit_Verification.md`, `IEEE_Paper_Quality_Audit.md`, `IEEE_References_Verification.md` | **Untouched** |
| `paper/manuscripts/venue/ICETC_P1/*` (template, build script, frozen Paper 1 package) | **Untouched** (read-only reuse of the template and the builder's pattern) |
| Production application code (`agents/`, `apps/`, `services/`, `rl/`) | **Untouched** |
| PPO checkpoints, training configuration | **Untouched** |
| Frozen datasets, historical results (`research/results/*`, `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`) | **Untouched** (read-only citation) |
| Test files, historical logs | **Untouched** |
| External submission or publication | **None performed** |

## 7b. Post-delivery correction: architecture-diagram arrow routing

A second visual defect was reported after §7a's fix: in Fig. 1 (the architecture diagram), arrow lines were
misaligned, not straight, and passed through component boxes rather than connecting cleanly between them. The
original `fig1_architecture.png` (in `IEEE_Figures/`, backing the preserved original paper) had no regenerable
source script in the repository — it appears to have been produced by an earlier, undocumented ad hoc process —
so it could not be "fixed" in place; a new figure was built from scratch instead.

**Fix:** a new script, `review_v2/make_fig1_architecture.py` (matplotlib), lays the nine components out as a
true hub-and-spoke diagram — the orchestrator occupies the centre cell of a 3x3 grid, and the eight other
components occupy the eight surrounding cells. Every arrow is a short, straight spoke drawn from the
orchestrator's box edge to one neighbour's box edge (edge-to-edge, not centre-to-centre), which makes it
geometrically impossible for a spoke to cross through a third box. No arrow is drawn between two non-
orchestrator boxes, which is also more accurate: it matches the verified finding
(`17_Architecture_Audit_Report.md` / `24_Architecture_and_Baseline_Comparison_Specification_v2.md`, the
comparative-experiment package, not this IEEE-paper package) that no component calls another as a peer — all
coordination is orchestrator-mediated.

**Output:** `review_v2/fig1_architecture_v2.png` (new file; the original `IEEE_Figures/fig1_architecture.png` is
untouched). `ieee_paper_specialised_architecture_v2.md` and `build_revised_ieee_paper.py` were updated to
reference the new figure (the build script's image-path resolution now checks the `review_v2/` folder before
falling back to `IEEE_Figures/`, so Fig. 2 and Fig. 3 still correctly resolve to the original, unchanged files).

**Re-verified:** rebuilt docx, re-ran `Repaginate()` + `ComputeStatistics(wdStatisticPages)` — **still exactly 5
pages** — and visually inspected the rendered Fig. 1: all eight spokes are now straight, edge-to-edge, and none
crosses a box.

**Current correct file:** `build/PrepAIred_IEEE_Paper_SpecialisedArchitecture_v2_FIXEDFIG.pdf`. As in §7a, the
two older PDFs in the same folder (`PrepAIred_IEEE_Paper_SpecialisedArchitecture_v2.pdf` and
`..._v2_FINAL.pdf`) are stale pre-fix builds that a persistent OS-level file lock prevented this session from
deleting or overwriting even after confirming no Word process held them; they should be deleted manually once
the lock clears.

## 7a. Post-delivery correction: figure column layout

After initial delivery, a figure-layout defect was identified and fixed: the build script (adapted from Paper
1's `build_icetc_docx.py`) had placed each figure inside a full-page-width, single-column *section break*
between the surrounding two-column text — a convention correct for Paper 1's `figure*` (starred, full-width)
figures, but **wrong** for this paper, whose original `.tex` used non-starred `\begin{figure}[t]` at
`0.85\linewidth` (i.e. single-column width, no page-wide break). This made all three figures visually appear to
"spread across both columns" rather than sit inside one column with text flowing in the other, as a standard IEEE
in-column figure should.

**Fix applied** (`build_revised_ieee_paper.py`): removed the section-break-to-one-column logic around each
figure and caption; figures are now inserted as ordinary inline paragraphs directly inside the normal
two-column flow, sized to the column's own width (3.0 in, close to the original paper's `0.85×`column-width
convention) instead of the page's full width.

**Re-verified after the fix:** rebuilt docx, re-ran Word's `Repaginate()` + `ComputeStatistics(wdStatisticPages)`
— **still exactly 5 pages** — and visually inspected all 5 rendered pages again. All three figures (architecture
diagram, evaluator scatter, equivalence forest plot) now render entirely inside a single column, with body text
flowing normally in the other column alongside each one; no clipping, no page-count regression.

**Output file note:** the corrected PDF is `build/PrepAIred_IEEE_Paper_SpecialisedArchitecture_v2_FINAL.pdf`. An
earlier, now-superseded PDF at `build/PrepAIred_IEEE_Paper_SpecialisedArchitecture_v2.pdf` (built before this
fix, with the full-width figure spans) could not be deleted or overwritten in this session because the OS held a
file lock on it that did not release even after closing the Word process that created it; it is stale and should
be deleted manually once that lock clears. The `.docx` in the same folder is also from the pre-fix build and
should be disregarded in favor of re-running `build_revised_ieee_paper.py` if an updated `.docx` is needed.

## 8. Residual notes for human review

- The `.tex` source (Deliverable 3) has **not been locally compiled** in this environment (no LaTeX distribution available, same limitation disclosed in the original paper's own `.tex` header) — it is a content-equivalent mirror of the page-verified Word build, not independently page-verified itself. Compile and re-check before relying on it for a LaTeX-based submission pipeline.
- Reference [5] (Argos, Microsoft Research) remains a corporate publication rather than peer-reviewed, as already disclosed in `IEEE_References_Verification.md`; this is unchanged and not re-assessed here.
- The live-orchestrator-vs-canonical-guardrail divergence (§IV-B) is reported in the paper as a disclosed implementation detail, consistent with `17_Architecture_Audit_Report.md`; this paper does not resolve it, and no code was changed.
