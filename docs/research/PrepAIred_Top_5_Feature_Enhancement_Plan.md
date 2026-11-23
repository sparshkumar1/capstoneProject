# PrepAIred — Top 5 Feature Enhancement Plan

**Baseline:** branch `final-eval/controlled-improvements`, commit `1caa90b`. **Inspection method:** direct code reading of `apps/web/src/` (every page component), `apps/backend/main.py` (every route + WS handler), `agents/orchestrator/interview_orchestrator.py`, and the live `data/prepaired.db` schema — not inference from documentation.

## Phase 1 finding that reshaped this plan

PrepAIred already has a **fully built** personalized dashboard (KPIs, score trend, streak, weekly goal, suggested next steps), a **full analytics page** (performance-over-time, topic mastery, by-difficulty/by-type breakdown, attempt comparison), a **full weakness map** (per-concept classification, spaced-repetition flip-cards with self-rating, declining-topic detection, focused-practice launcher), a **preparation-plan generator** (date + minutes/day → weekly focus plan), and an **admin dashboard** (stats, filterable/sortable session table, per-session drill-down with score rings and behavior insights). A **per-session difficulty timeline** also already exists in the post-session report (`Report.jsx`'s "Timeline" tab, backed by `difficulty_history`).

Per this task's own instruction ("do not suggest an existing feature as a new feature"), none of the above are proposed again below. The five features below were selected specifically because they are either **absent** (verified by direct grep — zero matches anywhere in `apps/web/src`) or **documented as broken/incomplete** by this project's own prior testing evidence.

## 12 ideas considered

| # | Idea | Status after inspection |
|---|---|---|
| 1 | Personalized dashboard | **Exists** — not proposed |
| 2 | Weak-topic analytics | **Exists** (`WeaknessMap.jsx`) — not proposed |
| 3 | Progress/trend charts | **Exists** (`Analytics.jsx`) — not proposed |
| 4 | Streaks/goals/study plan | **Exists** (`Dashboard.jsx`'s `PrepPlan`) — not proposed, but its **backend persistence gap** is real → selected as Feature 5 |
| 5 | Spaced-repetition revision | **Exists** (`WeaknessMap.jsx` flip-cards) — not proposed |
| 6 | Session comparison | **Exists** (`Analytics.jsx`'s `ComparePanel`) — not proposed |
| 7 | Difficulty trajectory visualization | **Exists** (`Report.jsx` Timeline tab) — not proposed |
| 8 | **On-demand hints during an interview** | **Documented broken** (DEF-001, `testing_output/PrepAIred_Comprehensive_Testing_Report.md`): WS dispatcher has no `request_hint` handler; direct grep also confirms the frontend has **no UI trigger at all** → **selected (Feature 1)** |
| 9 | **Question bookmarks / notes** | **Absent** (zero matches for "bookmark" anywhere in `apps/web/src` or the DB schema) → **selected (Feature 2)** |
| 10 | **Downloadable/shareable PDF session report** | **Absent** — no PDF export route or button found anywhere | **selected (Feature 3)** |
| 11 | **Admin per-candidate drill-down (cross-session view)** | **Absent** — admin dashboard is session-table-only, no "all sessions for this candidate" aggregate view | **selected (Feature 4)** |
| 12 | Video/facial analysis | Out of scope — explicitly a disclosed, deliberate non-feature of this project (no camera pipeline exists); adding it would be a major new capability, not a contained enhancement |

**Why not more UI-polish ideas:** the existing UI (dark/light theme, consistent card/panel system, `EmptyState`/`ErrorState`/`Skeleton` components) is already professionally built and consistent — see the inspection notes. Generic "improve the UI" ideas were dropped in favor of concrete, verifiably-absent capabilities.

## Selected 5

### Feature 1 — Complete the On-Demand Hint Feature
**Problem:** a documented-but-non-functional feature. The backend WebSocket dispatcher's own docstring lists `request_hint` as a supported client message and `hint` as a server response, but the `elif` chain handling messages has no branch for it — any client message is silently dropped. The frontend has no button to send it either.
**Value:** candidates stuck on a question currently have no in-session help path besides skipping. A working hint button is a core interview-prep expectation.
**UX:** a "Hint" button next to the question, disabled while evaluating; shows the returned hint text in a dismissible panel; a quota (one hint per question) to prevent it replacing genuine effort.
**Frontend:** `apps/web/src/useInterviewWS.js` (add `case "hint"`), `apps/web/src/InterviewRoom.jsx` (hint button, hint panel, `requestHint` call, per-question quota state).
**Backend:** `apps/backend/main.py` (new `elif mtype == "request_hint":` branch calling the already-existing, already-working `orch.request_hint(question_id)`).
**DB:** none.
**Dependencies:** `InterviewOrchestrator.request_hint()` (already implemented and independently verified working in-process by prior testing) and the Qwen hint HTTP endpoint (already implemented and independently verified working by prior testing) — this feature only wires two already-correct pieces together.
**Complexity:** Low. **Risk:** Very low — one new, additive `elif` branch; no existing branch touched.
**Testing:** live WS round-trip (`{"type":"request_hint","payload":{"question_id":...}}` → expect a `hint` message), plus full regression suite.

### Feature 2 — Question Bookmarks & Notes
**Problem:** a candidate has no way to flag a question for later review or attach a personal note to it; the only options today are the system-chosen weakness map and spaced-repetition queue, which are not candidate-directed.
**Value:** direct candidate control over what they want to revisit — a standard, expected feature of any serious prep platform.
**UX:** a bookmark toggle icon on each question in `Report.jsx`'s Questions tab and `WeaknessMap.jsx`'s question list; a new "Bookmarks" view (reachable from the dashboard) listing all bookmarked questions with the candidate's note, editable inline, with a "Practice this" launcher reusing the existing `practice.js` session-launch helper.
**Frontend:** new `Bookmarks.jsx` page + nav entry, a reusable `BookmarkToggle` component, wiring into `Report.jsx`/`WeaknessMap.jsx`.
**Backend:** new routes `POST/DELETE /api/candidates/{id}/bookmarks`, `GET /api/candidates/{id}/bookmarks` in `apps/backend/main.py`.
**DB:** new table `bookmarks(id, candidate_id, question_id, note, created_at)` added via `services/storage/database.py` (additive migration — `CREATE TABLE IF NOT EXISTS`, no existing table altered).
**Dependencies:** existing candidate auth (`SessionContext`), existing question-bank lookup for display text.
**Complexity:** Medium. **Risk:** Low — purely additive table and routes; no existing route or table modified.
**Testing:** backend route tests (create/list/delete roundtrip against a disposable DB copy), frontend render/interaction check, full regression suite.

### Feature 3 — Downloadable PDF Session Report
**Problem:** a candidate's only way to keep or share a session report is to leave the browser tab open; there is no export.
**Value:** lets a candidate save their report or share it with a mentor/recruiter — meaningfully increases the report's real-world usefulness, and showcases the product well in a demo.
**UX:** a "Download PDF" button on `Report.jsx`, generating and downloading a formatted PDF of the same report data already on screen.
**Frontend:** button + fetch-and-download handling in `Report.jsx`.
**Backend:** new route `GET /api/sessions/{id}/report/pdf` in `apps/backend/main.py`, rendering the already-computed report dict (same data `getReport` already returns) to a PDF using `reportlab` (already a dependency of this repo's own deliverable-building scripts, so no new dependency is introduced).
**DB:** none — reads the same report data already assembled for the JSON endpoint.
**Dependencies:** the existing `/api/sessions/{id}/report` data assembly logic (reused, not duplicated).
**Complexity:** Medium. **Risk:** Low — purely additive route; existing `/report` JSON route untouched.
**Testing:** direct call to the new route confirming a valid PDF is returned (content-type, non-trivial byte size, page count), full regression suite.

### Feature 4 — Admin Per-Candidate Drill-Down View
**Problem:** the admin dashboard (`AdminDashboard.jsx`) is session-centric — a faculty/evaluator reviewing one candidate's overall progress must manually find and open each of that candidate's sessions one at a time from a flat table.
**Value:** gives the admin/faculty persona an aggregate, at-a-glance view of one candidate's trajectory across all their sessions — directly useful for the "could be demonstrated to faculty members" objective.
**UX:** clicking a candidate name/email in the admin session table opens a candidate-level panel: all sessions for that candidate, their score trend, and topic coverage, reusing the existing `ScoreRing`/`LineChart` components for visual consistency.
**Frontend:** new `AdminCandidateDrilldown` panel/component in `AdminDashboard.jsx`.
**Backend:** new route `GET /api/admin/candidates/{id}/sessions` in `apps/backend/main.py`, reusing the already-fixed `list_sessions()` persistence logic filtered by candidate.
**DB:** none — reads existing `sessions`/`candidates` tables.
**Dependencies:** the admin session-merge logic already fixed earlier in this engagement (`_admin_sessions_merged()`).
**Complexity:** Medium. **Risk:** Low — new, additive route and UI panel; existing admin table/detail view untouched.
**Testing:** backend route check against the real DB (27 existing sessions), frontend interaction check, full regression suite.

### Feature 5 — Server-Synced Study Goals (enhancement, not new)
**Problem (classified honestly as an enhancement, not a new feature):** `Dashboard.jsx`'s weekly goal and preparation plan are fully built but persisted **only in `localStorage`** — lost on cache clear, not synced across devices/browsers for the same candidate.
**Value:** makes an already-valuable feature actually reliable for a candidate who studies from more than one device.
**UX:** unchanged — the existing goal/plan UI is reused as-is; only its persistence layer moves from the browser to the backend, transparently.
**Frontend:** `Dashboard.jsx`'s goal/plan read/write calls switch from `localStorage` to the new API, with `localStorage` kept as an offline fallback/cache (graceful degradation if the API call fails).
**Backend:** new routes `GET/PUT /api/candidates/{id}/study-goal` in `apps/backend/main.py`.
**DB:** new table `study_goals(candidate_id PRIMARY KEY, target_date, minutes_per_day, plan_json, updated_at)` (additive).
**Dependencies:** none beyond existing candidate auth.
**Complexity:** Low–Medium. **Risk:** Low — additive table/routes; the existing localStorage code path is preserved as a fallback, not deleted, so nothing breaks if the new API is unreachable.
**Testing:** backend route roundtrip test, frontend fallback-to-localStorage check (simulate API failure), full regression suite.

## Implementation order (smallest/lowest-risk first)

1. Feature 1 (On-Demand Hints) — smallest, most isolated, highest-confidence fix.
2. Feature 2 (Bookmarks & Notes) — new table, contained.
3. Feature 3 (PDF Export) — new route only, reuses existing data assembly.
4. Feature 4 (Admin Drill-Down) — new route + UI panel, reuses existing merge logic.
5. Feature 5 (Server-Synced Goals) — touches existing frontend state code the most (switching a data source), done last so the other four are stable first.

Each feature is implemented, manually verified against the live stack, and the full backend `pytest` + frontend `Vitest` suites are re-run before moving to the next — per the task's own "keep changes logically separated and easy to review" instruction.
