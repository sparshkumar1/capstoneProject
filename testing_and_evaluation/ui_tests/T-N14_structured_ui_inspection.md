# T-N14 — Structured UI Inspection (category M)

**Scope note:** per `Test_Strategy.md`, a genuine participant usability study is out of scope (no participants recruited, no ethics approval — consistent with `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §C.3's existing finding that human-subject provenance is an open gap project-wide). This is a **structured, code-level interface inspection**, labeled as exactly that, not a user study — live browser screenshots were not captured in this pass (no confirmed browser-automation tool available in this session; rather than attempt an unreliable workaround, the automated frontend test suite plus direct code reading were used instead, which is both faster and produces more precise, reproducible evidence).

## What was inspected

The two primary views (`apps/web/src/InterviewRoom.jsx`, 550 lines; `apps/web/src/Report.jsx`, 792 lines) and the already-passing automated test suite that targets them (`apps/web/src/__tests__/*.test.jsx`, 28/28 passing — see `Baseline_Record.md`).

## Findings

### Report.jsx — explicit loading/error states (not a bare blank screen on failure)
- `loading`/`error` state variables with a dedicated `<LoadingSkeleton />` component shown while fetching.
- On fetch failure: explicit error card with human-readable messaging ("Failed to load session report from server. Please retry.") rather than a silent failure or raw stack trace — directly exercised and confirmed by the already-passing test `ui_fixes.test.jsx::"Report.jsx displays explicit error state on API failure without mock data"`.
- Distinguishes "no session ID found" (user navigated directly without a session) from "fetch failed" (network/server issue) as two different, correctly-worded error states.

### InterviewRoom.jsx — error handling across three independent input modalities
- Microphone errors (`micError`) surfaced inline near the recording control, not just logged silently.
- Code-execution errors (`codeResult.error`/`codeResult.stderr`) rendered in a dedicated styled output block (`error`/`passed`/`failed` CSS states), with stderr shown separately from the error message.
- WebSocket-level errors logged via an `onError` callback (`console.error("[Interview error]", err)`) — present, though this one is console-only rather than user-facing; worth a note for Task 2's limitations section (minor, not a defect — console logging for a debug/dev-facing error path is a reasonable design choice, just not independently user-facing).

### Already-verified via the automated suite (not re-derived here, just cited)
- `question_progress.test.jsx`: primary-question vs. follow-up numbering displays correctly ("Question 1 of 15", "Follow-up to Question 1", "Question 2 of 15").
- `best_answer_authority.test.jsx`: frontend correctly reflects "no eligible best answer" from the backend rather than fabricating a best-answer UI when none exists — a genuine anti-fabrication UI check, consistent with the project's broader "don't fabricate" discipline extending into the frontend layer.
- `ui_fixes.test.jsx`: confirms raw numerical scores/percentages are hidden from the candidate-facing feedback card (qualitative presentation only) and that the interviewer-avatar component doesn't duplicate intro bubbles or leak percentage values.

## What this does NOT establish

- Visual layout quality, responsiveness across screen sizes, actual rendered appearance, color contrast/accessibility, or any subjective usability judgment — none of these were assessed (would require either real screenshots or a participant walkthrough, neither performed).
- Real end-user task completion time, confusion points, or satisfaction — would require the formal human-subject study the project's own Ch.7.3 Future Work already identifies as outstanding.

## Conclusion

The frontend has substantive, deliberate error/loading-state handling (not an afterthought), confirmed by direct code inspection and corroborated by 28 passing automated tests targeting exactly these behaviors. This is genuine evidence of implementation quality — but it is structural/functional evidence, not usability evidence, and should be presented as such in Task 2/3/4.
