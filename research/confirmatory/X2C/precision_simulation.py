#!/usr/bin/env python
"""X2-C precision simulation (Paper 2). PREPARATION ARTIFACT — reads only the OLD (exploratory) benchmark to calibrate variance
components; creates and collects NO human data; is NOT a registered protocol step until the user confirms the precision target.

Question answered: for Q questions x K answers per question, what is the expected half-width (coverage is NOT simulated here) of a two-level (question -> answer)
cluster-bootstrap 95% interval for a pooled Spearman rho between an evaluator score and a human consensus score, under assumed
true agreement levels? It informs the choice of Q and K; it does not change the primary outcome and is not a success threshold.

Model (assumptions, all stated):
  human_ij  = mu_q + w_ij, mu_q ~ N(m, s_q^2), w_ij ~ N(0, s_w^2)   (s_q, s_w calibrated from the 64-case gold by one-way ANOVA)
  eval_ij   = a * z(human_ij) + sqrt(1-a^2) * noise_ij, with a set so that the population Pearson correlation equals rho_target
  Spearman rho is computed on the pooled sample. Rater noise is ignored (ICC(2,k) = 0.98 in the old data), so widths are
  slightly optimistic. Question-level dependence of the evaluator error is NOT modelled beyond the shared human question effect.
Run: python precision_simulation.py [--b-sim 200] [--b-boot 400] [--seed 20260920]
"""
import argparse, csv, hashlib, json, sys
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

REPO = Path(__file__).resolve().parents[3]
GOLD = REPO / "research/data/evaluator_benchmark/final_human_gold.csv"
DATA = REPO / "research/data/evaluator_benchmark/benchmark_dataset.csv"
OUT = Path(__file__).resolve().parent / "precision_simulation_results.json"
RHOS = (0.2, 0.4, 0.6)
QS = (16, 20, 24, 30, 40)
KS = (6, 8, 10)
TARGET_HALF_WIDTH = 0.12          # the draft's suggestion; NOT confirmed by the user


def calibrate():
    gold = {r["case_id"]: float(r["final_gold_score"]) for r in csv.DictReader(open(GOLD, encoding="utf-8"))}
    qid = {r["case_id"]: r["qid"] for r in csv.DictReader(open(DATA, encoding="utf-8"))}
    groups = {}
    for c, g in gold.items():
        groups.setdefault(qid[c], []).append(g)
    allv = np.array([v for g in groups.values() for v in g])
    grand = allv.mean()
    ss_w = sum(((np.array(g) - np.mean(g)) ** 2).sum() for g in groups.values())
    df_w = len(allv) - len(groups)
    ms_w = ss_w / df_w
    k = len(allv) / len(groups)
    ms_b = sum(len(g) * (np.mean(g) - grand) ** 2 for g in groups.values()) / (len(groups) - 1)
    s_w2 = ms_w
    s_q2 = max((ms_b - ms_w) / k, 0.0)
    return {"n_cases": len(allv), "n_questions": len(groups), "grand_mean": float(grand), "sd_total": float(allv.std(ddof=1)),
            "s_q": float(np.sqrt(s_q2)), "s_w": float(np.sqrt(s_w2)), "icc_question": float(s_q2 / (s_q2 + s_w2))}


def spearman(x, y):
    rx, ry = rankdata(x), rankdata(y)
    rx -= rx.mean()
    ry -= ry.mean()
    return float((rx * ry).sum() / np.sqrt((rx ** 2).sum() * (ry ** 2).sum()))


def simulate_dataset(rng, Q, K, rho, cal):
    mu = rng.normal(cal["grand_mean"], cal["s_q"], Q)
    h = mu[:, None] + rng.normal(0, cal["s_w"], (Q, K))
    z = (h - h.mean()) / h.std()
    e = rho * z + np.sqrt(1 - rho ** 2) * rng.normal(0, 1, (Q, K))
    return h, e


def boot_ci(h, e, rng, b):
    Q, K = h.shape
    stats = np.empty(b)
    for i in range(b):
        qi = rng.integers(0, Q, Q)
        ai = rng.integers(0, K, (Q, K))
        hh = h[qi[:, None], ai]
        ee = e[qi[:, None], ai]
        stats[i] = spearman(hh.ravel(), ee.ravel())
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return lo, hi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--b-sim", type=int, default=200)
    ap.add_argument("--b-boot", type=int, default=400)
    ap.add_argument("--seed", type=int, default=20260920)
    a = ap.parse_args()
    cal = calibrate()
    rows = []
    for rho in RHOS:
        for Q in QS:
            for K in KS:
                rng = np.random.default_rng([a.seed, int(rho * 10), Q, K])
                hw, est = [], []
                for _ in range(a.b_sim):
                    h, e = simulate_dataset(rng, Q, K, rho, cal)
                    lo, hi = boot_ci(h, e, rng, a.b_boot)
                    r = spearman(h.ravel(), e.ravel())
                    hw.append((hi - lo) / 2)
                    est.append(r)
                # population Spearman for this generative setting (large sample) used as the coverage target
                rngp = np.random.default_rng([a.seed, 99, int(rho * 10)])
                hp, ep = simulate_dataset(rngp, 2000, 10, rho, cal)
                pop_rho = spearman(hp.ravel(), ep.ravel())
                rows.append({"rho_target_pearson": rho, "population_spearman_approx": round(pop_rho, 4), "Q": Q, "K": K, "n": Q * K,
                             "mean_half_width": round(float(np.mean(hw)), 4), "p90_half_width": round(float(np.percentile(hw, 90)), 4),
                             "share_half_width_le_target": round(float(np.mean(np.array(hw) <= TARGET_HALF_WIDTH)), 3),
                             "mean_estimate": round(float(np.mean(est)), 4), "sd_estimate": round(float(np.std(est, ddof=1)), 4)})
                print(rows[-1], flush=True)
    out = {"status": "PREPARATION ONLY - not registered; precision target 0.12 is the draft's suggestion awaiting user confirmation; no human data",
           "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "b_sim": a.b_sim, "b_boot": a.b_boot, "seed": a.seed,
           "calibration_from_old_exploratory_benchmark": cal, "assumptions": __doc__.split("Model (assumptions, all stated):")[1].split("Run:")[0].strip(),
           "target_half_width": TARGET_HALF_WIDTH, "grid": rows}
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
