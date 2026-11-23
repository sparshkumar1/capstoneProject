# Academic Requirement Traceability Matrix

Maps every mandatory requirement found in the four `Details/` reference documents (university report guideline, PPT guideline, and — where it imposes format/process requirements rather than content — the two paper drafts) to its destination output file/section. Status reflects Phase-1 (inspection) completion only; "Pending" items depend on Phase 2+ (testing) or user decisions not yet made.

| Req. ID | Requirement | Source | Destination file/section | Status |
|---|---|---|---|---|
| R1 | A4, 1.5 spacing, 2cm margins, Times New Roman, justified body | `Report-Guidelines.pdf` #1, #11 | `02_University_Project_Report/` (whole doc) | Pending (Task 2) |
| R2 | TOC = Intro, Problem Definition, Lit. Review, PRS, HLD, LLD, System Design, Methodology, Implementation+Pseudocode, Results+Discussion, Conclusion+Future Work, Bibliography, [User Manual] | `Report-Guidelines.pdf` #7 | Report chapter structure | Pending — PRS/HLD/LLD format not supplied, needs user input |
| R3 | Chapter/section/subsection numbering + font sizes (18/16/14/12) | `Report-Guidelines.pdf` #8–#10 | Report formatting | Pending (Task 2) |
| R4 | Figures/tables numbered chapter-wise | `Report-Guidelines.pdf` #12 | Report formatting | Pending (Task 2) |
| R5 | Conclusion chapter must reference plan-of-work carried from Capstone-2 | `Report-Guidelines.pdf` #13 | Report "Conclusion and Future Work" | Pending — needs `revised_report_v5.pdf` Ch.7's future-work items as the "carried-forward plan" |
| R6 | References numbered serially, IEEE in-text bracket style | `Report-Guidelines.pdf` #14 | Report "Bibliography/References" | Pending (Task 2) |
| R7 | SI units, numbered equations | `Report-Guidelines.pdf` #15 | Report body | Pending (Task 2) |
| R8 | No verbatim reproduction without quotation/citation | `Report-Guidelines.pdf` #16 | All reused content | Partially addressed — reuse matrix flags sources; final text must paraphrase/cite |
| R9 | Hard-bound, cream cover, plastic cover, specific header/footer layout | `Report-Guidelines.pdf` #19–#21 | Physical submission (outside this session's scope — can prepare PDF layout only) | N/A to AI deliverable — note for user |
| R10 | Plagiarism check ≤15%, done only at PESU library | `Report-Guidelines.pdf` #22 | User action | N/A to AI deliverable — flag for user |
| R11 | Upload documentation + presentation + user manual to project repo server | `Report-Guidelines.pdf` #23 | User action | N/A to AI deliverable — flag for user |
| R12 | Acknowledgement paragraph order: Guide → Coordinator (Dr. Chaitra B) → Chairperson → Registrar → VC → CEO → Chancellor → Parents → Family | `Report-Guidelines.pdf` p.4-5 | Report front matter | Ready — template already correct in `Report initial Pages/Page 3-8.docx` |
| R13 | Front matter: inner title, certificate, declaration, acknowledgement, abstract (≤150 words), TOC, list of tables/figures | `Report-Guidelines.pdf` #5–#6 | Report front matter | Ready — blank templates in `Report initial Pages/` |
| P1 | Slide: Title (Project Title/ID/Guide/Team) | PPT template slide 1 | `04_Final_Presentation/` | Pending — needs user-supplied team/guide/ID |
| P2 | Slide: Outline | PPT template slide 2 | Presentation | Ready to populate from this TOC |
| P3 | Slide: Abstract | PPT template slide 3 | Presentation | Pending (Task 4, draws on Report abstract) |
| P4 | Slide: Suggestions from Review-2 | PPT template slide 4 | Presentation | **Blocked — requires real panel feedback from the user; cannot be generated** |
| P5 | Slide: Implementation Details (module/tech/code + pseudocode) | PPT template slide 5 | Presentation | Pending (Task 4, draws on Report Implementation) |
| P6 | Slide: Project Demonstration | PPT template slide 6 | Presentation | Pending — needs real screenshots (Task 1 / `run` skill) |
| P7 | Slide: Test Plan and Strategy (types, roles, tools, benefits/drawbacks) | PPT template slide 7 | Presentation | Pending (Task 1 output) |
| P8 | Slide: Results and Discussion (expected vs actual, graphs) | PPT template slide 8 | Presentation | Pending (Task 1 output) |
| P9 | Slide: Applicability in Other Domains | PPT template slide 9 | Presentation | Pending — must respect `docs/PROJECT_STATE.md`'s unresolved "domain transfer" decision; discuss, don't claim implemented |
| P10 | Slide: Timeline – Report completion status | PPT template slide 10 | Presentation | Pending |
| P11 | Slide: Conclusion and Future Work | PPT template slide 11 | Presentation | Pending |
| P12 | Slide: References (IEEE format) | PPT template slide 12/15 | Presentation | Pending — same reference set as Report |
| P13 | Slide: IEEE Draft status + target venues, official IEEE template link | PPT template slide 13 | Presentation | **Blocked on the Springer-paper fabrication decision** (see chat) — cannot state completion status honestly until scope is resolved |
| P14 | Slide: Any other information | PPT template slide 14 | Presentation | Optional |
| P15 | Slide: Thank You | PPT template slide 16 | Presentation | Ready |
| I1 | IEEE paper must use official two-column IEEE conference template (`Conference-template-A4.doc`) | PPT template slide 13 | `03_Research_Paper/` | Pending — current draft (`Coordination_Specialization...pdf`) is Springer `llncs` single-column; needs full template migration regardless of content decision |
| I2 | Every IEEE paper number must trace to stored evidence; no fabricated results | `CLAUDE.md`, master prompt §9.1/§13.5 | `03_Research_Paper/` | **Blocked** — current draft's headline results fail this requirement; see `Springer_Paper_Content_Analysis.md` §0 |
| MP1 | Separate file per deliverable, no combined dumps | Master prompt §3 ("Additional Execution Instructions") | `final_deliverables/` structure | Acknowledged, will apply once Phase 2+ begins |
| MP2 | No codebase changes | Master prompt ("Additional Execution Instructions" cover note) | All phases | Honored — only `reference_material_analysis/` and restored files touched so far; restoring the 156 deleted files was a data-recovery action, not a feature change |
| MP3 | Preserve existing work, protect frozen artifacts | `CLAUDE.md` frozen-artifact list + master prompt §3.3 | All phases | Honored — nothing in `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`, `research/papers/*`, `rl/checkpoints/*`, etc. was touched |

## Items requiring the user before Phase 2 (testing) can start in earnest

1. **PRS/HLD/LLD document formats** — not supplied in `Details/`; needed for Report TOC items 4–6.
2. **Panel feedback from Review-2** — needed for PPT slide 4; cannot be fabricated.
3. **Team/guide/project-ID details for Phase-3** — needed for front matter and PPT slide 1 (the Phase-2 report's team is known; confirm it's unchanged for Phase-3).
4. **The Strategy/Coaching MAS-layer / IEEE-paper scope decision** — see chat message; blocks I1/I2/P13 until resolved.
