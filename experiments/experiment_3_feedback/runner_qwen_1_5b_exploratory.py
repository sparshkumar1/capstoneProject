"""
runner_qwen_1_5b_exploratory.py — Optional Exploratory Lightweight Qwen2.5-1.5B Deployment Evaluation
Stage 16.4 Optional Exploratory Runner.

Classification: EXPLORATORY / SUPPLEMENTARY (NOT a replacement for EXP-3 Qwen-7B).
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["OMP_NUM_THREADS"] = "12"
os.environ["MKL_NUM_THREADS"] = "12"

import argparse
import csv
import hashlib
import json
import math
import re
import sys
import time
from datetime import datetime
from pathlib import Path
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

torch.set_num_threads(12)

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.evaluator.app import evaluate

SNAPSHOT_PATH = os.path.abspath(
    "models/qwen_1b/models--Qwen--Qwen2.5-1.5B-Instruct/snapshots/989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
)


def _compute_sha256(filepath: Path) -> str:
    if not filepath.exists():
        return "MISSING"
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _extract_tokens(text: str) -> set:
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    stop_words = {"the", "and", "for", "that", "this", "with", "from", "you", "your", "are", "have", "can", "use"}
    return set(w for w in words if w not in stop_words)


def _bootstrap_ci(data, num_resamples=10000, alpha=0.05):
    if len(data) == 0:
        return [0.0, 0.0]
    rng = np.random.RandomState(42)
    means = [np.mean(rng.choice(data, size=len(data), replace=True)) for _ in range(num_resamples)]
    low = np.percentile(means, 100 * (alpha / 2))
    high = np.percentile(means, 100 * (1 - alpha / 2))
    return [round(float(low), 4), round(float(high), 4)]


def run_exploratory_1_5b(config_path: str, output_dir: str):
    start_time = time.time()

    # Load rubrics lookup
    rubrics_path = ROOT / "data/rubrics/rubrics_final_clean.json"
    with open(rubrics_path, "r", encoding="utf-8") as f:
        rubrics_list = json.load(f)
    rubrics_by_qid = {str(r.get("qid")): r for r in rubrics_list}

    # Load 20-sample pilot benchmark answers
    ratings_path = ROOT / "ablation/results/ratings_averaged.csv"
    eval_items = []
    with open(ratings_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            qid_str = str(row["qid"]).strip()
            rub = rubrics_by_qid.get(qid_str, {})
            eval_items.append({
                "item_id": f"pilot_{idx+1}_qid{qid_str}",
                "qid": qid_str,
                "question": row["question"],
                "answer": row["answer"],
                "human_score": float(row["human_score"]),
                "rubric": rub
            })

    print(f"[Exploratory-1.5B] Loading Tokenizer from {SNAPSHOT_PATH}...")
    tokenizer = AutoTokenizer.from_pretrained(SNAPSHOT_PATH, local_files_only=True)

    print("[Exploratory-1.5B] Loading Model Qwen2.5-1.5B-Instruct in bfloat16 on CPU...")
    model = AutoModelForCausalLM.from_pretrained(
        SNAPSHOT_PATH,
        torch_dtype=torch.bfloat16,
        low_cpu_mem_usage=True,
        local_files_only=True,
    )
    model.eval()
    model_load_time = round(time.time() - start_time, 2)
    print(f"[Exploratory-1.5B] Model loaded in {model_load_time}s.")

    evaluations = []

    for idx, item in enumerate(eval_items):
        item_start = time.time()
        qid = item["item_id"]
        qn_text = item["question"]
        cand_text = item["answer"]
        rubric = item["rubric"]
        cand_tokens = _extract_tokens(cand_text)

        eval_res = evaluate(qn_text, cand_text, rubric) if cand_text.strip() else {
            "final_score": 0.0, "covered_concepts": [], "missing_concepts": ["core algorithmic logic"], "incorrect_claims": []
        }
        sc = eval_res["final_score"]
        covered = eval_res.get("covered_concepts", [])
        missing = eval_res.get("missing_concepts", []) or eval_res.get("concepts_missed", [])
        incorrect = eval_res.get("incorrect_claims", [])

        prompt = (
            f"<|im_start|>system\n"
            f"You are an expert technical interviewer. Provide 1 concise formative feedback sentence and 1 actionable improvement step based on the candidate answer and concept breakdown.<|im_end|>\n"
            f"<|im_start|>user\n"
            f"Question: {qn_text}\n"
            f"Answer: \"{cand_text}\"\n"
            f"Score: {sc:.2f}/1.00\n"
            f"Covered: {', '.join(covered) if covered else 'None'}\n"
            f"Missed: {', '.join(missing) if missing else 'None'}\n"
            f"Feedback:<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

        inputs = tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=36,
                do_sample=False,
                temperature=None,
                top_p=None,
                use_cache=True,
            )
        generated_feedback = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
        item_runtime = round(time.time() - item_start, 2)

        # Compute metrics
        fb_tokens = _extract_tokens(generated_feedback)
        grounding_ratio = len(fb_tokens & cand_tokens) / max(len(cand_tokens), 1)
        gap_cov = 1.0 if not missing else (1.0 if any(m.lower() in generated_feedback.lower() for m in missing) else 0.5)

        actionability_count = len(re.findall(r'(?:^\s*[-*•\d+.]|\b(?:step|practice|review|implement|ensure|use|focus|consider|add)\b)', generated_feedback, re.IGNORECASE | re.MULTILINE))
        actionability_count = max(1, min(actionability_count, 5))

        evaluations.append({
            "run_id": f"EXP3_exploratory_1_5b_{qid}",
            "item_id": qid,
            "condition_id": "qwen_1_5b_exploratory_feedback",
            "score": sc,
            "transcript": cand_text,
            "evaluator_evidence": {
                "final_score": sc,
                "covered_concepts": covered,
                "missing_concepts": missing,
                "incorrect_claims": incorrect
            },
            "generated_feedback": generated_feedback,
            "runtime_seconds": item_runtime,
            "grounding_ratio": round(float(grounding_ratio), 4),
            "gap_coverage": round(float(gap_cov), 4),
            "actionability_count": int(actionability_count),
            "status": "COMPLETED",
            "errors": None
        })

        print(f"[Exploratory-1.5B] ({idx+1}/20) Evaluated {qid} in {item_runtime}s (Grounding: {grounding_ratio:.4f}, Gap: {gap_cov:.2f}, Act: {actionability_count})")

    elapsed_total = round(time.time() - start_time, 2)

    # Compute aggregate metrics
    grs = [e["grounding_ratio"] for e in evaluations]
    gaps = [e["gap_coverage"] for e in evaluations]
    acts = [e["actionability_count"] for e in evaluations]
    runtimes = [e["runtime_seconds"] for e in evaluations]

    exploratory_payload = {
        "experiment_id": "EXP-3-EXPLORATORY",
        "classification": "EXPLORATORY / SUPPLEMENTARY (NOT a replacement for EXP-3 Qwen-7B)",
        "model_name": "Qwen/Qwen2.5-1.5B-Instruct",
        "model_revision": "989aa7980e4cf806f80c7fef2b1adb7bc71aa306",
        "timestamp": datetime.utcnow().isoformat(),
        "runtime_seconds": elapsed_total,
        "mean_inference_latency_seconds": round(float(np.mean(runtimes)), 2),
        "device": "cpu",
        "dtype": "bfloat16",
        "threads": 12,
        "provenance": {
            "ratings_averaged_sha256": _compute_sha256(ratings_path),
            "rubrics_sha256": _compute_sha256(rubrics_path),
            "model_snapshot_path": SNAPSHOT_PATH,
        },
        "total_samples": len(evaluations),
        "aggregated_metrics": {
            "mean_grounding_ratio": round(float(np.mean(grs)), 4),
            "grounding_ci_95": _bootstrap_ci(grs),
            "mean_gap_coverage": round(float(np.mean(gaps)), 4),
            "mean_actionability_count": round(float(np.mean(acts)), 4),
            "mean_latency_seconds": round(float(np.mean(runtimes)), 2),
        },
        "evaluations": evaluations,
        "status": "COMPLETED"
    }

    raw_path = ROOT / "research/results/raw/experiment_3_qwen_1_5b_exploratory_raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(exploratory_payload, f, indent=2)

    proc_path = ROOT / "research/results/processed/experiment_3_qwen_1_5b_exploratory_analysis.csv"
    with open(proc_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["run_id", "item_id", "score", "grounding_ratio", "gap_coverage", "actionability_count", "runtime_seconds", "generated_feedback"])
        for e in evaluations:
            w.writerow([e["run_id"], e["item_id"], e["score"], e["grounding_ratio"], e["gap_coverage"], e["actionability_count"], e["runtime_seconds"], e["generated_feedback"]])

    print(f"[Exploratory-1.5B] Saved raw results to {raw_path} and analysis to {proc_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="experiments/experiment_3_feedback/config.json")
    parser.add_argument("--out", default="experiments/experiment_3_feedback")
    args = parser.parse_args()
    run_exploratory_1_5b(args.config, args.out)
