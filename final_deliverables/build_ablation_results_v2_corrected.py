"""Build the corrected PrepAIred ablation-results summary PDF (v2).

Supersedes `final_deliverables/Ablation_Results_Visual_Summary (1).pdf` (v1, undated,
generating script not recoverable). v1's evaluator-ablation panel (Full=0.915,
S1+S2=0.917, R-only=0.587, from `ablation/results/evaluator_ablation_summary.json`)
reproduces a Spearman rho (0.9152) that `research/audit/rho_provenance.md` and
`research/claims/CLAIM_REGISTRY.csv` row P2-C010 both mark WITHDRAWN (pure synthetic
proxy ratings, pre-fix evaluator weights) -- not the project's current approved
evaluator-vs-human result.

This script reads ONLY already-frozen, already-verified result files (it runs no new
experiments and does not touch any frozen artifact) and regenerates every figure from
real stored data:
  - Evaluator ablation: research/results/paper2/paper2_ablation_results.csv (N=64,
    3-rater gold set) + a real paired bootstrap recomputed from
    research/results/paper2/paper2_case_level_results.csv.
  - RL/guardrail attribution: research/results/paper3/paper3_baseline_results.csv,
    the frozen Paper-3 PPO-contribution finding (P0-2, CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md).
  - Real PPO training convergence: research/results/paper3/paper3_training_curves.csv
    (5 seeds, 24,576 timesteps each) -- replaces v1's mislabeled "RL Convergence"
    panel, which was actually a within-session cumulative average.
  - Real per-dimension sensitivity sweep and guardrail-intervention log:
    research/results/paper3/paper3_sensitivity_results.csv,
    research/results/paper3/paper3_guardrail_results.csv -- replaces v1's
    `ablation/results/sensitivity_summary.json`, whose non-baseline rows share an
    identical nested `question_metrics` block byte-for-byte with the baseline row
    across state/action/reward variants that should have produced different session
    data; that file is not retained here.
  - The pre-existing rho-pipeline RL ablation (`ablation/results/rl_ablation_summary.json`)
    and topic-wise comparison (`ablation/results/topic_analysis_summary.json`) are kept,
    each with an explicit provenance caveat, because they are read from real frozen
    files even though their generating scripts could not be located in this repo.

Run: `.venv/Scripts/python.exe final_deliverables/build_ablation_results_v2_corrected.py`
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import spearmanr

REPO = Path(__file__).resolve().parent.parent
OUT_PDF = Path(__file__).resolve().parent / "Ablation_Results_Visual_Summary_v2_corrected.pdf"

BLUE = "#1f6feb"
GRAY = "#57606a"
RED = "#cf222e"
GREEN = "#1a7f37"


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def new_page_fig(figsize=(8.27, 11.69)):
    fig = plt.figure(figsize=figsize)
    return fig


def add_header(fig, title: str, subtitle: str = ""):
    fig.text(0.08, 0.955, title, fontsize=16, fontweight="bold", va="top")
    if subtitle:
        fig.text(0.08, 0.925, subtitle, fontsize=9.5, color=GRAY, va="top")


def add_bottom_text(fig, shows: str, conclusion: str, caveat: str = "", y0: float = 0.30):
    y = y0
    fig.text(0.08, y, "What this shows", fontsize=11, fontweight="bold", color=BLUE)
    y -= 0.025
    fig.text(0.08, y, shows, fontsize=9, va="top", wrap=True,
              transform=fig.transFigure)
    y -= 0.025 + 0.016 * (shows.count("\n") + len(shows) // 95)
    fig.text(0.08, y, "Conclusion", fontsize=11, fontweight="bold", color=BLUE)
    y -= 0.025
    fig.text(0.08, y, conclusion, fontsize=9, va="top")
    if caveat:
        y -= 0.025 + 0.016 * (conclusion.count("\n") + len(conclusion) // 95)
        fig.text(0.08, y, "Provenance / caveat", fontsize=10, fontweight="bold", color=RED)
        y -= 0.022
        fig.text(0.08, y, caveat, fontsize=8.7, va="top", color="#333333")


def page_title(pdf: PdfPages):
    fig = new_page_fig()
    fig.text(0.5, 0.62, "PrepAIred — Ablation Results (Corrected, v2)", fontsize=20,
              fontweight="bold", ha="center")
    fig.text(0.5, 0.57, "Supersedes: Ablation_Results_Visual_Summary (1).pdf  —  built from frozen, audited data only",
              fontsize=10.5, ha="center", color=GRAY)
    body = (
        "What changed from v1, and why:\n\n"
        "1. The evaluator-ablation panel (v1 p.3/p.8: Full=0.915, S1+S2=0.917, R-only=0.587) reproduced\n"
        "   ablation/results/evaluator_ablation_summary.json, whose exact value (rho=0.9152) is formally\n"
        "   WITHDRAWN in research/claims/CLAIM_REGISTRY.csv (row P2-C010) and research/audit/rho_provenance.md\n"
        "   — it is a pure-synthetic-proxy artifact under pre-fix evaluator weights, not a current result.\n"
        "   This version uses the project's current approved benchmark instead: N=64, 3 raters,\n"
        "   research/results/paper2/paper2_ablation_results.csv.\n\n"
        "2. v1's 'RL Convergence' panel (p.5) plotted within-session cumulative averages, not PPO training\n"
        "   convergence. This version adds the real training-reward-vs-timestep curves (5 seeds,\n"
        "   research/results/paper3/paper3_training_curves.csv) that v1 never used.\n\n"
        "3. v1's 'Sensitivity Analysis' panel (p.7, ablation/results/sensitivity_summary.json) has every\n"
        "   non-baseline row sharing an identical nested per-question metrics block with the baseline row\n"
        "   — including state/action-space variants that should change session data. That file is not used\n"
        "   here; this version uses the real per-dimension input sweep instead\n"
        "   (research/results/paper3/paper3_sensitivity_results.csv).\n\n"
        "4. The guardrails-only-vs-PPO question is answered using the project's own frozen, already-audited\n"
        "   Paper-3 finding (constant-action+guardrails statistically equals PPO+guardrails; the claim\n"
        "   'PPO improves tracking' is withdrawn) rather than restated as an open question.\n\n"
        "5. Figures retained from v1 (rho-pipeline RL ablation, topic-wise comparison) are kept because they\n"
        "   are read from real frozen files, but each now carries an explicit provenance caveat: their\n"
        "   generating scripts could not be located in this repository.\n\n"
        "No frozen artifact was edited, regenerated, or deleted to produce this document. v1 remains on disk\n"
        "unchanged, dated 2026-11-21."
    )
    fig.text(0.08, 0.46, body, fontsize=9.3, va="top")
    pdf.savefig(fig)
    plt.close(fig)


def page_evaluator_real(pdf: PdfPages):
    rows = read_csv(REPO / "research" / "results" / "paper2" / "paper2_ablation_results.csv")
    order = ["Full Composite (0.15/0.35/0.50)", "S1 + R (0.23/0.77)", "R only (CrossEncoder)",
              "S2 + R (0.41/0.59)", "S2 only (FAISS)", "S1 + S2 (0.30/0.70)", "S1 only (Semantic)"]
    by_cfg = {r["configuration"]: r for r in rows}
    labels, rhos, lo, hi = [], [], [], []
    for cfg in order:
        r = by_cfg[cfg]
        labels.append(cfg.split(" (")[0])
        rhos.append(float(r["spearman_rho"]))
        lo.append(float(r["spearman_rho"]) - float(r["spearman_ci95_low"]))
        hi.append(float(r["spearman_ci95_high"]) - float(r["spearman_rho"]))

    fig = new_page_fig()
    add_header(fig, "Evaluator Component Ablation — Current, Real Data",
               "N=64 constructed answers to 8 questions, 3-rater consensus gold (research/results/paper2/paper2_ablation_results.csv)")
    ax = fig.add_axes([0.17, 0.52, 0.78, 0.32])
    y_pos = np.arange(len(labels))
    colors = [GREEN if lab == "Full Composite" else BLUE for lab in labels]
    ax.barh(y_pos, rhos, xerr=[lo, hi], color=colors, height=0.6, capsize=3)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Spearman rho vs. human consensus (95% case-bootstrap CI)", fontsize=9)
    ax.set_xlim(-0.1, 0.8)
    ax.axvline(0, color="#999999", lw=0.7)
    for i, (v, lo_, hi_) in enumerate(zip(rhos, lo, hi)):
        ax.text(v + hi_ + 0.02, i, f"{v:.3f}", va="center", fontsize=8)
    ax.set_title("Evaluator comparison (real, current benchmark)", fontsize=10)

    shows = (
        "Seven versions of the evaluator ranked by Spearman rho against the real 3-rater human-consensus\n"
        "gold set (N=64 answers, 8 questions) — the project's current approved benchmark."
    )
    conclusion = (
        "The full three-ingredient composite (rho=0.381) does NOT top this ranking: R-only (0.483) and\n"
        "S1+R (0.488) both correlate higher with human judgment. S1-only (0.207) and S1+S2 (0.289) are the\n"
        "weakest configurations, and S1-only's CI includes 0. The correct framing (locked wording,\n"
        "CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md section C.2): the full composite is safety-hardened, not\n"
        "accuracy-optimal — bonus/penalty/mandatory-cap terms exist to prevent specific failure modes, at a\n"
        "measurable cost to raw rank agreement with human raters."
    )
    caveat = (
        "v1 of this document reported Full=0.915, S1+S2=0.917, R-only=0.587 from "
        "ablation/results/evaluator_ablation_summary.json. That value (0.9152) is formally WITHDRAWN "
        "(CLAIM_REGISTRY.csv row P2-C010; research/audit/rho_provenance.md) — it was computed on fabricated "
        "synthetic-proxy ratings (0.05/0.20/0.55/0.90) under pre-fix evaluator weights, not real human "
        "ratings. Scope: this N=64 set is exploratory/initial evidence, not a general validity claim — "
        "theta=0.30 and the R-dampening were tuned on an earlier pilot sharing 4 of these 8 questions."
    )
    add_bottom_text(fig, shows, conclusion, caveat, y0=0.465)
    pdf.savefig(fig)
    plt.close(fig)


def page_evaluator_significance_real(pdf: PdfPages):
    cases = read_csv(REPO / "research" / "results" / "paper2" / "paper2_case_level_results.csv")
    human = np.array([float(c["human_gold_score"]) for c in cases])
    full = np.array([float(c["final_score"]) for c in cases])
    S1 = np.array([float(c["S1"]) for c in cases])
    S2 = np.array([float(c["S2"]) for c in cases])
    R = np.array([float(c["R"]) for c in cases])

    configs = {
        "S1 only": S1,
        "S2 only": S2,
        "R only": R,
        "S1+S2 (.30/.70)": 0.30 * S1 + 0.70 * S2,
        "S1+R (.23/.77)": 0.23 * S1 + 0.77 * R,
        "S2+R (.41/.59)": 0.41 * S2 + 0.59 * R,
    }

    rng = np.random.default_rng(42)
    n = len(human)
    n_boot = 5000
    idx_all = rng.integers(0, n, size=(n_boot, n))

    results = {}
    for name, scores in configs.items():
        deltas = np.empty(n_boot)
        for b in range(n_boot):
            idx = idx_all[b]
            h, s, f = human[idx], scores[idx], full[idx]
            if np.std(h) < 1e-9 or np.std(s) < 1e-9 or np.std(f) < 1e-9:
                deltas[b] = np.nan
                continue
            rho_cfg = spearmanr(s, h).statistic
            rho_full = spearmanr(f, h).statistic
            deltas[b] = rho_cfg - rho_full
        deltas = deltas[~np.isnan(deltas)]
        lo_, hi_ = np.percentile(deltas, [2.5, 97.5])
        point = spearmanr(scores, human).statistic - spearmanr(full, human).statistic
        p_val = 2 * min((deltas > 0).mean(), (deltas < 0).mean())
        results[name] = (point, lo_, hi_, p_val)

    fig = new_page_fig()
    add_header(fig, "Evaluator Significance (Recomputed)",
               "Paired case-bootstrap (B=5000, seed=42) on the real N=64 gold set; delta = config rho - full composite rho")
    ax = fig.add_axes([0.16, 0.54, 0.79, 0.30])
    names = list(results.keys())
    points = [results[n_][0] for n_ in names]
    los = [results[n_][0] - results[n_][1] for n_ in names]
    his = [results[n_][2] - results[n_][0] for n_ in names]
    p_vals = [results[n_][3] for n_ in names]
    y_pos = np.arange(len(names))
    sig_colors = []
    for p, pt in zip(p_vals, points):
        if p < 0.05 and pt > 0:
            sig_colors.append(GREEN)
        elif p < 0.05 and pt < 0:
            sig_colors.append(RED)
        else:
            sig_colors.append(GRAY)
    ax.errorbar(points, y_pos, xerr=[los, his], fmt="none", ecolor="#999999",
                capsize=4)
    for i, c in enumerate(sig_colors):
        ax.plot(points[i], i, "o", color=c, markersize=7, zorder=5)
    ax.axvline(0, color="#999999", lw=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Delta Spearman rho vs. full composite (95% CI)", fontsize=9)
    for i, (pt, p) in enumerate(zip(points, p_vals)):
        ax.text(pt, i - 0.28, f"delta={pt:+.3f}  p={p:.3g}", fontsize=7.6, ha="center")

    shows = (
        "A forest plot, recomputed directly from the real per-case N=64 scores (paper2_case_level_results.csv),\n"
        "of how much each reduced evaluator configuration's agreement with the human gold set differs from\n"
        "the full composite's — with a paired bootstrap 95% CI and two-sided p-value, same methodology as v1's\n"
        "forest plot but applied to real data instead of the withdrawn synthetic-proxy set."
    )
    conclusion = (
        "No reduced configuration is significantly WORSE than the full composite at the 0.05 level on this\n"
        "N=64 set. One trends the other way: S1+R is significantly HIGHER than the full composite\n"
        "(delta=+0.107, p=0.03) -- consistent with the point-estimate ranking on the previous page. The other\n"
        "five deltas are not significant, which does not mean those components are provably redundant --\n"
        "with N=64 answers over only 8 questions this test is under-powered to detect anything but a large\n"
        "effect, and 'not significant' must not be read as 'equivalent' (no equivalence/non-inferiority test\n"
        "was run)."
    )
    caveat = (
        "v1's forest plot (ablation/results/significance_statistics.json) used the same withdrawn N=20\n"
        "synthetic-proxy data as its 'Full (paper)'=0.915 bar chart, with no multiple-comparison correction\n"
        "across 6 comparisons. This page is a new computation (not a frozen artifact) using the real,\n"
        "approved N=64 case-level data; it is not yet registered as a formal experiment result and should be\n"
        "treated as AUDIT-REPLAY-tier evidence, not a frozen finding, until reviewed and stored as one."
    )
    add_bottom_text(fig, shows, conclusion, caveat, y0=0.485)
    pdf.savefig(fig)
    plt.close(fig)


def page_rl_attribution_real(pdf: PdfPages):
    rows = read_csv(REPO / "research" / "results" / "paper3" / "paper3_summary_results.csv")
    by_cond = {r["condition"]: r for r in rows}
    order = ["Fixed Baseline (d=3.0)", "Heuristic Baseline", "PPO Raw (Aligned, Seed 123)",
              "PPO + Guardrails (Aligned, Seed 123)", "PPO + Guardrails (5-Seed Mean +/- SD)"]
    labels = ["Fixed\n(d=3.0)", "Heuristic\nonly", "PPO raw\n(seed 123)", "PPO+Guardrails\n(seed 123)",
              "PPO+Guardrails\n(5-seed mean)"]
    maes, errs = [], []
    for cond in order:
        r = by_cond[cond]
        mae = float(r["mean_tracking_error"].split(" +/- ")[0])
        ci = r["tracking_error_95ci"].strip("[]").split(", ")
        maes.append(mae)
        errs.append([mae - float(ci[0]), float(ci[1]) - mae])
    errs = np.array(errs).T

    fig = new_page_fig()
    add_header(fig, "RL/Guardrail Attribution — Frozen Paper-3 Finding",
               "research/results/paper3/paper3_summary_results.csv — lower MAE is better tracking of the simulated candidate's target difficulty")
    ax = fig.add_axes([0.10, 0.56, 0.85, 0.28])
    x = np.arange(len(labels))
    colors = [GRAY, "#e07b00", BLUE, GREEN, GREEN]
    ax.bar(x, maes, yerr=errs, color=colors, capsize=4, width=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8.3)
    ax.set_ylabel("Mean tracking error (MAE, lower=better)", fontsize=9)
    for i, v in enumerate(maes):
        ax.text(i, v + 0.05, f"{v:.3f}", ha="center", fontsize=8.5)

    shows = (
        "Difficulty-tracking error (distance from the simulated candidate's known target difficulty) for\n"
        "five conditions, from the frozen, already-peer-audited Paper-3 study (5 training seeds for the\n"
        "guarded-PPO row; seed 123 only for the single-seed rows)."
    )
    conclusion = (
        "Heuristic-only (MAE=0.473) outperforms every PPO variant, including PPO+Guardrails (0.673-0.687\n"
        "across 5 seeds). A separate audit (research/audit/P0_2_PPO_CONTRIBUTION_FORENSIC.md) built the\n"
        "missing guardrails-only control for this metric: a constant-'Same'-action policy plus the same\n"
        "guardrails scores MAE=0.673 — statistically equal to PPO+Guardrails, differing on only 5 of 125\n"
        "sessions. Locked conclusion (CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md, P0-2): 'The guardrails account\n"
        "for essentially all of the improvement over Fixed... PPO's contribution under guardrails is not\n"
        "identified by the frozen study. Claim \"PPO improves tracking\" is withdrawn.'"
    )
    caveat = (
        "This is a DIFFERENT pipeline/metric (tracking MAE against a known simulated target) from the\n"
        "adaptation-rho ablation on the next page (correlation between delivered difficulty and the\n"
        "candidate's own score trace, no independent ground truth). The two pipelines are not directly\n"
        "comparable and should not be conflated; this page is the more rigorous of the two because it has\n"
        "an independent ground-truth target and an already-built guardrails-only control."
    )
    add_bottom_text(fig, shows, conclusion, caveat, y0=0.50)
    pdf.savefig(fig)
    plt.close(fig)


def page_rl_rho_pipeline_caveated(pdf: PdfPages):
    with (REPO / "ablation" / "results" / "rl_ablation_summary.json").open(encoding="utf-8") as f:
        data = json.load(f)
    order = ["PPO + Guardrails", "PPO only", "Heuristic only", "Fixed difficulty"]
    labels, means, errs = [], [], []
    for cond in order:
        rho = data[cond]["adaptation_rho"]
        labels.append(cond)
        if rho["n"] == 0:
            means.append(np.nan)
            errs.append(0)
        else:
            means.append(rho["mean"])
            errs.append(rho["ci95"])

    fig = new_page_fig()
    add_header(fig, "RL/Guardrail Ablation — Separate Rho-Pipeline",
               "Retained from v1 (ablation/results/rl_ablation_summary.json) — real frozen data; generating script not located")
    ax = fig.add_axes([0.22, 0.58, 0.62, 0.26])
    y_pos = np.arange(len(labels))
    valid = [i for i, m in enumerate(means) if not np.isnan(m)]
    ax.barh([y_pos[i] for i in valid], [means[i] for i in valid],
             xerr=[errs[i] for i in valid], color=BLUE, height=0.55, capsize=4)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Adaptation rho (difficulty vs. own score trace), mean +/- 95% CI", fontsize=9)
    ax.text(0.05, 3.25, "rho undefined (difficulty never varies)", fontsize=8, color=GRAY, va="center")
    for i in valid:
        ax.text(means[i] + errs[i] + 0.02, i, f"{means[i]:.3f} +/- {errs[i]:.3f}", va="center", fontsize=8)

    shows = (
        "The same bar chart as v1 (p.6): how well delivered difficulty correlates with the candidate's own\n"
        "running score, across 10 evaluation sessions per condition (one trained PPO checkpoint)."
    )
    conclusion = (
        "Numbers are unchanged from v1 and are read correctly from the frozen JSON (PPO+Guardrails 0.871,\n"
        "PPO only 0.467 on n=8 sessions, Heuristic only -0.040 on n=8, Fixed undefined)."
    )
    caveat = (
        "Three limitations not disclosed in v1: (1) only ONE trained PPO checkpoint exists in this repo\n"
        "(rl/checkpoints/seed_123) — these error bars are session-to-session variance of one policy, not\n"
        "seed-to-seed robustness; (2) the script that produced this JSON could not be located in the repo,\n"
        "so the exact 'adaptation rho' construction cannot be independently re-derived here — sibling scripts\n"
        "compute an analogous metric by correlating score at turn t against difficulty at turn t+1, where\n"
        "turn t+1's difficulty choice is itself partly a function of that same score, a possible source of\n"
        "circularity not ruled out for this specific file; (3) no guardrails-only control exists for this\n"
        "metric specifically (see the previous page for the equivalent control on the separate MAE metric)."
    )
    add_bottom_text(fig, shows, conclusion, caveat, y0=0.52)
    pdf.savefig(fig)
    plt.close(fig)


def page_training_convergence(pdf: PdfPages):
    rows = read_csv(REPO / "research" / "results" / "paper3" / "paper3_training_curves.csv")
    by_seed = defaultdict(list)
    for r in rows:
        by_seed[r["seed"]].append((int(r["timestep"]), float(r["mean_reward_rolling"])))
    for s in by_seed:
        by_seed[s].sort()

    fig = new_page_fig()
    add_header(fig, "Genuine PPO Training Convergence (New)",
               "Not in v1 — research/results/paper3/paper3_training_curves.csv, 5 independent training seeds, 24,576 timesteps each")
    ax = fig.add_axes([0.10, 0.56, 0.85, 0.28])
    for seed, pts in sorted(by_seed.items()):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax.plot(xs, ys, label=f"seed {seed}", alpha=0.85, lw=1.2)
    ax.set_xlabel("Training timestep", fontsize=9)
    ax.set_ylabel("Rolling mean episode reward", fontsize=9)
    ax.legend(fontsize=7.5, ncol=5, loc="lower right")
    ax.axhline(0, color="#999999", lw=0.6)

    shows = (
        "Reward-vs-timestep curves for all 5 PPO training seeds (42/123/456/789/999) used in the frozen\n"
        "Paper-3 study — this is what 'RL convergence' should actually mean, as opposed to v1's page 5,\n"
        "which plotted within-session cumulative score/difficulty averages (renamed on the next retained\n"
        "page, not removed, since that is still a real and separately useful figure)."
    )
    conclusion = (
        "All 5 seeds show high-variance, noisy reward traces around a roughly flat band rather than a clean\n"
        "monotonic rise — consistent with the locked finding that the reward function is largely an\n"
        "imitation objective against a rule oracle (CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md section D.1) and\n"
        "that the tracking-error evaluation metric is not the training objective. This is a descriptive\n"
        "reading of the curves, not a formal convergence test."
    )
    add_bottom_text(fig, shows, conclusion, y0=0.50)
    pdf.savefig(fig)
    plt.close(fig)


def page_guardrail_interventions(pdf: PdfPages):
    rows = read_csv(REPO / "research" / "results" / "paper3" / "paper3_guardrail_results.csv")
    rule_counts = Counter(r["guardrail_id"] for r in rows)
    changed = sum(1 for r in rows if r["raw_action"] != r["final_action"])
    total = len(rows)

    fig = new_page_fig()
    add_header(fig, "Guardrail Intervention Frequency (New)",
               "Not in v1 — research/results/paper3/paper3_guardrail_results.csv, rule activations by ID, both frozen conditions pooled")
    ax = fig.add_axes([0.30, 0.58, 0.62, 0.26])
    names = sorted(rule_counts, key=lambda k: -rule_counts[k])
    vals = [rule_counts[n] for n in names]
    ax.barh(names, vals, color=BLUE)
    ax.set_xlabel("Rule activations (both PPO+Guardrails conditions pooled)", fontsize=9)
    for i, v in enumerate(vals):
        ax.text(v + 0.5, i, str(v), va="center", fontsize=8)

    shows = (
        "How often each named guardrail rule fired across every logged PPO+Guardrails turn in the frozen\n"
        f"Paper-3 study ({total} logged activation rows total)."
    )
    conclusion = (
        f"{changed} of {total} logged activations ({changed/total*100:.1f}%) actually changed the action\n"
        "PPO had proposed; the rest fired but left PPO's own choice unchanged — matching the locked finding\n"
        "(CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md, P0-4) that only 7.9% of all 1,250 study turns had the final\n"
        "action differ from PPO's proposal, i.e. most 'interventions' are the guardrail agreeing with PPO,\n"
        "not overriding it — the real override rate is much lower than raw activation counts suggest."
    )
    add_bottom_text(fig, shows, conclusion, y0=0.52)
    pdf.savefig(fig)
    plt.close(fig)


def page_sensitivity_real(pdf: PdfPages):
    rows = read_csv(REPO / "research" / "results" / "paper3" / "paper3_sensitivity_results.csv")
    by_dim = defaultdict(list)
    for r in rows:
        by_dim[r["dimension"]].append((float(r["input_value"]), r["action_name"]))
    action_order = ["Easier", "Same", "Harder"]
    action_y = {a: i for i, a in enumerate(action_order)}

    fig = new_page_fig()
    add_header(fig, "Per-Dimension Sensitivity Sweep (New)",
               "Not in v1 — research/results/paper3/paper3_sensitivity_results.csv, each dimension swept 0.0-1.0 alone, others fixed")
    dims = sorted(by_dim.keys())
    n = len(dims)
    for i, dim in enumerate(dims):
        ax = fig.add_axes([0.10 + (i % 3) * 0.29, 0.56 - (i // 3) * 0.17, 0.24, 0.13])
        pts = sorted(by_dim[dim])
        xs = [p[0] for p in pts]
        ys = [action_y[p[1]] for p in pts]
        ax.step(xs, ys, where="mid", color=BLUE, lw=1.4)
        ax.set_yticks([0, 1, 2])
        ax.set_yticklabels(action_order, fontsize=7)
        ax.set_title(dim, fontsize=8)
        ax.set_xlabel("input value", fontsize=6.5)
        ax.tick_params(labelsize=6.5)

    shows = (
        "For each of the 6 state dimensions (performance, average performance, confidence, hesitation,\n"
        "progress, current difficulty), the chosen action as that one input is swept 0.0 to 1.0 with every\n"
        "other input held fixed — a genuine one-at-a-time sensitivity sweep of the trained policy."
    )
    conclusion = (
        "Most dimensions never change the action across their full range (policy insensitive at this\n"
        "operating point) except s1_avg_perf (switches Easier->Same near 0.1-0.2) and s5_diff (switches\n"
        "Harder->Same near 0.5-0.6) — i.e. the policy's action here is most sensitive to average performance\n"
        "and current difficulty, not to confidence or hesitation."
    )
    caveat = (
        "v1's sensitivity page (ablation/results/sensitivity_summary.json) is not used here: every\n"
        "non-baseline row in that file shares an identical nested per-question metrics block with the\n"
        "baseline row, including rows labelled as different state-dimension/action-space architectures that\n"
        "should have produced different session data — strong evidence those rows were not real independent\n"
        "reruns. This page uses a real, directly-inspectable sweep of the actual deployed policy instead."
    )
    add_bottom_text(fig, shows, conclusion, caveat, y0=0.33)
    pdf.savefig(fig)
    plt.close(fig)


def page_topic_wise(pdf: PdfPages):
    with (REPO / "ablation" / "results" / "topic_analysis_summary.json").open(encoding="utf-8") as f:
        data = json.load(f)
    topics = data["topics"]
    labels = [t["topic"] for t in topics]
    human = [t["avg_human_score"] for t in topics]
    system = [t["avg_system_score"] for t in topics]

    fig = new_page_fig()
    add_header(fig, "Human vs. System Score by Topic (Retained from v1)",
               f"source: {data['source']} — 1 question/topic, 5 ratings each")
    ax = fig.add_axes([0.10, 0.58, 0.85, 0.26])
    x = np.arange(len(labels))
    w = 0.35
    ax.bar(x - w / 2, human, w, label="Human rater score", color=GRAY)
    ax.bar(x + w / 2, system, w, label="System (evaluator) score", color="#e07b00")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{l}\n(n=5)" for l in labels], fontsize=8)
    ax.legend(fontsize=8)
    ax.set_ylabel("Average score (0-1)", fontsize=9)

    shows = (
        "Average human vs. evaluator score per topic, one question per topic rated 5 times — unchanged\n"
        "from v1."
    )
    conclusion = (
        "Scores do not line up topic by topic; for Arrays the evaluator under-scores (0.55 vs 0.70 human),\n"
        "for the other three topics it over-scores, most notably C_Programming (0.61 vs 0.30). With one\n"
        "question per topic this flags where disagreement concentrates, it does not generalize."
    )
    caveat = (
        "Source is ablation/results/ratings_averaged_real.csv, an earlier small pilot rating set (not the\n"
        "current N=64, 3-rater gold benchmark used on the evaluator-ablation pages above). Treat this page\n"
        "as the same superseded-pilot tier as the old rho=0.6975 result, not current-benchmark evidence."
    )
    add_bottom_text(fig, shows, conclusion, caveat, y0=0.52)
    pdf.savefig(fig)
    plt.close(fig)


def main():
    with PdfPages(OUT_PDF) as pdf:
        page_title(pdf)
        page_evaluator_real(pdf)
        page_evaluator_significance_real(pdf)
        page_rl_attribution_real(pdf)
        page_rl_rho_pipeline_caveated(pdf)
        page_training_convergence(pdf)
        page_guardrail_interventions(pdf)
        page_sensitivity_real(pdf)
        page_topic_wise(pdf)
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    main()
