"""
InterviewOrchestrator — runtime controller for a single interview session.

One instance per session, stored in SESSIONS[sid].
Coordinates all sub-agents: evaluator, timer, validator, feedback, strategy (RL), logger.

Usage in frontend/main.py:
    orch = InterviewOrchestrator(session_id, candidate, config,
                                 evaluator_fn=_run_integrated_evaluator,
                                 select_questions_fn=select_questions)
    SESSIONS[sid] = orch
    result = await orch.start()
    result = await orch.handle_voice_answer(transcript, qid, attempts)
    report = await orch.end()
"""

from __future__ import annotations

import asyncio
import uuid
import re
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# ── Guarded sub-agent imports ────────────────────────────────────────────

_STRATEGY_READY = False
HybridOrchestrator = None
try:
    from agents.strategy.hybrid_orchestrator import HybridOrchestrator as _HO
    HybridOrchestrator = _HO
    _STRATEGY_READY = True
except ImportError:
    pass

_TIMER_READY = False
QuestionTimer = None
try:
    from agents.timing.timer import QuestionTimer as _QT
    QuestionTimer = _QT
    _TIMER_READY = True
except ImportError:
    pass

_VALIDATOR_READY = False
ScoreValidator = None
try:
    from agents.validation.score_validator import ScoreValidator as _SV
    ScoreValidator = _SV
    _VALIDATOR_READY = True
except ImportError:
    pass

_LOGGER_READY = False
SessionLogger = None
try:
    from agents.orchestrator.logger import SessionLogger as _SL
    SessionLogger = _SL
    _LOGGER_READY = True
except ImportError:
    pass

_FEEDBACK_READY = False
FEEDBACK_AGENT = None
try:
    from agents.orchestrator.feedback_agent import FEEDBACK_AGENT as _FA
    FEEDBACK_AGENT = _FA
    _FEEDBACK_READY = True
except ImportError:
    pass

# ── Action maps ──────────────────────────────────────────────────────────
_ACTION_IDX_TO_NAME: Dict[int, str] = {
    0: "Easier", 1: "Same", 2: "Harder", 3: "Hint", 4: "Follow-up"
}
_ACTION_NAME_TO_IDX: Dict[str, int] = {v: k for k, v in _ACTION_IDX_TO_NAME.items()}

# ── Module-level constants (verbatim from main.py) ───────────────────────
_STATIC_HINTS: dict = {
    "pointers": (
        "Think about what the pointer stores (an address, not a value). "
        "When you dereference (*ptr), you go to that address. "
        "Pointer arithmetic moves by sizeof(type) — try stepping through with a small example."
    ),
    "memory_management": (
        "Every malloc must have a matching free. "
        "Trace every exit path of your function — does each one free the memory? "
        "Also: always check if malloc returned NULL before using the pointer."
    ),
    "linked_list": (
        "Draw 3 nodes on paper, label prev/curr/next. "
        "Walk through the pointer reassignment step-by-step before writing code. "
        "What are the edge cases: empty list, single node, last node?"
    ),
    "dynamic_programming": (
        "Start with the recurrence: dp[i] = f(dp[i-1], ...). "
        "What is the smallest subproblem (base case)? "
        "Then decide: top-down (memoization) or bottom-up (tabulation)?"
    ),
    "graphs": (
        "BFS uses a queue and finds shortest paths in unweighted graphs. "
        "DFS uses a stack (or recursion). Always track visited nodes to avoid cycles. "
        "What is your adjacency representation — list or matrix?"
    ),
    "sorting": (
        "For divide-and-conquer sorts: focus on the split and merge steps separately. "
        "Merge sort: O(n log n) time, O(n) space. "
        "Quick sort: O(n log n) average, O(n²) worst — pivot choice matters."
    ),
    "arrays_algo": (
        "Two-pointer: one at start, one at end, move based on the invariant you need to maintain. "
        "Sliding window: expand right, shrink left when condition violated. "
        "State your invariant before coding."
    ),
    "trees": (
        "Recurse on the base case first: what do you return for NULL? For a leaf? "
        "Then write the recursive case. "
        "In-order gives sorted output for BST. Height = 1 + max(left_height, right_height)."
    ),
    "stacks_queues": (
        "Stack: LIFO — push/pop from same end. Queue: FIFO — enqueue at back, dequeue from front. "
        "Common pattern: use a stack when you need to reverse order or match brackets."
    ),
    "bit_manipulation": (
        "Show your work in binary. "
        "Set bit k: n | (1 << k). Clear: n & ~(1 << k). Toggle: n ^ (1 << k). Check: (n >> k) & 1. "
        "Walk through one example in binary to verify."
    ),
}

_MISSING_Q_HINT = "Break the problem into the smallest subproblem and solve that first."


# ── Module-level helpers (verbatim from main.py) ─────────────────────────

