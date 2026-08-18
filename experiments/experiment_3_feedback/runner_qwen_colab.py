"""
runner_qwen_colab.py — Standalone Self-Contained GPU Runner for EXP-3 Qwen-7B Condition
Can be executed in Google Colab, Kaggle GPU, or any local/remote CUDA environment.

Usage:
    python runner_qwen_colab.py --output_dir results/
"""

import os
import sys
import time
import json
import csv
import re
import hashlib
from datetime import datetime
from pathlib import Path
import numpy as np

try:
    import torch
    import transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM
except ImportError:
    print("[ERROR] Required packages not found. Please run: pip install torch transformers accelerate safetensors huggingface_hub scipy")
    sys.exit(1)

# Pre-registered Model & Revision
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
MODEL_REVISION = "a09a35458c702b33eeacc393d103063234e8bc28"

# 20 Pre-registered Benchmark Items
BENCHMARK_ITEMS = [
  {
    "item_id": "pilot_01_qid1",
    "qid": "1",
    "question": "Explain your logic to find the two indices in an array that sum to a target value.",
    "answer": "Iterate through the array with a single loop. For each element, calculate the complement (target - current). Check if the complement exists in a hash map. If it does, return the current index and the index stored in the map. If not, insert the current value and its index into the map.",
    "score": 0.95,
    "covered_concepts": ["single pass iteration", "complement calculation (target - current)", "hash map for storing values", "store value-to-index mapping"],
    "missing_concepts": [],
    "incorrect_claims": []
  },
  {
    "item_id": "pilot_02_qid1",
    "qid": "1",
    "question": "Explain your logic to find the two indices in an array that sum to a target value.",
    "answer": "Use two nested loops. The outer loop picks the first element and the inner loop checks all remaining elements to see if they sum to target. Time complexity is O(n^2).",
    "score": 0.40,
    "covered_concepts": ["checks all remaining elements", "nested loops"],
    "missing_concepts": ["hash map for storing values", "complement calculation (target - current)", "O(n) time complexity with O(n) space trade-off"],
    "incorrect_claims": []
  },
  {
    "item_id": "pilot_03_qid1",
    "qid": "1",
    "question": "Explain your logic to find the two indices in an array that sum to a target value.",
    "answer": "Sort the array first in O(n log n). Then use two pointers at left and right ends. Move left rightward if sum is too small, move right leftward if sum is too large. But sorting loses original indices unless stored as pairs.",
    "score": 0.65,
    "covered_concepts": ["two pointers at left and right ends", "sorting array first", "handles index tracking trade-off"],
    "missing_concepts": ["hash map for storing values", "complement calculation (target - current)"],
    "incorrect_claims": []
  },
  {
    "item_id": "pilot_04_qid1",
    "qid": "1",
    "question": "Explain your logic to find the two indices in an array that sum to a target value.",
    "answer": "Just use binary search on every element to find target minus element in O(n log n).",
    "score": 0.35,
    "covered_concepts": ["target minus element"],
    "missing_concepts": ["binary search requires sorted array", "hash map for storing values", "complement calculation (target - current)"],
    "incorrect_claims": ["Binary search directly on unsorted array"]
  },
  {
    "item_id": "pilot_05_qid1",
    "qid": "1",
    "question": "Explain your logic to find the two indices in an array that sum to a target value.",
    "answer": "Create a hash map. First insert every element and its index into the map. Then in a second loop, look up target - nums[i]. If found and index != i, return [i, map[target-nums[i]]].",
    "score": 0.80,
    "covered_concepts": ["hash map for storing values", "complement calculation (target - current)", "handles self-match edge case"],
    "missing_concepts": ["single pass iteration optimization"],
    "incorrect_claims": []
  },
  {
    "item_id": "pilot_06_qid3",
    "qid": "3",
    "question": "Describe the approach to reverse a singly linked list iteratively and explain the pointer manipulations.",
    "answer": "Maintain three pointers: prev initialized to NULL, curr initialized to head, and next. In a while loop while curr is not NULL, store curr->next in next, point curr->next to prev, move prev to curr, and move curr to next. Finally return prev as the new head.",
    "score": 0.95,
    "covered_concepts": ["prev initialized to NULL", "curr initialized to head", "store curr->next in temporary pointer", "reverse pointer direction curr->next = prev", "advance prev and curr", "return prev as new head"],
    "missing_concepts": [],
    "incorrect_claims": []
  },
  {
    "item_id": "pilot_07_qid3",
    "qid": "3",
    "question": "Describe the approach to reverse a singly linked list iteratively and explain the pointer manipulations.",
    "answer": "Just set head->next to NULL and iterate forward.",
    "score": 0.15,
    "covered_concepts": ["iterate forward"],
    "missing_concepts": ["prev initialized to NULL", "three-pointer tracking", "temporary next storage", "return prev as new head"],
    "incorrect_claims": ["Loses rest of linked list by setting head->next to NULL immediately"]
  },
  {
    "item_id": "pilot_08_qid3",
    "qid": "3",
    "question": "Describe the approach to reverse a singly linked list iteratively and explain the pointer manipulations.",
    "answer": "Use recursion where reverseList(head) recursively reverses the sublist and attaches head at the end with head->next->next = head and head->next = NULL.",
    "score": 0.70,
    "covered_concepts": ["head->next->next = head", "head->next = NULL", "base case handling"],
    "missing_concepts": ["iterative three-pointer manipulation (prev, curr, next) requested in prompt"],
    "incorrect_claims": []
  },
  {
    "item_id": "pilot_09_qid3",
    "qid": "3",
    "question": "Describe the approach to reverse a singly linked list iteratively and explain the pointer manipulations.",
    "answer": "Push all nodes onto a stack in O(n) space, then pop them one by one to re-link pointers in reverse order.",
    "score": 0.55,
    "covered_concepts": ["stack for reversing order", "O(n) auxiliary space"],
    "missing_concepts": ["in-place O(1) space iterative pointer reversal"],
    "incorrect_claims": []
  },
  {
    "item_id": "pilot_10_qid3",
    "qid": "3",
    "question": "Describe the approach to reverse a singly linked list iteratively and explain the pointer manipulations.",
    "answer": "Two pointers p and q where q = p->next and p->next = NULL, but forget to save next node so the list is severed.",
    "score": 0.30,
    "covered_concepts": ["pointer redirection"],
    "missing_concepts": ["three-pointer tracking (prev, curr, next)", "preserving next before updating link"],
    "incorrect_claims": ["Severing list without temporary next pointer"]
  },
  {
    "item_id": "pilot_11_qid10",
    "qid": "10",
    "question": "Explain the BFS (Level Order) traversal of a binary tree and how a queue is used.",
    "answer": "Use a FIFO queue. Push the root node to the queue. While the queue is not empty, get the queue size to process level by level. Dequeue a node, record its value, and enqueue its left and right children if they exist.",
    "score": 0.95,
    "covered_concepts": ["FIFO queue data structure", "enqueue root initially", "while queue is not empty", "level size for level-by-level segmentation", "enqueue left and right children"],
    "missing_concepts": [],
    "incorrect_claims": []
  },
  {
    "item_id": "pilot_12_qid10",
    "qid": "10",
    "question": "Explain the BFS (Level Order) traversal of a binary tree and how a queue is used.",
    "answer": "BFS visits root, then left subtree with recursion, then right subtree with recursion.",
    "score": 0.20,
    "covered_concepts": ["visits nodes"],
    "missing_concepts": ["queue data structure", "iterative level order traversal", "FIFO ordering"],
    "incorrect_claims": ["Confused BFS with DFS / Pre-order traversal"]
  },
  {
    "item_id": "pilot_13_qid10",
    "qid": "10",
    "question": "Explain the BFS (Level Order) traversal of a binary tree and how a queue is used.",
    "answer": "Use a stack to push nodes and pop them. First in last out gives you level order.",
    "score": 0.25,
    "covered_concepts": ["push and pop nodes"],
    "missing_concepts": ["queue (FIFO) rather than stack (LIFO)", "level order traversal requires FIFO"],
    "incorrect_claims": ["Stack produces DFS, not BFS"]
  },
  {
    "item_id": "pilot_14_qid10",
    "qid": "10",
    "question": "Explain the BFS (Level Order) traversal of a binary tree and how a queue is used.",
    "answer": "Put root in queue. Pop from queue and add left and right child. Time complexity O(N), Space complexity O(W) where W is maximum tree width.",
    "score": 0.85,
    "covered_concepts": ["queue data structure", "enqueue root", "enqueue children", "O(N) time complexity", "O(W) space complexity"],
    "missing_concepts": ["explicit level size segmentation for 2D level grouping"],
    "incorrect_claims": []
  },
  {
    "item_id": "pilot_15_qid10",
    "qid": "10",
    "question": "Explain the BFS (Level Order) traversal of a binary tree and how a queue is used.",
    "answer": "BFS uses DFS internally with depth parameter to insert into list of lists.",
    "score": 0.45,
    "covered_concepts": ["depth tracking", "list of lists grouping"],
    "missing_concepts": ["queue data structure", "standard iterative BFS algorithm"],
    "incorrect_claims": ["Claims BFS is implemented with DFS"]
  },
  {
    "item_id": "pilot_16_qid41",
    "qid": "41",
    "question": "What is a pointer in C and how do you dereference it?",
    "answer": "A pointer is a variable that stores the memory address of another variable. You declare it using the asterisk syntax (int *p = &x) and dereference it with *p to access or modify the value stored at that address.",
    "score": 0.95,
    "covered_concepts": ["stores memory address of another variable", "address-of operator (&)", "dereference operator (*)", "access/modify value at memory address"],
    "missing_concepts": [],
    "incorrect_claims": []
  },
  {
    "item_id": "pilot_17_qid41",
    "qid": "41",
    "question": "What is a pointer in C and how do you dereference it?",
    "answer": "A pointer is an arrow that points to code. You dereference with the arrow -> operator only.",
    "score": 0.30,
    "covered_concepts": ["points to data"],
    "missing_concepts": ["stores memory address", "address-of operator (&)", "unary asterisk dereference operator (*)"],
    "incorrect_claims": ["Pointers point to code only", "Dereferencing only uses ->"]
  },
  {
    "item_id": "pilot_18_qid41",
    "qid": "41",
    "question": "What is a pointer in C and how do you dereference it?",
    "answer": "It is an integer holding an address. *ptr gives value, &var gives address. NULL pointer check is important before dereferencing to prevent segmentation fault.",
    "score": 0.85,
    "covered_concepts": ["stores memory address", "*ptr gives value", "&var gives address", "NULL check prevents segfault"],
    "missing_concepts": ["type-specific pointer arithmetic semantics"],
    "incorrect_claims": []
  },
  {
    "item_id": "pilot_19_qid41",
    "qid": "41",
    "question": "What is a pointer in C and how do you dereference it?",
    "answer": "Pointers are references like in Java. You don't need to do anything to dereference, C does it automatically.",
    "score": 0.20,
    "covered_concepts": ["concept of referencing"],
    "missing_concepts": ["stores memory address", "explicit unary dereference operator (*)", "address-of operator (&)"],
    "incorrect_claims": ["C does automatic dereferencing like Java references"]
  },
  {
    "item_id": "pilot_20_qid41",
    "qid": "41",
    "question": "What is a pointer in C and how do you dereference it?",
    "answer": "A pointer holds a memory location. Using *p reads the value at that location. Failing to initialize causes dangling pointers or undefined behavior.",
    "score": 0.90,
    "covered_concepts": ["holds memory location", "*p reads value at location", "dangling pointer / undefined behavior warning"],
    "missing_concepts": ["address-of operator (&) initialization syntax"],
    "incorrect_claims": []
  }
]


