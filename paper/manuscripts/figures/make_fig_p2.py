"""Paper 2 figures (descriptive re-plots of frozen files; no new inference).

Fig. 1 (fig_p2_scatter): composite score vs human reference score for the 64 constructed answers.
  Source: research/results/paper2/paper2_case_level_results.csv (columns human_gold_score [field name],
  model_score, category, gold_method). Groups follow the construction labels used for the AUROC analysis
  (correct-reference: concise_correct, verbose_correct, suboptimal_correct, paraphrase; adversarial:
  keyword_stuffed, misconception, contradictory, incorrect, verbose_wrong; partial_incomplete separate).
  Ring = adjudicated reference score (gold_method != mean_of_three). Spearman is recomputed only to
  print the stored value 0.3812 as a check; the plotted quantity is the raw scores.
Fig. 2 (fig_p2_category_gap): per-category mean human reference vs mean composite (descriptive, n shown).
  Same source; means computed by category; equals Table V of the manuscript.
Fig. 3 (fig_p2_forest): Spearman with the consensus and TWO-LEVEL cluster bootstrap intervals (B=10,000).
  Sources: research/analysis/phase1/x2_a/x2a_bootstrap_rho.csv (composite, R_only, S1, S1_plus_R) and
  research/confirmatory/X2-B/results/metrics_point_ci.csv (baselines). The composite two-level upper
  bound is 0.6490 in X2-A (0.6473 in X2-B; different bootstrap streams); the X2-A value is plotted.
  S2-containing rows are omitted because the stored two-level interval is for S2_eff, not the
  ablation's S2 (0.3021).
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _style import *

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
R = os.path.join(ROOT, "research")
OUT = os.path.dirname(__file__)
d = pd.read_csv(os.path.join(R, "results", "paper2", "paper2_case_level_results.csv"))
d = d.rename(columns={"human_gold_score": "human"})
setup()

# ---------- Fig 1: scatter
GROUP = {**{c: "correct-reference" for c in ["concise_correct", "verbose_correct", "suboptimal_correct", "paraphrase"]},
         **{c: "adversarial" for c in ["keyword_stuffed", "misconception", "contradictory", "incorrect", "verbose_wrong"]},
         "partial_incomplete": "partial"}
STY = {"correct-reference": (BLUE, "o", "correct-reference (22)"), "partial": ("#7f7f7f", "s", "partial (14)"),
       "adversarial": (VERM, "^", "adversarial (34)")}
fig, ax = plt.subplots(figsize=(COL_W, 3.2))
ax.plot([0, 1], [0, 1], color=GRID, lw=0.8, ls="--", zorder=0)
for g, (c, m, lab) in STY.items():
    s = d[d.category.map(GROUP) == g]
    ax.scatter(s.human, s.model_score, s=16, c=c, marker=m, alpha=0.85, edgecolor="white", linewidth=0.4, label=lab, zorder=2)
adj = d[d.gold_method != "mean_of_three"]
ax.scatter(adj.human, adj.model_score, s=48, facecolor="none", edgecolor=INK, linewidth=0.7, label="adjudicated reference (10)", zorder=3)
ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.02)
ax.set_xlabel("Human reference score"); ax.set_ylabel("Composite evaluator score")
ax.grid(True, lw=0.4)
ax.text(0.03, 0.96, "n = 64 answers, 8 questions\nSpearman 0.3812 (stored value)\ndashed line: equality", fontsize=6.2, va="top", color=MUTED)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, frameon=False, handletextpad=0.3, columnspacing=1.0)
save(fig, "fig_p2_scatter", OUT)
from scipy.stats import spearmanr
print("check spearman", round(spearmanr(d.human, d.model_score)[0], 4), "under-scored", int((d.model_score < d.human).sum()))

# ---------- Fig 2: category gap (dumbbell)
g = d.groupby("category").agg(n=("human", "size"), human=("human", "mean"), model=("model_score", "mean")).sort_values("human", ascending=False)
NAMES = {"verbose_correct": "Verbose correct", "concise_correct": "Concise correct", "paraphrase": "Paraphrase",
         "suboptimal_correct": "Suboptimal correct", "partial_incomplete": "Partial / incomplete",
         "keyword_stuffed": "Keyword-stuffed", "contradictory": "Contradictory", "misconception": "Misconception",
         "verbose_wrong": "Verbose wrong", "incorrect": "Incorrect"}
fig, ax = plt.subplots(figsize=(COL_W, 3.0))
y = np.arange(len(g))[::-1]
for yi, (cat, r) in zip(y, g.iterrows()):
    ax.plot([r.model, r.human], [yi, yi], color=GRID, lw=1.6, zorder=1)
    ax.scatter(r.human, yi, s=22, c=INK, marker="o", zorder=3)
    ax.scatter(r.model, yi, s=24, c=VERM, marker="D", zorder=3)
ax.set_yticks(y); ax.set_yticklabels([f"{NAMES[c]} (n={int(r.n)})" for c, r in g.iterrows()])
ax.set_xlim(0, 1.05); ax.set_xlabel("Mean score by category (descriptive; no intervals)")
ax.grid(True, axis="x", lw=0.4)
ax.scatter([], [], s=22, c=INK, marker="o", label="human reference"); ax.scatter([], [], s=24, c=VERM, marker="D", label="composite")
ax.legend(loc="lower right", frameon=False, handletextpad=0.3)
save(fig, "fig_p2_category_gap", OUT)
print(g.round(3).to_string())

# ---------- Fig 3: forest, two-level intervals
a = pd.read_csv(os.path.join(R, "analysis", "phase1", "x2_a", "x2a_bootstrap_rho.csv")).set_index("scorer")
b = pd.read_csv(os.path.join(R, "confirmatory", "X2-B", "results", "metrics_point_ci.csv")).set_index("scorer")
rows = [("Full composite", a.loc["composite", "spearman"], a.loc["composite", "two_level_ci_low"], a.loc["composite", "two_level_ci_high"], "comp"),
        ("Cross-encoder R only", a.loc["R_only", "spearman"], a.loc["R_only", "two_level_ci_low"], a.loc["R_only", "two_level_ci_high"], "comp"),
        ("S1 + R", a.loc["S1_plus_R", "spearman"], a.loc["S1_plus_R", "two_level_ci_low"], a.loc["S1_plus_R", "two_level_ci_high"], "comp"),
        ("S1 only", a.loc["S1", "spearman"], a.loc["S1", "two_level_ci_low"], a.loc["S1", "two_level_ci_high"], "comp"),
        ("Word count", b.loc["length_only", "spearman"], b.loc["length_only", "sp_ci_low"], b.loc["length_only", "sp_ci_high"], "base"),
        ("Reference-token overlap", b.loc["token_overlap", "spearman"], b.loc["token_overlap", "sp_ci_low"], b.loc["token_overlap", "sp_ci_high"], "base"),
        ("BM25", b.loc["bm25", "spearman"], b.loc["bm25", "sp_ci_low"], b.loc["bm25", "sp_ci_high"], "base"),
        ("TF-IDF cosine", b.loc["tfidf", "spearman"], b.loc["tfidf", "sp_ci_low"], b.loc["tfidf", "sp_ci_high"], "base"),
        ("Upstream cross-encoder", b.loc["upstream_ce", "spearman"], b.loc["upstream_ce", "sp_ci_low"], b.loc["upstream_ce", "sp_ci_high"], "base")]
fig, ax = plt.subplots(figsize=(COL_W, 2.9))
yy = np.arange(len(rows))[::-1]
for yi, (lab, p, lo, hi, kind) in zip(yy, rows):
    col, mk = (BLUE, "o") if kind == "comp" else (VERM, "s")
    ax.plot([lo, hi], [yi, yi], color=col, lw=1.2, zorder=2)
    ax.scatter(p, yi, s=20, c=col, marker=mk, zorder=3)
    ax.text(1.02, yi, f"{p:.4f}  [{lo:.4f}, {hi:.4f}]", va="center", fontsize=5.8, color=INK)
ax.axvline(0, color=MUTED, lw=0.6); ax.axvline(a.loc["composite", "spearman"], color=GRID, lw=0.8, ls="--", zorder=0)
ax.set_yticks(yy); ax.set_yticklabels([r[0] for r in rows]); ax.set_xlim(-0.2, 1.0)
ax.set_xlabel("Spearman correlation with human reference score\n(95% two-level question-and-answer cluster intervals)")
ax.grid(True, axis="x", lw=0.4)
ax.scatter([], [], s=20, c=BLUE, marker="o", label="evaluator configurations"); ax.scatter([], [], s=20, c=VERM, marker="s", label="baselines")
ax.legend(loc="upper center", frameon=False, handletextpad=0.3, bbox_to_anchor=(0.45, -0.28), ncol=2)
save(fig, "fig_p2_forest", OUT)
print(pd.DataFrame(rows, columns=["scorer", "rho", "lo", "hi", "kind"]).round(4).to_string())
