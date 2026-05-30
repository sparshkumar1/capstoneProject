"""Simple Streamlit app to collect human ratings for the ablation answers.

Run:
  pip install streamlit
  streamlit run ablation/web_rater.py -- --answers ablation/data/ablation_answers.json --out ablation/results/ratings_rater_streamlit.csv

Features:
- Loads JSON of Q&A pairs (same format as `human_eval_harness.py`).
- Presents question and answer, accepts a 0–10 rating or skip.
- Appends ratings to CSV and shows progress.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import streamlit as st


def load_items(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "question_results" in data:
        items = []
        for qr in data["question_results"]:
            items.append({
                "qid": qr.get("question_id", ""),
                "question_text": qr.get("question_text", qr.get("question", "")),
                "answer": qr.get("transcript", qr.get("answer", "")),
                "system_score": qr.get("score", qr.get("final_score", None)),
            })
        return items
    raise ValueError(f"Unrecognised JSON format: {path}")


def main(answers_path: str, out_path: str):
    items = load_items(answers_path)
    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Load already-saved rows to support resume
    done_keys = set()
    if out_file.exists():
        with open(out_file, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                done_keys.add(r["qid"] + "|" + r["answer"][:40])

    todo = [it for it in items if (it.get("qid", "") + "|" + it.get("answer", "")[:40]) not in done_keys]

    st.title("PrepAIred — Web Rater")
    st.write(f"{len(todo)} items to rate (resume mode: {len(done_keys)} already done)")

    index = st.session_state.get("index", 0)

    if "index" not in st.session_state:
        st.session_state.index = 0

    if index >= len(todo):
        st.success("All items rated — thank you!")
        st.stop()

    item = todo[index]
    st.subheader(f"[{index+1}/{len(todo)}] QID: {item.get('qid','?')}")
    st.markdown("**Question:**")
    st.write(item.get("question_text", "(no text)"))
    st.markdown("**Answer:**")
    st.write(item.get("answer", "(no answer)"))

    rating = st.slider("Your rating (0 = worst, 10 = expert)", 0.0, 10.0, 5.0, step=0.5)
    skip = st.checkbox("Skip this item")

    cols = st.columns(3)
    if cols[0].button("Save & Next"):
        human = None if skip else rating
        row = {
            "qid": item.get("qid", ""),
            "question": item.get("question_text", "")[:120],
            "answer": item.get("answer", "")[:200],
            "system_score": f"{float(item.get('system_score')):.4f}" if item.get("system_score") is not None else "",
            "human_score": f"{(human/10):.4f}" if human is not None else "",
        }
        write_header = not out_file.exists()
        with open(out_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["qid", "question", "answer", "system_score", "human_score"])
            if write_header:
                writer.writeheader()
            writer.writerow(row)
        st.success("Saved")
        st.session_state.index += 1
        st.experimental_rerun()

    if cols[1].button("Previous"):
        if st.session_state.index > 0:
            st.session_state.index -= 1
            st.experimental_rerun()

    if cols[2].button("Quit (save progress)"):
        st.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Web rater")
    parser.add_argument("--answers", default="ablation/data/ablation_answers.json")
    parser.add_argument("--out", default="ablation/results/ratings_rater_streamlit.csv")
    args, _ = parser.parse_known_args()
    main(args.answers, args.out)
