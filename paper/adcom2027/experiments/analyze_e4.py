"""Analysis of E4 (amendment A2)."""
import csv, json
from collections import defaultdict
from pathlib import Path
from scipy.stats import beta

R = Path(__file__).parents[1] / "results"
rows = [json.loads(l) for l in open(R / "e4_runs.jsonl")]
cell = defaultdict(list)
for r in rows:
    cell[(r["cell"], r["strict"])].append(r)


def cp(k, n):
    return (0.0 if k == 0 else beta.ppf(.025, k, n - k + 1)), (1.0 if k == n else beta.ppf(.975, k + 1, n - k))

out = []
for c in dict.fromkeys(r["cell"] for r in rows):
    for strict in (False, True):
        rs = cell[(c, strict)]
        n = len(rs)
        i1 = sum(r["I1_committed_without_valid_eval"] > 0 for r in rs)
        i1c = sum(r["I1_committed_without_valid_eval"] for r in rs)
        done = sum(r["I4_terminated"] for r in rs)
        out.append({"cell": c, "variant": "S(strict)" if strict else "B(baseline)", "sessions": n,
                    "sessions_with_invalid_commit": i1, "invalid_commits": i1c,
                    "ci_lo": round(cp(i1, n)[0], 3), "ci_hi": round(cp(i1, n)[1], 3),
                    "sessions_terminated": done, "mean_committed_answers": round(sum(r["n_scores"] for r in rs) / n, 2)})
with open(R / "e4_cells.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
# F0 identity
b = {(r["seed"], r["session"]): r for r in cell[("F0", False)]}
s = {(r["seed"], r["session"]): r for r in cell[("F0", True)]}
keys = ["committed_scores", "difficulty_path", "followup_flags", "decision_path", "score_path"]
ident = all(all(b[k][x] == s[k][x] for x in keys) for k in b)
json.dump({"F0_paths_identical_B_vs_S": ident, "sessions": len(b)}, open(R / "e4_f0_identity.json", "w"))
for o in out: print(o)
print("F0 identical:", ident, len(b))
