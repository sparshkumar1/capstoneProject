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
from datetime import UTC, datetime
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
    0: "Easier", 1: "Same", 2: "Harder"
}
_ACTION_NAME_TO_IDX: Dict[str, int] = {v: k for k, v in _ACTION_IDX_TO_NAME.items()}



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
        if select_questions_fn is None:
            try:
                from apps.backend.main import select_questions
                self._select_questions_fn = select_questions
            except Exception:
                self._select_questions_fn = None
        else:
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
            baseline_max = 3

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
            "strengths": [],
            "weaknesses": [],

            "concepts_mastered": [],
            "concepts_missed": [],
            "misconceptions": [],
            "topic_performance": {},
            "recent_performance": [],
            "difficulty_history": [start_diff],
            "question_history": [q["id"] for q in questions],
            "followup_history": [],
            "technical_performance": 0.0,
            "communication_indicators": {},
            "response_timing": [],
            "coding_performance": {"attempted": 0, "passed": 0, "pass_rate": 0.0},
            "rl_perf_history": [],
            "rl_last_action": "Same",
            "last_confidence_score": 0.5,
            "last_audio_analysis": None,
            "last_time_norm": 0.0,
            "last_time_overrun": False,
            "main_questions_count": 0,
            "followups_count": 0,
            "consecutive_followups": 0,
            "status": "created",
            "created_at": datetime.now(UTC).isoformat(),
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
            timing_data = {
                "time_taken_sec": 0.0,
                "allowed_time_sec": 60.0,
                "time_ratio": 1.0,
                "time_norm": 0.0,
                "is_overrun": False,
            }
            if self._timer and self._timer_snapshot:
                timing = self._timer.stop(self._timer_snapshot)
                timing_data.update(timing)
                self._state["last_time_norm"] = timing.get("time_norm", 0.0)
                self._state["last_time_overrun"] = timing.get("is_overrun", False)
                self._timer_snapshot = None

            qid = (current_q or {}).get("id", question_id)
            self._attempt_counts[qid] = self._attempt_counts.get(qid, 0) + attempts

            # Evaluate
            if not transcript or transcript.strip() == "" or transcript.startswith("[STT error"):
                eval_result = {
                    "final_score": 0.0,
                    "grade": "Ungraded",
                    "correct_claims": [],
                    "incorrect_claims": [],
                    "missing_concepts": list((current_q or {}).get("expected_concepts", [])),
                    "justification": "No authoritative server transcript available for evaluation.",
                    "stt_status": "stt_unavailable",
                    "decision_source": "stt_failure_handler",
                }
            else:
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

            raw_score = float(eval_result.get("final_score", feedback.get("final_score", 0.5)))
            if eval_result.get("stt_status") == "stt_unavailable":
                timing_mod = {
                    "raw_score": 0.0,
                    "time_ratio": timing_data.get("time_ratio", 1.0),
                    "timing_score": 0.0,
                    "timing_modifier": 0.0,
                    "final_score": 0.0,
                    "is_fast": False,
                    "is_overrun": False,
                    "speed_bonus_eligible": False,
                }
            elif self._timer:
                timing_mod = self._timer.compute_timing_modifier(
                    raw_score=raw_score,
                    time_ratio=timing_data.get("time_ratio", 1.0),
                )
            else:
                timing_mod = {
                    "raw_score": raw_score,
                    "time_ratio": timing_data.get("time_ratio", 1.0),
                    "timing_score": 1.0,
                    "timing_modifier": 0.0,
                    "final_score": raw_score,
                    "is_fast": False,
                    "is_overrun": False,
                    "speed_bonus_eligible": False,
                }

            score = float(timing_mod["final_score"])
            feedback["raw_evaluator_score"] = raw_score
            feedback["timing_modifier"] = timing_mod["timing_modifier"]
            feedback["timing_score"] = timing_mod["timing_score"]
            feedback["time_ratio"] = timing_mod["time_ratio"]
            feedback["time_taken_sec"] = timing_data.get("time_taken_sec", 0.0)
            feedback["allowed_time_sec"] = timing_data.get("allowed_time_sec", 60.0)
            feedback["final_score"] = score

            # Update state first (so _adapt_difficulty sees correct answered count)
            self._update_session_state(
                current_q or {}, score, feedback, transcript=transcript,
                raw_score=raw_score, timing_mod=timing_mod,
            )

            # Adapt difficulty (RL difficulty policy)
            new_diff, reason, action = await self._adapt_difficulty(score)

            # Follow-up decision is owned by Follow-Up Agent (decoupled from RL difficulty)
            followup_injected = await self._decide_and_inject_followup(
                current_q or {}, transcript=transcript, eval_result=eval_result
            )

            # Handle action side-effects
            hint_text = None
            if action == "Hint":
                h_obj = await self._get_hint(current_q or {}, mode="hint")
                hint_text = h_obj.get("text", "") if isinstance(h_obj, dict) else str(h_obj)
                if self._state["answers"]:
                    self._state["answers"][-1]["hint_given"] = True

            self._log_turn({
                "question_id": qid,
                "transcript": transcript,
                "raw_score": raw_score,
                "score": score,
                "timing_modifier": timing_mod["timing_modifier"],
                "timing_score": timing_mod["timing_score"],
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
            timing_data = {
                "time_taken_sec": 0.0,
                "allowed_time_sec": 180.0,
                "time_ratio": 1.0,
                "time_norm": 0.0,
                "is_overrun": False,
            }
            if self._timer and self._timer_snapshot:
                timing = self._timer.stop(self._timer_snapshot)
                timing_data.update(timing)
                self._state["last_time_norm"] = timing.get("time_norm", 0.0)
                self._state["last_time_overrun"] = timing.get("is_overrun", False)
                self._timer_snapshot = None

            qid = (current_q or {}).get("id", question_id)

            # Evaluate code
            result = self._evaluate_code(
                code, current_q or {},
                passed, tests_passed, tests_total, stdout, stderr,
            )

            raw_score = float(result.get("final_score", 0.5))
            if self._timer:
                timing_mod = self._timer.compute_timing_modifier(
                    raw_score=raw_score,
                    time_ratio=timing_data.get("time_ratio", 1.0),
                )
            else:
                timing_mod = {
                    "raw_score": raw_score,
                    "time_ratio": timing_data.get("time_ratio", 1.0),
                    "timing_score": 1.0,
                    "timing_modifier": 0.0,
                    "final_score": raw_score,
                    "is_fast": False,
                    "is_overrun": False,
                    "speed_bonus_eligible": False,
                }

            score = float(timing_mod["final_score"])
            result["raw_evaluator_score"] = raw_score
            result["timing_modifier"] = timing_mod["timing_modifier"]
            result["timing_score"] = timing_mod["timing_score"]
            result["time_ratio"] = timing_mod["time_ratio"]
            result["time_taken_sec"] = timing_data.get("time_taken_sec", 0.0)
            result["allowed_time_sec"] = timing_data.get("allowed_time_sec", 180.0)
            result["final_score"] = score

            # Update state
            self._update_session_state(
                current_q or {}, score, result, code=code,
                raw_score=raw_score, timing_mod=timing_mod,
            )

            # Adapt difficulty
            new_diff, reason, action = await self._adapt_difficulty(score)

            hint_text = None
            if action == "Hint":
                h_obj = await self._get_hint(current_q or {}, mode="hint")
                hint_text = h_obj.get("text", "") if isinstance(h_obj, dict) else str(h_obj)
                if self._state["answers"]:
                    self._state["answers"][-1]["hint_given"] = True

            elif action == "Follow-up":
                await self._inject_followup_question(current_q or {}, context_text=code[:400], eval_result=result)

            self._log_turn({
                "question_id": qid,
                "code": code[:200],
                "raw_score": raw_score,
                "score": score,
                "timing_modifier": timing_mod["timing_modifier"],
                "timing_score": timing_mod["timing_score"],
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
        Return a hint for the given question from Qwen microservice.
        Returns explicit llm_unavailable state if Qwen service is unreachable.
        """
        q = next((x for x in self._question_queue if x.get("id") == question_id), None)
        if q is None:
            return {"status": "error", "text": "Question not found.", "error": "Invalid question_id"}
        return await self._get_hint(q, mode="hint")


    async def skip_question(self, question_id: str) -> dict:
        """
        Skip current question (score 0). Does NOT add to answers array.
        Returns: {type: "question"} | {type: "session_end"}
        """
        async with self._lock:
            self._state["scores"].append(0.0)
            self._state.setdefault("raw_scores", []).append(0.0)
            self._state.setdefault("timing_scores", []).append(0.0)
            self._state.setdefault("timing_modifiers", []).append(0.0)
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
        Ensures the initial question (index 0) is Easy/Easy-Medium (difficulty <= 2).
        Starts the question timer. Returns the question dict or None (session done).
        """
        if self._current_q_index >= len(self._question_queue):
            return None

        # The initial question must be Easy / Easy-Medium (difficulty <= 2)
        target_diff = 2 if self._current_q_index == 0 else int(self._state.get("current_difficulty", 3))

        self._prepare_next_question(
            target_diff,
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
        if action_name == "Easier":
            return "verbal"
        if action_name == "Harder" and code_streak < 2:
            return "code"
        if score >= 0.75 and code_streak < 2:
            return "code"
        if score <= 0.45:
            return "verbal"
        return "code" if prev_type == "verbal" and code_streak < 2 else "verbal"

    def _rebuild_remaining_questions(self, new_diff: int) -> None:
        """Replace unanswered questions with personalized ones at new_diff, avoiding seen questions."""
        remaining = len(self._question_queue) - self._current_q_index - 1
        if remaining <= 0 or not self._select_questions_fn:
            return
        try:
            exclude_ids = set(self._state.get("question_history", [])) | {q.get("id") for q in self._state.get("answers", [])}
            new_q = self._select_questions_fn(
                self._state.get("c_topics", []),
                self._state.get("dsa_topics", []),
                remaining,
                new_diff,
                exclude_ids=exclude_ids,
                candidate_state=self._state,
            )
            self._question_queue[self._current_q_index + 1:] = new_q
        except TypeError:
            try:
                new_q = self._select_questions_fn(
                    self._state.get("c_topics", []),
                    self._state.get("dsa_topics", []),
                    remaining,
                    new_diff,
                )
                self._question_queue[self._current_q_index + 1:] = new_q
            except Exception:
                pass
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
        """Run the authoritative evaluator; returns explicit failure state if unavailable."""
        if self._evaluator_fn:
            try:
                loop = asyncio.get_event_loop()
                fut = loop.run_in_executor(None, self._evaluator_fn, transcript, question)
                raw = await asyncio.wait_for(fut, timeout=180.0)
                if raw:
                    if self._validator:
                        try:
                            rs = float(raw.get("final_score", 0.0))
                            ev = {"mandatory_pass": bool(raw.get("mandatory_pass", True)),
                                  "mistake_penalty": float(raw.get("mistake_penalty", 0.0))}
                            v = self._validator.validate(rs, ev, is_coding=False)
                            raw["final_score"] = float(v.get("validated_score", rs))
                            raw["validation_trace"] = v.get("validation_trace", [])
                        except Exception:
                            pass
                    return raw
            except asyncio.TimeoutError:
                if self._logger:
                    try:
                        self._logger.log_turn({"error": "Verbal evaluation timed out (>180.0s)"})
                    except Exception:
                        pass
            except Exception as eval_err:
                if self._logger:
                    try:
                        self._logger.log_turn({"error": f"Verbal evaluation failed: {str(eval_err)}"})
                    except Exception:
                        pass

        await asyncio.sleep(0.0)  # yield to event loop
        return {
            "status": "evaluator_unavailable",
            "final_score": 0.0,
            "raw_evaluator_score": 0.0,
            "justification": "Authoritative verbal evaluation service is unavailable. No score fabricated.",
            "covered_concepts": [],
            "missing_concepts": [],
            "what_was_incorrect": [],
            "decision_source": "evaluator_unavailable",
            "transcript": transcript or "",
            "score_breakdown": {},
        }


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
            score = (tests_passed / max(tests_total, 1)) if tests_total > 0 else (0.85 if passed else 0.35)
            justification = (
                "All test cases passed." if passed
                else f"Passed {tests_passed}/{tests_total} tests. Check edge cases and boundary conditions."
            )
            if stderr and not passed:
                justification += f" Compiler output: {stderr[:80]}"

            result = {
                "final_score": round(score, 3),
                "justification": justification,
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

        result["tests_passed"] = tests_passed
        result["tests_total"] = tests_total
        result["passed"] = passed
        result["status"] = result.get("status", "accepted" if passed else "failed")
        result["pass_rate"] = tests_passed / max(tests_total, 1)

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
        if eval_result.get("stt_status") == "stt_unavailable":
            return {
                "final_score": 0.0,
                "grade": "Ungraded",
                "score_breakdown": {"s1": 0.0, "s2": 0.0, "r": 0.0},
                "what_candidate_said": transcript or "",
                "what_was_correct": [],
                "what_was_incorrect": [],
                "what_was_incomplete": list(question.get("expected_concepts", [])),
                "missing_concepts": list(question.get("expected_concepts", [])),
                "actionable_improvements": ["Ensure microphone is connected and audio is clear before re-attempting."],
                "strong_points": [],
                "communication_tips": ["No audio was received or audio transcription failed."],
                "covered_concepts": [],
                "justification": "No authoritative server transcript available for evaluation.",
                "narrative_feedback": "No authoritative server transcript available for evaluation.",
                "transcript": transcript or "",
                "decision_source": "stt_failure_handler",
                "stt_status": "stt_unavailable",
                "llm_status": "llm_skipped",
                "vague_points": [],
            }

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


    async def _get_hint(self, question: dict, mode: str = "hint", context: str = "") -> dict:
        """Generate hint via Qwen microservice or return explicit unavailable state."""
        if not question:
            return {"status": "error", "text": "No active question for hint", "error": "No active question"}

        topic = question.get("topic", "")
        q_text = question.get("text", "")[:200]

        try:
            import httpx
            payload = {
                "question_text": q_text,
                "topic": topic,
                "transcript": context[:400] if context else "",
                "difficulty": int(self._state.get("current_difficulty", 3)),
                "strong_points": [],
                "missing_concepts": [],
            }
            async with httpx.AsyncClient(timeout=6.0) as client:
                for ep in ("/api/qwen/hint", "/hint"):
                    resp = await client.post(f"http://localhost:8001{ep}", json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data.get("hint") or data.get("text") or ""
                        if len(text) > 15:
                            return {"status": "ok", "text": text, "source": "qwen_hint"}
        except Exception as exc:
            if self._logger:
                try:
                    self._logger.log_turn({"error": f"Hint generation failed: {str(exc)}"})
                except Exception:
                    pass

        return {
            "status": "llm_unavailable",
            "text": "Personalized hint is currently unavailable (LLM service unreachable).",
            "error": "Qwen service unreachable",
            "source": "llm_unavailable",
        }


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
        Returns (possibly overridden) action index and updates self._last_guardrail_name.
        Priority order: G4 is highest.
        """
        consec = int(self._state.get("consecutive_followups", 0))

        # G4 — critically struggling candidate
        if perf < 0.30 and hes > 0.60:
            self._last_guardrail_name = "guardrail_G4"
            return _ACTION_NAME_TO_IDX["Easier"]

        # G1 — low performance at mid difficulty
        if perf < 0.30 and 0.4 <= diff_norm <= 0.7:
            self._last_guardrail_name = "guardrail_G1"
            return _ACTION_NAME_TO_IDX["Easier"]

        # G2 — low confidence + high hesitation
        if conf < 0.30 and hes > 0.70 and perf < 0.80:
            self._last_guardrail_name = "guardrail_G2"
            return _ACTION_NAME_TO_IDX["Easier"] if hes > 0.85 else _ACTION_NAME_TO_IDX["Same"]

        # G3/G5 collapsed into conservative same/easier behavior in the frozen design.
        if 0.40 < perf < 0.65 and avg_perf < 0.60 and consec < 2:
            self._last_guardrail_name = "guardrail_G3"
            return _ACTION_NAME_TO_IDX["Same"]

        # G6 — strong candidate, push harder
        gap = perf - avg_perf
        nervous_expert = conf < 0.40 and hes > 0.60
        if perf >= 0.90 and gap > 0.25 and not nervous_expert:
            self._last_guardrail_name = "guardrail_G6"
            return _ACTION_NAME_TO_IDX["Harder"]

        self._last_guardrail_name = None
        return action_idx


    async def _adapt_difficulty(self, score: float) -> Tuple[int, str, str]:
        """
        Full baseline + RL + guardrails pipeline.
        score MUST already be appended to self._state["scores"] by caller.
        """
        mode = self._state["interview_mode"]
        baseline_min = self._state["baseline_min_questions"]
        baseline_max = self._state["baseline_max_questions"]
        answered_main = int(self._state.get("main_questions_count", 0)) or len(self._state["scores"])
        current_diff = int(self._state["current_difficulty"])

        # ── BASELINE PHASE ────────────────────────────────────────────────
        if (mode == "demo_rl" or baseline_min > 0) and not self._state["baseline_complete"]:
            self._state["last_decision_source"] = "baseline_warmup"
            self._state["rl_status"] = "baseline_warmup"
            self._state["raw_rl_action"] = None
            self._state["guardrail_applied"] = None
            target = self._baseline_phase_difficulty(answered_main - 1)  # answered_main includes current main Q
            if target != current_diff:
                self._state["current_difficulty"] = target
                self._state["difficulty_history"].append(target)
                self._rebuild_remaining_questions(target)
                current_diff = target

            main_scores = [
                a["score"] for a in self._state["answers"]
                if not (a.get("feedback", {}).get("is_followup") or a.get("question_id", "").startswith("fu_"))
            ]
            baseline_scores = main_scores[:min(len(main_scores), baseline_max)] if main_scores else self._state["scores"][:baseline_max]

            self._state["next_question_type"] = self._next_type_from_action(
                "Baseline", score, str(self._state.get("last_question_type", "verbal"))
            )

            if answered_main < baseline_min:
                return (
                    current_diff,
                    f"Baseline phase ({answered_main}/{baseline_min} main questions) easy→mid — RL disabled",
                    "Baseline",
                )
            elif answered_main < baseline_max and not self._baseline_established(baseline_scores):
                return (
                    current_diff,
                    f"Baseline not yet stable after {answered_main} main answers (mid) — asking 1 more baseline question",
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
                    f"Baseline established in {len(baseline_scores)} main question(s) "
                    f"(avg={baseline_avg:.2f}) — RL enabled",
                    "Baseline->RL",
                )


        # ── RL / ADAPTATION PHASE ─────────────────────────────────────────
        if self._strategy is not None:
            if not getattr(self._strategy, "ready", False):
                try:
                    self._strategy._try_load()
                except Exception:
                    pass

        if self._strategy is not None and getattr(self._strategy, "ready", False) and getattr(self._strategy, "is_compatible", True):
            new_diff, reason, action_name = self._strategy.suggest(
                score, current_diff, self._state
            )
            raw_source = "ppo"
            self._state["rl_status"] = "available"
            self._state["raw_rl_action"] = action_name
        else:
            # Explicit Non-RL Recovery Path (operational continuity only, not RL intelligence)
            if score > 0.8 and current_diff < 5:
                action_name, reason = "Harder", "Non-RL Recovery: Strong answer — increasing difficulty"
            elif score < 0.4 and current_diff > 1:
                action_name, reason = "Easier", "Non-RL Recovery: Needs support — decreasing difficulty"
            else:
                action_name, reason = "Same", "Non-RL Recovery: Maintaining difficulty"
            new_diff = (
                max(1, current_diff - 1) if action_name == "Easier" else
                min(5, current_diff + 1) if action_name == "Harder" else
                current_diff
            )
            raw_source = "non_rl_heuristic_recovery"
            self._state["rl_status"] = "rl_unavailable"
            self._state["raw_rl_action"] = None

        # Apply guardrails
        conf = float(self._state.get("last_confidence_score", 0.5))
        hes = max(0.0, 1.0 - conf)
        rl_hist = self._state.get("rl_perf_history", [])
        avg_perf = sum(rl_hist) / max(len(rl_hist), 1)
        diff_norm = current_diff / 5.0
        action_idx = _ACTION_NAME_TO_IDX.get(action_name, 1)
        self._last_guardrail_name = None
        action_idx = self._apply_guardrails(action_idx, score, avg_perf, conf, hes, diff_norm)
        final_action_name = _ACTION_IDX_TO_NAME.get(action_idx, "Same")

        if self._last_guardrail_name:
            decision_source = self._last_guardrail_name.lower()
            self._state["guardrail_applied"] = self._last_guardrail_name
        else:
            decision_source = raw_source
            self._state["guardrail_applied"] = None

        self._state["last_decision_source"] = decision_source

        # Recompute difficulty from (possibly overridden) action
        new_diff = (
            max(1, current_diff - 1) if final_action_name == "Easier" else
            min(5, current_diff + 1) if final_action_name == "Harder" else
            current_diff
        )

        # Update next question type
        self._state["next_question_type"] = self._next_type_from_action(
            final_action_name, score, str(self._state.get("last_question_type", "verbal"))
        )

        # Apply difficulty change
        if new_diff != current_diff:
            self._state["current_difficulty"] = new_diff
            self._state["difficulty_history"].append(new_diff)
            self._rebuild_remaining_questions(new_diff)

        self._state["rl_last_action"] = final_action_name if raw_source == "ppo" else None
        return new_diff, reason, final_action_name



    async def _decide_and_inject_followup(
        self,
        question: dict,
        transcript: str,
        eval_result: dict,
    ) -> bool:
        """
        Follow-Up Agent Policy:
        Decides whether to trigger a targeted follow-up question based on Evaluator evidence.
        - Hard cap: If consecutive_followups >= 2, stop follow-ups and proceed to next main question.
        - Strong answer: Score >= 0.85 with no missing concepts and no misconceptions -> Skip follow-up.
        - Partial answer, misconception, or gap -> Trigger targeted Qwen follow-up probe.
        """
        consec = int(self._state.get("consecutive_followups", 0))
        if consec >= 2:
            return False

        score = float(eval_result.get("final_score", 0.5))
        missing = list(eval_result.get("missing_concepts", []))
        incorrect = list(eval_result.get("incorrect_claims", []))
        weakest_gap = eval_result.get("weakest_gap")

        # Strong answer check: no gaps, no misconceptions
        if score >= 0.85 and not missing and not incorrect and (not weakest_gap or "None" in str(weakest_gap)):
            return False

        # Incomplete / misconception / low performance check
        if missing or incorrect or score < 0.80:
            return await self._inject_followup_question(question, context_text=transcript, eval_result=eval_result)

        return False

    async def _inject_followup_question(
        self,
        question: dict,
        context_text: str = "",
        eval_result: Optional[dict] = None,
    ) -> bool:
        """Generate a structured Qwen follow-up and insert it after the current question."""
        eval_result = eval_result or {}
        q_text = str(question.get("text", "") or question.get("question_text", ""))
        topic = str(question.get("topic", "general"))

        prev_questions = [str(q.get("text", "")) for q in self._question_queue[:self._current_q_index + 1]]
        prev_followups = [str(q.get("text", "")) for q in self._question_queue if q.get("source") == "qwen_followup"]

        payload = {
            "original_question": q_text,
            "topic": topic,
            "candidate_answer": context_text[:600],
            "structured_evaluation": eval_result,
            "correct_concepts": list(eval_result.get("correct_claims", [])),
            "incorrect_concepts": list(eval_result.get("incorrect_claims", [])),
            "missing_concepts": list(eval_result.get("missing_concepts", [])),
            "misconceptions": list(eval_result.get("incorrect_claims", [])),
            "weakest_gap": str(eval_result.get("weakest_gap", "")),
            "current_difficulty": int(self._state.get("current_difficulty", 3)),
            "candidate_state": {
                "scores": self._state.get("scores", []),
                "turns_completed": len(self._state.get("scores", [])),
            },
            "previous_questions": prev_questions,
            "previous_followups": prev_followups,
        }

        fu_data = None
        try:
            import httpx
            for attempt in range(2):
                try:
                    async with httpx.AsyncClient(timeout=6.0) as client:
                        for ep in ("/api/qwen/followup", "/followup"):
                            resp = await client.post(f"http://localhost:8001{ep}", json=payload)
                            if resp.status_code == 200:
                                data = resp.json()
                                if isinstance(data, dict) and "followup" in data and len(data["followup"].strip()) > 15:
                                    fu_data = data
                                    break
                    if fu_data:
                        break
                except Exception:
                    await asyncio.sleep(0.1)
        except Exception:
            pass

        # Fallback to local structured synthesizer if microservice is offline
        if not fu_data:
            try:
                from services.qwen.app import _synthesize_structured_followup, FollowupRequest
                req = FollowupRequest(**payload)
                res = _synthesize_structured_followup(req)
                fu_data = res.model_dump() if hasattr(res, "model_dump") else res.dict()
            except Exception:
                return False

        fu_text = fu_data.get("followup", "").strip()
        if not fu_text:
            return False

        dec_source = fu_data.get("decision_source", "qwen_followup")
        llm_stat = fu_data.get("llm_status", "available" if ("qwen" in str(dec_source).lower() and "non_llm" not in str(dec_source).lower()) else "llm_unavailable")

        fu_q = {
            "id": f"fu_{uuid.uuid4().hex[:8]}",
            "text": fu_text,
            "topic": topic,
            "difficulty": int(self._state.get("current_difficulty", 3)),
            "type": "verbal",
            "source": dec_source,
            "decision_source": dec_source,
            "llm_status": llm_stat,
            "reason": fu_data.get("reason", "Targeted probe on candidate performance gap"),
            "target_concepts": fu_data.get("target_concepts", []),
            "parent_question_id": question.get("id", ""),
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
        raw_score: Optional[float] = None,
        timing_mod: Optional[dict] = None,
    ) -> None:
        """Update mutable candidate and session state after an answer."""
        self._state["scores"].append(score)
        r_score = float(raw_score if raw_score is not None else score)
        self._state.setdefault("raw_scores", []).append(r_score)

        t_score = float((timing_mod or {}).get("timing_score", 1.0))
        t_mod = float((timing_mod or {}).get("timing_modifier", 0.0))
        self._state.setdefault("timing_scores", []).append(t_score)
        self._state.setdefault("timing_modifiers", []).append(t_mod)

        qid = question.get("id", "")
        topic = question.get("topic", "general")
        qtype = "code" if question.get("type") == "code" else "verbal"
        is_followup = bool(
            str(qid).startswith("fu_")
            or question.get("parent_question_id")
            or question.get("source") in {"qwen_followup", "non_llm_structured_recovery", "qwen_1.5b_llm"}
            or question.get("is_followup")
        )

        # 1. History tracking
        self._state.setdefault("question_history", []).append(qid)
        self._state["answers"].append({
            "question_id": qid,
            "topic": topic,
            "type": qtype,
            "transcript": transcript or "",
            "code_submitted": code or "",
            "raw_score": r_score,
            "score": score,
            "timing_score": t_score,
            "timing_modifier": t_mod,
            "feedback": feedback,
            "hint_given": hint_given,
        })

        if is_followup:
            self._state["followups_count"] = int(self._state.get("followups_count", 0)) + 1
            self._state["consecutive_followups"] = int(self._state.get("consecutive_followups", 0)) + 1
            self._state.setdefault("followup_history", []).append({
                "question_id": qid,
                "text": question.get("text", ""),
                "raw_score": r_score,
                "score": score,
                "target_concepts": question.get("target_concepts", []),
            })
        else:
            self._state["main_questions_count"] = int(self._state.get("main_questions_count", 0)) + 1
            self._state["consecutive_followups"] = 0

        # 2. Topic performance tracking
        tc = self._state.setdefault("topic_counts", {})
        tc[topic] = int(tc.get(topic, 0)) + 1
        self._state["last_topic"] = topic

        tp = self._state.setdefault("topic_performance", {})
        if topic not in tp:
            tp[topic] = {"scores": [], "avg_score": 0.0, "attempts": 0}
        tp[topic]["scores"].append(score)
        tp[topic]["attempts"] += 1
        tp[topic]["avg_score"] = round(sum(tp[topic]["scores"]) / len(tp[topic]["scores"]), 3)

        # 3. Strengths & Weaknesses
        strengths = self._state.setdefault("strengths", [])
        weaknesses = self._state.setdefault("weaknesses", [])
        if score >= 0.75 and topic not in strengths:
            strengths.append(topic)
        elif score < 0.50 and topic not in weaknesses:
            weaknesses.append(topic)

        # 4. Concepts mastered, missed & misconceptions
        covered = feedback.get("covered_concepts", []) or feedback.get("what_was_correct", [])
        missing = feedback.get("missing_concepts", []) or feedback.get("what_was_incomplete", [])
        incorrect = feedback.get("what_was_incorrect", []) or feedback.get("incorrect_claims", [])

        mastered_set = self._state.setdefault("concepts_mastered", [])
        for c in covered:
            if c and c not in mastered_set:
                mastered_set.append(c)

        missed_set = self._state.setdefault("concepts_missed", [])
        for m in missing:
            if m and m not in missed_set:
                missed_set.append(m)

        miscon_set = self._state.setdefault("misconceptions", [])
        for inc in incorrect:
            if inc and inc not in miscon_set:
                miscon_set.append(inc)

        # 5. Recent performance & Technical performance
        self._state["recent_performance"] = list(self._state["scores"][-3:])
        raw_list = self._state.get("raw_scores", self._state["scores"])
        self._state["technical_performance"] = round(sum(raw_list) / max(len(raw_list), 1), 3)


        # 6. Response timing
        self._state.setdefault("response_timing", []).append({
            "question_id": qid,
            "time_taken_sec": feedback.get("time_taken_sec", 0.0),
            "allowed_time_sec": feedback.get("allowed_time_sec", 60.0),
            "time_ratio": feedback.get("time_ratio", 1.0),
            "time_norm": self._state.get("last_time_norm", 0.0),
            "is_overrun": self._state.get("last_time_overrun", False),
            "timing_score": t_score,
            "timing_modifier": t_mod,
            "raw_evaluator_score": r_score,
            "final_score": score,
        })

        # 7. Coding performance
        if qtype == "code" or code:
            if feedback.get("status") == "sandbox_error":
                self._state.setdefault("infrastructure_errors", []).append({
                    "question_id": qid,
                    "type": "sandbox_error",
                    "error": feedback.get("error", "Sandbox execution failed"),
                })
            else:
                self._state["coding_attempted"] = int(self._state.get("coding_attempted", 0)) + 1
                self._state.setdefault("coding_accepted", 0)
                is_acc = feedback.get("status") == "accepted" or feedback.get("passed") is True or score >= 0.70
                if is_acc:
                    self._state["coding_accepted"] = int(self._state["coding_accepted"]) + 1
                else:
                    self._state.setdefault("coding_failures", []).append({
                        "question_id": qid,
                        "status": feedback.get("status", "failed"),
                        "failed_test_ids": feedback.get("failed_test_ids", []),
                    })

                self._state.setdefault("coding_history", []).append({
                    "question_id": qid,
                    "topic": topic,
                    "status": feedback.get("status", "accepted" if is_acc else "failed"),
                    "tests_passed": feedback.get("tests_passed", 0),
                    "tests_total": feedback.get("tests_total", 0),
                    "pass_rate": feedback.get("pass_rate", 1.0 if is_acc else 0.0),
                    "execution_time_ms": feedback.get("execution_time_ms", 0.0),
                })

            tot_att = self._state.get("coding_attempted", 0)
            tot_acc = self._state.get("coding_accepted", 0)
            self._state["coding_pass_rate"] = round(tot_acc / max(tot_att, 1), 3) if tot_att > 0 else 0.0

            topics_list = self._state.setdefault("coding_topics", [])
            if topic and topic not in topics_list:
                topics_list.append(topic)

            cp = self._state.setdefault("coding_performance", {"attempted": 0, "passed": 0, "pass_rate": 0.0})
            cp["attempted"] = tot_att
            cp["passed"] = tot_acc
            cp["pass_rate"] = self._state["coding_pass_rate"]
            self._state["code_streak"] = int(self._state.get("code_streak", 0)) + 1
            self._state["verbal_streak"] = 0
        else:
            self._state["verbal_streak"] = int(self._state.get("verbal_streak", 0)) + 1
            self._state["code_streak"] = 0


        # 8. Communication indicators
        audio = self._state.get("last_audio_analysis")
        if isinstance(audio, dict) and not audio.get("error"):
            trans_meta = audio.get("transcription", {})
            self._state["communication_indicators"] = {
                "confidence_score": float(audio.get("confidence_score", 0.5)),
                "speaking_rate": float(trans_meta.get("true_speaking_rate", 0.0)),
                "pause_count": int(trans_meta.get("pause_count", 0)),
                "total_pause_time": float(trans_meta.get("total_pause_time", 0.0)),
            }

        self._state["question_index"] = self._current_q_index


    async def _finalize_session(self) -> dict:
        """Finalize session and return the full report. Idempotent via _cached_report."""
        if self._cached_report is not None:
            return self._cached_report

        self._state["status"] = "completed"
        self._state["ended_at"] = datetime.now(UTC).isoformat()
        scores = self._state.get("scores", [])
        raw_scores = self._state.get("raw_scores", scores)
        self._state["overall_score"] = round(sum(scores) / max(len(scores), 1), 3)
        self._state["raw_technical_score"] = round(sum(raw_scores) / max(len(raw_scores), 1), 3)

        report = self._generate_report()
        self._state["report_id"] = report["id"]
        self._cached_report = report

        if self._logger:
            try:
                self._logger.finalize({
                    "session_id": self._state["id"],
                    "overall_score": self._state["overall_score"],
                    "raw_technical_score": self._state["raw_technical_score"],
                })
            except Exception:
                pass

        return report

    def _generate_report(self) -> dict:
        """Generate full post-session report from session state."""
        scores = self._state.get("scores", [])
        raw_scores = self._state.get("raw_scores", scores)
        answers = self._state.get("answers", [])
        overall = sum(scores) / max(len(scores), 1)
        raw_technical = sum(raw_scores) / max(len(raw_scores), 1)

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
        concept_scores: list = []
        reasoning_scores: list = []
        timing_scores: list = list(self._state.get("timing_scores", []))
        timing_modifiers: list = list(self._state.get("timing_modifiers", []))
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
            raw_s = float(ans.get("raw_score", score))
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
            if "s2" in sb:
                try:
                    concept_scores.append(float(sb["s2"]))
                except (TypeError, ValueError):
                    pass
            elif fb.get("covered_concepts"):
                tot = len(fb.get("covered_concepts", [])) + len(fb.get("missing_concepts", []))
                if tot > 0:
                    concept_scores.append(len(fb.get("covered_concepts", [])) / tot)

            if "r" in sb:
                try:
                    reasoning_scores.append(float(sb["r"]))
                except (TypeError, ValueError):
                    pass

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
                "raw_score": raw_s,
                "score": score,
                "timing_score": ans.get("timing_score", 1.0),
                "timing_modifier": ans.get("timing_modifier", 0.0),
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
        avg_code_q = round(sum(code_scores) / max(len(code_scores), 1), 3) if code_scores else None

        avg_concept = round(sum(concept_scores) / max(len(concept_scores), 1), 3) if concept_scores else round(raw_technical, 3)
        avg_reasoning = round(sum(reasoning_scores) / max(len(reasoning_scores), 1), 3) if reasoning_scores else round(raw_technical, 3)
        avg_timing = round(sum(timing_scores) / max(len(timing_scores), 1), 3) if timing_scores else 1.0
        net_timing_mod = round(sum(timing_modifiers), 4) if timing_modifiers else 0.0

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
            "raw_technical_score": round(raw_technical, 3),
            "c_score": round(sum(c_scores) / max(len(c_scores), 1), 3),
            "dsa_score": round(sum(dsa_scores) / max(len(dsa_scores), 1), 3),
            "strengths": [k for k, _ in strong_counts.most_common(6)],
            "missing_concepts": [k for k, _ in missing_counts.most_common(8)],
            "covered_concepts": [k for k, _ in covered_counts.most_common(8)],
            "topic_scores": topic_scores,
            "difficulty_history": self._state.get("difficulty_history", []),
            "score_history": scores,
            "raw_score_history": raw_scores,
            "question_results": q_results,
            "all_concepts": all_concepts,
            "recommendations": _make_recommendations(missing_counts),
            "trend_summary": trend_summary,
            "component_breakdown": {
                "technical_score": round(raw_technical, 3),
                "concept_score": avg_concept,
                "reasoning_score": avg_reasoning,
                "communication_score": clarity,
                "timing_score": avg_timing,
                "coding_score": avg_code_q,
                "final_overall": round(overall, 3),
            },
            "timing_analysis": {
                "avg_timing_score": avg_timing,
                "net_timing_modifier": net_timing_mod,
                "response_timing": self._state.get("response_timing", []),
            },
            "behaviour": {
                "avg_confidence": avg_conf,
                "hesitation_rate": hes_rate,
                "clarity_score": clarity,
                "completeness": completeness,
                "code_quality": avg_code_q or 0.0,
                "hints_used": hints_used,
            },
        }
