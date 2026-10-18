"""
analytics.py — Read-only learner analytics built from stored interview attempts.

Everything here is derived from rows already written by the interview flow
(`sessions` and `question_attempts`) plus the question bank. Nothing is stored,
estimated by a model, or invented:

* Scores are the evaluator's validated scores (`validated_score`).
* Bands reuse the evaluator's existing grade boundaries (>= 0.60 Good, >= 0.40 Average;
  see services/storage/best_answer.py). No new thresholds are introduced for scoring.
* Concept statistics count how often a concept text was reported as covered, missing, or
  incorrect by the evaluator. They are *measured counts*; every classification carries the
  number of observations it rests on and is flagged `low_data` when that number is small.
* Streaks and weekly counts use the attempt timestamps shifted by the client's UTC offset.

Public functions return plain dicts that FastAPI can serialize directly.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from services.storage.database import get_connection

GOOD_FLOOR = 0.60       # evaluator grade "Good" boundary
AVERAGE_FLOOR = 0.40    # evaluator grade "Average" boundary
MIN_OBS_FOR_CLASS = 2   # a concept/topic needs at least this many observations to be classified
LOW_DATA_BELOW = 3      # fewer observations than this are flagged low_data
DECLINE_MIN_ATTEMPTS = 4
DECLINE_DROP = 0.10


# ── helpers ──────────────────────────────────────────────────────────────────

def _parse_ts(value: Any) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


def _loads(value: Any, default: Any) -> Any:
    if value is None or value == "":
        return default
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return default


def band_for(score: Optional[float]) -> str:
    if score is None:
        return "unknown"
    if score >= GOOD_FLOOR:
        return "strong"
    if score >= AVERAGE_FLOOR:
        return "developing"
    return "needs_work"


def pretty_topic(topic: str) -> str:
    return str(topic or "General").replace("_", " ").strip()


def _norm(text: Any) -> str:
    return " ".join(str(text or "").lower().split())


def _mean(values: List[float]) -> Optional[float]:
    return round(sum(values) / len(values), 4) if values else None


def _load_attempts(candidate_id: str, db_path: Optional[Path | str]) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT id, session_id, question_id, attempt_number, attempt_type, parent_question_id,
                   answer_type, transcript, code_submitted, validated_score, covered_concepts,
                   missing_concepts, incorrect_claims, weakest_gap, created_at
            FROM question_attempts
            WHERE candidate_id = ?
            ORDER BY created_at ASC, id ASC;
            """,
            (str(candidate_id),),
        ).fetchall()
    finally:
        conn.close()
    out = []
    for r in rows:
        d = dict(r)
        d["covered_concepts"] = _loads(d.get("covered_concepts"), [])
        d["missing_concepts"] = _loads(d.get("missing_concepts"), [])
        d["incorrect_claims"] = _loads(d.get("incorrect_claims"), [])
        d["score"] = float(d["validated_score"]) if d.get("validated_score") is not None else None
        d["ts"] = _parse_ts(d.get("created_at"))
        out.append(d)
    return out


