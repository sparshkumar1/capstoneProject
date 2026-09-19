"""
Master Evaluator Experiment Suite for PrepAIred (Paper 2 & Master Evidence Package).
Executes:
- EXP-EVAL-1: Component Ablation (7-way) across Human Rater 1, Synthetic Proxies, and Averaged set
- EXP-EVAL-2: Adversarial Keyword-Stuffing Resistance Test
- EXP-EVAL-3: Concept Matching Threshold Sensitivity Sweep
- EXP-EVAL-4: Qualitative Error Analysis & Confusion Matrix
"""

from __future__ import annotations

import csv
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import confusion_matrix

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from services.evaluator.app import (
    CONCEPT_THRESHOLD,
    _cosine_similarity,
    _detect_misconceptions,
    _ensure_evaluator_assets_loaded,
    _extract_concept_texts,
    bonus_score,
    cross_encoder_verification,
    embed,
    evaluate,
    get_rubric,
    get_vectors_by_type,
    mandatory_check,
    mistake_penalty,
    semantic_score,
    split_sentences,
)

RAW_DIR = REPO_ROOT / "research" / "raw"
PROCESSED_DIR = REPO_ROOT / "research" / "processed"
TABLES_DIR = REPO_ROOT / "research" / "tables"
FIGURES_DIR = REPO_ROOT / "research" / "figures"