def _detailed_fallback_feedback(transcript: str, question: dict, score: float) -> dict:
    """Rule-based fallback when evaluator/feedback agent is unavailable."""
    text = (transcript or "").strip()
    words = [w for w in text.split() if w]
    word_count = len(words)
    lower = text.lower()

    uncertainty_markers = ["maybe", "i think", "not sure", "probably", "guess", "idk", "i don't know"]
    filler_markers = ["um", "uh", "like", "you know", "basically", "actually"]
    structure_markers = ["first", "second", "because", "therefore", "for example", "in c",
                         "time complexity", "space complexity"]

    uncertainty_hits = sum(1 for m in uncertainty_markers if m in lower)
    filler_hits = sum(1 for m in filler_markers if f" {m} " in f" {lower} ")
    structure_hits = sum(1 for m in structure_markers if m in lower)

    depth_score = min(1.0, (word_count / 140.0) + (0.08 * structure_hits))
    clarity_penalty = min(0.35, (0.05 * uncertainty_hits) + (0.03 * filler_hits))
    confidence_proxy = max(0.05, min(1.0, score - clarity_penalty + 0.08))
    depth_label = "good" if depth_score >= 0.75 else ("moderate" if depth_score >= 0.45 else "shallow")

    strong_points = []
    if word_count >= 80:
        strong_points.append("Good answer length with substantive detail")
    if structure_hits >= 2:
        strong_points.append("Reasoning structure is visible (cause/effect or stepwise explanation)")
    if "time complexity" in lower or "space complexity" in lower:
        strong_points.append("Included complexity discussion")

    vague_points = []
    if word_count < 45:
        vague_points.append("Answer is too brief; key implementation details were skipped")
    if structure_hits == 0:
        vague_points.append("Reasoning flow is unclear; no explicit step-by-step logic")
    if uncertainty_hits > 0:
        vague_points.append("Hedging language lowers confidence; use assertive technical statements")

    missing_concepts = []
    if "time complexity" not in lower:
        missing_concepts.append("Time complexity and trade-off explanation")
    if "space complexity" not in lower:
        missing_concepts.append("Space usage and memory trade-offs")
    if "example" not in lower and "for example" not in lower:
        missing_concepts.append("Concrete example or test case walkthrough")

    improve_tips = [
        "Use this format: Problem -> Core idea -> Steps -> Edge cases -> Complexity",
        "Prefer: 'I will handle X by ... because ...' instead of uncertain phrasing",
        "Close with: 'Time complexity is O(...), space complexity is O(...)'",
    ]

    topic = str(question.get("topic", "general"))
    justification = (
        f"Performance {score:.2f}. Confidence proxy {confidence_proxy:.2f}. "
        f"Depth is {depth_label} (word_count={word_count}, structure_signals={structure_hits}). "
        f"Question focus: {topic}."
    )

    return {
        "final_score": round(score, 2),
        "justification": justification,
        "strong_points": strong_points[:5],
        "vague_points": (vague_points + improve_tips)[:8],
        "missing_concepts": missing_concepts[:8],
        "decision_source": "detailed_fallback",
        "transcript": transcript,
    }


def _make_recommendations(missing: dict) -> list:
    """Map missing concepts to learning recommendations."""
    recs = {
        "struct padding": "Study struct alignment: compile with -Wpadded and use offsetof() to understand layout.",
        "double pointers": "Practice: write functions that modify a pointer via double pointer.",
        "graph cycle detection": "Implement both DFS-based cycle detection and Floyd's algorithm.",
        "recursion": "Master the call stack: trace through a recursive function by hand for small inputs.",
        "DP memoization": "Implement Fibonacci, climbing stairs, and coin change using both memoization and tabulation.",
        "edge cases": "Always test: empty input, single element, all-same elements, negative numbers, overflow cases.",
        "complexity analysis": "For every function you write, determine its Big-O time and space complexity.",
    }
    result = []
    for concept in list(missing.keys())[:5]:
        for key, rec in recs.items():
            if key in concept.lower():
                result.append(rec)
                break
        else:
            result.append(f"Review and practice: {concept}")
    return result[:5]


# ── Main class ────────────────────────────────────────────────────────────

