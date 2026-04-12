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
from typing import Optional

try:
    import httpx
    _HTTPX = True
except ImportError:
    _HTTPX = False

QWEN_URL = "http://localhost:8001"
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
    ) -> dict:
        """Build and return rich feedback dict."""
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
        rubric_groups: list = []
        if eval_result.get("raw"):
            # concept_groups may be in rubric embedded in raw
            rubric_groups = raw.get("concept_groups", [])

        covered_concepts: list[str] = []
        missed_concepts: list[str] = []
        for cd in concept_details:
            label = str(cd.get("concept") or cd.get("label") or "concept")
            if cd.get("covered"):
                covered_concepts.append(label)
            else:
                missed_concepts.append(label)

        # Fallback from eval_result missing_concepts
        missing_concepts = list(eval_result.get("missing_concepts") or missed_concepts or [])

        # ── Build all sections ────────────────────────────────────────
        strong_points         = self._strong_points(eval_result, transcript, s1, s2, r)
        incorrect_items       = self._detect_incorrect(transcript, question, concept_details)
        how_to_improve        = self._improvement_tips(transcript, question, s1, s2, r, missing_concepts)
        communication_tips    = self._comm_tips(word_count, filler_count, hesitation_rate, uncertainty, conf)
        trend, trend_note     = self._trend(score, session_history or [], turn_number)
        grade                 = raw.get("grade") or self._grade(score)

        score_breakdown = {
            "semantic_similarity": round(s1, 3),
            "concept_coverage":    round(s2, 3),
            "reasoning_quality":   round(r,  3),
            "confidence_signal":   round(conf, 3),
            "overall":             round(score, 3),
        }

        justification = self._justification(
            score, grade, s1, s2, r, conf, word_count,
            strong_points, missing_concepts, question,
        )

        # Try to enrich justification via Qwen narrative (non-blocking)
        qwen_narrative = await self._qwen_feedback(transcript, question, score, missing_concepts)
        if qwen_narrative:
            justification = qwen_narrative

        return {
            "final_score":              round(score, 3),
            "grade":                    grade,
            "score_breakdown":          score_breakdown,
            "strong_points":            strong_points[:5],
            "incorrect_or_incomplete":  incorrect_items[:4],
            "missing_concepts":         missing_concepts[:6],
            "how_to_improve":           how_to_improve[:5],
            "communication_tips":       communication_tips[:4],
            "covered_concepts":         covered_concepts[:6],
            "trend":                    trend,
            "trend_note":               trend_note,
            "justification":            justification,
            "transcript":               transcript or "",
            "decision_source":          eval_result.get("decision_source", "evaluator"),
            # backward-compat
            "vague_points":             how_to_improve[:3],
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
    ) -> dict:
        """Rich feedback for code submissions."""
        score = (tests_passed / max(tests_total, 1)) if tests_total > 0 else (0.85 if passed else 0.35)
        grade = self._grade(score)

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

        trend, trend_note = self._trend(score, session_history or [], turn_number)

        justification = (
            f"Code grade {grade} ({score:.0%}). "
            f"{'All tests passed.' if passed else f'{tests_passed}/{tests_total} tests passed.'} "
            + (f"Compiler output: {stderr[:80]}" if stderr and not passed else "")
        )

        return {
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
            "decision_source":         "sandbox_evaluator",
            "vague_points":            tips[:3],
        }

    # ── Private helpers ───────────────────────────────────────────────────

    def _grade(self, score: float) -> str:
        if score >= 0.85: return "A"
        if score >= 0.70: return "B"
        if score >= 0.55: return "C"
        if score >= 0.40: return "D"
        return "F"

    def _strong_points(self, eval_result: dict, transcript: str, s1: float, s2: float, r: float) -> list[str]:
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

    async def _qwen_feedback(self, transcript: str, question: dict, score: float, missing: list) -> Optional[str]:
        """Call Qwen /report for a 1-paragraph narrative. Non-blocking; returns None on any failure."""
        if not _HTTPX:
            return None
        if self._qwen_ok is False:
            return None
        try:
            payload = {
                "transcript": (transcript or "")[:600],
                "question":   (question.get("text") or "")[:200],
                "score":      round(score, 3),
                "missing":    missing[:4],
            }
            async with httpx.AsyncClient(timeout=QWEN_TIMEOUT) as client:
                r = await client.post(f"{self.qwen_url}/report", json=payload)
                if r.status_code == 200:
                    self._qwen_ok = True
                    data = r.json()
                    return data.get("text") or data.get("narrative") or None
                self._qwen_ok = False
                return None
        except Exception:
            self._qwen_ok = False
            return None


# Module-level singleton — import and reuse across requests
FEEDBACK_AGENT = FeedbackAgent()