def _load_sessions(candidate_id: str, db_path: Optional[Path | str]) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT id, interview_mode, c_topics, dsa_topics, duration_minutes, num_questions,
                   start_difficulty, status, overall_score, created_at, completed_at
            FROM sessions WHERE candidate_id = ? ORDER BY created_at ASC;
            """,
            (str(candidate_id),),
        ).fetchall()
    finally:
        conn.close()
    out = []
    for r in rows:
        d = dict(r)
        d["c_topics"] = _loads(d.get("c_topics"), [])
        d["dsa_topics"] = _loads(d.get("dsa_topics"), [])
        d["ts"] = _parse_ts(d.get("created_at"))
        out.append(d)
    return out


def _question_info(qlookup: Dict[str, dict], qid: str, parent: str = "") -> Dict[str, Any]:
    q = qlookup.get(str(qid)) or (qlookup.get(str(parent)) if parent else None) or {}
    return {
        "id": str(q.get("id") or qid),
        "text": str(q.get("text") or ""),
        "topic": str(q.get("topic") or "general"),
        "difficulty": int(q.get("difficulty") or 0) or None,
        "type": str(q.get("type") or ""),
        "known": bool(q),
    }


def _local_date(ts: Optional[datetime], tz_offset_minutes: int):
    if ts is None:
        return None
    return (ts + timedelta(minutes=tz_offset_minutes)).date()


def _streak(days: Iterable, today) -> Tuple[int, int]:
    """Return (current streak, longest streak) over a set of activity dates."""
    day_set = set(days)
    if not day_set:
        return 0, 0
    ordered = sorted(day_set)
    longest = run = 1
    for prev, cur in zip(ordered, ordered[1:]):
        run = run + 1 if (cur - prev).days == 1 else 1
        longest = max(longest, run)
    # current streak counts back from today, or from yesterday if nothing yet today
    anchor = today if today in day_set else (today - timedelta(days=1))
    current = 0
    d = anchor
    while d in day_set:
        current += 1
        d -= timedelta(days=1)
    return current, longest


# ── core aggregations ────────────────────────────────────────────────────────

def _topic_stats(primary: List[Dict[str, Any]], qlookup: Dict[str, dict]) -> List[Dict[str, Any]]:
    by_topic: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for a in primary:
        if a["score"] is None:
            continue
        info = _question_info(qlookup, a["question_id"], a.get("parent_question_id") or "")
        by_topic[info["topic"]].append(a)
    stats = []
    for topic, items in by_topic.items():
        scores = [a["score"] for a in items]
        avg = _mean(scores)
        entry = {
            "topic": topic,
            "label": pretty_topic(topic),
            "attempts": len(items),
            "questions": len({a["question_id"] for a in items}),
            "avg_score": avg,
            "best_score": round(max(scores), 4),
            "last_score": round(scores[-1], 4),
            "last_at": items[-1]["created_at"],
            "band": band_for(avg),
            "low_data": len(items) < LOW_DATA_BELOW,
            "trend": "insufficient_data",
        }
        if len(items) >= DECLINE_MIN_ATTEMPTS:
            half = len(scores) // 2
            earlier, recent = _mean(scores[:half]), _mean(scores[half:])
            delta = round(recent - earlier, 4)
            entry["trend_delta"] = delta
            entry["trend"] = "declining" if delta <= -DECLINE_DROP else ("improving" if delta >= DECLINE_DROP else "stable")
        stats.append(entry)
    stats.sort(key=lambda t: (t["avg_score"] if t["avg_score"] is not None else 1.0))
    return stats


def _session_rows(sessions: List[Dict[str, Any]], attempts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    per_session: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for a in attempts:
        if a["attempt_type"] == "primary" and a["score"] is not None:
            per_session[a["session_id"]].append(a)
    rows = []
    for s in sessions:
        items = per_session.get(s["id"], [])
        scores = [a["score"] for a in items]
        rows.append({
            "id": s["id"],
            "created_at": s["created_at"],
            "mode": s["interview_mode"],
            "status": s["status"],
            "topics": list(s["c_topics"]) + list(s["dsa_topics"]),
            "planned_questions": s["num_questions"],
            "answered": len(items),
            "avg_score": _mean(scores),
            "stored_overall_score": s["overall_score"],
            "has_activity": bool(items),
        })
    return rows


def _next_steps(topic_stats: List[Dict[str, Any]], weak: Dict[str, Any], retry_candidates: List[Dict[str, Any]],
                has_history: bool) -> List[Dict[str, Any]]:
    steps: List[Dict[str, Any]] = []
    if not has_history:
        steps.append({"kind": "start", "title": "Complete your first practice session",
                      "detail": "Your dashboard fills in after you answer a few questions."})
        return steps
    needs = [t for t in topic_stats if t["band"] == "needs_work" and t["attempts"] >= MIN_OBS_FOR_CLASS]
    if needs:
        t = needs[0]
        steps.append({"kind": "practice_topics", "title": f"Practice {t['label']}",
                      "detail": f"Average {round(t['avg_score'] * 100)}% over {t['attempts']} attempts.",
                      "topics": [t["topic"]]})
    if weak["revise_first"]:
        c = weak["revise_first"][0]
        steps.append({"kind": "weakness_map", "title": "Review your most-missed concept",
                      "detail": f"“{c['concept'][:90]}” was missed in {c['missing'] + c['incorrect']} of {c['observations']} observations."})
    if retry_candidates:
        r = retry_candidates[0]
        steps.append({"kind": "compare", "question_id": r["question_id"], "title": "Retry a question you have already attempted",
                      "detail": f"Best so far {round(r['best_score'] * 100)}% on “{r['text'][:80]}”."})
    if not steps:
        steps.append({"kind": "start", "title": "Keep practicing",
                      "detail": "No clear weak area yet. Try a new mix of topics."})
    return steps[:3]


def _comparable(primary_all: List[Dict[str, Any]], qlookup: Dict[str, dict]) -> List[Dict[str, Any]]:
    by_q: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for a in primary_all:
        if a["score"] is not None:
            by_q[a["question_id"]].append(a)
    out = []
    for qid, items in by_q.items():
        if len(items) < 2:
            continue
        info = _question_info(qlookup, qid)
        scores = [a["score"] for a in items]
        out.append({
            "question_id": qid, "text": info["text"], "topic": info["topic"], "attempts": len(items),
            "first_score": round(scores[0], 4), "latest_score": round(scores[-1], 4),
            "best_score": round(max(scores), 4), "delta": round(scores[-1] - scores[0], 4),
        })
    out.sort(key=lambda r: (-r["attempts"], r["latest_score"]))
    return out


def build_weakness_map(candidate_id: str, qlookup: Dict[str, dict], db_path: Optional[Path | str] = None,
                       attempts: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    attempts = attempts if attempts is not None else _load_attempts(candidate_id, db_path)
    verbal = [a for a in attempts if a["answer_type"] != "code"]
    stats: Dict[str, Dict[str, Any]] = {}
    mis: Dict[str, Dict[str, Any]] = {}

    def entry(store, key, display):
        e = store.get(key)
        if e is None:
            e = {"concept": display, "covered": 0, "missing": 0, "incorrect": 0, "recent": [],
                 "questions": Counter(), "last_seen": None, "texts": Counter()}
            store[key] = e
        e["texts"][display] += 1
        return e

    for a in verbal:
        qid = a.get("parent_question_id") or a["question_id"]
        for kind, items in (("covered", a["covered_concepts"]), ("missing", a["missing_concepts"])):
            for text in items:
                if not str(text).strip():
                    continue
                e = entry(stats, _norm(text), str(text).strip())
                e[kind] += 1
                e["recent"].append("c" if kind == "covered" else "m")
                e["questions"][qid] += 1
                e["last_seen"] = a["created_at"]
        for text in a["incorrect_claims"]:
            if not str(text).strip():
                continue
            e = entry(mis, _norm(text), str(text).strip())
            e["incorrect"] += 1
            e["questions"][qid] += 1
            e["last_seen"] = a["created_at"]

    concepts: List[Dict[str, Any]] = []
    for key, e in stats.items():
        obs = e["covered"] + e["missing"]
        rate = e["covered"] / obs if obs else None
        if obs < MIN_OBS_FOR_CLASS:
            cls = "not_enough_data"
        elif rate >= 0.80:
            cls = "strong"
        elif rate <= 0.34:
            cls = "frequently_missed"
        else:
            cls = "partial"
        top_q = [q for q, _ in e["questions"].most_common(4)]
        related = []
        for qid in top_q:
            info = _question_info(qlookup, qid)
            q_scores = [a["score"] for a in attempts if (a.get("parent_question_id") or a["question_id"]) == qid
                        and a["attempt_type"] == "primary" and a["score"] is not None]
            related.append({"question_id": qid, "text": info["text"], "topic": info["topic"],
                            "difficulty": info["difficulty"], "attempts": len(q_scores),
                            "best_score": round(max(q_scores), 4) if q_scores else None})
        primary_q = related[0] if related else None
        q_full = qlookup.get(str(primary_q["question_id"])) if primary_q else None
        card = None
        if q_full and cls in ("frequently_missed", "partial"):
            reference = str(q_full.get("reference_answer") or "").strip()
            mistakes = [str(m) for m in (q_full.get("common_mistakes") or []) if str(m).strip()][:3]
            card = {
                "concept": e["texts"].most_common(1)[0][0],
                "recall_prompt": q_full.get("text", ""),
                "reference": reference[:480],
                "common_mistakes": mistakes,
                "source": "question rubric",
                "question_id": primary_q["question_id"],
            }
        concepts.append({
            "key": key,
            "concept": e["texts"].most_common(1)[0][0],
            "classification": cls,
            "covered": e["covered"], "missing": e["missing"], "incorrect": 0,
            "observations": obs,
            "coverage_rate": round(rate, 3) if rate is not None else None,
            "low_data": obs < LOW_DATA_BELOW,
            "recent": e["recent"][-6:],
            "last_seen": e["last_seen"],
            "topic": related[0]["topic"] if related else "general",
            "related_questions": related,
            "revision_card": card,
        })
    concepts.sort(key=lambda c: (c["classification"] != "frequently_missed", -(c["missing"]), c["concept"]))

    misconceptions = []
    for key, e in mis.items():
        qid = e["questions"].most_common(1)[0][0] if e["questions"] else ""
        info = _question_info(qlookup, qid) if qid else {"topic": "general", "text": ""}
        misconceptions.append({"claim": e["concept"], "times": e["incorrect"], "last_seen": e["last_seen"],
                               "topic": info["topic"], "question_id": qid, "question_text": info["text"]})
    misconceptions.sort(key=lambda m: (-m["times"], m["claim"]))

    primary = [a for a in attempts if a["attempt_type"] == "primary"]
    topic_stats = _topic_stats(primary, qlookup)
    declining = [t for t in topic_stats if t["trend"] == "declining"]
    revise_first = [c for c in concepts if c["classification"] == "frequently_missed"][:5]
    counts = Counter(c["classification"] for c in concepts)
    return {
        "candidate_id": candidate_id,
        "summary": {
            "concepts_tracked": len(concepts),
            "strong": counts.get("strong", 0),
            "partial": counts.get("partial", 0),
            "frequently_missed": counts.get("frequently_missed", 0),
            "not_enough_data": counts.get("not_enough_data", 0),
            "repeated_misconceptions": sum(1 for m in misconceptions if m["times"] >= 2),
            "verbal_attempts_used": len(verbal),
            "code_attempts_excluded": len([a for a in attempts if a["answer_type"] == "code"]),
        },
        "concepts": concepts[:150],
        "misconceptions": misconceptions[:30],
        "declining_topics": declining,
        "topic_stats": topic_stats,
        "revise_first": revise_first,
        "notes": [
            "Counts come from the evaluator's covered / missing concept lists for your spoken answers.",
            f"A concept is classified only after {MIN_OBS_FOR_CLASS}+ observations; fewer than {LOW_DATA_BELOW} is flagged as low data.",
            "Code answers are excluded because their stored 'concepts' are test results, not conceptual coverage.",
        ],
    }


def build_dashboard(candidate_id: str, qlookup: Dict[str, dict], db_path: Optional[Path | str] = None,
                    tz_offset_minutes: int = 0, now: Optional[datetime] = None) -> Dict[str, Any]:
    attempts = _load_attempts(candidate_id, db_path)
    sessions = _load_sessions(candidate_id, db_path)
    now = now or datetime.now(UTC)
    today = _local_date(now, tz_offset_minutes)

    primary = [a for a in attempts if a["attempt_type"] == "primary"]
    scored_primary = [a for a in primary if a["score"] is not None]
    session_rows = _session_rows(sessions, attempts)
    active_sessions = [s for s in session_rows if s["has_activity"]]
    trend = [{"session_id": s["id"], "date": s["created_at"], "avg_score": s["avg_score"], "answered": s["answered"]}
             for s in active_sessions]

    # recent vs earlier (windows of up to 3 sessions each)
    comparison = None
    if len(active_sessions) >= 2:
        k = min(3, len(active_sessions) // 2)
        recent = active_sessions[-k:]
        earlier = active_sessions[-2 * k:-k]
        e_avg, r_avg = _mean([s["avg_score"] for s in earlier]), _mean([s["avg_score"] for s in recent])
        if e_avg is not None and r_avg is not None and earlier:
            comparison = {"earlier_avg": e_avg, "recent_avg": r_avg, "delta": round(r_avg - e_avg, 4),
                          "earlier_sessions": len(earlier), "recent_sessions": len(recent)}

    activity_days = {_local_date(a["ts"], tz_offset_minutes) for a in attempts if a["ts"]}
    activity_days.discard(None)
    current_streak, longest_streak = _streak(activity_days, today)
    week_start = today - timedelta(days=6)
    week_attempts = [a for a in attempts if a["ts"] and _local_date(a["ts"], tz_offset_minutes) >= week_start]
    week_sessions = {a["session_id"] for a in week_attempts if a["attempt_type"] == "primary"}
    week_days = sorted({_local_date(a["ts"], tz_offset_minutes) for a in week_attempts})

    topic_stats = _topic_stats(primary, qlookup)
    weak = build_weakness_map(candidate_id, qlookup, db_path, attempts=attempts)
    comparable = _comparable(primary, qlookup)

    # difficulty distribution
    by_diff: Dict[int, List[float]] = defaultdict(list)
    for a in scored_primary:
        d = _question_info(qlookup, a["question_id"], a.get("parent_question_id") or "")["difficulty"]
        if d:
            by_diff[d].append(a["score"])
    difficulty = [{"level": lvl, "attempts": len(v), "avg_score": _mean(v)} for lvl, v in sorted(by_diff.items())]

    last_cfg = None
    if sessions:
        s = sessions[-1]
        last_cfg = {"c_topics": s["c_topics"], "dsa_topics": s["dsa_topics"], "interview_mode": s["interview_mode"],
                    "duration_minutes": s["duration_minutes"], "num_questions": s["num_questions"]}

    all_scores = [a["score"] for a in scored_primary]
    return {
        "candidate_id": candidate_id,
        "generated_at": now.isoformat(),
        "has_history": bool(attempts),
        "totals": {
            "attempts": len(attempts),
            "primary_attempts": len(primary),
            "questions_attempted": len({a["question_id"] for a in primary}),
            "sessions_started": len(sessions),
            "sessions_with_answers": len(active_sessions),
            "sessions_completed": len([s for s in session_rows if s["status"] == "completed"]),
            "avg_score": _mean(all_scores),
            "best_score": round(max(all_scores), 4) if all_scores else None,
            "followups_answered": len([a for a in attempts if a["attempt_type"] == "followup"]),
        },
        "streak": {"current_days": current_streak, "longest_days": longest_streak,
                   "last_active": max(activity_days).isoformat() if activity_days else None},
        "week": {"sessions": len(week_sessions), "attempts": len([a for a in week_attempts if a["attempt_type"] == "primary"]),
                 "active_days": len(week_days), "window_start": week_start.isoformat(), "window_end": today.isoformat()},
        "score_trend": trend,
        "recent_vs_earlier": comparison,
        "topics": topic_stats,
        "difficulty": difficulty,
        "recent_sessions": list(reversed(session_rows))[:8],
        "weakness_summary": weak["summary"],
        "revise_first": weak["revise_first"][:3],
        "declining_topics": weak["declining_topics"],
        "comparable_questions": comparable[:8],
        "next_steps": _next_steps(topic_stats, weak, comparable, bool(attempts)),
        "last_session_config": last_cfg,
        "notes": ["Dates use your browser's UTC offset.",
                  "Averages use evaluator-validated scores for primary answers; follow-ups are counted separately."],
    }


def build_analytics(candidate_id: str, qlookup: Dict[str, dict], db_path: Optional[Path | str] = None,
                    tz_offset_minutes: int = 0) -> Dict[str, Any]:
    """Detailed analytics: per-attempt timeline, topic mastery, difficulty stats, comparable questions."""
    base = build_dashboard(candidate_id, qlookup, db_path, tz_offset_minutes)
    attempts = _load_attempts(candidate_id, db_path)
    timeline = []
    for a in attempts:
        if a["attempt_type"] != "primary" or a["score"] is None:
            continue
        info = _question_info(qlookup, a["question_id"], a.get("parent_question_id") or "")
        timeline.append({"date": a["created_at"], "score": round(a["score"], 4), "question_id": a["question_id"],
                         "topic": info["topic"], "difficulty": info["difficulty"], "answer_type": a["answer_type"]})
    base["attempt_timeline"] = timeline
    by_type: Dict[str, List[float]] = defaultdict(list)
    for t in timeline:
        by_type[t["answer_type"] or "verbal"].append(t["score"])
    base["by_answer_type"] = [{"answer_type": k, "attempts": len(v), "avg_score": _mean(v)} for k, v in by_type.items()]
    return base


def build_compare(candidate_id: str, question_id: str, qlookup: Dict[str, dict],
                  db_path: Optional[Path | str] = None) -> Dict[str, Any]:
    attempts = [a for a in _load_attempts(candidate_id, db_path)
                if a["question_id"] == str(question_id) and a["attempt_type"] == "primary"]
    info = _question_info(qlookup, question_id)
    items = []
    for i, a in enumerate(attempts, start=1):
        items.append({
            "n": i, "attempt_number": a["attempt_number"], "created_at": a["created_at"], "session_id": a["session_id"],
            "score": round(a["score"], 4) if a["score"] is not None else None,
            "answer_type": a["answer_type"],
            "answer": (a["transcript"] or a["code_submitted"] or "")[:4000],
            "covered": a["covered_concepts"], "missing": a["missing_concepts"], "incorrect": a["incorrect_claims"],
        })
    summary: Dict[str, Any] = {"attempts": len(items)}
    if len(items) >= 2:
        first, last = items[0], items[-1]
        prior = items[:-1]
        prior_missing = {_norm(m) for it in prior for m in it["missing"]}
        last_missing = {_norm(m) for m in last["missing"]}
        last_covered = {_norm(c) for c in last["covered"]}
        recovered = [c for c in last["covered"] if _norm(c) in prior_missing]
        miss_counts = Counter(_norm(m) for it in items for m in it["missing"])
        repeated = [m for m in last["missing"] if miss_counts[_norm(m)] >= 2]
        newly_missed = [m for m in last["missing"] if _norm(m) not in prior_missing
                        and _norm(m) in {_norm(c) for it in prior for c in it["covered"]}]
        scores = [it["score"] for it in items if it["score"] is not None]
        summary.update({
            "first_score": first["score"], "latest_score": last["score"],
            "best_score": round(max(scores), 4) if scores else None,
            "delta": round(last["score"] - first["score"], 4) if (last["score"] is not None and first["score"] is not None) else None,
            "recovered_concepts": recovered, "repeated_missing": repeated, "newly_missed": newly_missed,
            "still_missing": [m for m in last["missing"]],
            "answer_words_first": len((first["answer"] or "").split()), "answer_words_latest": len((last["answer"] or "").split()),
        })
    return {"candidate_id": candidate_id, "question": info, "attempts": items, "summary": summary}
