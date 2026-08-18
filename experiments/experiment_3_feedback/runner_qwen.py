"""
runner_qwen.py — Dedicated Execution Runner for EXP-3 Qwen2.5-7B-Instruct Condition
Stage 16.3 Protocol Execution.
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

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

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.evaluator.app import evaluate

SNAPSHOT_PATH = os.path.abspath(
    "models/qwen_7b/models--Qwen--Qwen2.5-7B-Instruct/snapshots/a09a35458c702b33eeacc393d103063234e8bc28"
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


def run_qwen_condition(config_path: str, output_dir: str):
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

    print(f"[EXP-3-Qwen] Loading Qwen2.5-7B-Instruct Tokenizer from {SNAPSHOT_PATH}...")
    tokenizer = AutoTokenizer.from_pretrained(SNAPSHOT_PATH, local_files_only=True)

    print("[EXP-3-Qwen] Loading Qwen2.5-7B-Instruct Model in bfloat16 on CPU...")
    model = AutoModelForCausalLM.from_pretrained(
        SNAPSHOT_PATH,
        torch_dtype=torch.bfloat16,
        low_cpu_mem_usage=True,
        local_files_only=True,
    )
    model.eval()
    model_load_time = round(time.time() - start_time, 2)
    print(f"[EXP-3-Qwen] Model loaded in {model_load_time}s.")

    qwen_evaluations = []

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
            f"You are an expert technical interviewer. Provide grounded formative feedback and actionable remediation based on the candidate's exact answer and evaluation breakdown.<|im_end|>\n"
            f"<|im_start|>user\n"
            f"Question: {qn_text}\n"
            f"Candidate Answer: \"{cand_text}\"\n"
            f"Score: {sc:.2f}/1.00\n"
            f"Concepts Covered: {', '.join(covered) if covered else 'None'}\n"
            f"Concepts Missed: {', '.join(missing) if missing else 'None'}\n"
            f"Provide 2 concise feedback points explaining what was missing and 2 specific actionable steps to improve.<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

        inputs = tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=96,
                do_sample=False,
                temperature=None,
                top_p=None,
            )
        generated_feedback = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
        item_runtime = round(time.time() - item_start, 2)

        # Compute grounding metrics
        fb_tokens = _extract_tokens(generated_feedback)
        grounding_ratio = len(fb_tokens & cand_tokens) / max(len(cand_tokens), 1)

        # Check gap coverage
        gap_cov = 1.0 if not missing else (1.0 if any(m.lower() in generated_feedback.lower() for m in missing) else 0.5)

        # Count actionability bullet points / numbered items
        actionability_count = len(re.findall(r'(?:^\s*[-*•\d+.]|\b(?:step|practice|review|implement|ensure|use|focus)\b)', generated_feedback, re.IGNORECASE | re.MULTILINE))
        actionability_count = max(1, min(actionability_count, 5))

        qwen_evaluations.append({
            "run_id": f"EXP3_qwen7b_{qid}",
            "item_id": qid,
            "condition_id": "qwen_7b_grounded_feedback",
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

        print(f"[EXP-3-Qwen] ({idx+1}/20) Evaluated {qid} in {item_runtime}s (Grounding: {grounding_ratio:.4f}, Gap: {gap_cov:.2f}, Actionability: {actionability_count})")

    elapsed_total = round(time.time() - start_time, 2)

    # Save dedicated Qwen-7B raw output
    qwen_raw_payload = {
        "experiment_id": "EXP-3",
        "condition": "qwen_7b_grounded_feedback",
        "model_name": "Qwen/Qwen2.5-7B-Instruct",
        "model_revision": "a09a35458c702b33eeacc393d103063234e8bc28",
        "timestamp": datetime.utcnow().isoformat(),
        "runtime_seconds": elapsed_total,
        "device": "cpu",
        "dtype": "bfloat16",
        "provenance": {
            "ratings_averaged_sha256": _compute_sha256(ratings_path),
            "rubrics_sha256": _compute_sha256(rubrics_path),
            "model_snapshot_path": SNAPSHOT_PATH,
        },
        "total_samples": len(qwen_evaluations),
        "evaluations": qwen_evaluations,
        "status": "COMPLETED"
    }

    qwen_raw_path = ROOT / "research/results/raw/experiment_3_qwen_raw.json"
    with open(qwen_raw_path, "w", encoding="utf-8") as f:
        json.dump(qwen_raw_payload, f, indent=2)
    print(f"[EXP-3-Qwen] Saved Qwen raw results to {qwen_raw_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="experiments/experiment_3_feedback/config.json")
    parser.add_argument("--out", default="experiments/experiment_3_feedback")
    args = parser.parse_args()
    run_qwen_condition(args.config, args.out)
