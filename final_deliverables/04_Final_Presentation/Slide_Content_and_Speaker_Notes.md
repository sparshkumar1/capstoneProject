# PrepAIred — Phase-3 Review-3 Presentation Content

**SUPERSEDED (2026-11-13):** per explicit user decision, `PrepAIred_Final_Presentation.pptx`/`.pdf` is the
canonical final presentation. The `PrepAIred_Phase3_Review3.pptx`/`.pdf` this document describes is a preserved
earlier, separately-built file — kept, not deleted, but not the one to present or submit. Its Slide 4 (filled in
earlier the same day, before this supersession decision) described the Review-2 suggestions; the canonical file's
Slide 4 now carries the same content in its own established style — see
`final_deliverables/FINAL_ACADEMIC_DELIVERABLE_COMPLETION_CHECKLIST.md` and `Slide_by_Slide_Quality_Audit.md` for
the canonical file's status.

**Format note:** no PPTX-authoring tool (python-pptx) was available in this session (would require another `pip install`, same pattern as `pytest`/`httpx` earlier — install it and I can generate the actual `.pptx` file directly into `Details/PPT-Template_Phase3- Review3.pptx`'s structure). This document is the complete slide-by-slide content and speaker notes, ready to transfer into that template's existing 16 slides (structure extracted and confirmed in Phase 1 — do not add or remove slides, per the template's own fixed structure).

---

## Slide 1 — Title

**Project Title:** PrepAIred: A Reinforcement-based LLM-powered Interview Preparation System
**Project ID:** PW26_UD05
**Project Guide:** Dr Uma D
**Project Team:** Sparsh Kumar, Naveen S Khadd, Manasa S A, Athreya Shashidhara

*(No speaker notes needed — title slide.)*

---

## Slide 2 — Outline

Bullet list matching the template's own fixed outline exactly:
Abstract · Suggestions from Review-2 · Implementation Details · Project Demonstration · Test Plan and Strategy · Results and Discussion · Applicability in Other Domains · Timeline · Conclusion and Future Work · References · IEEE Paper Draft · Any Other Information

---

## Slide 3 — Abstract

**Bullets:**
- PrepAIred: adaptive technical-interview practice system — rubric-anchored semantic evaluation + RL-driven difficulty adaptation + structured per-turn feedback.
- Phase-3 contribution: a complete, evidence-based testing and verification programme on top of the Phase-2 implementation.
- Headline result: 264/283 automated tests passing (93.3%), two real defects found and fixed, eight documentation-vs-code discrepancies corrected.

**Speaker notes:** Set the context in under a minute — this is not a new feature phase, it's a verification phase. The interesting story is what testing found, not just that testing was done. Lead with the guardrail-gap finding as the headline, since it's the most technically substantive result.

---

## Slide 4 — Suggestions from Review-2

**Bullets:**
- Suggestions received from the Review-2 panel:
- 1. Best-answer retention: remember and display the candidate's best answer for each question, across attempts and sessions.
- 2. Multiple attempts per question: allow a candidate to retry a question within the same session before moving on.
- Response: Both are implemented: `services/storage/best_answer.py` selects and retains each candidate's strongest eligible attempt per question, carried into feedback and the session report; the orchestrator's retry flow lets a candidate resubmit an answer within a session, rolling back the superseded attempt so only the best one is scored.

**Speaker notes:** Name both suggestions explicitly before describing the response, so the panel recognizes their own feedback. Point to `best_answer.py`'s eligibility rules (correct/partial attempts only) if asked how "best" is decided, and to the orchestrator's retry flow for how a resubmission is scored.

---

## Slide 5 — Implementation Details

**Bullets (module / technology / what it does):**
- Orchestrator (`agents/orchestrator/`) — Python, asyncio — sole authoritative session-state owner, `asyncio.Lock`-serialised
- Evaluator (`services/evaluator/`) — **Flask** (corrected from an earlier FastAPI claim) — 3-component semantic scoring (SBERT + FAISS + CrossEncoder)
- Strategy/RL (`agents/strategy/`, `rl/`) — Stable-Baselines3 PPO, `Discrete(3)` actions, 6 deterministic guardrail rules
- Coding sandbox (`agents/coding_executor/`) — Docker, isolated per-submission containers
- Frontend (`apps/web/`) — React + Vite, WebSocket-driven

**Pseudocode to show (from the accompanying report, Ch.9):** the adaptive-difficulty pipeline pseudocode — short, visual, shows the guardrail-override step clearly (this sets up Slide 8's results).

**Speaker notes:** Keep this slide architecture-level, not code-dump. Point to the report for full pseudocode. Emphasize the guardrail-as-safety-layer framing since it pays off later.

---

## Slide 6 — Project Demonstration

**Content:** a live or recorded walkthrough of a full interview session (start → question → verbal/code answer → feedback → adaptive next question → session report).

**Status:** the backend and evaluator services were confirmed live and healthy during this phase's smoke testing (real health-check responses captured, real question bank loaded). A full live demo was not recorded as a video/screenshot asset in this pass — no screen-capture/browser-automation tool was available in this session. **Recommend:** run `python launch.py` yourself and screen-record a session before the review; I can help script a representative demo scenario (e.g. one strong answer, one weak answer, one code submission) if useful.

**Speaker notes:** If a live demo isn't feasible in the room, show the Report.jsx screenshot (if captured) or describe the flow using Slide 5's pseudocode as a visual aid.

---

## Slide 7 — Test Plan and Strategy

**Bullets:**
- 22 testing categories classified by actual relevance to this codebase (not generic checklist) — see `testing_and_evaluation/Test_Strategy.md`
- Functional/Non-functional split: Unit+Integration+E2E (existing 283-test suite) · API contract, adversarial-input, DB integrity, security-config, performance, UI-structural (11 new scripts this phase)
- Test environment: Windows 11, Python 3.11.9, documented git commit, full environment record
- Each team member's role: *[fill in — who ran/owned which test category]*
- Tools: pytest, Vitest, direct Python scripts against production code (no mocking of the function under test)
- Benefit: found 2 real defects + 8 documentation errors that a generic test-count-only approach would have missed
- Drawback: 18 tests remain blocked pending a running Docker daemon in the test environment (documented, not hidden)

**Speaker notes:** This is the panel's highest-attention slide per the template's own instructions — don't compress it. Walk through the diagnose→fix→reverify cycle for the guardrail gap as the concrete example of "why this methodology matters," not just "what categories we covered."

---

## Slide 8 — Results and Discussion

**Bullets:**
- **264/283 automated tests passing (93.3%)** — every one of the 19 remaining failures fully attributed (18 × Docker daemon down, 1 × pre-existing documented issue), zero unexplained failures
- **Real defect found and fixed:** guardrail coverage gap (perf 0.30–0.40 unguarded against difficulty escalation) — found via direct testing of the live policy checkpoint, fixed with a single-threshold change, verified 13/13, zero regressions
- **Real defect found and fixed:** `launch.py` crashed on Windows consoles (Unicode encoding) — fixed, verified
- **8 documentation-vs-code discrepancies corrected** (e.g. question selection is rule-based, not FAISS-retrieval as previously documented; evaluator is Flask, not FastAPI; PPO training figures corrected)
- Deviation from initial expectation: yes — testing was expected to confirm existing behaviour; it instead surfaced genuine new findings, which is reported honestly rather than smoothed over

**Chart suggestion** (build from real data, not illustrative): a simple bar chart of pass/fail/skip counts before vs. after the two dependency installs (pytest, httpx) and the two fixes, from `testing_and_evaluation/Master_Results_Table.md` — all four numbers are real and logged.

**Speaker notes:** This is the strongest slide — lead with the guardrail finding, it's the most defensible, most interesting result. Don't bury it under the pass-rate percentage.

---

## Slide 9 — Applicability of Proposed Methodology in Other Domains

**Bullets:**
- **Potential domains:** any adaptive-assessment system pairing a learned policy with a deterministic safety/guardrail layer — e.g. adaptive e-learning platforms, medical-training simulators, automated proctoring/scoring systems
- **Common problem:** a safety layer is assumed correct because it's deterministic and rule-based, but is rarely boundary-tested against the live policy it constrains
- **Methodology components that map over:** (1) direct-against-production testing (no mocking the function under test), (2) boundary-case construction at and around every documented rule threshold, (3) diagnose→minimal-fix→reverify→full-regression discipline
- **Modifications required:** domain-specific state-vector dimensions and guardrail conditions; otherwise the testing *methodology* is domain-agnostic
- **Feasibility/limitations:** requires a deterministic, inspectable guardrail function (not a black-box policy) — this methodology doesn't directly transfer to end-to-end black-box ML systems
- **Future scope:** package the guardrail-boundary-testing scripts as a reusable harness for other RL+guardrail systems

**Speaker notes:** This slide exists in the PES template specifically — don't improvise generic "AI is everywhere" content. Keep it to the testing-methodology transfer, which is this phase's genuine contribution, not an unsubstantiated claim about the whole system generalising.

---

## Slide 10 — Timeline: Update on Tasks

**Bullets:**
- Phase-2 (Jan–May 2026): full implementation delivered
- Phase-3 (this phase): inspection → test strategy design → baseline testing → diagnosis & fixes → results consolidation → report/paper/PPT drafting
- Project report status: **drafted in full** (13 files, front matter + 11 chapters + bibliography) — pending transfer into the official DOCX template and resolution of 2 flagged citations
- *[Fill in: remaining team-specific milestones/dates]*

**Speaker notes:** Be concrete about what's genuinely done (report content, testing) vs. what's pending (DOCX formatting, citation resolution, live demo recording) — don't overstate completion.

---

## Slide 11 — Conclusion and Future Work

**Bullets:**
- Verified: core architecture functions as designed; 10/12 stated objectives met with direct evidence
- Two real defects found and fixed in this phase (guardrail gap, launcher crash)
- Future work: close the Docker-dependent test gap; resolve the 1 pre-existing known test failure; formal human-subject evaluation; real WER evaluation of the audio pipeline; a separate, explicitly-scoped decision on whether to build the multi-agent coordination layer described in a supplied (currently unverified-against-this-codebase) research paper draft

**Speaker notes:** Mirror the report's Chapter 11 — don't introduce new claims here that aren't in the report.

---

## Slide 12 / 15 — References (IEEE format)

Use the bibliography from the accompanying project report (`final_deliverables/02_University_Project_Report/12_Bibliography.md`) — note 2 citations ([6] Wu et al., [7] Auctores Online) are flagged as unresolved; either resolve before the review or omit them from the slide version.

---

## Slide 13 — IEEE Paper Draft

**Bullets:**
- Status: **drafted in full** — `final_deliverables/03_Research_Paper/PrepAIred_IEEE_Paper_Draft.md`
- Scope: rescoped in this phase to describe only the real, verified system (a separate draft describing an unbuilt multi-agent coordination layer was found not to correspond to the codebase and was explicitly excluded — stated transparently, not hidden)
- Core contribution: the guardrail-gap discovery-and-fix case study (Slide 8), framed as a testing-methodology paper
- Target: official IEEE two-column conference template (not yet transferred — content is ready, formatting pending)
- Target conferences/journals: *[fill in — not specified in supplied materials; suggest discussing with your guide given the paper's actual scope (a testing-methodology case study, not a novel-algorithm paper) to pick an appropriately-scoped venue]*

**Speaker notes:** Be upfront that this is a rescoped paper, not the originally-circulated "bounded authority" draft — and explain briefly *why* (research integrity, not a downgrade): the original draft's results didn't exist in the codebase, so submitting it as-is would have been presenting fabricated results.

---

## Slide 14 — Any Other Information

Optional. Suggested content if used: the discrepancy-correction process itself as a methodological note (how 8 documentation errors were found and fixed), since it's a genuine, slightly unusual contribution worth a mention if time allows.

---

## Slide 16 — Thank You

*(No content needed.)*

---

## Summary of blockers for a complete, review-ready deck

1. ~~**Slide 4** (panel feedback)~~ — resolved: both Review-2 suggestions and the response are filled in (2026-11-13).
2. **Slide 6** (live demo) — needs a screen recording/screenshots; I can help script the demo scenario.
3. **Actual `.pptx` file** — needs `python-pptx` installed (same pattern as earlier installs) for me to generate it directly, or manual transfer of this content into the template by you.
4. **References** [6]/[7] need resolving before the References slides are finalized.
