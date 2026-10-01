# Git Provenance, Code Snapshot & Preservation Audit (V10)

**Date**: 2026-09-30  
**Auditor**: Independent Software Verification Engineer  
**Scope**: Verification of Git Branches, Commit Identity, Source File Hashes, Reconstructibility, and Work Preservation  

---

## 1. REPOSITORY & WORKTREE TOPOLOGY

PrepAIred utilizes a primary git repository and an authorized feature worktree created specifically for isolated orchestrator and evaluation hardening without disrupting main development.

### 1.1 Main Repository
- **Directory Path**: `C:\Users\spars\Downloads\PrepAIred`
- **Current Branch**: `workspace/human-eval-clean-push`
- **HEAD Commit**: `8e6cea89e81b672727142135ae3e2db71be802d3`
- **Commit Subject**: `prereg: register E1 Dynamics Match V1 (2x2x2 factorial, user-approved)`
- **Remote Tracking**: Branch is ahead of `origin/workspace/human-eval-clean-push` by 4 commits.
- **Working Tree State**: Contains uncommitted experiment logs, calibration scripts, and research notes from parallel capstone tasks (e.g., E1 series, X2-C sensitivity scripts). In accordance with preservation rules, zero git reset, rebase, checkout, or commit commands were executed.

### 1.2 Authorized Feature Worktree
- **Directory Path**: `C:\Users\spars\Downloads\PrepAIred\.claude\worktrees\exp032-orchestrator-concept-list-fix`
- **Current Branch**: `worktree-exp032-orchestrator-concept-list-fix`
- **Base Commit**: `b4161d9aae222ae92d0a0fc2dd793bc9693345a0`
- **Commit Subject**: `test: cover prompt-builder and LLM-response-parsing call sites, fix non-discriminating validator test`
- **Working Tree Classification**: Development snapshot with pre-authorized reliability improvements.

---

## 2. MODIFIED & UNTRACKED CODE ARTIFACTS IN WORKTREE

A strict `git diff` against base commit `b4161d9aae222ae92d0a0fc2dd793bc9693345a0` reveals that code changes in the worktree are tightly bounded, fully expected, and strictly focused on score validation and reliability hardening:

```text
 agents/orchestrator/interview_orchestrator.py | 15 +++++++-
 agents/validation/score_validator.py          | 23 +++++++++++-
 tests/unit/test_score_validator.py            | 51 +++++++++++++++++++++++++++
 3 files changed, 87 insertions(+), 2 deletions(-)
```

### Detailed File Modifications:
1. **`agents/validation/score_validator.py` (+23, -1 lines)**:
   - Added defensive type parsing (`try ... float(raw_score) except (ValueError, TypeError)`).
   - Added explicit `math.isnan(score) or math.isinf(score)` non-finite check.
   - Added contradictory status override logic: if upstream evidence reports `evaluation_status: "success"` but the score is missing, non-numeric, or non-finite, overrides `eval_status` to `"invalid_score"` or `"non_finite_score"` and flags `is_infrastructure_failure = True`.
2. **`agents/orchestrator/interview_orchestrator.py` (+15, -1 lines)**:
   - Preserves raw `final_score` from evaluator rather than silently defaulting to `0.0`.
   - Propagates `evaluation_status` and `is_infrastructure_failure` from `ScoreValidator`.
   - Logs an explicit entry into `_state["infrastructure_errors"]` when `evaluation_status in {"non_finite_score", "invalid_score", "unavailable"}`.
3. **`tests/unit/test_score_validator.py` (+51 lines)**:
   - Added regression test `test_validator_flags_non_finite_score_as_infrastructure_failure`.
   - Added regression test `test_validator_does_not_accept_invalid_score_under_success_status`.
4. **`tests/unit/test_evaluator_infrastructure_failure_flag.py` (Untracked, 114 lines)**:
   - Dedicated end-to-end integration test exercising `InterviewOrchestrator._evaluate_verbal` across mock evaluator responses (non-finite float, missing score, non-numeric string, and genuine candidate zero).

---

## 3. INDEPENDENT CRYPTOGRAPHIC HASH AUDIT (SHA-256)

Every load-bearing implementation file described in Manuscript V10 was directly hashed on the local filesystem using Python's `hashlib.sha256()`. The resulting hashes were compared against the authoritative ledger in `CODE_SNAPSHOT_V10.md`:

