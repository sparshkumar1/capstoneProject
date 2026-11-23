"""
FeedbackAgent — rich, structured per-turn feedback for PrepAIred.

Combines:
  - Evaluator scores  (S1 semantic, S2 concept, R reasoning)
  - Audio signals     (confidence, hesitation, fillers, word count)
  - Rubric concept details (covered vs missed, with labels)
  - Session history   (trend analysis)
  - Qwen narrative    (when microservice is reachable)

Output contract (all keys always present):
  final_score, grade, score_breakdown,
  strong_points, incorrect_or_incomplete, missing_concepts,
  how_to_improve, communication_tips, covered_concepts,
  trend, trend_note, justification, transcript, decision_source,
  vague_points  (backward-compat alias for how_to_improve[:3])
"""

from __future__ import annotations
import asyncio
import os
from typing import Optional

try:
    import httpx
    _HTTPX = True
except ImportError:
    _HTTPX = False

QWEN_URL = os.getenv("QWEN_URL", "http://localhost:8001")
QWEN_TIMEOUT = 6.0

# Topic-specific misconceptions: (trigger phrase, correction, severity)
_MISCONCEPTIONS: dict[str, list[tuple[str, str, str]]] = {
    "pointers": [
        ("malloc initializes", "malloc does NOT zero-init — use calloc() for that", "major"),
        ("pointer is an array", "A pointer stores an address; arrays decay to pointers but they are distinct types", "major"),
        ("free sets null", "free() deallocates but does NOT set the pointer to NULL — do it manually to avoid use-after-free", "major"),
        ("pointer arithmetic byte", "Pointer arithmetic steps by sizeof(type), not always 1 byte", "minor"),
    ],
    "memory_management": [
        ("stack is manually", "Stack memory is automatically managed by the call frame — heap (malloc/free) is manual", "major"),
        ("realloc always copies", "realloc may extend in-place or copy — never assume; always capture the return value", "major"),
        ("malloc returns int", "malloc returns void* — always assign to the correct pointer type", "minor"),
    ],
    "dynamic_programming": [
        ("greedy same as dp", "Greedy makes locally optimal choices; DP explores all subproblems — they are different paradigms", "major"),
        ("dp is always o(2^n)", "DP trades exponential time for polynomial by caching subproblems", "major"),
    ],
    "graphs": [
        ("dijkstra negative", "Dijkstra fails with negative edge weights — use Bellman-Ford instead", "major"),
        ("bfs dfs same complexity", "BFS and DFS both O(V+E) but BFS finds shortest path in unweighted graphs; DFS does not", "minor"),
    ],
    "sorting": [
        ("merge sort in-place", "Merge sort requires O(n) auxiliary space; it is NOT in-place", "major"),
        ("quicksort always o(n log n)", "Quicksort is O(n²) worst case (bad pivots) — only average O(n log n)", "major"),
    ],
    "trees": [
        ("bst search o(n)", "BST search is O(h) where h is height — O(log n) only for balanced trees", "minor"),
    ],
}

_TOPIC_STRUCTURE_TIPS: dict[str, str] = {
    "pointers": "For pointer questions: type → what it points to → how to dereference → NULL/bounds edge cases",
    "memory_management": "Cover: malloc/calloc/realloc/free → failure handling (NULL check) → how to avoid leaks",
    "dynamic_programming": "State the recurrence relation → base cases → table-filling order → time/space complexity",
    "graphs": "Specify representation (adj list/matrix) → algorithm steps → visited tracking → complexity",
    "sorting": "Explain: divide strategy → merge/partition step → recursion depth → time and space complexity",
    "linked_list": "Draw the pointer changes: track prev, curr, next through 2-3 nodes before explaining generally",
    "trees": "Anchor on the recursive case first, then base cases (null node, leaf), then complexity",
    "stacks_queues": "State the backing structure (array/linked list) → push/pop semantics → edge cases (empty, full)",
    "arrays_algo": "Identify invariant → two-pointer or sliding window logic → prove correctness on an example",
    "bit_manipulation": "Show the bitmask and operation step by step: before → operation → after, in binary",
}


