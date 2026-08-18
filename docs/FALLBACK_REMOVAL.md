# PrepAIred — Fallback Removal & Anti-Fabrication Audit

**Document Version:** 2.0.0 (Authoritative Stage 13 Consolidation)
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform

---

## 1. Audit Rationale & Scope

In automated AI interview platforms, a major risk to scientific validity is the presence of **hidden heuristic fallbacks, hardcoded mock results, or fabricated metrics** that masquerade as genuine AI intelligence.

PrepAIred underwent an exhaustive repository-wide audit (Stages 8 through 12) to:
1. Identify and eliminate all obsolete mock/fake data generators in production paths.
2. Ensure that when microservices are unavailable, the system transparently logs and exposes genuine degraded states.
3. Replace all misleading fallback labels with explicit, auditable attribution.

---

## 2. Eliminated Production Fallbacks & Fake Intelligence

| Component | Obsolete / Fabricated Behavior Removed | Authoritative Verified Behavior |
|---|---|---|
| **Frontend Report (`Report.jsx`)** | `.catch(() => setReport(MOCK_REPORT))` rendered fake 85% scores on network failure | Renders an explicit error boundary with diagnostic message and retry button |
| **Admin Dashboard (`AdminDashboard.jsx`)** | Fabricated dummy candidates on API error | Displays live API status or empty state with error details |
| **Qwen Microservice (`services/qwen/app.py`)** | Unconditionally labeled non-LLM output as Qwen generation | Returns `decision_source = "non_llm_structured_recovery"` and `llm_status = "llm_unavailable"` |
| **Strategy Orchestrator (`hybrid_orchestrator.py`)** | Mislabeled heuristic fallback decisions as PPO | Explicitly assigns `decision_source = "non_rl_heuristic_recovery"` and `rl_status = "rl_unavailable"` |
| **Candidate State** | Fabricated acoustic hesitation scores during pure coding turns | Preserves genuine prior speech hesitation without hallucinating fake prosody |

---

## 3. Preserved Research & Offline Recovery Mechanisms

> [!IMPORTANT]
> **Preservation Rule:** Legitimate offline recovery mechanisms and research simulation code were explicitly preserved, but clearly segregated from production intelligence:

1. **Non-LLM Structured Recovery:** When Qwen is unavailable, deterministic synthesis generates questions/feedback grounded in Stage 1 evaluator evidence, with transparent attribution (`llm_status = "llm_unavailable"`).
2. **Simulated Candidate Generators:** Preserved in `rl/candidate_simulator/` for offline PPO training and policy benchmarking.
3. **Question Selector Baseline:** Preserved in `agents/question_selector/question_selector.py` for experimental comparison against the adaptive production selector.

---

## 4. Verification Checklist & Regression Tests

- **Frontend Error Boundaries:** Verified by Vitest tests (`apps/web/src/tests/ui_fixes.test.jsx`).
- **Qwen Attribution Matrix:** Verified by `tests/unit/test_qwen_followup_feedback.py::test_qwen_attribution_available_vs_unavailable`.
- **RL Attribution Matrix:** Verified by `tests/unit/test_personalization_questions.py::test_decision_source_attribution`.
