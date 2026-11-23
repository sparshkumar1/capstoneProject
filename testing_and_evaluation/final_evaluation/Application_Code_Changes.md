# Application Code Changes — Final Evaluation Phase

**Branch:** `final-eval/controlled-improvements` (created from `workspace/human-eval-clean-push` at commit `9d5c528b3596d0d80c6bb8d606547f64c036b081`, the exact commit the prior `Independent_Project_Audit` was run against — no drift existed before this phase began).
**Pre-existing uncommitted changes carried over unchanged:** `launch.py`, `rl/guardrails.py` (both already present and already documented in `testing_and_evaluation/Phase4_Diagnosis_and_Fixes.md` before this phase started — not touched further here).

**Scope authorization:** this phase operates under the explicit "IMPORTANT CHANGE — CONTROLLED APPLICATION IMPROVEMENTS ARE PERMITTED" instruction, which supersedes the earlier blanket no-code-change rule. Every change below follows the mandated 10-step process (identify → evidence → root cause → minimal change → preserve baseline → isolated branch → rerun tests → compare → regression check → record), is a narrow bug fix or reliability fix (not a redesign), and preserves the project's existing architecture, frameworks, and identity unchanged.

**Files changed this phase (4 files, all listed):**
1. `services/qwen/app.py`
2. `apps/backend/main.py`
3. `services/storage/database.py`
4. `rl/env/interview_env.py`

No model weights, checkpoints, training scripts, reward function, PPO configuration, database schema, or frontend code were touched. No file outside the four listed above was modified during this phase.

---

## Change 1 — Qwen feedback/follow-up JSON-field parsing bug (`services/qwen/app.py`)

### Step 1 — Identify the problem
While capturing real Qwen outputs for the quality-evaluation task (Phase 1, see `07_Qwen_Feedback_Quality_Evaluation.md`), live calls to `POST /api/qwen/feedback` returned list fields (`what_was_correct`, `what_was_incorrect`, `what_was_incomplete`, `missing_concepts`) shredded into **individual characters** instead of complete phrases, e.g. `"what_was_correct": ["A", " ", "p", "o", "i", "n", "t", "e", "r", ...]` instead of `["A pointer stores a memory address."]`. This is not a crash-safety issue (the endpoint still returned `200 OK`) — it is a silent data-corruption bug that would reach every real candidate's feedback screen whenever it occurs.

### Step 2 — Establish evidence
Reproduced directly against the live, running Qwen service (not a mock) with a real question/answer pair. Raw evidence saved: `testing_output/Testing_Evidence/QWEN_QUALITY_SAMPLES.json` (pre-fix capture, both feedback samples affected).

### Step 3 — Root cause
`services/qwen/app.py`, `generate_feedback()` (and `_validate_feedback_output()`, and `generate_followup()`) built these fields with `[str(x) for x in data.get("what_was_correct", [])]`. When the local GGUF model (Qwen2.5-1.5B-Instruct, quantized) emits a JSON **string** for a field the schema defines as an array — which it does intermittently, a known reliability characteristic of small/quantized LLMs under JSON-schema prompting — Python's `for x in <string>` iterates the string **character by character**, since strings are iterable. No type check existed before the comprehension ran. This is a genuine application defect, confirmed by direct code reading and live reproduction, not a testing artifact.

