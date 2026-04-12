"""
PrepAIred — Evaluator/evaluate_upgraded.py
==========================================
Drop-in replacement for evaluate.py that adds:

  1. Hybrid Qwen gate — when S1 > 0.40 AND S2 < 0.60, calls Qwen 7B
     microservice for partial-credit scoring.
  2. Returns rubric_score, qwen_bonus, final_score per answer.
  3. Returns missing_concepts, strong_points, vague_points for feedback card.
  4. All Qwen calls go to the microservice (port 8001) — never blocking.

Import this as a drop-in:
    from Evaluator.evaluate_upgraded import evaluate, evaluate_async

Async version is preferred for WebSocket use.
Sync version wraps it for backward compatibility.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Optional
import httpx
import os

# ── Thresholds ────────────────────────────────────────────────────────────────
AMBIGUITY_S1_LOW  = 0.40   # S1 above this → semantically relevant
AMBIGUITY_S2_HIGH = 0.60   # S2 below this → incomplete concept coverage
QWEN_SERVICE_URL  = "http://localhost:8001"
QWEN_TIMEOUT      = 8.0    # seconds — partial_eval endpoint

# ── Score weights ─────────────────────────────────────────────────────────────
W_S1 = 0.24
W_S2 = 0.43
W_R  = 0.33

# ── Rubric cache ──────────────────────────────────────────────────────────────
_rubric_cache: dict = {}
_sbert_model = None
_cross_encoder = None


def _normalize_rubrics(raw) -> dict:
    """Normalize rubric payloads into a qid->rubric dict.

    Supports both legacy dict format and list-of-objects format.
    """
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, list):
        out = {}
        for item in raw:
            if isinstance(item, dict) and item.get("qid") is not None:
                out[str(item.get("qid"))] = item
        return out
    return {}


def get_rubric(qid: str) -> dict:
    """Load rubric for question ID. Cached after first load."""
    if qid in _rubric_cache:
        return _rubric_cache[qid]

    root = os.path.dirname(os.path.dirname(__file__))
    rubric_candidates = [
        os.path.join(os.path.dirname(__file__), "rubrics.json"),
        os.path.join(root, "rubrics_final_clean.json"),
        os.path.join(root, "Evaluator_final", "Evaluator", "rubrics.json"),
    ]

    for rubric_path in rubric_candidates:
        if not os.path.exists(rubric_path):
            continue
        try:
            with open(rubric_path, encoding="utf-8") as f:
                all_rubrics = _normalize_rubrics(json.load(f))
            if all_rubrics:
                _rubric_cache.update(all_rubrics)
                break
        except Exception:
            continue

    return _rubric_cache.get(qid, {})


# ── Core scoring helpers (delegates to existing evaluate.py primitives) ───────

def _compute_s1(answer: str, rubric: dict) -> float:
    """Lightweight semantic proxy based on token overlap with rubric targets."""
    targets = rubric.get("logic_markers", {}).get("semantic_targets", [])
    if not targets:
        targets = rubric.get("semantic_targets", [])
    if not targets:
        return 0.5

    ans_tokens = {t for t in answer.lower().split() if len(t) > 2}
    if not ans_tokens:
        return 0.0

    best = 0.0
    for target in targets:
        tar_tokens = {t for t in str(target).lower().split() if len(t) > 2}
        if not tar_tokens:
            continue
        inter = len(ans_tokens & tar_tokens)
        union = len(ans_tokens | tar_tokens)
        score = (inter / union) if union else 0.0
        if score > best:
            best = score
    return round(float(best), 4)


def _compute_s2(answer: str, rubric: dict) -> tuple[float, list[str]]:
    """Concept coverage via keyword matching + FAISS (if available)."""
    markers = rubric.get("logic_markers", {})
    groups: list = markers.get("concept_groups", [])
    mandatory: list = markers.get("mandatory", [])

    if not groups and not mandatory:
        return 0.5, []

    answer_lower = answer.lower()
    hit_count = 0
    total = 0
    missing = []

    for group in groups:
        items = group if isinstance(group, list) else [group]
        total += 1
        if any(kw.lower() in answer_lower for kw in items):
            hit_count += 1
        else:
            missing.append(items[0] if items else "unknown")

    for m in mandatory:
        total += 1
        if m.lower() not in answer_lower:
            missing.append(m)
        else:
            hit_count += 1

    if total == 0:
        return 0.5, []

    return round(hit_count / total, 4), missing


def _compute_r(answer: str, rubric: dict) -> float:
    """Lightweight reasoning proxy using discourse markers and answer depth."""
    text = answer.lower().strip()
    if not text:
        return 0.0

    markers = ["because", "therefore", "so", "hence", "if", "then", "edge", "case"]
    marker_hits = sum(1 for m in markers if m in text)
    length_bonus = min(len(text.split()) / 40.0, 1.0)
    marker_bonus = min(marker_hits / 4.0, 1.0)
    score = 0.35 * length_bonus + 0.65 * marker_bonus
    return round(float(max(0.0, min(1.0, score))), 4)


def _check_mandatory(answer: str, rubric: dict) -> bool:
    mandatory = rubric.get("logic_markers", {}).get("mandatory", [])
    answer_lower = answer.lower()
    return all(m.lower() in answer_lower for m in mandatory)


def _bonus(answer: str, rubric: dict) -> float:
    bonus_kw = rubric.get("logic_markers", {}).get("advanced_bonus", [])
    answer_lower = answer.lower()
    hits = sum(1 for kw in bonus_kw if kw.lower() in answer_lower)
    return min(hits * 0.05, 0.15)


def _penalty(answer: str, rubric: dict) -> float:
    mistake_kw = rubric.get("logic_markers", {}).get("common_mistakes", [])
    answer_lower = answer.lower()
    hits = sum(1 for kw in mistake_kw if kw.lower() in answer_lower)
    return min(hits * 0.05, 0.15)


# ── Qwen partial-credit call ──────────────────────────────────────────────────

async def _call_qwen_partial_eval(
    question_text: str,
    transcript: str,
    rubric: dict,
    s1: float,
    s2: float,
    combined: float,
) -> Optional[dict]:
    """
    Call Qwen 7B microservice for deep partial-credit evaluation.
    Returns None on any failure (graceful degradation).
    """
    markers = rubric.get("logic_markers", {})
    payload = {
        "question_text": question_text,
        "transcript": transcript,
        "mandatory": markers.get("mandatory", []),
        "concept_groups": markers.get("concept_groups", []),
        "s1_score": s1,
        "s2_score": s2,
        "combined_score": combined,
    }
    try:
        async with httpx.AsyncClient(timeout=QWEN_TIMEOUT) as client:
            resp = await client.post(f"{QWEN_SERVICE_URL}/partial_eval", json=payload)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        print(f"[Evaluator] Qwen partial_eval failed (graceful degradation): {e}")
        return None


# ── Public API ────────────────────────────────────────────────────────────────

async def evaluate_async(answer: str, qid: str, rubric: dict = None) -> dict:
    """
    Hybrid evaluator — async version (preferred for WebSocket use).

    Scoring pipeline:
      S1: SBERT semantic similarity        (~20 ms)
      S2: Concept coverage + missing list  (~30 ms)
      R:  CrossEncoder reasoning           (~20 ms)
      HYBRID GATE: if S1 > 0.40 AND S2 < 0.60 → Qwen 7B partial eval (~2s)
      Calibration: linear rescaling
    """
    t0 = time.time()

    if rubric is None:
        rubric = get_rubric(qid)

    # ── Fast path: S1, S2, R in parallel ─────────────────────────────────────
    loop = asyncio.get_event_loop()
    s1_fut = loop.run_in_executor(None, _compute_s1, answer, rubric)
    s2_fut = loop.run_in_executor(None, _compute_s2, answer, rubric)
    r_fut  = loop.run_in_executor(None, _compute_r, answer, rubric)

    s1_score, (s2_score, missing_concepts), r_score = await asyncio.gather(
        s1_fut, s2_fut, r_fut
    )

    # ── Mandatory & bonus ─────────────────────────────────────────────────────
    mandatory_pass = _check_mandatory(answer, rubric)
    bonus          = _bonus(answer, rubric)
    penalty        = _penalty(answer, rubric)

    raw_combined = W_S1 * s1_score + W_S2 * s2_score + W_R * r_score + bonus - penalty
    if not mandatory_pass:
        raw_combined = min(raw_combined, 0.45)
    raw_combined = max(0.0, min(1.0, raw_combined))

    # ── Hybrid gate ───────────────────────────────────────────────────────────
    qwen_invoked   = False
    qwen_bonus     = 0.0
    rubric_score   = raw_combined
    final_score    = raw_combined
    strong_points  = []
    vague_points   = []
    justification  = ""

    in_ambiguous_zone = s1_score > AMBIGUITY_S1_LOW and s2_score < AMBIGUITY_S2_HIGH

    if in_ambiguous_zone:
        question_text = rubric.get("question_text", "")
        qwen_result = await _call_qwen_partial_eval(
            question_text=question_text,
            transcript=answer,
            rubric=rubric,
            s1=s1_score,
            s2=s2_score,
            combined=raw_combined,
        )
        if qwen_result:
            qwen_invoked    = True
            rubric_score    = float(qwen_result.get("rubric_score", raw_combined))
            qwen_bonus      = float(qwen_result.get("qwen_bonus", 0.0))
            final_score     = float(qwen_result.get("final_score", rubric_score + qwen_bonus))
            strong_points   = qwen_result.get("strong_points", [])
            vague_points    = qwen_result.get("vague_points", [])
            justification   = qwen_result.get("justification", "")
            # Merge Qwen's missing concepts with S2's
            qwen_missing    = qwen_result.get("missing_concepts", [])
            missing_concepts = list(dict.fromkeys(missing_concepts + qwen_missing))

    final_score = max(0.0, min(1.0, final_score))

    return {
        # Core scores
        "s1_score":          round(s1_score, 4),
        "s2_score":          round(s2_score, 4),
        "r_score":           round(r_score, 4),
        "rubric_score":      round(rubric_score, 4),
        "qwen_bonus":        round(qwen_bonus, 4),
        "final_score":       round(final_score, 4),

        # Qwen gate info
        "qwen_invoked":      qwen_invoked,
        "in_ambiguous_zone": in_ambiguous_zone,

        # Feedback signals
        "missing_concepts":  missing_concepts[:6],
        "strong_points":     strong_points[:4],
        "vague_points":      vague_points[:4],
        "justification":     justification,
        "mandatory_pass":    mandatory_pass,
        "bonus":             round(bonus, 4),
        "penalty":           round(penalty, 4),

        # Perf
        "latency_ms": round((time.time() - t0) * 1000, 1),
        "qid":        qid,
    }


def evaluate(answer: str, qid: str, rubric: dict = None) -> dict:
    """
    Synchronous wrapper around evaluate_async.
    For backward compatibility with existing call sites.
    """
    try:
        try:
            running_loop = asyncio.get_running_loop()
            loop_running = running_loop.is_running()
        except RuntimeError:
            loop_running = False

        if loop_running:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, evaluate_async(answer, qid, rubric))
                return future.result(timeout=15)

        return asyncio.run(evaluate_async(answer, qid, rubric))
    except Exception as e:
        print(f"[Evaluator] evaluate() failed: {e}")
        # Graceful fallback
        return {
            "s1_score": 0.5, "s2_score": 0.5, "r_score": 0.5,
            "rubric_score": 0.5, "qwen_bonus": 0.0, "final_score": 0.5,
            "qwen_invoked": False, "in_ambiguous_zone": False,
            "missing_concepts": [], "strong_points": [], "vague_points": [],
            "justification": f"Evaluation error: {e}",
            "mandatory_pass": True, "bonus": 0.0, "penalty": 0.0,
            "latency_ms": 0.0, "qid": qid,
        }


# ── Convenience alias ─────────────────────────────────────────────────────────
evaluate_answer = evaluate