for d in [RAW_DIR, PROCESSED_DIR, TABLES_DIR, FIGURES_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def bootstrap_ci(
    x: np.ndarray, y: np.ndarray, n_boot: int = 1000, seed: int = 42
) -> tuple[float, float, float, float]:
    """Calculate 95% bootstrap CI for Spearman rho and Pearson r."""
    rng = np.random.default_rng(seed)
    n = len(x)
    rhos, rs = [], []
    for _ in range(n_boot):
        idx = rng.choice(n, size=n, replace=True)
        bx, by = x[idx], y[idx]
        if np.std(bx) > 1e-9 and np.std(by) > 1e-9:
            rhos.append(spearmanr(bx, by).statistic)
            rs.append(pearsonr(bx, by).statistic)
    rhos = np.array(rhos)
    rs = np.array(rs)
    rho_low, rho_high = np.percentile(rhos, [2.5, 97.5])
    r_low, r_high = np.percentile(rs, [2.5, 97.5])
    return float(rho_low), float(rho_high), float(r_low), float(r_high)


def paired_bootstrap_delta(
    scores_a: np.ndarray,
    scores_full: np.ndarray,
    human: np.ndarray,
    n_boot: int = 1000,
    seed: int = 42,
) -> tuple[float, float]:
    """Calculate delta rho and empirical bootstrap p-value against full model."""
    rng = np.random.default_rng(seed)
    n = len(human)
    actual_delta = spearmanr(scores_a, human).statistic - spearmanr(scores_full, human).statistic
    deltas = []
    for _ in range(n_boot):
        idx = rng.choice(n, size=n, replace=True)
        ha, hf, hh = scores_a[idx], scores_full[idx], human[idx]
        if np.std(ha) > 1e-9 and np.std(hf) > 1e-9 and np.std(hh) > 1e-9:
            r_a = spearmanr(ha, hh).statistic
            r_f = spearmanr(hf, hh).statistic
            deltas.append(r_a - r_f)
    deltas = np.array(deltas)
    # two-sided p-value against null hypothesis of delta = 0
    p_val = float(np.mean(np.abs(deltas) >= np.abs(actual_delta)))
    return float(actual_delta), p_val


def evaluate_dataset(path: Path) -> list[dict]:
    """Run evaluator on all rows in a ratings dataset."""
    rows = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            qid = str(r["qid"]).strip()
            rubric = get_rubric(qid)
            res = evaluate(r["question"], r["answer"], rubric)
            rows.append(
                {
                    "qid": qid,
                    "question": r["question"],
                    "answer": r["answer"],
                    "human_score": float(r["human_score"]),
                    "system_score_recorded": float(r["system_score"]) if r.get("system_score") else None,
                    "s1": float(res["S1_semantic"]),
                    "s2": float(res["S2_structural"]),
                    "r": float(res["reasoning_score"]),
                    "s2_eff": float(res["S2_structural"] if res["reasoning_score"] > 0.30 else res["S2_structural"] * 0.60),
                    "bonus": float(res["bonus"]),
                    "penalty": float(res["penalty"]),
                    "mandatory_pass": bool(res["mandatory_pass"]),
                    "final_score": float(res["final_score"]),
                    "weakest_gap": res.get("weakest_gap", ""),
                    "correct_claims": res.get("correct_claims", []),
                    "missing_concepts": res.get("missing_concepts", []),
                }
            )
    return rows


def compute_ablation_metrics(rows: list[dict], dataset_name: str) -> dict:
    """Compute 7-way ablation metrics for a given dataset."""
    human = np.array([x["human_score"] for x in rows])
    configs = {
        "S1 only": np.array([x["s1"] for x in rows]),
        "S2 only": np.array([x["s2"] for x in rows]),
        "R only": np.array([x["r"] for x in rows]),
        "S1 + R": np.array([(0.15 * x["s1"] + 0.50 * x["r"]) / 0.65 for x in rows]),
        "S1 + S2": np.array([(0.15 * x["s1"] + 0.35 * x["s2"]) / 0.50 for x in rows]),
        "S2 + R": np.array([(0.35 * x["s2"] + 0.50 * x["r"]) / 0.85 for x in rows]),
        "Full (paper)": np.array([x["final_score"] for x in rows]),
    }

    full_scores = configs["Full (paper)"]
    results = {}
    for name, scores in configs.items():
        rho_res = spearmanr(scores, human)
        r_res = pearsonr(scores, human)
        mae = float(np.mean(np.abs(scores - human)))
        rmse = float(np.sqrt(np.mean((scores - human) ** 2)))
        rho_low, rho_high, r_low, r_high = bootstrap_ci(scores, human)

        if name == "Full (paper)":
            delta_rho, p_delta = 0.0, 1.0
        else:
            delta_rho, p_delta = paired_bootstrap_delta(scores, full_scores, human)

        results[name] = {
            "spearman_rho": float(rho_res.statistic),
            "spearman_p": float(rho_res.pvalue),
            "spearman_ci95": [rho_low, rho_high],
            "pearson_r": float(r_res.statistic),
            "pearson_p": float(r_res.pvalue),
            "pearson_ci95": [r_low, r_high],
            "mae": mae,
            "rmse": rmse,
            "delta_rho_vs_full": delta_rho,
            "delta_p_val": p_delta,
        }
    return {
        "dataset": dataset_name,
        "n_samples": len(rows),
        "metrics": results,
    }


# ==============================================================================
# EXP-EVAL-2: Adversarial Keyword-Stuffing Resistance Test
# ==============================================================================
def run_adversarial_keyword_test() -> list[dict]:
    """Test resilience against keyword stuffing across 5 technical questions."""
    test_cases = [
        {
            "qid": "1",
            "topic": "Arrays & Hashing (Two Sum)",
            "qn": "Explain your logic to find the two indices in an array that sum up to a target value.",
            "authentic": "I use a single pass with a hash map. As I iterate through each element, I calculate its complement which is target minus current number. If the complement exists in the map, I return its saved index and current index. Otherwise I store the current number and index.",
            "keyword_stuffing": "Hash table, hash map, dictionary, key-value, lookup, complement, target minus x, array, index, indices, single pass, O(n) time complexity, O(n) space complexity, constant time lookup.",
            "superficial": "Finding values in an array is important for performance. I like to structure my code cleanly with helper functions and modular abstractions so other engineers can read it.",
        },
        {
            "qid": "3",
            "topic": "Linked Lists (Reverse)",
            "qn": "Describe the approach to reverse a singly linked list in-place.",
            "authentic": "I initialize three pointers: prev as null, curr as head, and next_node as null. In a while loop until curr is null, I store curr.next in next_node, point curr.next backward to prev, advance prev to curr, and advance curr to next_node. Finally prev becomes the new head.",
            "keyword_stuffing": "Previous pointer, current pointer, next pointer, in-place reversal, three pointers, null termination, head update, O(1) auxiliary space, O(n) linear scan, redirect next pointer.",
            "superficial": "Linked lists are very dynamic structures. Reversing them requires good attention to detail so you do not get null reference errors during execution.",
        },
        {
            "qid": "10",
            "topic": "Binary Trees (BFS Traversal)",
            "qn": "Explain the BFS (Level Order) traversal logic for a binary tree.",
            "authentic": "BFS processes nodes level by level using a FIFO queue. We start by pushing the root into the queue. While the queue is not empty, we dequeue a node, process its value, and enqueue its left and right children if they exist.",
            "keyword_stuffing": "Queue FIFO data structure, level order, root enqueue, dequeue while not empty, push left child, push right child, breadth first search, O(V+E) time, level-by-level processing.",
            "superficial": "Tree traversal is fundamental. You can traverse trees in many directions depending on what algorithms your company needs to deploy.",
        },
        {
            "qid": "41",
            "topic": "C Programming (Pointers)",
            "qn": "What is a pointer in C and how do you declare one?",
            "authentic": "A pointer is a variable that stores the memory address of another variable. You declare it using an asterisk, for example int *ptr. You assign it with the address-of operator like ptr = &val, and dereference it using *ptr to access the underlying value.",
            "keyword_stuffing": "Memory address, asterisk dereference operator, address-of ampersand operator, pointer declaration, int *p, heap stack address, memory location, hex address storage.",
            "superficial": "C is a powerful low-level programming language used in operating systems and compilers. Pointers are important for memory efficiency.",
        },
        {
            "qid": "7",
            "topic": "Dynamic Programming (Climbing Stairs)",
            "qn": "How do you determine the number of distinct ways to climb n stairs if you can take 1 or 2 steps?",
            "authentic": "This is equivalent to the Fibonacci recurrence. The number of ways to reach step n is dp[n] = dp[n-1] + dp[n-2], with base cases dp[1]=1 and dp[2]=2. We can optimize space to O(1) by maintaining just two variables for previous steps.",
            "keyword_stuffing": "Dynamic programming, recurrence relation, subproblems, memoization, bottom up tabulation, Fibonacci sequence, dp[i] = dp[i-1] + dp[i-2], base cases, space optimization O(1).",
            "superficial": "Stairs problems can be solved step by step. You write a loop to calculate the steps carefully until you reach the top floor.",
        },
    ]

    results = []
    for tc in test_cases:
        rubric = get_rubric(tc["qid"])
        for cond_name, ans_text in [
            ("Authentic Technical", tc["authentic"]),
            ("Keyword Stuffing", tc["keyword_stuffing"]),
            ("Superficial", tc["superficial"]),
        ]:
            res = evaluate(tc["qn"], ans_text, rubric)
            s1 = res["S1_semantic"]
            s2 = res["S2_structural"]
            r = res["reasoning_score"]
            s2_eff = s2 if r > 0.30 else s2 * 0.60
            undampened = 0.15 * s1 + 0.35 * s2 + 0.50 * r + res["bonus"] - res["penalty"]
            undampened = max(0.0, min(1.0, undampened))
            dampened = res["final_score"]

            results.append(
                {
                    "qid": tc["qid"],
                    "topic": tc["topic"],
                    "condition": cond_name,
                    "s1": round(s1, 3),
                    "s2": round(s2, 3),
                    "reasoning_r": round(r, 3),
                    "s2_effective": round(s2_eff, 3),
                    "dampening_triggered": bool(r <= 0.30),
                    "undampened_score": round(undampened, 3),
                    "final_score": round(dampened, 3),
                    "delta_dampening": round(undampened - dampened, 3),
                    "grade": res["grade"],
                    "weakest_gap": res.get("weakest_gap", ""),
                }
            )
    return results


# ==============================================================================
# EXP-EVAL-3: Concept Matching Threshold Sensitivity Sweep
# ==============================================================================
def run_threshold_sweep(rater1_rows: list[dict]) -> list[dict]:
    """Sweep concept matching threshold theta across [0.15, 0.60]."""
    _ensure_evaluator_assets_loaded()
    thresholds = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
    human = np.array([x["human_score"] for x in rater1_rows])

    sweep_results = []
    for theta in thresholds:
        s2_list = []
        final_list = []
        concepts_detected_list = []

        for r in rater1_rows:
            candidate = r["answer"]
            rubric = get_rubric(r["qid"])
            sentences = split_sentences(candidate)

            if not sentences:
                s2 = 0.0
                detected_cnt = 0
            else:
                sent_emb = embed(sentences)
                qid = rubric.get("qid")
                concept_vectors = get_vectors_by_type(qid, "concept") if qid else []
                if len(concept_vectors) == 0 and rubric.get("expected_concepts"):
                    concept_vectors = embed(rubric["expected_concepts"])

                if len(concept_vectors) == 0:
                    s2 = 0.0
                    detected_cnt = 0
                else:
                    sims = _cosine_similarity(sent_emb, concept_vectors)
                    best_scores = np.max(sims, axis=0)
                    detected_cnt = int(sum(best_scores > theta))
                    s2 = detected_cnt / len(best_scores)

            s2_list.append(s2)
            concepts_detected_list.append(detected_cnt)

            # Recalculate final score with this S2
            s1 = r["s1"]
            reasoning = r["r"]
            s2_eff = s2 if reasoning > 0.30 else s2 * 0.60
            base = 0.15 * s1 + 0.35 * s2_eff + 0.50 * reasoning
            fin = base + r["bonus"] - r["penalty"]
            fin = max(0.0, min(1.0, fin))
            if not r["mandatory_pass"]:
                fin = min(fin, 0.60)
            final_list.append(fin)

        s2_arr = np.array(s2_list)
        final_arr = np.array(final_list)

        rho_s2 = spearmanr(s2_arr, human).statistic
        rho_final = spearmanr(final_arr, human).statistic
        mae_final = float(np.mean(np.abs(final_arr - human)))
        avg_concepts = float(np.mean(concepts_detected_list))

        sweep_results.append(
            {
                "threshold": theta,
                "s2_spearman_rho": round(float(rho_s2), 4),
                "final_spearman_rho": round(float(rho_final), 4),
                "mae": round(mae_final, 4),
                "mean_detected_concepts": round(avg_concepts, 2),
            }
        )
    return sweep_results


# ==============================================================================
# EXP-EVAL-4: Qualitative Error Analysis & Confusion Matrix
# ==============================================================================
def run_error_analysis(rater1_rows: list[dict]) -> dict:
    """Analyze confusion matrix, false positives, false negatives on pilot dataset."""

    def to_tier(score: float) -> str:
        if score >= 0.75:
            return "Excellent"
        if score >= 0.60:
            return "Good"
        if score >= 0.40:
            return "Average"
        return "Poor"

    tier_labels = ["Poor", "Average", "Good", "Excellent"]
    y_true = [to_tier(x["human_score"]) for x in rater1_rows]
    y_pred = [to_tier(x["final_score"]) for x in rater1_rows]

    cm = confusion_matrix(y_true, y_pred, labels=tier_labels)

    # Discrepancy analysis
    large_errors = []
    for x in rater1_rows:
        diff = x["final_score"] - x["human_score"]
        if abs(diff) >= 0.20:
            large_errors.append(
                {
                    "qid": x["qid"],
                    "question": x["question"],
                    "answer": x["answer"],
                    "human_score": x["human_score"],
                    "system_score": x["final_score"],
                    "diff": round(diff, 4),
                    "error_type": "False Positive (Overestimated)" if diff > 0 else "False Negative (Underestimated)",
                    "s1": x["s1"],
                    "s2": x["s2"],
                    "reasoning_score": x["r"],
                    "weakest_gap": x["weakest_gap"],
                }
            )

    return {
        "tier_labels": tier_labels,
        "confusion_matrix": cm.tolist(),
        "total_evaluated": len(rater1_rows),
        "exact_agreement": int(sum(1 for t, p in zip(y_true, y_pred) if t == p)),
        "exact_agreement_rate": round(sum(1 for t, p in zip(y_true, y_pred) if t == p) / len(y_true), 4),
        "large_errors": large_errors,
    }


# ==============================================================================
# TABLES & FIGURES WRITERS
# ==============================================================================
def write_ablation_markdown_table(ablation_summary: dict, out_path: Path) -> None:
    lines = [
        "# Evaluator Component Ablation (EXP-EVAL-1)",
        "",
        "This table reports component ablations across three evaluation sets ($N=20$ each):",
        "1. **Human Rater 1 (Pilot)**: Real human computer science educator.",
        "2. **Synthetic Proxy Raters**: Synthetic proxy baseline.",
        "3. **Averaged Ratings**: Averaged human + synthetic proxies.",
        "",
        "> [!IMPORTANT]",
        "> Per Research Adjustment 4, synthetic proxy ratings are strictly separated from real human ratings.",
        "",
    ]

    for dname, data in ablation_summary.items():
        lines.append(f"## Dataset: {dname} ($N={data['n_samples']}$)")
        lines.append("")
        lines.append(
            "| Configuration | Spearman $\\rho$ | 95% CI ($\\rho$) | Pearson $r$ | 95% CI ($r$) | MAE | RMSE | $\\Delta \\rho$ vs Full | $p$-val |"
        )
        lines.append(
            "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
        )
        for cfg, m in data["metrics"].items():
            rho_ci = f"[{m['spearman_ci95'][0]:.3f}, {m['spearman_ci95'][1]:.3f}]"
            r_ci = f"[{m['pearson_ci95'][0]:.3f}, {m['pearson_ci95'][1]:.3f}]"
            d_rho = f"{m['delta_rho_vs_full']:+.4f}" if cfg != "Full (paper)" else "ref"
            d_p = f"{m['delta_p_val']:.4f}" if cfg != "Full (paper)" else "-"
            lines.append(
                f"| **{cfg}** | {m['spearman_rho']:.4f} | {rho_ci} | {m['pearson_r']:.4f} | {r_ci} | {m['mae']:.4f} | {m['rmse']:.4f} | {d_rho} | {d_p} |"
            )
        lines.append("")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


def write_adversarial_markdown_table(adv_results: list[dict], out_path: Path) -> None:
    lines = [
        "# Adversarial Keyword-Stuffing Resistance (EXP-EVAL-2)",
        "",
        "Evaluation of reasoning-conditioned concept dampening ($S_{2,\\text{eff}} = S_2 \\times 0.60$ when $R \\le 0.30$):",
        "",
        "| QID | Topic | Condition | $S_1$ | $S_2$ | $R$ (Reasoning) | $S_{2,\\text{eff}}$ | Undampened | Final Score | Grade | Dampening Triggered? |",
        "| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]
    for r in adv_results:
        trig = "YES (Triggered)" if r["dampening_triggered"] else "No"
        lines.append(
            f"| Q{r['qid']} | {r['topic']} | **{r['condition']}** | {r['s1']:.3f} | {r['s2']:.3f} | {r['reasoning_r']:.3f} | {r['s2_effective']:.3f} | {r['undampened_score']:.3f} | {r['final_score']:.3f} | {r['grade']} | {trig} |"
        )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


def write_threshold_markdown_table(sweep_results: list[dict], out_path: Path) -> None:
    lines = [
        "# Concept Matching Threshold Sensitivity Sweep (EXP-EVAL-3)",
        "",
        "Sensitivity analysis of concept detection threshold $\\theta \\in [0.15, 0.60]$ on Pilot Human Rater 1 ($N=20$):",
        "",
        "| Threshold $\\theta$ | $S_2$ Spearman $\\rho$ | Final Score Spearman $\\rho$ | MAE | Mean Concepts Detected / Item | Notes |",
        "| :---: | :---: | :---: | :---: | :---: | :--- |",
    ]
    for r in sweep_results:
        note = "Selected Operating Point" if r["threshold"] == 0.30 else ""
        lines.append(
            f"| {r['threshold']:.2f} | {r['s2_spearman_rho']:.4f} | {r['final_spearman_rho']:.4f} | {r['mae']:.4f} | {r['mean_detected_concepts']:.2f} | {note} |"
        )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


def write_error_analysis_markdown(error_data: dict, out_path: Path) -> None:
    lines = [
        "# Qualitative Error Analysis & Confusion Matrix (EXP-EVAL-4)",
        "",
        f"**Exact Agreement Rate**: {error_data['exact_agreement']}/{error_data['total_evaluated']} ({error_data['exact_agreement_rate'] * 100:.1f}%)",
        "",
        "## Confusion Matrix (Human Tier vs System Tier)",
        "",
        "| True \\ Predicted | Poor | Average | Good | Excellent |",
        "| :--- | :---: | :---: | :---: | :---: |",
    ]
    cm = error_data["confusion_matrix"]
    tiers = error_data["tier_labels"]
    for i, t in enumerate(tiers):
        lines.append(f"| **{t}** | {cm[i][0]} | {cm[i][1]} | {cm[i][2]} | {cm[i][3]} |")

    lines.append("")
    lines.append("## Discrepancy Breakdown ($|\\text{System} - \\text{Human}| \\ge 0.20$)")
    lines.append("")
    for item in error_data["large_errors"]:
        ans_preview = item["answer"][:100] + "..." if len(item["answer"]) > 100 else item["answer"]
        if not ans_preview.strip():
            ans_preview = "*(Empty / Non-response)*"
        lines.append(f"### Q{item['qid']}: {item['question']}")
        lines.append(f"- **Answer**: \"{ans_preview}\"")
        lines.append(f"- **Human Score**: {item['human_score']:.4f} | **System Score**: {item['system_score']:.4f} ($\\Delta = {item['diff']:+.4f}$)")
        lines.append(f"- **Error Classification**: {item['error_type']}")
        lines.append(f"- **Diagnostic**: $S_1 = {item['s1']:.3f}, S_2 = {item['s2']:.3f}, R = {item['reasoning_score']:.3f}$")
        lines.append(f"- **Weakest Identified Gap**: {item['weakest_gap']}")
        lines.append("")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


def generate_figures(
    ablation_summary: dict, sweep_results: list[dict], figures_dir: Path
) -> None:
    """Generate publication-ready figures for Paper 2."""
    plt.rcParams.update(
        {
            "figure.dpi": 200,
            "savefig.dpi": 300,
            "font.size": 9,
            "font.family": "sans-serif",
            "axes.titlesize": 10,
            "axes.labelsize": 9,
        }
    )

    # Figure 1: Ablation Comparison Across Datasets
    fig, ax = plt.subplots(figsize=(8, 4.2))
    configs = list(next(iter(ablation_summary.values()))["metrics"].keys())
    x = np.arange(len(configs))
    width = 0.26

    datasets = [
        ("Human Rater 1 (Pilot)", "steelblue", -width),
        ("Synthetic Proxy", "coral", 0.0),
        ("Averaged Set", "forestgreen", width),
    ]

    for dname, color, offset in datasets:
        rhos = [ablation_summary[dname]["metrics"][c]["spearman_rho"] for c in configs]
        err_low = [
            rhos[i] - ablation_summary[dname]["metrics"][c]["spearman_ci95"][0]
            for i, c in enumerate(configs)
        ]
        err_high = [
            ablation_summary[dname]["metrics"][c]["spearman_ci95"][1] - rhos[i]
            for i, c in enumerate(configs)
        ]
        yerr = [err_low, err_high]
        ax.bar(
            x + offset,
            rhos,
            width,
            label=dname,
            color=color,
            alpha=0.85,
            edgecolor="black",
            linewidth=0.8,
            yerr=yerr,
            capsize=3,
        )

    ax.set_ylabel("Spearman Rank Correlation ($\\rho$)")
    ax.set_title("Evaluator Component Ablation Across Rating Datasets (EXP-EVAL-1)")
    ax.set_xticks(x)
    ax.set_xticklabels(configs, rotation=20, ha="right")
    ax.set_ylim(0.3, 1.05)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend(frameon=True, facecolor="white", loc="lower right")
    plt.tight_layout()
    fig1_path = figures_dir / "eval_ablation_comparison.png"
    plt.savefig(fig1_path)
    plt.close()
    print(f"Generated {fig1_path}")

    # Figure 2: Threshold Sensitivity
    fig, ax1 = plt.subplots(figsize=(7, 3.8))
    thetas = [r["threshold"] for r in sweep_results]
    rho_s2 = [r["s2_spearman_rho"] for r in sweep_results]
    rho_fin = [r["final_spearman_rho"] for r in sweep_results]
    mean_concepts = [r["mean_detected_concepts"] for r in sweep_results]

    color = "tab:blue"
    ax1.set_xlabel("Concept Matching Threshold ($\\theta$)")
    ax1.set_ylabel("Spearman $\\rho$", color=color)
    (l1,) = ax1.plot(thetas, rho_fin, "o-", color="royalblue", lw=2, label="Final Score $\\rho$")
    (l2,) = ax1.plot(thetas, rho_s2, "s--", color="deepskyblue", lw=1.5, label="$S_2$ Concept $\\rho$")
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.set_ylim(0.4, 0.8)
    ax1.axvline(0.30, color="firebrick", linestyle=":", lw=2, label="Selected $\\theta=0.30$")

    ax2 = ax1.twinx()
    color = "tab:red"
    ax2.set_ylabel("Mean Concepts Detected / Answer", color=color)
    (l3,) = ax2.plot(thetas, mean_concepts, "^-.", color="darkorange", lw=1.8, label="Concepts Detected")
    ax2.tick_params(axis="y", labelcolor=color)
    ax2.set_ylim(0, 5)

    lines = [l1, l2, l3]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper right", frameon=True, facecolor="white")
    ax1.set_title("Concept Matching Sensitivity Sweep Across Threshold $\\theta$ (EXP-EVAL-3)")
    plt.tight_layout()
    fig2_path = figures_dir / "eval_threshold_sensitivity.png"
    plt.savefig(fig2_path)
    plt.close()
    print(f"Generated {fig2_path}")


def main() -> None:
    print("=== STARTING EXP-EVAL SUITE ===")

    # 1. EXP-EVAL-1: Ablation on 3 datasets
    print("Running EXP-EVAL-1 (Component Ablation across 3 datasets)...")
    rater1_path = REPO_ROOT / "ablation" / "results" / "ratings_rater1.csv"
    proxy_path = REPO_ROOT / "ablation" / "results" / "ratings_proxy.csv"
    avg_path = REPO_ROOT / "ablation" / "results" / "ratings_averaged.csv"

    rater1_rows = evaluate_dataset(rater1_path)
    proxy_rows = evaluate_dataset(proxy_path)
    avg_rows = evaluate_dataset(avg_path)

    ablation_summary = {
        "Human Rater 1 (Pilot)": compute_ablation_metrics(rater1_rows, "Human Rater 1 (Pilot)"),
        "Synthetic Proxy": compute_ablation_metrics(proxy_rows, "Synthetic Proxy"),
        "Averaged Set": compute_ablation_metrics(avg_rows, "Averaged Set"),
    }

    # Save raw ablation
    raw_ablation_path = RAW_DIR / "eval_ablation_raw.json"
    raw_ablation_path.write_text(json.dumps(ablation_summary, indent=2), encoding="utf-8")
    print(f"Saved {raw_ablation_path}")

    write_ablation_markdown_table(ablation_summary, TABLES_DIR / "table_eval_ablation.md")

    # 2. EXP-EVAL-2: Adversarial Keyword-Stuffing
    print("Running EXP-EVAL-2 (Adversarial Keyword-Stuffing Resistance)...")
    adv_results = run_adversarial_keyword_test()
    raw_adv_path = RAW_DIR / "eval_adversarial_raw.json"
    raw_adv_path.write_text(json.dumps(adv_results, indent=2), encoding="utf-8")
    write_adversarial_markdown_table(adv_results, TABLES_DIR / "table_eval_adversarial.md")

    # 3. EXP-EVAL-3: Threshold Sweep
    print("Running EXP-EVAL-3 (Threshold Sensitivity Sweep)...")
    sweep_results = run_threshold_sweep(rater1_rows)
    raw_sweep_path = RAW_DIR / "eval_threshold_raw.json"
    raw_sweep_path.write_text(json.dumps(sweep_results, indent=2), encoding="utf-8")
    write_threshold_markdown_table(sweep_results, TABLES_DIR / "table_eval_threshold.md")

    # 4. EXP-EVAL-4: Qualitative Error Analysis
    print("Running EXP-EVAL-4 (Qualitative Error Analysis & Confusion Matrix)...")
    error_analysis = run_error_analysis(rater1_rows)
    raw_error_path = RAW_DIR / "eval_error_analysis_raw.json"
    raw_error_path.write_text(json.dumps(error_analysis, indent=2), encoding="utf-8")
    write_error_analysis_markdown(error_analysis, TABLES_DIR / "table_eval_error_analysis.md")

    # 5. Generate Figures
    print("Generating Publication Figures...")
    generate_figures(ablation_summary, sweep_results, FIGURES_DIR)

    print("=== EXP-EVAL SUITE COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
