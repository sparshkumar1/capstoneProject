# PPT Guideline Analysis

**Source:** `Details/PPT-Template_Phase3- Review3.pptx` — PES University Capstone Phase-3, "Project Progress Review 3" template, 16 slides. Extracted via raw OOXML text run inspection (no `python-pptx` installed in `.venv`; did not install it, to avoid touching the pinned/reconciliation-pending environment — used `unzip` + text extraction instead).

## Slide-by-slide structure (mandatory sections per slide 2's own outline)

| # | Slide title | Required content (verbatim instructions on the slide) |
|---|---|---|
| 1 | Title slide | Project Title, Project ID, Project Guide, Project Team — placeholders only |
| 2 | Outline | Lists the 11 sections below — this is the deck's own table of contents |
| 3 | Abstract | "Basic introduction of the project and overview of scope. Set the context." |
| 4 | Suggestions from Review – 2 | "Suggestions and remarks given by the panel... feasibility on the same showing progress" |
| 5 | Implementation Details | "Module-wise implementation details: module name, technology used, code explanation. Interpretation with Algorithms & Pseudocode (applicable for Research projects)" |
| 6 | Project Demonstration | "Exhibit the demonstration of the complete project. Complete in all aspects. Exhibit working." |
| 7 | Test Plan and Strategy | "Testing activities + timeline. What test methods and why (Functional: Unit/Integration; Non-Functional: Performance/Security). Test environment + each member's role. Benefits/drawbacks. Tools used (automated/open-source). Note: appropriate modifications for Research Projects; add slides as required." |
| 8 | Results and Discussion | "Results/discussions post-testing. Match expected vs actual, explain deviations. Comparison with other technology/methodology, graphs/charts if applicable." |
| 9 | Applicability of Proposed Methodology in Other Domains | Identify potential domains, map methodology components, modifications required, suitable datasets, expected benefits, feasibility/limitations, comparison with existing approaches, future scope |
| 10 | Timeline – Update on Tasks | "Project should be complete in all aspects. Display the Project Report to the Panel. Status on completion of Project Report." |
| 11 | Conclusion and Future Work | Summarize key points + glimpse of future work |
| 12 | References | IEEE format, numbered, with worked example given |
| 13 | **IEEE Draft** | "Display the draft of your project work in an IEEE template if prepared to submit to a Conference/Journal. Indicate status of completion. **Download the official IEEE conference template**: `https://www.ieee.org/content/dam/ieee-org/ieee/web/org/conferences/Conference-template-A4.doc`. Mention target conferences/journals." |
| 14 | Any other information | Free slot; changes need guide's consent |
| 15 | References (duplicate of 12 in source file — likely a template artifact, not two separate required slides) |
| 16 | Thank You | Closing slide |

## Key implications for Task 4

1. **The deck itself demands the IEEE paper as a visible deliverable** (slide 13) — confirms Task 3 and Task 4 are tightly coupled in this phase's evaluation, not independent. The IEEE-paper status/progress must be shown and target venues named.
2. **Authoritative IEEE template is explicitly the official two-column IEEE conference `.doc` template**, not the Springer `llncs` style used by `Details/Coordination_Specialization...pdf`. Whatever becomes "the IEEE paper" must be migrated to this exact template before it can satisfy slide 13.
3. Testing (slide 7) is given a full dedicated slide with explicit sub-requirements (test types, per-member roles, tooling, benefits/drawbacks) — matches the master prompt's "testing is the highest priority" framing and should not be compressed.
4. Slide 9 ("Applicability in Other Domains") is a PES-specific requirement not present in the generic master-prompt slide outline — must be added to Task 4's slide plan; it asks for a transfer-learning / generalization discussion, which should be answered honestly given `docs/PROJECT_STATE.md`'s unresolved "scope of company/domain transfer learning" decision (i.e., describe this as a discussion of applicability, not a claim that transfer has been implemented or tested).
5. Slide 4 ("Suggestions from Review – 2") requires actual panel feedback from a prior review — this is information only the user has; it cannot be fabricated and must be supplied by the user before Task 4 can be completed.
6. No slide count / timing constraint is stated anywhere in the template itself (unlike the master prompt's generic "10-12 min, 10-14 slides" placeholder) — the 16-slide structure above is PES's actual fixed structure for this review and should be followed as-is rather than the master prompt's generic suggestion.

## Visual design

Template includes a consistent slide master (header "Title of the Project" / footer "name1_name2_name3_name4" placeholder on every slide) — actual design/theme was not rendered as images in this pass (text-only OOXML extraction); a visual check of the master slide's color scheme/fonts should be done when actually populating the deck in Task 4.