| File Path | Recorded Hash in `CODE_SNAPSHOT_V10.md` | Actual Hash on Disk (2026-09-30) | Verification Finding |
|---|---|---|:---:|
| `agents/validation/score_validator.py` | `bd4250a9e87b6198796a99824740d6b93561765fa1b545e54e0a055a4d9b5af9` | `bd4250a9e87b6198796a99824740d6b93561765fa1b545e54e0a055a4d9b5af9` | **EXACT MATCH** |
| `agents/orchestrator/interview_orchestrator.py` | `303dad61c1ec71e7db88cc40829bcb48143b06224df1cdea39a02c2aa4072ec9` | `303dad61c1ec71e7db88cc40829bcb48143b06224df1cdea39a02c2aa4072ec9` | **EXACT MATCH** |
| `services/evaluator/app.py` | `93cb3432a55e724e226a30debed8314c1eafab79690ace3d15a2a6a8096985ed` | `93cb3432a55e724e226a30debed8314c1eafab79690ace3d15a2a6a8096985ed` | **EXACT MATCH** |
| `services/qwen/app.py` | `13cef913419bc15b1fc91df51a8cd5f3302d2f0ca2b22b10e66d313c384b0f9e` | `13cef913419bc15b1fc91df51a8cd5f3302d2f0ca2b22b10e66d313c384b0f9e` | **EXACT MATCH** |
| `rl/env/interview_env.py` | `d776e19d1525091b6dc4fb6a64041a0053d113cbf82b20ba62b587b90ed095f4` | `d776e19d1525091b6dc4fb6a64041a0053d113cbf82b20ba62b587b90ed095f4` | **EXACT MATCH** |
| `rl/guardrails.py` | `e6e7b77d4f9b0e40358713e845bfdd96b6f8b54cb97780e5f9a45d477d7c1aa5` | `e6e7b77d4f9b0e40358713e845bfdd96b6f8b54cb97780e5f9a45d477d7c1aa5` | **EXACT MATCH** |
| `agents/timing/timer.py` | `a8d31bf66b6f118f928b1fa82853d5153bed0b442cb8d00f2c91616bb1a2c4eb` | `a8d31bf66b6f118f928b1fa82853d5153bed0b442cb8d00f2c91616bb1a2c4eb` | **EXACT MATCH** |
| `agents/audio/confidence_scorer.py` | `eabeb48c08ad81e70fbedae9d2f47884d963c92b816bfc2306de1fdf0fae0797` | `eabeb48c08ad81e70fbedae9d2f47884d963c92b816bfc2306de1fdf0fae0797` | **EXACT MATCH** |
| `agents/audio/hesitation_scorer.py` | `554f899683012e1ab4372187eae5c4db619344451ce5f443dd832412481a73a0` | `554f899683012e1ab4372187eae5c4db619344451ce5f443dd832412481a73a0` | **EXACT MATCH** |
| `agents/coding_executor/coding_executor.py` | `ed20243d52fe5590f69d87120eb72ab7c6e70a7205857819035e4b792f9e43ef` | `ed20243d52fe5590f69d87120eb72ab7c6e70a7205857819035e4b792f9e43ef` | **EXACT MATCH** |
| `apps/web/src/FeedbackCard.jsx` | `e975d5fa7049ff56549180c63aeec1dc9b6c980a4df72c563ae1b22e10a1f290` | `e975d5fa7049ff56549180c63aeec1dc9b6c980a4df72c563ae1b22e10a1f290` | **EXACT MATCH** |
| `tests/unit/test_score_validator.py` | `f9d9460f8dedb0a5df3c284122aa957da8d9b62b434085f9a0d3f75b5aced9e4` | `f9d9460f8dedb0a5df3c284122aa957da8d9b62b434085f9a0d3f75b5aced9e4` | **EXACT MATCH** |
| `tests/unit/test_evaluator_infrastructure_failure_flag.py` | `b1e0f3ffb3118aebe9f86d88544ca586ad68c02b1e8b01131f5b5816ff27b1d4` | `b1e0f3ffb3118aebe9f86d88544ca586ad68c02b1e8b01131f5b5816ff27b1d4` | **EXACT MATCH** |

**Finding**: 13 out of 13 SHA-256 hashes match identically. There is zero cryptographic drift between the documented code snapshot and the active disk state.

---

## 4. CODE RECONSTRUCTIBILITY & PRESERVATION CHECKS

| Check Target | Expected Condition | Verified State | Audit Outcome |
|---|---|---|:---:|
| **Snapshot Reconstructibility** | Base commit + patch = V10 snapshot | `git diff b4161d9` generates 87 insertions across 3 files; combined with `test_evaluator_infrastructure_failure_flag.py`, the exact snapshot is reproducible. | **PASSED** |
| **Commit History Integrity** | No rewritten git commits | `git log` shows uninterrupted linear history; no rebase, no squash, no altered commit timestamps. | **PASSED** |
| **Prior Mission Preservation** | Previous mission logs unmodified | `research/paper_audit/` contains complete historical logs (`MISSION_LOG.md`, `V8_AUDIT_AND_READINESS_REPORT.md`, `V9_CHANGE_AND_VERIFICATION_NOTE.md`) completely intact. | **PASSED** |
| **V9 Manuscript Preservation** | V9 drafts and PDFs byte-preserved | `PROPOSED_REVISION_DRAFT_V9.md`, `PROPOSED_REVISION_DRAFT_V9_BLIND.md`, `manuscript_v9_author.pdf`, and `manuscript_v9_blind.pdf` were not overwritten or modified. | **PASSED** |
| **Teammate Work Preservation** | Teammate modules untouched | Teammate modules (`apps/backend/`, `apps/web/`, `research/confirmatory/X2C/`, and Sparsh/Athreya/Manasa allocations) remain fully preserved. | **PASSED** |
| **Clean Separation** | V10 in dedicated folder | All V10 revision files live in `research/paper_audit_v10/`; all independent audit files live in `research/audit_v10_independent/`. | **PASSED** |

---

## 5. GIT PROVENANCE VERDICT

The Git provenance and snapshot preservation audit **PASSES without reservations**. The code changes are strictly scoped, transparently documented, and 100% cryptographically verified against the active filesystem.
