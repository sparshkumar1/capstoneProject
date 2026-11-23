"""Figure 2: difficulty path of replay session 0 (fault-free) for the shipped system, without guardrails, and without PPO. Data: results/e1_runs.jsonl."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
import matplotlib.pyplot as plt
R = Path(__file__).parents[1] / "results"
rows = [json.loads(l) for l in open(R / "e1_runs.jsonl")]
get = lambda v: next(r for r in rows if r["fault"] == "F0" and r["variant"] == v and r["session"] == 0)
fig, axes = plt.subplots(1, 3, figsize=(6.4, 1.9), dpi=300, sharey=True)
titles = {"V0": "shipped (PPO + guardrails)", "V2": "no guardrails", "V3": "no PPO (heuristic)"}
for ax, v in zip(axes, ["V0", "V2", "V3"]):
    r = get(v); x = list(range(1, len(r["difficulty_path"]) + 1))
    ax.step(x, r["difficulty_path"], where="post", color="#333333", lw=0.9)
    for xi, d, s in zip(x, r["difficulty_path"], r["decision_path"]):
        m, c = ("s", "#b30000") if s.startswith("guardrail") else (("o", "#1f4e79") if s == "ppo" else (("^", "#7f7f7f")))
        ax.plot(xi, d, m, color=c, ms=3.2)
    ax.set_title(titles[v], fontsize=6.5); ax.set_xlabel("committed turn", fontsize=6.5)
    ax.tick_params(labelsize=6); ax.set_yticks([1, 2, 3, 4, 5]); ax.grid(alpha=.25, lw=.4)
axes[0].set_ylabel("difficulty after turn", fontsize=6.5)
from matplotlib.lines import Line2D
axes[2].legend(handles=[Line2D([], [], marker="o", color="#1f4e79", ls="", ms=3, label="PPO"),
                        Line2D([], [], marker="s", color="#b30000", ls="", ms=3, label="guardrail"),
                        Line2D([], [], marker="^", color="#7f7f7f", ls="", ms=3, label="baseline / heuristic")],
               fontsize=5.2, loc="upper right", frameon=False)
fig.tight_layout()
fig.savefig(Path(__file__).parent / "fig2_difficulty_paths.pdf", bbox_inches="tight"); fig.savefig(Path(__file__).parent / "fig2_difficulty_paths.png", bbox_inches="tight")