class FeedbackAgent:
    """Async-safe, Qwen-optional rich feedback generator."""

    def __init__(self, qwen_url: str = QWEN_URL):
        """Create a feedback agent targeting a given Qwen microservice.

        Args:
            qwen_url (str): Base URL of the Qwen feedback microservice
                (default from `QWEN_URL` env var or
                "http://localhost:8001").

        Returns:
            None.
        """
        self.qwen_url = qwen_url
        self._qwen_ok: Optional[bool] = None  # None = untested

    # ── Public API ────────────────────────────────────────────────────────

    async def generate(
        self,
        transcript: str,
        question: dict,
        eval_result: dict,
        audio_result: Optional[dict] = None,
        session_history: Optional[list] = None,
        turn_number: int = 1,
        is_code: bool = False,
        attempt_number: int = 1,
        comparison: Optional[dict] = None,
    ) -> dict:
        """Build the full structured feedback dict for one verbal/theory turn.

        Combines the evaluator's score breakdown and concept details with
        audio-derived signals (confidence, hesitation, fillers) and session
        trend, then tries the Qwen feedback microservice for a richer
        narrative; falls back to a deterministic justification and template
        tips if Qwen is unreachable or returns nothing usable. Note:
        `covered_concepts`/`missing_concepts` here come directly from
        `eval_result`/`raw["concept_details"]`, not from
        `_strong_points`/`_detect_incorrect` (which are not called by this
        method).

        Args:
            transcript (str): Candidate's answer transcript.
            question (dict): Question record (`topic`, `text`, etc.).
            eval_result (dict): Evaluator output (`final_score`, `raw`,
                `covered_concepts`/`missing_concepts`/`incorrect_claims` or
                their `what_was_*` aliases, `grade`, `decision_source`).
            audio_result (Optional[dict]): Audio-pipeline output
                (`confidence_score`, `hesitation`, `linguistic`), if
                available.
            session_history (Optional[list]): Prior turn scores, for trend
                analysis.
            turn_number (int): 1-based turn index (default 1).
            is_code (bool): Unused by this method (code turns are handled
                by `generate_code_feedback`); accepted for call-site
                compatibility.
            attempt_number (int): 1-based attempt index within this turn
                (default 1).
            comparison (Optional[dict]): Prior-attempt comparison info
                (`resolved_concepts`, `score_delta`, etc.) when
                `attempt_number > 1`.

        Returns:
            dict: The full feedback contract (see module docstring) —
                `final_score`, `grade`, `score_breakdown`,
                `strong_points`/`what_was_correct`,
                `incorrect_or_incomplete`/`what_was_incorrect`,
                `missing_concepts`/`what_was_incomplete`,
                `how_to_improve`/`actionable_improvements`,
                `communication_tips`, `covered_concepts`, `trend`,
                `trend_note`, `justification`/`narrative_feedback`,
                `transcript`, `decision_source`, `llm_status`,
                `vague_points`, `attempt_number`, `comparison`.
        """
        score = float(eval_result.get("final_score", 0.5))
        raw = eval_result.get("raw") or {}

        s1 = float(raw.get("S1_semantic", score))
        s2 = float(raw.get("S2_structural", score))
        r  = float(raw.get("reasoning_score", score))

        # ── Audio signals ─────────────────────────────────────────────
        conf          = 0.5
        hesitation_rate = 0.0
        filler_count  = 0
        word_count    = 0
        uncertainty   : list[str] = []

        if audio_result and not audio_result.get("error"):
            conf = float(audio_result.get("confidence_score", 0.5))
            hes  = audio_result.get("hesitation") or {}
            hesitation_rate = float(hes.get("hesitation_score", 0.0))
            ling = audio_result.get("linguistic") or {}
            filler_count = int(ling.get("filler_count", 0))
            word_count   = int(ling.get("word_count", 0))
            uncertainty  = list(ling.get("uncertainty_markers", []))

        words = [w for w in (transcript or "").split() if w]
        if word_count == 0:
            word_count = len(words)

        # ── Concept details ───────────────────────────────────────────
        concept_details: list[dict] = raw.get("concept_details", [])
        raw_covered: list[str] = list(eval_result.get("covered_concepts") or eval_result.get("correct_claims") or [])
        raw_missing: list[str] = list(eval_result.get("missing_concepts") or eval_result.get("what_was_incomplete") or [])
        incorrect_claims: list[str] = list(eval_result.get("incorrect_claims") or eval_result.get("what_was_incorrect") or [])

        topic_name = str(question.get("topic", "Core Logic")).replace("_", " ").title()
        covered_concepts = [c for c in raw_covered if not str(c).strip().lower().startswith("concept ")]
        missing_concepts = [m for m in raw_missing if not str(m).strip().lower().startswith("concept ")]

        if not covered_concepts and not missing_concepts:
            for i, cd in enumerate(concept_details):
                label = str(cd.get("concept_text") or cd.get("concept") or cd.get("label") or "").strip()
                if not label or label.lower().startswith("concept "):
                    label = f"{topic_name} key mechanism"
                if cd.get("covered"):
                    covered_concepts.append(label)
                else:
                    missing_concepts.append(label)


        # ── Audio & Communication Tips ────────────────────────────────
        communication_tips = self._comm_tips(word_count, filler_count, hesitation_rate, uncertainty, conf)
        trend, trend_note  = self._trend(score, session_history or [], turn_number)
        grade              = raw.get("grade") or eval_result.get("grade") or self._grade(score)

        score_breakdown = {
            "semantic_similarity": round(s1, 3),
            "concept_coverage":    round(s2, 3),
            "reasoning_quality":   round(r,  3),
            "confidence_signal":   round(conf, 3),
            "overall":             round(score, 3),
        }

        # ── Query Qwen Feedback Microservice ──────────────────────────
        qwen_res = await self._query_qwen_feedback(
            transcript=transcript,
            question=question,
            eval_result=eval_result,
            candidate_state={"confidence": conf, "hesitation": hesitation_rate, "turn": turn_number},
            history=session_history or [],
            attempt_number=attempt_number,
            comparison=comparison,
        )

        if qwen_res:
            return {
                "final_score":              round(score, 4),
                "grade":                    grade,
                "score_breakdown":          score_breakdown,
                "what_candidate_said":      qwen_res.get("what_candidate_said", transcript[:150]),
                "what_was_correct":         qwen_res.get("what_was_correct", covered_concepts[:5]),
                "what_was_incorrect":       qwen_res.get("what_was_incorrect", incorrect_claims[:4]),
                "what_was_incomplete":      qwen_res.get("what_was_incomplete", missing_concepts[:4]),
                "missing_concepts":         qwen_res.get("missing_concepts", missing_concepts[:6]),
                "how_to_answer":            qwen_res.get("how_to_answer", ""),
                "stronger_answer_guide":    qwen_res.get("stronger_answer_guide", ""),
                "how_to_improve":           qwen_res.get("actionable_improvements", []),
                "actionable_improvements":  qwen_res.get("actionable_improvements", []),
                "strong_points":            qwen_res.get("what_was_correct", covered_concepts[:5]),
                "communication_tips":       communication_tips[:4],
                "covered_concepts":         covered_concepts[:6],
                "trend":                    trend,
                "trend_note":               trend_note,
                "justification":            qwen_res.get("narrative_feedback", ""),
                "narrative_feedback":       qwen_res.get("narrative_feedback", ""),
                "transcript":               transcript or "",
                "decision_source":          qwen_res.get("decision_source", "qwen_feedback"),
                # truthful pass-through: the service reports "llm_unavailable" when it returned its deterministic template
                "llm_status":               qwen_res.get("llm_status", "available"),
                "vague_points":             qwen_res.get("actionable_improvements", [])[:3],
                "attempt_number":           attempt_number,
                "comparison":               comparison or qwen_res.get("comparison"),
            }

        # ── Explicit LLM Unavailable State (Preserves Evaluator Evidence) ──
        deterministic_justification = self._justification(
            score, grade, s1, s2, r, conf, word_count,
            covered_concepts, missing_concepts, question,
        )

        if attempt_number > 1 and comparison:
            res_str = f"Resolved: {', '.join(comparison.get('resolved_concepts', []))}." if comparison.get('resolved_concepts') else ""
            delta_val = comparison.get('score_delta')
            delta_str = f"Score change: {delta_val:+.2f}." if delta_val is not None else ""
            deterministic_justification = f"[Attempt #{attempt_number}] {delta_str} {res_str} {deterministic_justification}".strip()

        return {
            "final_score":              round(score, 4),
            "grade":                    grade,
            "score_breakdown":          score_breakdown,
            "what_candidate_said":      transcript[:150] if transcript else "No answer provided",
            "what_was_correct":         covered_concepts[:5],
            "what_was_incorrect":       incorrect_claims[:4],
            "what_was_incomplete":      missing_concepts[:4],
            "missing_concepts":         missing_concepts[:6],
            "how_to_answer":            f"Review standard optimal algorithm for {question.get('topic', 'topic')}.",
            "stronger_answer_guide":    "Explain invariants, step-by-step logic, and complexity trade-offs clearly.",
            "how_to_improve":           [f"Cover missing concept: {m}" for m in missing_concepts[:3]],
            "actionable_improvements":  [f"Cover missing concept: {m}" for m in missing_concepts[:3]],
            "strong_points":            covered_concepts[:5] if covered_concepts else ["Attempted question"],
            "communication_tips":       communication_tips[:4],
            "covered_concepts":         covered_concepts[:6],
            "trend":                    trend,
            "trend_note":               trend_note,
            "justification":            deterministic_justification,
            "narrative_feedback":       deterministic_justification,
            "transcript":               transcript or "",
            "decision_source":          eval_result.get("decision_source", "evaluator_structured"),
            "llm_status":               "llm_unavailable",
            "vague_points":             [f"Cover missing concept: {m}" for m in missing_concepts[:3]],
            "attempt_number":           attempt_number,
            "comparison":               comparison,
        }

    def generate_code_feedback(
        self,
        code: str,
        passed: bool,
        tests_passed: int,
        tests_total: int,
        stdout: str,
        stderr: str,
        question: dict,
        session_history: Optional[list] = None,
        turn_number: int = 1,
        attempt_number: int = 1,
        comparison: Optional[dict] = None,
    ) -> dict:
        """Build the structured feedback dict for one code-submission turn.

        Derives a rule-based (not LLM-generated) set of strengths, issues,
        and tips by pattern-matching the submitted code (NULL checks,
        malloc/free pairing, comments, etc.) and the sandbox's pass/fail
        output.

        Args:
            code (str): Candidate's submitted source code.
            passed (bool): Whether the sandbox judged the submission
                accepted.
            tests_passed (int): Number of test cases passed.
            tests_total (int): Total number of test cases.
            stdout (str): Captured stdout from the sandbox run.
            stderr (str): Captured stderr (or compiler output) from the
                sandbox run.
            question (dict): Question record (`topic`, etc.).
            session_history (Optional[list]): Prior turn scores, for trend
                analysis.
            turn_number (int): 1-based turn index (default 1).
            attempt_number (int): 1-based attempt index within this turn
                (default 1).
            comparison (Optional[dict]): Prior-attempt comparison info
                (`score_delta`) when `attempt_number > 1`.

        Returns:
            dict: `status` (accepted/wrong_answer/compilation_error/
                sandbox_error), `final_score`, `grade`, `score_breakdown`,
                `strong_points`, `incorrect_or_incomplete` (list of
                `{what_was_said, correction, severity}`), `missing_concepts`
                (always empty here), `how_to_improve`,
                `communication_tips`, `covered_concepts` (always empty),
                `trend`, `trend_note`, `justification`, `transcript`
                (always empty), `decision_source`, `vague_points`,
                `attempt_number`, `comparison`.
        """
        score = (tests_passed / max(tests_total, 1)) if tests_total > 0 else (0.85 if passed else 0.35)
        grade = self._grade(score)
        trend, trend_note = self._trend(score, session_history or [], turn_number)

        strong_points: list[str] = []
        issues: list[dict] = []
        tips: list[str] = []
        comm_tips: list[str] = []

        code_lower = code.lower()
        topic = question.get("topic", "")

        if passed:
            strong_points.append("All test cases passed — functional correctness confirmed")
        if tests_total > 0:
            strong_points.append(f"Passed {tests_passed}/{tests_total} test cases")

        # Code quality signals
        if "null" in code_lower or "nullptr" in code_lower:
            strong_points.append("NULL pointer check present — good defensive coding")
        if "free(" in code_lower and topic in ("pointers", "memory_management", "linked_list"):
            strong_points.append("Memory freed after use — no obvious leak")
        if "return" in code_lower:
            strong_points.append("Return value handled correctly")

        # Issues
        if not passed:
            if stderr:
                issues.append({
                    "what_was_said": f"Compiler/runtime error: {stderr[:120]}",
                    "correction": "Fix the error above, then re-run test cases",
                    "severity": "major",
                })
            if tests_total > 0 and tests_passed < tests_total:
                issues.append({
                    "what_was_said": f"Failed {tests_total - tests_passed} of {tests_total} test cases",
                    "correction": "Trace through the failing cases manually — check boundary conditions",
                    "severity": "major",
                })

        # Memory-specific checks
        if topic in ("pointers", "memory_management", "linked_list"):
            if "malloc" in code_lower and "free" not in code_lower:
                issues.append({
                    "what_was_said": "malloc called but no free() found",
                    "correction": "Every malloc must have a corresponding free() — add cleanup",
                    "severity": "major",
                })
            if "malloc" in code_lower and "== null" not in code_lower and "!= null" not in code_lower:
                issues.append({
                    "what_was_said": "malloc return value not checked for NULL",
                    "correction": "Always check: if (ptr == NULL) { handle error; }",
                    "severity": "minor",
                })

        # Improvement tips
        tips.append("After passing tests, always consider: what happens with empty input? max-size input? negative values?")
        if not passed:
            tips.append("Debug strategy: add printf statements at each step, check intermediate values")
        if topic in _TOPIC_STRUCTURE_TIPS:
            tips.append(_TOPIC_STRUCTURE_TIPS[topic])
        tips.append("Add inline comments explaining WHY each block exists, not just what it does")

        # Communication
        line_count = len([l for l in code.split("\n") if l.strip()])
        comm_tips.append(f"Code is {line_count} lines — {'concise' if line_count < 40 else 'consider refactoring for clarity'}")
        if "// " not in code and "/* " not in code:
            comm_tips.append("No comments detected — add comments for complex logic and edge case handling")

        if not passed and ("sandbox daemon" in stderr.lower() or "sandbox_error" in stderr.lower() or "docker daemon" in stderr.lower() or "unreachable" in stderr.lower()):
            status = "sandbox_error"
        else:
            status = "accepted" if passed else ("compilation_error" if "error:" in stderr.lower() or "expected" in stderr.lower() else "wrong_answer")

        attempt_prefix = ""
        if attempt_number > 1 and comparison:
            delta_val = comparison.get("score_delta")
            delta_str = f"Score change: {delta_val:+.2f}." if delta_val is not None else ""
            attempt_prefix = f"[Attempt #{attempt_number}] {delta_str} "

        justification = (
            f"{attempt_prefix}Code grade {grade} ({score:.0%}). "
            f"{'All tests passed.' if passed else f'{tests_passed}/{tests_total} tests passed.'} "
            + (f"Compiler output: {stderr[:80]}" if stderr and not passed else "")
        ).strip()

        return {
            "status":                  status,
            "final_score":             round(score, 3),
            "grade":                   grade,
            "score_breakdown":         {"functional_correctness": round(score, 3), "tests_passed": tests_passed, "tests_total": tests_total},
            "strong_points":           strong_points[:5],
            "incorrect_or_incomplete": issues[:4],
            "missing_concepts":        [],
            "how_to_improve":          tips[:5],
            "communication_tips":      comm_tips[:3],
            "covered_concepts":        [],
            "trend":                   trend,
            "trend_note":              trend_note,
            "justification":           justification,
            "transcript":              "",
            "decision_source":         "sandbox_evaluator" if status != "sandbox_error" else "sandbox_error",
            "vague_points":            tips[:3],
            "attempt_number":          attempt_number,
            "comparison":              comparison,
        }

    # ── Private helpers ───────────────────────────────────────────────────

    def _grade(self, score: float) -> str:
        """Map a numeric score to a letter grade.

        Args:
            score (float): Score in [0, 1].

        Returns:
            str: "A" (>=0.85), "B" (>=0.70), "C" (>=0.55), "D" (>=0.40), or
                "F".
        """
        if score >= 0.85: return "A"
        if score >= 0.70: return "B"
        if score >= 0.55: return "C"
        if score >= 0.40: return "D"
        return "F"

    def _strong_points(self, eval_result: dict, transcript: str, s1: float, s2: float, r: float) -> list[str]:
        """Derive a list of strengths from the evaluator scores and transcript text.

        Note: this method is defined but is dead code — `generate()` does
        not call it; the live `strong_points`/`what_was_correct` fields
        come from `eval_result`'s own `covered_concepts` instead.

        Args:
            eval_result (dict): Evaluator output; its own `strong_points`
                is used first if rich enough.
            transcript (str): Candidate's answer transcript.
            s1 (float): Semantic-similarity sub-score.
            s2 (float): Concept-coverage sub-score.
            r (float): Reasoning sub-score.

        Returns:
            list[str]: Up to 5 strength statements, or a single generic
                fallback if none apply.
        """
        # Use evaluator's strong_points if rich enough
        ev_strong = [p for p in (eval_result.get("strong_points") or []) if len(p) > 10]
        if len(ev_strong) >= 2:
            return ev_strong[:5]

        text = (transcript or "").lower()
        pts: list[str] = []

        if s1 >= 0.65: pts.append(f"Answer is semantically on-topic (similarity {s1:.0%})")
        if s2 >= 0.60: pts.append(f"Good concept coverage — {s2:.0%} of key ideas addressed")
        if r  >= 0.65: pts.append("Sound reasoning — logical flow detected")

        struct_words = ["first", "then", "because", "therefore", "which means", "so that"]
        if sum(1 for w in struct_words if w in text) >= 2:
            pts.append("Structured explanation with cause-effect reasoning")

        if "complexity" in text or "o(" in text:
            pts.append("Complexity analysis included — shows depth of understanding")

        wc = len(text.split())
        if wc >= 80:
            pts.append(f"Sufficient depth ({wc} words)")

        if "example" in text or "for instance" in text or "e.g" in text:
            pts.append("Concrete example provided to illustrate the concept")

        return pts or ["Answer attempted — be more specific about the core concept"]

    def _detect_incorrect(self, transcript: str, question: dict, concept_details: list) -> list[dict]:
        """Flag misconceptions and other issues in a transcript via substring matching.

        Checks the transcript against `_MISCONCEPTIONS`'s topic-keyed
        trigger phrases, unjustified absolute claims ("always"/"never"
        without "because"/"since"), and answers under 25 words.

        Note: this method is defined but is dead code — `generate()` does
        not call it; the live `incorrect_or_incomplete`/`what_was_incorrect`
        fields come from the evaluator's own `incorrect_claims` instead.

        Args:
            transcript (str): Candidate's answer transcript.
            question (dict): Question record; `topic` selects which
                misconception set to check.
            concept_details (list): Unused by the current implementation;
                accepted for call-site compatibility.

        Returns:
            list[dict]: Issues found, each `{what_was_said, correction,
                severity}`.
        """
        text = (transcript or "").lower()
        topic = (question.get("topic") or "").lower()
        issues: list[dict] = []

        # Topic-specific misconceptions
        for key, checks in _MISCONCEPTIONS.items():
            if key in topic:
                for trigger, correction, severity in checks:
                    if trigger in text:
                        issues.append({
                            "what_was_said": f'Contains: "{trigger}..."',
                            "correction": correction,
                            "severity": severity,
                        })
                break

        # Generic absolute claims
        for word in ("always", "never"):
            if word in text and "because" not in text and "since" not in text:
                issues.append({
                    "what_was_said": f'Used "{word}" without justification',
                    "correction": f"Explain WHY '{word}' — specify the conditions that make it so",
                    "severity": "minor",
                })
                break

        # Too brief
        wc = len(text.split())
        if wc < 25:
            issues.append({
                "what_was_said": f"Answer was only {wc} words — key concepts left unexplained",
                "correction": "Aim for 80–120 words: Problem → Core idea → Steps → Edge cases → Complexity",
                "severity": "major",
            })

        return issues

    def _improvement_tips(self, transcript: str, question: dict, s1: float, s2: float, r: float, missing: list) -> list[str]:
        """Generate actionable improvement tips from the score breakdown and transcript.

        Note: this method is defined but is dead code — `generate()` does
        not call it; the live `how_to_improve`/`actionable_improvements`
        fields are built from `missing_concepts` directly (or from Qwen).

        Args:
            transcript (str): Candidate's answer transcript.
            question (dict): Question record (`topic`, `text`).
            s1 (float): Semantic-similarity sub-score.
            s2 (float): Concept-coverage sub-score.
            r (float): Reasoning sub-score.
            missing (list): Missing concept labels.

        Returns:
            list[str]: Improvement tips, always including a general
                structure tip plus any triggered by low sub-scores, missing
                complexity/example discussion, or a topic-specific
                structure tip from `_TOPIC_STRUCTURE_TIPS`.
        """
        text  = (transcript or "").lower()
        topic = (question.get("topic") or "")
        tips: list[str] = []

        tips.append("Structure every answer: Problem → Core Idea → Steps/Logic → Edge Cases → Complexity")

        if s1 < 0.50:
            snip = (question.get("text") or "")[:60]
            tips.append(f"Re-read the question — your answer drifted from the topic. Focus on: '{snip}...'")

        if s2 < 0.50 and missing:
            tips.append(f"Cover these missing concepts: {', '.join(missing[:3])}")

        if r < 0.50:
            tips.append("Add 'because' / 'therefore' / 'which means' — make your reasoning explicit, not just facts")

        if "o(" not in text and "complexity" not in text:
            tips.append("Always close with complexity: 'This runs in O(n) time and O(1) space because...'")

        if "example" not in text and "for instance" not in text:
            tips.append("Add a concrete example — walk through 1–2 values to prove your logic works")

        if topic in _TOPIC_STRUCTURE_TIPS:
            tips.append(_TOPIC_STRUCTURE_TIPS[topic])

        return tips

    def _comm_tips(self, word_count: int, filler_count: int, hesitation_rate: float, uncertainty: list, conf: float) -> list[str]:
        """Generate delivery/communication tips from audio-derived signals.

        Args:
            word_count (int): Number of words in the answer.
            filler_count (int): Count of filler words (um/uh/like) detected.
            hesitation_rate (float): Hesitation score in [0, 1].
            uncertainty (list): Hedging-phrase strings detected in the
                transcript.
            conf (float): Vocal confidence score in [0, 1].

        Returns:
            list[str]: Tips covering answer length, filler words, hedging
                language, hesitation, and vocal confidence — always
                non-empty.
        """
        tips: list[str] = []

        if word_count < 40:
            tips.append(f"Answer too short ({word_count} words). Aim for 80–120 words minimum for theory questions.")
        elif word_count > 320:
            tips.append(f"Very long answer ({word_count} words). Be concise — interviewers value clarity over volume.")
        else:
            tips.append(f"Good answer length ({word_count} words).")

        if filler_count > 3:
            tips.append(f"Detected {filler_count} filler words (um/uh/like). Pause and think instead of filling silence.")
        elif filler_count == 0:
            tips.append("No filler words detected — clean, confident delivery.")

        if uncertainty:
            listed = ", ".join(f'"{m}"' for m in uncertainty[:3])
            tips.append(f"Hedging language detected: {listed}. Use assertive phrasing: 'malloc allocates uninitialized memory' not 'I think malloc...'")

        if hesitation_rate > 0.55:
            tips.append("High hesitation detected. Practise saying the key technical terms aloud — fluency builds with repetition.")

        if conf < 0.40:
            tips.append("Low confidence signal in delivery. Speak at a steady pace and maintain consistent volume.")
        elif conf >= 0.70:
            tips.append(f"Good vocal confidence ({conf:.0%}) — assertive delivery detected.")

        return tips

    def _trend(self, current: float, history: list, turn: int) -> tuple[str, str]:
        """Classify the candidate's score trend against their recent rolling average.

        Args:
            current (float): This turn's score.
            history (list): Prior turn scores; the last 3 (or fewer) are
                used as the rolling-average baseline.
            turn (int): 1-based turn index, used only in the "not enough
                history" message.

        Returns:
            tuple[str, str]: `(trend, trend_note)` where `trend` is
                "improving" (delta >= +0.08), "declining" (delta <= -0.08),
                or "stable", and `trend_note` is a human-readable
                explanation.
        """
        if len(history) < 2:
            return "stable", f"Turn {turn} — not enough history yet for trend analysis"
        recent = history[-3:] if len(history) >= 3 else history
        avg = sum(recent) / len(recent)
        delta = current - avg
        if delta >= 0.08:
            return "improving", f"Score improving: {avg:.2f} → {current:.2f} (+{delta:.2f})"
        if delta <= -0.08:
            return "declining", f"Score dropped: {avg:.2f} → {current:.2f} ({delta:.2f})"
        return "stable", f"Score stable around {avg:.2f} (current {current:.2f})"

    def _justification(self, score, grade, s1, s2, r, conf, word_count, strong, missing, question) -> str:
        """Build the deterministic fallback narrative used when Qwen is unreachable.

        Args:
            score (float): Final weighted score.
            grade (str): Letter grade.
            s1 (float): Semantic-similarity sub-score.
            s2 (float): Concept-coverage sub-score.
            r (float): Reasoning sub-score.
            conf (float): Vocal confidence score.
            word_count (int): Number of words in the answer.
            strong (list): Covered-concept labels (first one is quoted if
                present).
            missing (list): Missing-concept labels (first two are quoted if
                present).
            question (dict): Question record; `topic` is used in the
                opening sentence.

        Returns:
            str: A short, human-readable justification sentence sequence
                covering grade, sub-scores, and any missing-concept/
                brevity flags.
        """
        topic = question.get("topic", "general")
        parts = [
            f"Grade {grade} ({score:.0%}) on {topic}.",
            f"Semantic {s1:.0%} | Concept coverage {s2:.0%} | Reasoning {r:.0%} | Confidence {conf:.0%}.",
        ]
        if strong:
            parts.append(f"Strength: {strong[0]}.")
        if missing:
            parts.append(f"Missing: {', '.join(missing[:2])}.")
        if s2 < 0.50:
            parts.append("Concept coverage below 50% — key ideas were not addressed.")
        elif s2 >= 0.75:
            parts.append("Strong concept coverage.")
        if word_count < 40:
            parts.append(f"Answer too brief ({word_count} words) to demonstrate depth.")
        return " ".join(parts)

    async def _query_qwen_feedback(
        self,
        transcript: str,
        question: dict,
        eval_result: dict,
        candidate_state: dict,
        history: list,
        attempt_number: int = 1,
        comparison: Optional[dict] = None,
    ) -> Optional[dict]:
        """Query the Qwen feedback microservice for grounded narrative feedback.

        Tries `/api/qwen/feedback` then `/feedback` on the configured Qwen
        URL, with one retry (0.1s backoff) on connection/timeout errors.
        Never raises — any failure results in None, signaling the caller to
        use the deterministic fallback.

        Args:
            transcript (str): Candidate's answer transcript.
            question (dict): Question record (`text`/`question_text`,
                `topic`).
            eval_result (dict): Evaluator output, sent as
                `structured_evaluation`.
            candidate_state (dict): Current confidence/hesitation/turn
                state.
            history (list): Prior turn scores; up to the last 3 numeric
                entries are sent.
            attempt_number (int): 1-based attempt index (default 1).
            comparison (Optional[dict]): Prior-attempt comparison info,
                merged into the payload if present.

        Returns:
            Optional[dict]: The Qwen service's JSON response if a call
                succeeded (HTTP 200 with a `what_candidate_said` key), else
                None. Also sets `self._qwen_ok`.
        """
        if not _HTTPX:
            return None

        payload = {
            "question_text": str(question.get("text", "") or question.get("question_text", "")),
            "topic": str(question.get("topic", "general")),
            "candidate_answer": str(transcript or ""),
            "structured_evaluation": eval_result,
            "candidate_state": candidate_state or {},
            "history": [{"score": float(s)} for s in history[-3:] if isinstance(s, (int, float))],
            "attempt_number": attempt_number,
        }
        if comparison:
            payload.update({
                "previous_best_answer": comparison.get("previous_best_answer"),
                "previous_best_score": comparison.get("previous_best_score"),
                "resolved_concepts": comparison.get("resolved_concepts", []),
                "remaining_concepts": comparison.get("remaining_concepts", []),
                "score_delta": comparison.get("score_delta"),
            })

        # Attempt call with 1 immediate retry on connection/timeout error
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=QWEN_TIMEOUT) as client:
                    # Try structured endpoint, fallback to /feedback
                    for ep in ("/api/qwen/feedback", "/feedback"):
                        r = await client.post(f"{self.qwen_url}{ep}", json=payload)
                        if r.status_code == 200:
                            self._qwen_ok = True
                            data = r.json()
                            if isinstance(data, dict) and "what_candidate_said" in data:
                                return data
            except Exception:
                await asyncio.sleep(0.1)

        self._qwen_ok = False
        return None


# Module-level singleton — import and reuse across requests
FEEDBACK_AGENT = FeedbackAgent()
