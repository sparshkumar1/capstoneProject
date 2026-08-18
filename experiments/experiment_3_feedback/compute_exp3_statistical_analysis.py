"""
compute_exp3_statistical_analysis.py — Master 3-Condition Statistical Analysis for EXP-3
"""

import json
import csv
import numpy as np
from scipy import stats

def bootstrap_ci(data, num_resamples=10000, alpha=0.05):
    rng = np.random.RandomState(42)
    means = [np.mean(rng.choice(data, size=len(data), replace=True)) for _ in range(num_resamples)]
    low = np.percentile(means, 100 * (alpha / 2))
    high = np.percentile(means, 100 * (1 - alpha / 2))
    return [round(float(low), 4), round(float(high), 4)]

def cohens_d(x, y):
    diff = np.array(x) - np.array(y)
    return float(np.mean(diff) / (np.std(diff, ddof=1) + 1e-8))

def holm_bonferroni(p_values):
    # p_values is a list of tuples: (name, p_val)
    sorted_p = sorted(p_values, key=lambda x: x[1])
    m = len(sorted_p)
    corrected = []
    for rank, (name, p) in enumerate(sorted_p):
        p_adj = min(1.0, p * (m - rank))
        corrected.append((name, p, p_adj))
    # restore original order
    order_dict = {name: (p, p_adj) for name, p, p_adj in corrected}
    return [(name, order_dict[name][0], order_dict[name][1]) for name, _ in p_values]

# 1. Load Generic & Structured Recovery from experiment_3_raw.json
with open("research/results/raw/experiment_3_raw.json", "r", encoding="utf-8") as f:
    exp3_raw = json.load(f)

generic_items = [e for e in exp3_raw["sample_evaluations"] if e["condition_id"] == "generic_template"]
struct_items = [e for e in exp3_raw["sample_evaluations"] if e["condition_id"] == "structured_evaluator_recovery"]

# 2. Load Qwen-7B from experiment_3_qwen_raw.json
with open("research/results/raw/experiment_3_qwen_raw.json", "r", encoding="utf-8") as f:
    qwen_raw = json.load(f)

qwen_items = qwen_raw["evaluations"]

# Verify alignment
assert len(generic_items) == 20
assert len(struct_items) == 20
assert len(qwen_items) == 20

# Metrics arrays
gen_gr = [e["grounding_ratio"] for e in generic_items]
gen_gap = [e["gap_coverage"] for e in generic_items]
gen_act = [e["actionability_count"] for e in generic_items]

struct_gr = [e["grounding_ratio"] for e in struct_items]
struct_gap = [e["gap_coverage"] for e in struct_items]
struct_act = [e["actionability_count"] for e in struct_items]

qwen_gr = [e["grounding_ratio"] for e in qwen_items]
qwen_gap = [e["gap_coverage"] for e in qwen_items]
qwen_act = [e["actionability_count"] for e in qwen_items]
qwen_lat = [e["runtime_seconds"] for e in qwen_items]

print("=" * 60)
print("EXP-3 MASTER 3-CONDITION DESCRIPTIVE STATISTICS (n=20)")
print("=" * 60)
print(f"Generic Template:        Grounding = {np.mean(gen_gr):.4f} {bootstrap_ci(gen_gr)} | Gap = {np.mean(gen_gap):.4f} | Act = {np.mean(gen_act):.2f}")
print(f"Structured Recovery:     Grounding = {np.mean(struct_gr):.4f} {bootstrap_ci(struct_gr)} | Gap = {np.mean(struct_gap):.4f} | Act = {np.mean(struct_act):.2f}")
print(f"Qwen-7B Grounded:        Grounding = {np.mean(qwen_gr):.4f} {bootstrap_ci(qwen_gr)} | Gap = {np.mean(qwen_gap):.4f} | Act = {np.mean(qwen_act):.2f} | Latency = {np.mean(qwen_lat):.2f}s")

# Pairwise Wilcoxon tests
print("\n" + "=" * 60)
print("PAIRWISE STATISTICAL COMPARISONS (Wilcoxon Signed-Rank Test)")
print("=" * 60)