def _extract_tokens(text: str) -> set:
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    stop_words = {"the", "and", "for", "that", "this", "with", "from", "you", "your", "are", "have", "can", "use", "will", "what"}
    return set(w for w in words if w not in stop_words)


def _bootstrap_ci(data, num_resamples=10000, alpha=0.05):
    if len(data) == 0:
        return [0.0, 0.0]
    rng = np.random.RandomState(42)
    means = [np.mean(rng.choice(data, size=len(data), replace=True)) for _ in range(num_resamples)]
    low = np.percentile(means, 100 * (alpha / 2))
    high = np.percentile(means, 100 * (1 - alpha / 2))
    return [round(float(low), 4), round(float(high), 4)]


def run_qwen_cuda_experiment(output_dir: str = "results"):
    print("=" * 60)
    print("EXP-3: Qwen2.5-7B-Instruct Grounded Feedback on CUDA GPU")
    print("=" * 60)

    # 1. Environment and CUDA verification
    python_ver = sys.version
    torch_ver = torch.__version__
    trans_ver = transformers.__version__
    cuda_avail = torch.cuda.is_available()

    print(f"Python: {python_ver.split()[0]}")
    print(f"PyTorch: {torch_ver}")
    print(f"Transformers: {trans_ver}")
    print(f"CUDA Available: {cuda_avail}")

    if not cuda_avail:
        raise RuntimeError("FATAL: CUDA GPU is required for Qwen-7B inference. Please enable a GPU runtime.")

    gpu_name = torch.cuda.get_device_name(0)
    vram_total_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    cuda_ver = torch.version.cuda
    print(f"GPU: {gpu_name}")
    print(f"Total VRAM: {vram_total_gb:.2f} GB")
    print(f"CUDA Version: {cuda_ver}")

    # 2. Model Loading
    print(f"\n[1/3] Loading Tokenizer & Model: {MODEL_ID} (rev: {MODEL_REVISION[:12]})...")
    start_load = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        torch_dtype=torch.bfloat16,
        device_map="cuda",
    )
    model.eval()
    load_time = round(time.time() - start_load, 2)
    vram_used_gb = torch.cuda.memory_allocated(0) / (1024**3)
    print(f"Model loaded successfully in {load_time}s. VRAM allocated: {vram_used_gb:.2f} GB.")

    # 3. Model Load Smoke Test
    print("\n[2/3] Running Model Smoke Test...")
    smoke_prompt = (
        "<|im_start|>system\nYou are an expert technical interviewer.<|im_end|>\n"
        "<|im_start|>user\nProvide 1 concise sentence of formative feedback for a candidate reversing a linked list using prev, curr, and next pointers.<|im_end|>\n"
        "<|im_start|>assistant\n"
    )
    smoke_start = time.time()
    smoke_inputs = tokenizer(smoke_prompt, return_tensors="pt").to("cuda")
    with torch.no_grad():
        smoke_out = model.generate(
            **smoke_inputs,
            max_new_tokens=48,
            do_sample=False,
            temperature=None,
            top_p=None,
            use_cache=True,
        )
    smoke_text = tokenizer.decode(smoke_out[0][smoke_inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
    smoke_lat = round(time.time() - smoke_start, 2)
    print(f"Smoke Test Generation completed in {smoke_lat}s:")
    print(f"Output: \"{smoke_text}\"")

    # 4. Running 20 Benchmark Evaluations
    print(f"\n[3/3] Executing 20 Benchmark Items...")
    qwen_evaluations = []
    runtimes = []

    for idx, item in enumerate(BENCHMARK_ITEMS):
        t0 = time.time()
        qid = item["item_id"]
        qn_text = item["question"]
        cand_text = item["answer"]
        sc = item["score"]
        covered = item["covered_concepts"]
        missing = item["missing_concepts"]
        incorrect = item["incorrect_claims"]
        cand_tokens = _extract_tokens(cand_text)

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

        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=96,
                do_sample=False,
                temperature=None,
                top_p=None,
                use_cache=True,
            )
        generated_feedback = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
        item_runtime = round(time.time() - t0, 2)
        runtimes.append(item_runtime)

        # Grounding metrics
        fb_tokens = _extract_tokens(generated_feedback)
        grounding_ratio = len(fb_tokens & cand_tokens) / max(len(cand_tokens), 1)
        gap_cov = 1.0 if not missing else (1.0 if any(m.lower() in generated_feedback.lower() for m in missing) else 0.5)

        actionability_count = len(re.findall(r'(?:^\s*[-*•\d+.]|\b(?:step|practice|review|implement|ensure|use|focus|consider|add)\b)', generated_feedback, re.IGNORECASE | re.MULTILINE))
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

        print(f"  ({idx+1:02d}/20) {qid:18s} | Latency: {item_runtime:4.2f}s | Grounding: {grounding_ratio:.4f} | Gap: {gap_cov:.2f} | Actionability: {actionability_count}")

    # 5. Export Results
    os.makedirs(output_dir, exist_ok=True)
    grs = [e["grounding_ratio"] for e in qwen_evaluations]
    gaps = [e["gap_coverage"] for e in qwen_evaluations]
    acts = [e["actionability_count"] for e in qwen_evaluations]

    qwen_raw_payload = {
        "experiment_id": "EXP-3",
        "condition": "qwen_7b_grounded_feedback",
        "model_name": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "timestamp": datetime.utcnow().isoformat(),
        "hardware_environment": {
            "gpu_name": gpu_name,
            "vram_total_gb": round(vram_total_gb, 2),
            "vram_used_gb": round(vram_used_gb, 2),
            "cuda_version": cuda_ver,
            "torch_version": torch_ver,
            "transformers_version": trans_ver,
            "python_version": python_ver.split()[0]
        },
        "smoke_test_result": {
            "status": "SUCCESS",
            "load_time_seconds": load_time,
            "generation_latency_seconds": smoke_lat,
            "output": smoke_text
        },
        "total_samples_targeted": 20,
        "total_samples_completed": len(qwen_evaluations),
        "aggregated_metrics": {
            "mean_grounding_ratio": round(float(np.mean(grs)), 4),
            "grounding_ci_95": _bootstrap_ci(grs),
            "mean_gap_coverage": round(float(np.mean(gaps)), 4),
            "mean_actionability_count": round(float(np.mean(acts)), 4),
            "mean_latency_seconds": round(float(np.mean(runtimes)), 2),
        },
        "evaluations": qwen_evaluations,
        "status": "COMPLETED"
    }

    raw_file = os.path.join(output_dir, "experiment_3_qwen_raw.json")
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(qwen_raw_payload, f, indent=2)

    proc_file = os.path.join(output_dir, "experiment_3_qwen_processed.csv")
    with open(proc_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["run_id", "item_id", "condition_id", "score", "grounding_ratio", "gap_coverage", "actionability_count", "runtime_seconds", "generated_feedback"])
        for e in qwen_evaluations:
            writer.writerow([e["run_id"], e["item_id"], e["condition_id"], e["score"], e["grounding_ratio"], e["gap_coverage"], e["actionability_count"], e["runtime_seconds"], e["generated_feedback"]])

    print("\n" + "=" * 60)
    print("EXP-3 QWEN-7B EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Status: 20/20 COMPLETED")
    print(f"Mean Grounding Ratio: {np.mean(grs):.4f} (95% CI: {_bootstrap_ci(grs)})")
    print(f"Mean Gap Coverage:    {np.mean(gaps):.4f}")
    print(f"Mean Actionability:   {np.mean(acts):.2f}")
    print(f"Mean Latency:         {np.mean(runtimes):.2f}s per turn")
    print(f"Raw Output:           {raw_file}")
    print(f"Processed CSV:        {proc_file}")
    print("=" * 60)


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "results"
    run_qwen_cuda_experiment(out_dir)
