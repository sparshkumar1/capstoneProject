import csv
import json

with open("data/rubrics/rubrics_final_clean.json", "r", encoding="utf-8") as f:
    rubrics = {str(r.get("qid")): r for r in json.load(f)}

with open("ablation/results/ratings_averaged.csv", "r", encoding="utf-8") as f:
    items = list(csv.DictReader(f))

print(f"Total items: {len(items)}")
benchmark_data = []
for i, it in enumerate(items):
    qid = str(it["qid"]).strip()
    rub = rubrics.get(qid, {})
    benchmark_data.append({
        "item_id": f"pilot_{i+1}_qid{qid}",
        "qid": qid,
        "question": it["question"],
        "answer": it["answer"],
        "human_score": float(it["human_score"]),
        "rubric": rub
    })
    print(f"Item {i+1:02d}: QID={qid:3s} | Question={it['question'][:40]} | Concepts={len(rub.get('key_concepts', []))}")

with open("experiments/experiment_3_feedback/benchmark_items_dataset.json", "w", encoding="utf-8") as f:
    json.dump(benchmark_data, f, indent=2)

print("Saved benchmark items to experiments/experiment_3_feedback/benchmark_items_dataset.json")
