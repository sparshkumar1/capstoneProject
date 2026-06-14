"""Generate per-topic analysis tables from averaged human ratings.

This script joins the question bank with the averaged rater CSV and writes a
compact markdown report plus a machine-readable JSON summary.

Usage:
  python ablation/topic_analysis_tables.py
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
RESULTS = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Question:
    qid: str
    topic: str
    difficulty: float
    question_text: str


def _load_questions() -> dict[str, Question]:
    questions_path = REPO_ROOT / "data" / "questions" / "qns.json"
    with questions_path.open(encoding="utf-8") as f:
        raw_items = json.load(f)
    questions: dict[str, Question] = {}
    for item in raw_items:
        qid = str(item.get("qid", "")).strip()
        if not qid:
            continue
        questions[qid] = Question(
            qid=qid,
            topic=str(item.get("topic", "Unknown") or "Unknown"),
            difficulty=float(item.get("difficulty", 0.0) or 0.0),
            question_text=str(item.get("question_text", "") or ""),
        )
    return questions


def _load_ratings() -> list[dict[str, str]]:
    for candidate in [RESULTS / "ratings_averaged_real.csv", RESULTS / "ratings_averaged.csv"]:
        if candidate.exists():
            with candidate.open(newline="", encoding="utf-8") as f:
                return list(csv.DictReader(f))
    raise SystemExit("No averaged ratings file found. Run the human-eval pipeline first.")


def _parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _truncate(text: str, limit: int = 88) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _qid_key(value: str) -> tuple[int, str]:
    if value.isdigit():
        return (0, f"{int(value):08d}")
    return (1, value)


def main() -> None:
    questions = _load_questions()
    ratings = _load_ratings()

    topic_rows: dict[str, list[dict[str, object]]] = defaultdict(list)
    qid_rows: dict[str, list[dict[str, object]]] = defaultdict(list)

    for row in ratings:
        qid = str(row.get("qid", "")).strip()
        question = questions.get(qid)
        if question is None:
            continue

        human_score = _parse_float(row.get("human_score"))
        system_score = _parse_float(row.get("system_score"))
        if human_score is None and system_score is None:
            continue

        entry = {
            "qid": qid,
            "topic": question.topic,
            "difficulty": question.difficulty,
            "question_text": question.question_text,
            "human_score": human_score,
            "system_score": system_score,
        }
        topic_rows[question.topic].append(entry)
        qid_rows[qid].append(entry)

    summary_topics: list[dict[str, object]] = []
    for topic in sorted(topic_rows):
        items = topic_rows[topic]
        per_question = []
        qids = sorted({str(item["qid"]) for item in items}, key=_qid_key)
        for qid in qids:
            q_items = qid_rows[qid]
            question = questions[qid]
            human_scores = [float(item["human_score"]) for item in q_items if item["human_score"] is not None]
            system_scores = [float(item["system_score"]) for item in q_items if item["system_score"] is not None]
            per_question.append(
                {
                    "qid": qid,
                    "difficulty": question.difficulty,
                    "human_score": mean(human_scores) if human_scores else None,
                    "system_score": mean(system_scores) if system_scores else None,
                    "gap": (mean(system_scores) - mean(human_scores)) if human_scores and system_scores else None,
                    "question_text": question.question_text,
                }
            )

        human_values = [float(item["human_score"]) for item in items if item["human_score"] is not None]
        system_values = [float(item["system_score"]) for item in items if item["system_score"] is not None]
        summary_topics.append(
            {
                "topic": topic,
                "questions": len(per_question),
                "ratings": len(items),
                "avg_difficulty": mean([questions[str(item["qid"])].difficulty for item in items]),
                "avg_human_score": mean(human_values) if human_values else None,
                "avg_system_score": mean(system_values) if system_values else None,
                "avg_gap": (mean(system_values) - mean(human_values)) if human_values and system_values else None,
                "questions_detail": per_question,
            }
        )

    payload = {
        "source": "ablation/results/ratings_averaged_real.csv",
        "question_bank": "data/questions/qns.json",
        "topics": summary_topics,
    }
    (RESULTS / "topic_analysis_summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = [
        "# Per-topic analysis tables",
        "",
        f"Source ratings: `{payload['source']}`",
        "",
        "## Topic summary",
        "",
        "| Topic | Questions | Ratings | Avg difficulty | Avg human | Avg system | Avg gap |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for topic in summary_topics:
        md_lines.append(
            "| {topic} | {questions} | {ratings} | {difficulty:.2f} | {human} | {system} | {gap} |".format(
                topic=topic["topic"],
                questions=topic["questions"],
                ratings=topic["ratings"],
                difficulty=float(topic["avg_difficulty"]),
                human=(f"{float(topic['avg_human_score']):.3f}" if topic["avg_human_score"] is not None else "n/a"),
                system=(f"{float(topic['avg_system_score']):.3f}" if topic["avg_system_score"] is not None else "n/a"),
                gap=(f"{float(topic['avg_gap']):+.3f}" if topic["avg_gap"] is not None else "n/a"),
            )
        )

    for topic in summary_topics:
        md_lines += [
            "",
            f"## {topic['topic']}",
            "",
            "| QID | Difficulty | Avg human | Avg system | Gap | Question |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
        for item in topic["questions_detail"]:
            md_lines.append(
                "| {qid} | {difficulty:.2f} | {human} | {system} | {gap} | {question} |".format(
                    qid=item["qid"],
                    difficulty=float(item["difficulty"]),
                    human=(f"{float(item['human_score']):.3f}" if item["human_score"] is not None else "n/a"),
                    system=(f"{float(item['system_score']):.3f}" if item["system_score"] is not None else "n/a"),
                    gap=(f"{float(item['gap']):+.3f}" if item["gap"] is not None else "n/a"),
                    question=_truncate(str(item["question_text"])),
                )
            )

    (RESULTS / "topic_analysis_summary.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"Wrote {RESULTS / 'topic_analysis_summary.md'}")
    print(f"Wrote {RESULTS / 'topic_analysis_summary.json'}")


if __name__ == "__main__":
    main()