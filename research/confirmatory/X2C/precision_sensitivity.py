#!/usr/bin/env python
"""Unregistered planning-only sensitivity simulation for X2-C.

This script creates synthetic scores only. It does not author benchmark items, contact
raters, or produce human judgments. It stress-tests the earlier optimistic precision
simulation by varying question-level heterogeneity, evaluator question-cluster error,
and reliability of the mean human rating. It is not preregistration or a sample-size
authorization.

The estimand is population Spearman correlation between evaluator scores and the mean
human rating. For each synthetic dataset, uncertainty is estimated with a two-stage
bootstrap (sample questions, then answers within each sampled question). Percentile
interval coverage is measured against the known Gaussian-copula population Spearman
correlation for the data-generating process.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import rankdata


DESIGNS = ((20, 8), (30, 8), (40, 8), (40, 10))
TARGET_RHOS = (0.2, 0.4, 0.6)
QUESTION_ICCS = (0.0, 0.10, 0.25)
EVALUATOR_CLUSTER_FRACTIONS = (0.0, 0.10)
HUMAN_CONSENSUS_RELIABILITY = 0.95


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx = rankdata(x, method="average")
    ry = rankdata(y, method="average")
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    denom = np.sqrt(np.dot(rx, rx) * np.dot(ry, ry))
    return float(np.dot(rx, ry) / denom) if denom else float("nan")


def population_spearman(rho_latent: float) -> float:
    # For a bivariate normal pair, rho_s = 6/pi * asin(rho_P/2).
    observed_pearson = rho_latent * math.sqrt(HUMAN_CONSENSUS_RELIABILITY)
    return (6.0 / math.pi) * math.asin(observed_pearson / 2.0)


def make_dataset(
    rng: np.random.Generator,
    q: int,
    k: int,
    rho: float,
    question_icc: float,
    evaluator_cluster_fraction: float,
) -> tuple[np.ndarray, np.ndarray]:
    q_effect = rng.normal(size=(q, 1))
    item_effect = rng.normal(size=(q, k))
    latent_human = (
        math.sqrt(question_icc) * q_effect
        + math.sqrt(1.0 - question_icc) * item_effect
    )
    evaluator_noise = (
        math.sqrt(evaluator_cluster_fraction) * rng.normal(size=(q, 1))
        + math.sqrt(1.0 - evaluator_cluster_fraction) * rng.normal(size=(q, k))
    )
    evaluator = rho * latent_human + math.sqrt(1.0 - rho * rho) * evaluator_noise

    # Independent per-item measurement error chosen to give the mean human rating the
    # stated reliability. This is an explicit sensitivity assumption, not an estimate
    # of a future panel's reliability.
    noise_variance = (1.0 - HUMAN_CONSENSUS_RELIABILITY) / HUMAN_CONSENSUS_RELIABILITY
    human_consensus = latent_human + rng.normal(
        0.0, math.sqrt(noise_variance), size=(q, k)
    )
    return evaluator, human_consensus


def cluster_bootstrap_ci(
    x: np.ndarray, y: np.ndarray, rng: np.random.Generator, b: int
) -> tuple[float, float]:
    q, k = x.shape
    q_idx = rng.integers(0, q, size=(b, q))
    a_idx = rng.integers(0, k, size=(b, q, k))
    xb = x[q_idx[:, :, None], a_idx].reshape(b, q * k)
    yb = y[q_idx[:, :, None], a_idx].reshape(b, q * k)
    rx = rankdata(xb, axis=1, method="average")
    ry = rankdata(yb, axis=1, method="average")
    rx -= rx.mean(axis=1, keepdims=True)
    ry -= ry.mean(axis=1, keepdims=True)
    denom = np.sqrt(np.sum(rx * rx, axis=1) * np.sum(ry * ry, axis=1))
    stats = np.sum(rx * ry, axis=1) / denom
    return tuple(np.percentile(stats, (2.5, 97.5)).tolist())


def run_cell(
    seed: int,
    simulations: int,
    bootstraps: int,
    q: int,
    k: int,
    rho: float,
    question_icc: float,
    evaluator_cluster_fraction: float,
) -> dict:
    rng = np.random.default_rng(seed)
    target = population_spearman(rho)
    widths: list[float] = []
    covered: list[bool] = []
    estimates: list[float] = []
    for _ in range(simulations):
        x, y = make_dataset(rng, q, k, rho, question_icc, evaluator_cluster_fraction)
        estimate = spearman(x.ravel(), y.ravel())
        lo, hi = cluster_bootstrap_ci(x, y, rng, bootstraps)
        estimates.append(estimate)
        widths.append(hi - lo)
        covered.append(lo <= target <= hi)
    return {
        "q_questions": q,
        "k_answers_per_question": k,
        "n_items": q * k,
        "latent_pearson_rho": rho,
        "population_spearman_target": round(target, 5),
        "question_icc": question_icc,
        "evaluator_question_error_fraction": evaluator_cluster_fraction,
        "human_consensus_reliability_assumption": HUMAN_CONSENSUS_RELIABILITY,
        "simulations": simulations,
        "bootstraps_per_dataset": bootstraps,
        "mean_ci_half_width": round(float(np.mean(widths)) / 2.0, 5),
        "p90_ci_half_width": round(float(np.percentile(widths, 90)) / 2.0, 5),
        "empirical_95pct_interval_coverage": round(float(np.mean(covered)), 4),
        "mean_sample_spearman": round(float(np.mean(estimates)), 5),
        "mc_se_coverage_approx": round(
            math.sqrt(float(np.mean(covered)) * (1 - float(np.mean(covered))) / simulations),
            4,
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulations", type=int, default=40)
    parser.add_argument("--bootstraps", type=int, default=250)
    parser.add_argument("--seed", type=int, default=20260929)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("precision_sensitivity_results.json"),
    )
    args = parser.parse_args()
    rows = []
    cell = 0
    for rho in TARGET_RHOS:
        for question_icc in QUESTION_ICCS:
            for evaluator_cluster_fraction in EVALUATOR_CLUSTER_FRACTIONS:
                for q, k in DESIGNS:
                    rows.append(
                        run_cell(
                            args.seed + cell,
                            args.simulations,
                            args.bootstraps,
                            q,
                            k,
                            rho,
                            question_icc,
                            evaluator_cluster_fraction,
                        )
                    )
                    cell += 1
    payload = {
        "status": "PLANNING ONLY; synthetic data; not registered; no human data",
        "script_sha256": __import__("hashlib").sha256(Path(__file__).read_bytes()).hexdigest(),
        "seed": args.seed,
        "number_of_scenarios": len(rows),
        "designs": [list(d) for d in DESIGNS],
        "limitations": [
            "Question ICC, evaluator clustering, and mean-human-score reliability are sensitivity assumptions, not estimated truths.",
            "Monte Carlo counts are exploratory; increase repetitions before using results to set a final sample size.",
            "The model does not represent answer-generation, rater fatigue, missing ratings, or non-Gaussian score distributions.",
            "No result is a success threshold, confirmatory finding, or permission to recruit or collect ratings.",
        ],
        "results": rows,
    }
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out} ({len(rows)} planning scenarios)")


if __name__ == "__main__":
    main()