class InterviewOrchestrator:
    """
    Runtime controller for a single interview session.
    One instance per session. Stored in SESSIONS[sid].
    All public mutating methods are serialised with self._lock.
    """

    def __init__(
        self,
        session_id: str,
        candidate: dict,
        config: dict,
        evaluator_fn=None,
        select_questions_fn=None,
    ):
        self._lock = asyncio.Lock()

        # Injected dependencies
        self._evaluator_fn = evaluator_fn
        self._select_questions_fn = select_questions_fn

        # Sub-agent instances (guarded)
        self._strategy = HybridOrchestrator() if _STRATEGY_READY and HybridOrchestrator else None
        self._timer = QuestionTimer() if _TIMER_READY and QuestionTimer else None
        self._validator = ScoreValidator() if _VALIDATOR_READY and ScoreValidator else None
        self._logger = SessionLogger() if _LOGGER_READY and SessionLogger else None

        # Question queue state
        self._question_queue: List[dict] = []
        self._current_q_index: int = 0
        self._timer_snapshot = None
        self._attempt_counts: Dict[str, int] = {}
        self._cached_report: Optional[dict] = None

        # Build session state from config
        sid = session_id
        interview_mode = (config.get("interview_mode") or "standard").strip().lower()
        if interview_mode in {"baseline_rl", "demo"}:
            interview_mode = "demo_rl"
        num_q = int(config.get("num_questions") or 10)
        if num_q >= 15:
            interview_mode = "demo_rl"
        if interview_mode not in {"standard", "demo_rl"}:
            interview_mode = "standard"

        baseline_min = 0
        baseline_max = 0
        effective_num = num_q
        if interview_mode == "demo_rl":
            effective_num = 15
            baseline_min = 2
            baseline_max = 3
        elif effective_num >= 5:
            baseline_min = 2
            baseline_max = 2

        exp = (candidate or {}).get("experience", "intermediate")
        start_diff = {"beginner": 2, "intermediate": 3, "advanced": 4}.get(exp, 3)
        if interview_mode == "demo_rl" or baseline_min > 0:
            start_diff = 2

        c_topics = config.get("c_topics") or []
        dsa_topics = config.get("dsa_topics") or []

        questions: List[dict] = []
        if self._select_questions_fn:
            try:
                questions = self._select_questions_fn(c_topics, dsa_topics, effective_num, start_diff)
            except Exception:
                questions = []

        self._question_queue = list(questions)

        self._state: dict = {
            "id": sid,
            "candidate_id": (candidate or {}).get("id", ""),
            "c_topics": c_topics,
            "dsa_topics": dsa_topics,
            "topics": c_topics + dsa_topics,
            "duration_minutes": int(config.get("duration_minutes") or 30),
            "num_questions": effective_num,
            "start_difficulty": start_diff,
            "current_difficulty": start_diff,
            "interview_mode": interview_mode,
            "baseline_min_questions": baseline_min,
            "baseline_max_questions": baseline_max,
            "baseline_questions": baseline_max,
            "baseline_complete": baseline_min == 0,
            "rl_enabled": baseline_min == 0,
            "next_question_type": "verbal",
            "last_question_type": "",
            "code_streak": 0,
            "verbal_streak": 0,
            "last_topic": "",
            "topic_counts": {},
            "pending_next": False,
            "question_ids": [q["id"] for q in questions],
            "question_index": 0,
            "questions": questions,
            "answers": [],
            "scores": [],
            "difficulty_history": [start_diff],
            "rl_perf_history": [],
            "rl_last_action": "Same",
            "last_confidence_score": 0.5,
            "last_audio_analysis": None,
            "last_time_norm": 0.0,
            "last_time_overrun": False,
            "consecutive_followups": 0,
            "status": "created",
            "created_at": datetime.utcnow().isoformat(),
        }

    # ── Public API ────────────────────────────────────────────────────────

    def to_session_dict(self) -> dict:
        """Return a copy of session state for REST endpoints."""
        return dict(self._state)

    def ingest_audio_analysis(self, audio_result: dict, confidence_score: Optional[float]) -> None:
        """Called by /api/transcribe to push audio signals without direct _state writes."""
        self._state["last_audio_analysis"] = audio_result
        if confidence_score is not None:
            self._state["last_confidence_score"] = float(confidence_score)

    def mark_abandoned(self) -> None:
        """Status transition for WS disconnect. No lock — fires outside message loop."""
        self._state["status"] = "abandoned"

    def mark_error(self) -> None:
        """Status transition for unhandled WS error. No lock — fires on error boundary."""
        self._state["status"] = "error"

    async def start(self) -> dict:
        """
        Set status=in_progress, return first question payload.
        Edge case: empty question bank → returns typed session_end envelope.
        Dispatcher should check result.get("type") == "session_end".
        """
        async with self._lock:
            self._state["status"] = "in_progress"
            q = self._select_and_send_question()
            if q is None:
                report = await self._finalize_session()
                return {"type": "session_end", "payload": {
                    "report_id": report["id"],
                    "overall_score": report.get("overall_score", 0.0),
                }}
            return q

    async def handle_voice_answer(
        self,
        transcript: str,
        question_id: str,
        attempts: int = 1,
    ) -> dict:
        """
        Evaluate a verbal answer end-to-end.
        Returns: {feedback, difficulty_update|None, hint|None, next_action}
        """
        async with self._lock:
            current_q = self._get_current_question(question_id)

            # Stop timer
            if self._timer and self._timer_snapshot:
                timing = self._timer.stop(self._timer_snapshot)
                self._state["last_time_norm"] = timing.get("time_norm", 0.0)
                self._state["last_time_overrun"] = timing.get("is_overrun", False)
                self._timer_snapshot = None

            qid = (current_q or {}).get("id", question_id)
            self._attempt_counts[qid] = self._attempt_counts.get(qid, 0) + attempts

            # Evaluate
            eval_result = await self._evaluate_verbal(transcript, current_q or {})
            eval_result["transcript"] = transcript

            # Update confidence from audio if available
            audio = self._state.get("last_audio_analysis")
            if isinstance(audio, dict) and not audio.get("error"):
                conf = audio.get("confidence_score")
                if conf is not None:
                    self._state["last_confidence_score"] = float(conf)

            # Generate feedback
            turn_num = len(self._state["scores"]) + 1
            feedback = await self._generate_feedback(
                transcript, current_q or {}, eval_result, audio,
                is_code=False, turn_num=turn_num,
            )

            score = float(feedback.get("final_score", 0.5))

            # Update state first (so _adapt_difficulty sees correct answered count)
            self._update_session_state(current_q or {}, score, feedback, transcript=transcript)

            # Adapt difficulty
            new_diff, reason, action = await self._adapt_difficulty(score)

            # Handle action side-effects
            hint_text = None
            if action == "Hint":
                hint_text = await self._get_hint(current_q or {}, mode="hint")
                if self._state["answers"]:
                    self._state["answers"][-1]["hint_given"] = True
            elif action == "Follow-up":
                await self._inject_followup_question(current_q or {}, context_text=transcript)

            self._log_turn({
                "question_id": qid,
                "transcript": transcript,
                "score": score,
                "action": action,
                "new_difficulty": new_diff,
                "time_norm": self._state.get("last_time_norm", 0.0),
                "attempts": attempts,
            })

            self._state["pending_next"] = True

            all_done = (
                self._current_q_index >= len(self._question_queue) - 1
                and action not in {"Follow-up"}
            )

            return {
                "feedback": feedback,
                "difficulty_update": None if action == "Hint" else {
                    "new_difficulty": new_diff,
                    "reason": reason,
                    "action": action,
                },
                "hint": hint_text,
                "next_action": "session_end" if all_done else "wait_for_next",
            }

    async def handle_code_submission(
        self,
        code: str,
        question_id: str,
        passed: bool,
        tests_passed: int,
        tests_total: int,
        stdout: str,
        stderr: str,
    ) -> dict:
        """
        Handle a code submission end-to-end.
        Returns: {feedback, difficulty_update|None, hint|None, next_action}
        """
        async with self._lock:
            current_q = self._get_current_question(question_id)

            # Stop timer
            if self._timer and self._timer_snapshot:
                timing = self._timer.stop(self._timer_snapshot)
                self._state["last_time_norm"] = timing.get("time_norm", 0.0)
                self._state["last_time_overrun"] = timing.get("is_overrun", False)
                self._timer_snapshot = None

            qid = (current_q or {}).get("id", question_id)

            # Evaluate code
            result = self._evaluate_code(
                code, current_q or {},
                passed, tests_passed, tests_total, stdout, stderr,
            )

            score = float(result.get("final_score", 0.5))

            # Update state
            self._update_session_state(current_q or {}, score, result, code=code)

            # Adapt difficulty
            new_diff, reason, action = await self._adapt_difficulty(score)

            hint_text = None
            if action == "Hint":
                hint_text = await self._get_hint(current_q or {}, mode="hint")
                if self._state["answers"]:
                    self._state["answers"][-1]["hint_given"] = True
            elif action == "Follow-up":
                await self._inject_followup_question(current_q or {}, context_text=code[:400])

            self._log_turn({
                "question_id": qid,
                "code": code[:200],
                "score": score,
                "action": action,
                "new_difficulty": new_diff,
                "passed": passed,
            })

            self._state["pending_next"] = True

            all_done = (
                self._current_q_index >= len(self._question_queue) - 1
                and action not in {"Follow-up"}
            )

            return {
                "feedback": result,
                "difficulty_update": None if action == "Hint" else {
                    "new_difficulty": new_diff,
                    "reason": reason,
                    "action": action,
                },
                "hint": hint_text,
                "next_action": "session_end" if all_done else "wait_for_next",
            }

    async def handle_next_question(self) -> dict:
        """
        Advance to the next question. Idempotent on duplicate events.
        Returns: {type: "question", payload: q} | {type: "session_end", payload: {...}}
        """
        async with self._lock:
            if not self._state.get("pending_next", False):
                # Duplicate event — return current question unchanged
                if self._current_q_index < len(self._question_queue):
                    return {"type": "question",
                            "payload": self._question_queue[self._current_q_index]}
                report = await self._finalize_session()
                return {"type": "session_end", "payload": {
                    "report_id": report["id"],
                    "overall_score": report.get("overall_score", 0.0),
                }}

            self._state["pending_next"] = False
            self._current_q_index += 1
            q = self._select_and_send_question()
            if q is None:
                report = await self._finalize_session()
                return {"type": "session_end", "payload": {
                    "report_id": report["id"],
                    "overall_score": report.get("overall_score", 0.0),
                }}
            return {"type": "question", "payload": q}

    async def request_hint(self, question_id: str) -> dict:
        """
        Return a hint for the given question.
        Never returns None — falls back to generic hint text.
        """
        q = next((x for x in self._question_queue if x.get("id") == question_id), None)
        if q is None:
            return {"text": _MISSING_Q_HINT}
        hint = await self._get_hint(q, mode="hint")
        return {"text": hint or _MISSING_Q_HINT}

    async def skip_question(self, question_id: str) -> dict:
        """
        Skip current question (score 0). Does NOT add to answers array.
        Returns: {type: "question"} | {type: "session_end"}
        """
        async with self._lock:
            self._state["scores"].append(0.0)
            self._current_q_index += 1
            q = self._select_and_send_question()
            if q is None:
                report = await self._finalize_session()
                return {"type": "session_end", "payload": {
                    "report_id": report["id"],
                    "overall_score": report.get("overall_score", 0.0),
                }}
            return {"type": "question", "payload": q}

    async def end(self) -> dict:
        """Finalize session and return full report dict. Idempotent."""
        async with self._lock:
            return await self._finalize_session()

    # ── Private helpers ───────────────────────────────────────────────────

    def _get_current_question(self, question_id: str) -> Optional[dict]:
        """Find question by id or fall back to current index."""
        if question_id:
            q = next((x for x in self._question_queue if x.get("id") == question_id), None)
            if q:
                return q
        if self._current_q_index < len(self._question_queue):
            return self._question_queue[self._current_q_index]
        return None

    def _select_and_send_question(self) -> Optional[dict]:
        """
        Pick the best question at current_q_index for the current difficulty/type.
        Starts the question timer. Returns the question dict or None (session done).
        """
        if self._current_q_index >= len(self._question_queue):
            return None

        self._prepare_next_question(
            int(self._state.get("current_difficulty", 3)),
            str(self._state.get("next_question_type", "")),
        )
        q = self._question_queue[self._current_q_index]
        self._state["question_index"] = self._current_q_index

        if self._timer:
            dur_min = float(self._state.get("duration_minutes", 30))
            n_q = max(int(self._state.get("num_questions", 10)), 1)
            allowed = dur_min * 60.0 / n_q
            self._timer_snapshot = self._timer.start(allowed_time_sec=allowed)

        return q

    def _prepare_next_question(self, target_diff: int, preferred_type: str = "") -> None:
        """Re-order question_queue so the best match is at current_q_index."""
        start = self._current_q_index
        if start >= len(self._question_queue):
            return

        candidates = self._question_queue[start:]
        if not candidates:
            return

        best_offset = 0
        best_score = None
        last_topic = str(self._state.get("last_topic", ""))
        topic_counts = self._state.get("topic_counts", {})

        for offset, q in enumerate(candidates):
            q_type = "code" if q.get("type") == "code" else "verbal"
            type_penalty = 0 if (not preferred_type or q_type == preferred_type) else 1
            diff_penalty = abs(int(q.get("difficulty", 3)) - int(target_diff))
            repeat_penalty = 1 if q.get("topic", "") == last_topic else 0
            diversity_penalty = float(topic_counts.get(q.get("topic", ""), 0)) * 0.2
            score = (type_penalty, diff_penalty + repeat_penalty + diversity_penalty, offset)
            if best_score is None or score < best_score:
                best_score = score
                best_offset = offset

        pick = start + best_offset
        if pick != start:
            self._question_queue[start], self._question_queue[pick] = (
                self._question_queue[pick], self._question_queue[start]
            )

    def _next_type_from_action(self, action_name: str, score: float, prev_type: str) -> str:
        """Determine the preferred question type for the next question."""
        code_streak = int(self._state.get("code_streak", 0))
        verbal_streak = int(self._state.get("verbal_streak", 0))

        if code_streak >= 2:
            return "verbal"
        if verbal_streak >= 2 and score >= 0.5:
            return "code"
        if action_name in {"Hint", "Follow-up", "Easier"}:
            return "verbal"
        if action_name == "Harder" and code_streak < 2:
            return "code"
        if score >= 0.75 and code_streak < 2:
            return "code"
        if score <= 0.45:
            return "verbal"
        return "code" if prev_type == "verbal" and code_streak < 2 else "verbal"

    def _rebuild_remaining_questions(self, new_diff: int) -> None:
        """Replace unanswered questions with ones at new_diff."""
        remaining = len(self._question_queue) - self._current_q_index - 1
        if remaining <= 0 or not self._select_questions_fn:
            return
        try:
            new_q = self._select_questions_fn(
                self._state.get("c_topics", []),
                self._state.get("dsa_topics", []),
                remaining,
                new_diff,
            )
            self._question_queue[self._current_q_index + 1:] = new_q
        except Exception as e:
            if self._logger:
                try:
                    self._logger.log_turn({"error": f"Question selection failed: {str(e)}"})
                except Exception:
                    pass

    def _baseline_target_difficulty(self, avg_score: float, current: int) -> int:
        """Map baseline average to an RL starting difficulty."""
        if avg_score >= 0.8:
            return min(5, current + 1)
        if avg_score >= 0.65:
            return current
        if avg_score >= 0.5:
            return max(1, current - 1)
        return max(1, current - 2)

    def _baseline_established(self, scores: List[float]) -> bool:
        """True when baseline signal is strong enough to activate RL."""
        if len(scores) < 2:
            return False
        if len(scores) >= 3:
            return True
        avg_score = sum(scores) / 2.0
        spread = abs(scores[0] - scores[1])
        strong_signal = avg_score <= 0.45 or avg_score >= 0.65
        consistent_signal = spread <= 0.18
        return strong_signal or consistent_signal

    def _baseline_phase_difficulty(self, answered_count: int) -> int:
        """Deterministic baseline: Q1=easy(2), Q2+=mid(3)."""
        return 2 if answered_count <= 0 else 3

    async def _evaluate_verbal(self, transcript: str, question: dict) -> dict:
        """Run the injected evaluator with timeout; fallback to rule-based."""
        if self._evaluator_fn:
            try:
                loop = asyncio.get_event_loop()
                fut = loop.run_in_executor(None, self._evaluator_fn, transcript, question)
                raw = await asyncio.wait_for(fut, timeout=180.0)
                if raw:
                    if self._validator:
                        try:
                            rs = float(raw.get("final_score", 0.5))
                            ev = {"mandatory_pass": bool(raw.get("mandatory_pass", True)),
                                  "mistake_penalty": float(raw.get("mistake_penalty", 0.0))}
                            v = self._validator.validate(rs, ev, is_coding=False)
                            raw["final_score"] = float(v.get("validated_score", rs))
                            raw["validation_trace"] = v.get("validation_trace", [])
                        except Exception:
                            pass
                    return raw
            except asyncio.TimeoutError:
                # Evaluator timeout; falling back to heuristic evaluation
                pass
            except Exception as eval_err:
                # Evaluator execution failed; using fallback
                if self._logger:
                    try:
                        self._logger.log_turn({"error": f"Verbal evaluation failed: {str(eval_err)}"})
                    except Exception:
                        pass

        await asyncio.sleep(0.0)  # yield to event loop
        score = min(1.0, max(0.1, 0.4 + len(transcript.split()) * 0.015))
        return _detailed_fallback_feedback(transcript, question, score)

    def _evaluate_code(
        self,
        code: str,
        question: dict,
        passed: bool,
        tests_passed: int,
        tests_total: int,
        stdout: str,
        stderr: str,
    ) -> dict:
        """Generate code feedback via FeedbackAgent (sync) or fallback."""
        result: Optional[dict] = None
        if _FEEDBACK_READY and FEEDBACK_AGENT is not None:
            try:
                result = FEEDBACK_AGENT.generate_code_feedback(
                    code=code,
                    passed=passed,
                    tests_passed=tests_passed,
                    tests_total=tests_total,
                    stdout=stdout,
                    stderr=stderr,
                    question=question,
                    session_history=list(self._state.get("scores", [])),
                    turn_number=len(self._state.get("scores", [])) + 1,
                )
            except Exception as feedback_err:
                if self._logger:
                    try:
                        self._logger.log_turn({"error": f"Code feedback generation failed: {str(feedback_err)}"})
                    except Exception:
                        pass

        if result is None:
            score = 0.85 if passed else (tests_passed / max(tests_total, 1) if tests_total else 0.35)
            result = {
                "final_score": round(score, 3),
                "justification": (
                    "All test cases passed." if passed
                    else f"Passed {tests_passed}/{tests_total} tests. Check edge cases and boundary conditions."
                ),
                "strong_points": ["Correct logic — all tests passed"] if passed else [],
                "vague_points": [] if passed else ["Review edge cases", "Check boundary conditions"],
                "missing_concepts": [] if passed else ["Boundary conditions", "Error handling"],
                "decision_source": "sandbox_evaluator",
            }

        if self._validator:
            try:
                rs = float(result.get("final_score", 0.5))
                ev = {"mandatory_pass": bool(passed), "mistake_penalty": 0.0}
                v = self._validator.validate(rs, ev, is_coding=True)
                result["final_score"] = float(v.get("validated_score", rs))
                result["validation_trace"] = v.get("validation_trace", [])
            except Exception:
                pass

        return result

    async def _generate_feedback(
        self,
        transcript: str,
        question: dict,
        eval_result: dict,
        audio: Optional[dict],
        is_code: bool,
        turn_num: int,
    ) -> dict:
        """Enrich eval_result with FeedbackAgent (async) or return as-is."""
        if _FEEDBACK_READY and FEEDBACK_AGENT is not None and not is_code:
            try:
                scores_so_far = list(self._state.get("scores", []))
                rich = await FEEDBACK_AGENT.generate(
                    transcript=transcript,
                    question=question,
                    eval_result=eval_result,
                    audio_result=audio,
                    session_history=scores_so_far,
                    turn_number=turn_num,
                )
                return rich
            except Exception:
                pass
        return eval_result

    async def _get_hint(self, question: dict, mode: str = "hint", context: str = "") -> str:
        """
        Generate hint or follow-up via Qwen microservice.
        Falls back to _STATIC_HINTS then generic text.
        """
        if not question:
            return _MISSING_Q_HINT

        topic = question.get("topic", "")
        q_text = question.get("text", "")[:200]
        static = _STATIC_HINTS.get(
            topic, "Break the problem into smaller pieces. Solve the simplest case first."
        )

        try:
            import httpx
            if mode == "hint":
                payload = {
                    "question": q_text,
                    "topic": topic,
                    "session_context": {
                        "current_difficulty": self._state.get("current_difficulty", 3),
                        "score_history": self._state.get("scores", [])[-3:],
                    },
                }
            else:  # followup
                payload = {
                    "question": q_text,
                    "topic": topic,
                    "mode": "followup",
                    "transcript": context[:400] if context else "",
                }

            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.post("http://localhost:8001/hint", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data.get("hint") or data.get("text") or ""
                    if len(text) > 20:
                        return text
        except Exception:
            pass

        return static if mode == "hint" else ""

    def _apply_guardrails(
        self,
        action_idx: int,
        perf: float,
        avg_perf: float,
        conf: float,
        hes: float,
        diff_norm: float,
    ) -> int:
        """
        Apply post-PPO guardrails G4→G1→G2→G3→G5→G6.
        Returns (possibly overridden) action index.
        Priority order: G4 is highest.
        """
        consec = int(self._state.get("consecutive_followups", 0))

        # G4 — critically struggling candidate
        if perf < 0.30 and hes > 0.60:
            return _ACTION_NAME_TO_IDX["Hint"]

        # G1 — low performance at mid difficulty
        if perf < 0.30 and 0.4 <= diff_norm <= 0.7:
            return _ACTION_NAME_TO_IDX["Easier"]

        # G2 — low confidence + high hesitation
        if conf < 0.30 and hes > 0.70 and perf < 0.80:
            if hes > 0.85:
                return _ACTION_NAME_TO_IDX["Hint"]
            return _ACTION_NAME_TO_IDX["Same"]

        # G3 — cap follow-up overuse
        if action_idx == _ACTION_NAME_TO_IDX["Follow-up"] and consec >= 2:
            return _ACTION_NAME_TO_IDX["Same"]

        # G5 — mid-performance candidate may benefit from follow-up
        if 0.40 < perf < 0.65 and avg_perf < 0.60 and consec < 2:
            return _ACTION_NAME_TO_IDX["Follow-up"]

        # G6 — strong candidate, push harder
        gap = perf - avg_perf
        nervous_expert = conf < 0.40 and hes > 0.60
        if perf >= 0.90 and gap > 0.25 and not nervous_expert:
            return _ACTION_NAME_TO_IDX["Harder"]

        return action_idx

    async def _adapt_difficulty(self, score: float) -> Tuple[int, str, str]:
        """
        Full baseline + RL + guardrails pipeline.
        score MUST already be appended to self._state["scores"] by caller.
        """
        mode = self._state["interview_mode"]
        baseline_min = self._state["baseline_min_questions"]
        baseline_max = self._state["baseline_max_questions"]
        answered = len(self._state["scores"])
        current_diff = int(self._state["current_difficulty"])

        # ── BASELINE PHASE ────────────────────────────────────────────────
        if (mode == "demo_rl" or baseline_min > 0) and not self._state["baseline_complete"]:
            target = self._baseline_phase_difficulty(answered - 1)  # answered already includes this score
            if target != current_diff:
                self._state["current_difficulty"] = target
                self._state["difficulty_history"].append(target)
                self._rebuild_remaining_questions(target)
                current_diff = target

            baseline_scores = self._state["scores"][:min(answered, baseline_max)]

            self._state["next_question_type"] = self._next_type_from_action(
                "Baseline", score, str(self._state.get("last_question_type", "verbal"))
            )

            if answered < baseline_min:
                return (
                    current_diff,
                    f"Baseline phase ({answered}/{baseline_min}) easy→mid — RL disabled",
                    "Baseline",
                )
            elif answered < baseline_max and not self._baseline_established(baseline_scores):
                return (
                    current_diff,
                    "Baseline not yet stable after 2 answers (mid) — asking 1 more baseline question",
                    "Baseline",
                )
            else:
                baseline_avg = sum(baseline_scores) / max(len(baseline_scores), 1)
                new_diff = self._baseline_target_difficulty(baseline_avg, current_diff)
                self._state["baseline_complete"] = True
                self._state["rl_enabled"] = True
                self._state["next_question_type"] = self._next_type_from_action(
                    "Baseline", baseline_avg, str(self._state.get("last_question_type", "verbal"))
                )
                if new_diff != current_diff:
                    self._state["current_difficulty"] = new_diff
                    self._state["difficulty_history"].append(new_diff)
                    self._rebuild_remaining_questions(new_diff)
                return (
                    self._state["current_difficulty"],
                    f"Baseline established in {len(baseline_scores)} question(s) "
                    f"(avg={baseline_avg:.2f}) — RL enabled",
                    "Baseline->RL",
                )

        # ── RL PHASE ──────────────────────────────────────────────────────
        if self._strategy is not None:
            # HybridOrchestrator appends to rl_perf_history internally
            new_diff, reason, action_name = self._strategy.suggest(
                score, current_diff, self._state
            )
        else:
            # Pure heuristic fallback
            if score > 0.8 and current_diff < 5:
                action_name, reason = "Harder", "Strong answer — increasing difficulty"
            elif score < 0.4 and current_diff > 1:
                action_name, reason = "Easier", "Needs support — decreasing difficulty"
            elif score < 0.55:
                action_name, reason = "Hint", "Low score — suggesting hint"
            else:
                action_name, reason = "Same", "Maintaining difficulty"
            new_diff = (
                max(1, current_diff - 1) if action_name == "Easier" else
                min(5, current_diff + 1) if action_name == "Harder" else
                current_diff
            )

        # Apply guardrails
        conf = float(self._state.get("last_confidence_score", 0.5))
        hes = max(0.0, 1.0 - conf)
        rl_hist = self._state.get("rl_perf_history", [])
        avg_perf = sum(rl_hist) / max(len(rl_hist), 1)
        diff_norm = current_diff / 5.0
        action_idx = _ACTION_NAME_TO_IDX.get(action_name, 1)
        action_idx = self._apply_guardrails(action_idx, score, avg_perf, conf, hes, diff_norm)
        action_name = _ACTION_IDX_TO_NAME.get(action_idx, "Same")

        # Recompute difficulty from (possibly overridden) action
        new_diff = (
            max(1, current_diff - 1) if action_name == "Easier" else
            min(5, current_diff + 1) if action_name == "Harder" else
            current_diff
        )

        # Track consecutive_followups
        if action_name == "Follow-up":
            self._state["consecutive_followups"] = self._state.get("consecutive_followups", 0) + 1
        else:
            self._state["consecutive_followups"] = 0

        # Update next question type
        self._state["next_question_type"] = self._next_type_from_action(
            action_name, score, str(self._state.get("last_question_type", "verbal"))
        )

        # Apply difficulty change
        if new_diff != current_diff:
            self._state["current_difficulty"] = new_diff
            self._state["difficulty_history"].append(new_diff)
            self._rebuild_remaining_questions(new_diff)

        self._state["rl_last_action"] = action_name
        return new_diff, reason, action_name

    async def _inject_followup_question(
        self, question: dict, context_text: str = ""
    ) -> bool:
        """Generate a Qwen follow-up and insert it after the current question. Returns True on success."""
        fu_text = await self._get_hint(question, mode="followup", context=context_text[:400])
        if not fu_text:
            return False
        fu_q = {
            "id": f"fu_{uuid.uuid4().hex[:8]}",
            "text": fu_text,
            "topic": question.get("topic", "general"),
            "difficulty": int(self._state.get("current_difficulty", 3)),
            "type": "verbal",
            "source": "qwen_followup",
        }
        self._question_queue.insert(self._current_q_index + 1, fu_q)
        return True

    def _log_turn(self, turn_data: dict) -> None:
        """Log turn to SessionLogger if available."""
        if self._logger:
            try:
                self._logger.log_turn(turn_data)
            except Exception:
                pass

    def _update_session_state(
        self,
        question: dict,
        score: float,
        feedback: dict,
        transcript: Optional[str] = None,
        code: Optional[str] = None,
        hint_given: bool = False,
    ) -> None:
        """Update mutable session state after an answer."""
        self._state["scores"].append(score)
        self._state["answers"].append({
            "question_id": question.get("id", ""),
            "transcript": transcript or "",
            "code_submitted": code or "",
            "score": score,
            "feedback": feedback,
            "hint_given": hint_given,
        })

        topic = question.get("topic", "")
        tc = self._state.setdefault("topic_counts", {})
        tc[topic] = int(tc.get(topic, 0)) + 1
        self._state["last_topic"] = topic

        qtype = "code" if question.get("type") == "code" else "verbal"
        self._state["last_question_type"] = qtype
        if qtype == "code":
            self._state["code_streak"] = int(self._state.get("code_streak", 0)) + 1
            self._state["verbal_streak"] = 0
        else:
            self._state["verbal_streak"] = int(self._state.get("verbal_streak", 0)) + 1
            self._state["code_streak"] = 0

        self._state["question_index"] = self._current_q_index

    async def _finalize_session(self) -> dict:
        """Finalize session and return the full report. Idempotent via _cached_report."""
        if self._cached_report is not None:
            return self._cached_report

        self._state["status"] = "completed"
        self._state["ended_at"] = datetime.utcnow().isoformat()
        scores = self._state.get("scores", [])
        self._state["overall_score"] = round(sum(scores) / max(len(scores), 1), 3)

        report = self._generate_report()
        self._state["report_id"] = report["id"]
        self._cached_report = report

        if self._logger:
            try:
                self._logger.finalize({
                    "session_id": self._state["id"],
                    "overall_score": self._state["overall_score"],
                })
            except Exception:
                pass

        return report

    def _generate_report(self) -> dict:
        """Generate full post-session report from session state."""
        scores = self._state.get("scores", [])
        answers = self._state.get("answers", [])
        overall = sum(scores) / max(len(scores), 1)

        c_topics = set(self._state.get("c_topics", []))
        dsa_topics = set(self._state.get("dsa_topics", []))
        c_scores, dsa_scores = [], []

        all_missing: list = []
        all_strong: list = []
        all_covered: list = []
        q_results: list = []

        conf_scores: list = []
        hes_scores: list = []
        word_counts: list = []
        code_scores: list = []
        hints_used = 0
        trend_history: list = []

        questions_map = {q["id"]: q for q in self._state.get("questions", [])}
        # Include follow-up questions injected into queue (not in initial questions list)
        for q in self._question_queue:
            questions_map.setdefault(q["id"], q)

        for ans in answers:
            fb = ans.get("feedback") or {}
            qid = ans.get("question_id", "")
            q = questions_map.get(qid, {})
            topic = q.get("topic", "")
            score = float(ans.get("score", 0))
            qtype = q.get("type", "verbal")

            if topic in c_topics:
                c_scores.append(score)
            elif topic in dsa_topics:
                dsa_scores.append(score)

            if qtype == "code":
                code_scores.append(score)

            all_missing.extend(fb.get("missing_concepts") or [])
            all_strong.extend(fb.get("strong_points") or [])
            all_covered.extend(fb.get("covered_concepts") or [])

            sb = fb.get("score_breakdown") or {}
            if "confidence_signal" in sb:
                conf_scores.append(float(sb["confidence_signal"]))

            t = fb.get("trend")
            if t:
                trend_history.append(t)

            for tip in (fb.get("communication_tips") or []):
                if "words" in tip.lower():
                    m = re.search(r"(\d+)\s*words", tip.lower())
                    if m:
                        word_counts.append(int(m.group(1)))
                if "filler" in tip.lower():
                    m2 = re.search(r"(\d+)\s*filler", tip.lower())
                    if m2 and int(m2.group(1)) > 3:
                        hes_scores.append(0.6)

            if ans.get("hint_given"):
                hints_used += 1

            q_results.append({
                "question_text": q.get("text", ""),
                "topic": topic,
                "type": qtype,
                "difficulty": q.get("difficulty"),
                "score": score,
                "transcript": ans.get("transcript") or "",
                "code_submitted": ans.get("code_submitted") or "",
                "feedback_full": fb,
                "feedback": fb.get("justification") or "",
                "grade": fb.get("grade") or "",
                "score_breakdown": fb.get("score_breakdown") or {},
                "strong_points": fb.get("strong_points") or [],
                "incorrect_or_incomplete": fb.get("incorrect_or_incomplete") or [],
                "missing_concepts": fb.get("missing_concepts") or [],
                "covered_concepts": fb.get("covered_concepts") or [],
                "how_to_improve": fb.get("how_to_improve") or [],
                "communication_tips": fb.get("communication_tips") or [],
                "trend": fb.get("trend") or "stable",
                "trend_note": fb.get("trend_note") or "",
            })

        missing_counts = Counter(all_missing)
        strong_counts = Counter(all_strong)
        covered_counts = Counter(all_covered)

        all_concepts: dict = {}
        for c, cnt in covered_counts.items():
            all_concepts[c] = min(0.95, 0.70 + 0.05 * cnt)
        for m, cnt in missing_counts.items():
            if m not in all_concepts:
                all_concepts[m] = max(0.10, 0.35 - 0.05 * (cnt - 1))

        topic_scores: dict = {}
        for topic in c_topics | dsa_topics:
            ta = [a for a in answers
                  if questions_map.get(a.get("question_id", ""), {}).get("topic") == topic]
            if ta:
                topic_scores[topic] = round(sum(a.get("score", 0) for a in ta) / len(ta), 3)

        avg_conf = round(sum(conf_scores) / max(len(conf_scores), 1), 3) if conf_scores else 0.70
        hes_rate = round(sum(hes_scores) / max(len(hes_scores), 1), 3) if hes_scores else 0.15
        avg_words = sum(word_counts) / max(len(word_counts), 1) if word_counts else 80
        clarity = round(min(1.0, avg_words / 120.0), 3)
        completeness = round(min(1.0, len(answers) / max(self._state.get("num_questions", 5), 1)), 3)
        avg_code_q = round(sum(code_scores) / max(len(code_scores), 1), 3) if code_scores else 0.0

        trend_summary = "stable"
        if trend_history.count("improving") > trend_history.count("declining"):
            trend_summary = "improving"
        elif trend_history.count("declining") > trend_history.count("improving"):
            trend_summary = "declining"

        report_id = str(uuid.uuid4())
        return {
            "id": report_id,
            "session_id": self._state["id"],
            "candidate_id": self._state.get("candidate_id"),
            "session_date": self._state.get("created_at"),
            "duration_minutes": self._state.get("duration_minutes"),
            "total_questions": len(scores),
            "overall_score": round(overall, 3),
            "c_score": round(sum(c_scores) / max(len(c_scores), 1), 3),
            "dsa_score": round(sum(dsa_scores) / max(len(dsa_scores), 1), 3),
            "strengths": [k for k, _ in strong_counts.most_common(6)],
            "missing_concepts": [k for k, _ in missing_counts.most_common(8)],
            "covered_concepts": [k for k, _ in covered_counts.most_common(8)],
            "topic_scores": topic_scores,
            "difficulty_history": self._state.get("difficulty_history", []),
            "score_history": scores,
            "question_results": q_results,
            "all_concepts": all_concepts,
            "recommendations": _make_recommendations(missing_counts),
            "trend_summary": trend_summary,
            "behaviour": {
                "avg_confidence": avg_conf,
                "hesitation_rate": hes_rate,
                "clarity_score": clarity,
                "completeness": completeness,
                "code_quality": avg_code_q,
                "hints_used": hints_used,
            },
        }