# Grounding comparisons
w_gs_gr, p_gs_gr = stats.wilcoxon(struct_gr, gen_gr)
w_gq_gr, p_gq_gr = stats.wilcoxon(qwen_gr, gen_gr)
w_sq_gr, p_sq_gr = stats.wilcoxon(qwen_gr, struct_gr)

gr_pairs = [
    ("Generic vs Structured", p_gs_gr),
    ("Generic vs Qwen-7B", p_gq_gr),
    ("Structured vs Qwen-7B", p_sq_gr)
]
gr_adj = holm_bonferroni(gr_pairs)

print("\n--- Lexical Grounding Ratio ---")
print(f"1. Generic vs Structured:  W = {w_gs_gr:.1f}, p_raw = {p_gs_gr:.4e}, p_holm = {gr_adj[0][2]:.4e}, Cohen's d = {cohens_d(struct_gr, gen_gr):.4f}")
print(f"2. Generic vs Qwen-7B:     W = {w_gq_gr:.1f}, p_raw = {p_gq_gr:.4e}, p_holm = {gr_adj[1][2]:.4e}, Cohen's d = {cohens_d(qwen_gr, gen_gr):.4f}")
print(f"3. Structured vs Qwen-7B:  W = {w_sq_gr:.1f}, p_raw = {p_sq_gr:.4e}, p_holm = {gr_adj[2][2]:.4e}, Cohen's d = {cohens_d(qwen_gr, struct_gr):.4f}")

# Gap Coverage comparisons
w_gs_gap, p_gs_gap = stats.wilcoxon(struct_gap, gen_gap)
w_gq_gap, p_gq_gap = stats.wilcoxon(qwen_gap, gen_gap)
w_sq_gap, p_sq_gap = stats.wilcoxon(struct_gap, qwen_gap)

gap_pairs = [
    ("Generic vs Structured", p_gs_gap),
    ("Generic vs Qwen-7B", p_gq_gap),
    ("Structured vs Qwen-7B", p_sq_gap)
]
gap_adj = holm_bonferroni(gap_pairs)

print("\n--- Rubric Gap Coverage ---")
print(f"1. Generic vs Structured:  W = {w_gs_gap:.1f}, p_raw = {p_gs_gap:.4e}, p_holm = {gap_adj[0][2]:.4e}, Cohen's d = {cohens_d(struct_gap, gen_gap):.4f}")
print(f"2. Generic vs Qwen-7B:     W = {w_gq_gap:.1f}, p_raw = {p_gq_gap:.4e}, p_holm = {gap_adj[1][2]:.4e}, Cohen's d = {cohens_d(qwen_gap, gen_gap):.4f}")
print(f"3. Structured vs Qwen-7B:  W = {w_sq_gap:.1f}, p_raw = {p_sq_gap:.4e}, p_holm = {gap_adj[2][2]:.4e}, Cohen's d = {cohens_d(struct_gap, qwen_gap):.4f}")

# Actionability comparisons
w_gs_act, p_gs_act = stats.wilcoxon(struct_act, gen_act)
w_gq_act, p_gq_act = stats.wilcoxon(qwen_act, gen_act)
w_sq_act, p_sq_act = stats.wilcoxon(struct_act, qwen_act)

act_pairs = [
    ("Generic vs Structured", p_gs_act),
    ("Generic vs Qwen-7B", p_gq_act),
    ("Structured vs Qwen-7B", p_sq_act)
]
act_adj = holm_bonferroni(act_pairs)

print("\n--- Actionable Directives Count ---")
print(f"1. Generic vs Structured:  W = {w_gs_act:.1f}, p_raw = {p_gs_act:.4e}, p_holm = {act_adj[0][2]:.4e}, Cohen's d = {cohens_d(struct_act, gen_act):.4f}")
print(f"2. Generic vs Qwen-7B:     W = {w_gq_act:.1f}, p_raw = {p_gq_act:.4e}, p_holm = {act_adj[1][2]:.4e}, Cohen's d = {cohens_d(qwen_act, gen_act):.4f}")
print(f"3. Structured vs Qwen-7B:  W = {w_sq_act:.1f}, p_raw = {p_sq_act:.4e}, p_holm = {act_adj[2][2]:.4e}, Cohen's d = {cohens_d(struct_act, qwen_act):.4f}")