### Step 4 — Minimum effective modification
Added one small, pure, defensively-typed helper function, `_as_str_list(value) -> list[str]`, and replaced the **7** vulnerable call sites (found by a full-file grep, not just the one that was first observed) with calls to it. The helper wraps a scalar/string as a one-element list instead of iterating it; it leaves genuine lists untouched (filtering only empty/`None` entries, matching the previous comprehensions' intent). No prompt, model, model configuration, or scoring logic was touched — this is purely a response-parsing fix.

**Exact call sites fixed** (file: `services/qwen/app.py`):
- `_validate_feedback_output()` — `missing`, `what_correct` (internal contradiction check)
- `generate_feedback()` — `what_was_correct`, `what_was_incorrect`, `what_was_incomplete`, `missing_concepts`, `actionable_improvements`
- `generate_followup()` — `target_concepts`

### Step 5 — Baseline preserved
Pre-fix evidence retained at `testing_output/Testing_Evidence/QWEN_QUALITY_SAMPLES.json`. No other file touched.

### Step 6 — Implemented on an isolated branch
`final-eval/controlled-improvements`.

### Step 7 — Rerun tests
1. **Unit-level**: `_as_str_list()` tested directly against the exact malformed pattern observed live, plus list/`None`/empty-string/mixed-`None` edge cases — 5/5 pass.
2. **Live, real-model regression**: a disposable second Qwen instance (port 8002, same code, same real GGUF model) was started so the fix could be exercised against genuine LLM output without disturbing the primary running service. The **identical** question/answer pair that previously produced character-split output was resubmitted and retried until a genuine LLM-sourced response (`decision_source: "qwen_1.5b_llm"`) was captured.

**Before (pre-fix, live model, real capture):**
```json
"what_was_correct": ["A"," ","p","o","i","n","t","e","r"," ","s","t","o","r","e","s", "..."]
```
**After (post-fix, live model, same prompt, real capture — `testing_output/Testing_Evidence/QWEN_POSTFIX_feedback_strong.json`):**
```json
"what_was_correct": ["A pointer stores a memory address."]
```

### Step 8 — Compare results
Before: every one of 2/2 captured real feedback samples exhibited the character-split defect. After: 0/2 retries exhibited it once resubmitted against the fixed code (full sentences preserved).

### Step 9 — Regression risk
None identified. The change only wraps malformed scalar output; well-formed list output is returned unchanged (verified in the unit test). No other endpoint, field, or code path references `_as_str_list`'s inputs in a way this change could affect.

### Step 10 — Outcome
**Fixed and verified.** Severity of the original defect: **High** (silent, user-visible data corruption in narrative feedback — the system's core candidate-facing explanation text) despite the HTTP layer reporting success throughout, which is exactly the kind of defect a crash-only test suite cannot catch.

### Related finding, NOT fixed (documented only, per instructions)
While tracing this code, direct reading of `generate_hint()` and `generate_report()` (same file) found that **neither function calls the LLM at all** — both are pure Python f-string templates. Their responses are labeled `decision_source: "qwen_hint"` / `"qwen_report"`, which reads as if LLM-sourced but is not. This contradicts how Qwen's hint/report role has been described in this project's own prior documentation (including this engagement's own earlier `Independent_Project_Audit` and IEEE paper draft, both of which characterized hints as LLM-generated). This is **not changed** here — it may be an intentional design choice (fast, deterministic hints/reports) — but it is recorded as a documentation-accuracy finding requiring correction in prior deliverables; see `07_Qwen_Feedback_Quality_Evaluation.md` §4 for full detail and `14_Executive_Summary.md` for the list of prior documents this affects.

---

## Change 2 — Admin dashboard reads only in-process state, not persisted history (`apps/backend/main.py`, `services/storage/database.py`)

### Step 1 — Identify the problem
`GET /api/admin/sessions`, `/api/admin/stats`, and `/api/admin/sessions/{id}` iterated only the module-global, in-process `SESSIONS` dict. Any session from a prior backend process (i.e. anything before the current process started) was invisible to the admin dashboard, even though `services/storage/database.py::save_session()` genuinely persists it. This was already identified, by static analysis only, in the prior `Independent_Project_Audit`; this phase closes it.

### Step 2 — Establish evidence
Confirmed directly: `GET /api/admin/sessions` before the fix returned only sessions created in the currently-running process. A direct, read-only SQLite query of `data/prepaired.db` independently confirmed 27 persisted session rows existed, none of which the admin endpoint could show.

### Step 3 — Root cause
No code path ever queried the `sessions` table for display; it was write-only from the admin dashboard's perspective.

### Step 4 — Minimum effective modification
- **`services/storage/database.py`**: added one new, read-only function, `list_sessions()`, that `SELECT`s from `sessions` joined with `candidates` (name/email/college/year), ordered by recency. It returns only the columns `sessions` already persists (`save_session`'s own write columns) — **no schema change**, no new table, no new persistence.
- **`apps/backend/main.py`**: added one helper, `_admin_sessions_merged()`, which reads `list_sessions()` first (so historical sessions are always included) and then overlays any in-process `SESSIONS` entries by id (richer live data wins when both exist — the in-memory entry has fields, like `c_score`/`dsa_score`/`behaviour`, that are not in the persisted schema). `admin_sessions`, `admin_stats`, and `admin_session_detail` were updated to use this merged view, with `admin_session_detail` additionally falling back to the persisted row when a requested id isn't in memory.

### Step 5 — Baseline preserved
No existing function was removed or altered in behavior for already-working callers; `get_candidate_history` and every other existing `database.py` function are untouched.

### Step 7 — Rerun tests / Step 8 — Compare results
Re-ran this phase's own admin test cases (originally `MOD-ADMIN-001`/`002` from the prior comprehensive testing report) against the live, auto-reloaded backend:

| Check | Before | After |
|---|---|---|
| `GET /api/admin/sessions` → total | Only sessions from the current process | **27 persisted sessions** returned, confirmed via an independent, process-isolated call to `list_sessions()` directly (not through the possibly-still-warm in-process dict) |
| A session from October 2026 (weeks before this engagement), candidate "Naveen", created in a since-ended process | Not visible | **Correctly returned**, with real `candidate_name`, `overall_score`, `topics` |
| `GET /api/admin/stats` → `total_sessions` | Process-local count only | Reflects the merged (persisted + live) count |

Full evidence: `services/storage/database.py::list_sessions()` output captured directly in a fresh, isolated Python process (immune to any possibly-stale in-memory state), and cross-checked by a separate, independent, raw read-only `sqlite3` query confirming the same session ids and field values exist in `data/prepaired.db`.

### Step 9 — Regression risk
Low. `c_score`, `dsa_score`, `final_difficulty`, `strengths`, `missing_concepts`, `behaviour` are `None`/empty for DB-sourced (historical) rows, since the `sessions` table does not persist those fields (this is disclosed, not silently papered over — see Limitations in `14_Executive_Summary.md`). Live, in-memory sessions are unaffected and keep full field richness, since they still take precedence on id collision.

### Step 10 — Outcome
**Fixed and verified**, with the caveat above honestly disclosed (partial field richness for pre-restart sessions) rather than claimed as a complete fix.

---

## Change 3 — Stale duplicate guardrail fallback boundary (`rl/env/interview_env.py`)

### Step 1 — Identify the problem
The prior, already-approved fix to `rl/guardrails.py` (2026-11-12, documented in `testing_and_evaluation/Phase4_Diagnosis_and_Fixes.md`) widened guardrail rule G5's lower bound from `perf > 0.40` to `perf >= 0.30`, closing a real safety-coverage gap. `rl/env/interview_env.py::InterviewEnv._apply_guardrails()` contains an **inline duplicate** of the same six guardrail rules, used only as a fallback if `from rl.guardrails import apply_canonical_guardrails` fails to import. That duplicate still had the **old** `0.40 < perf < 0.65` boundary — meaning a broken import would silently reintroduce the exact, already-fixed safety gap. This was already flagged, by static analysis only, in the prior `Independent_Project_Audit`.

### Step 2 — Establish evidence
Confirmed by direct code reading (`rl/env/interview_env.py` lines 229–272) and by reproducing the gap condition against the dormant fallback path directly (see Step 7).

### Step 3 — Root cause
The two implementations were never kept in sync when `rl/guardrails.py` was patched, because the inline copy is dead code under normal operation and so was not exercised by the tests that verified the original fix.

### Step 4 — Minimum effective modification
**One condition changed**, in the one place that needed it: `_apply_guardrails()`'s G5 branch, from `0.40 < perf < 0.65` to `0.30 <= perf < 0.65`, with an explanatory comment recording why and explicitly noting what was *not* touched.

**Explicitly NOT touched, and why:** `oracle_action_from_obs()` (the reward-function's hand-coded imitation-target oracle, rule "R5", same `0.40` boundary, line ~219) and the reward's own `critical_state` detection (same `0.40` boundary, line ~377) both **intentionally retain their original boundary** — these are reward-function/training-objective logic, explicitly protected by this phase's own instructions ("Do not change the reward function... Do not change frozen research artifacts"), and are a conceptually different thing from the inference-time guardrail safety shield even though they share a similar-looking condition by original design. Changing either would alter training-time behavior for any future retraining from this code, which was never authorized or intended here.

### Step 7 — Rerun tests / Step 8 — Compare results
The normal path (`apply_canonical_guardrails` importable, i.e. the actual live-system behavior) is unaffected — confirmed by rerunning `T-N02`/`T-N03` fresh (10/10, 13/13, identical to pre-change) and the Gymnasium `check_env()` official environment checker (passes, no warnings).

The **dormant fallback path specifically** was tested by monkeypatching `apply_canonical_guardrails` to `None` in-process (forcing the otherwise-unreachable branch to execute) and replaying the same 5 representative boundary cases `T-N03` uses:

| Case | perf | Before (fallback) | After (fallback) |
|---|---|---|---|
| The originally-unguarded gap | 0.35 | `none` (unguarded — bug reproduced) | `g5_partial_same` (fixed) |
| New lower boundary | 0.30 | `none` (unguarded) | `g5_partial_same` (fixed) |
| Just below the new boundary | 0.299 | `g1_overload_protection` (unaffected, correct) | `g1_overload_protection` (unaffected, correct) |
| Upper bound, unaffected region | 0.64 | `g5_partial_same` (already correct) | `g5_partial_same` (unaffected, correct) |
| G4 still takes priority | 0.20 | `g4_stuck_easier` (unaffected, correct) | `g4_stuck_easier` (unaffected, correct) |

All 5/5 match the live `rl/guardrails.py` behavior after the fix; the gap case specifically is confirmed closed in the fallback path too.

### Step 9 — Regression risk
None identified for the live system (the normal, non-fallback path is byte-for-byte unaffected by this change). The only behavior change is in a path that only executes if an import already fails — i.e. this change can only make that failure scenario *safer*, never less safe, relative to before.

### Step 10 — Outcome
**Fixed and verified**, including in the dormant path itself, not only the already-working primary path.

---

## Full diff footprint (this phase only, on `final-eval/controlled-improvements`)

```
 apps/backend/main.py         | 80 +++++++++++++++++++++++++++++++++++---------
 rl/env/interview_env.py      | 13 ++++++-
 services/qwen/app.py         | 35 ++++++++++++++-----
 services/storage/database.py | 41 +++++++++++++++++++++++
 4 files changed, 165 insertions(+), 24 deletions(-)
```
(`launch.py` and `rl/guardrails.py` also show as modified in `git diff --stat`, but those are the pre-existing, already-approved, already-documented changes from before this phase — not touched again here; included in the repository's working tree, not newly authored in this phase.)

No file was deleted. No model checkpoint, dataset, rubric, or frozen research artifact under `research/`, `ablation/`, or `rl/checkpoints/` was modified.
