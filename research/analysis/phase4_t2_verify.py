"""Phase 4 T2 verification: independent recomputation (different code path: pandas/scipy) of the headline numbers from stored per-item data.
Run: python -B research/analysis/phase4_t2_verify.py  (writes research/analysis/PHASE4_T2_VERIFICATION.md)"""
import json, sys, xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "research/tools")); import run_manifest as rm
lines = []; bad = 0
def chk(name, got, want, tol):
    global bad
    ok = abs(got - want) <= tol; bad += (not ok)
    lines.append(f"| {name} | {got:.5f} | {want:.5f} | {tol} | {'PASS' if ok else 'FAIL'} |")
# X3-A primary (pandas groupby, unrounded means)
s = pd.read_csv(REPO / "research/confirmatory/X3-A/results/sessions.csv")
g = s[s.stratum == "grid"]
ppo = g[g.condition == "PPO | G"].groupby(["training_seed", "persona_id"]).mae.mean().unstack(0)   # persona x seed
cs = g[g.condition == "Constant-Same | G"].groupby("persona_id").mae.mean()
D = ppo.sub(cs, axis=0)
dec = json.loads((REPO / "research/confirmatory/X3-A/results/x3a_decision.json").read_text())
chk("X3-A primary mean difference (PPO+G - ConstSame+G)", float(D.values.mean()), dec["point"], 1e-9)
chk("X3-A persona count", float(len(D)), 40.0, 0)
chk("X3-A sessions per grid condition (Constant-Same | G)", float((g.condition == "Constant-Same | G").sum()), 800.0, 0)
fz = s[s.stratum == "frozen"]
chk("X3-A frozen stratum Constant-Same|G MAE (compare X3-0c 0.6728)", float(fz[fz.condition == "Constant-Same | G"].mae.mean()), 0.672727, 5e-4)
# X2-B
sc = pd.read_csv(REPO / "research/confirmatory/X2-B/results/scores.csv")
for k, want in (("derived_ce", 0.4825), ("upstream_ce", 0.1454), ("length_only", 0.4897)):
    chk(f"X2-B Spearman {k} vs human gold", float(spearmanr(sc[k], sc.human_gold)[0]), want, 5e-5)
chk("X2-B derived_ce vs stored R (rank-equal, Spearman = 1 up to clipping ties)", float(spearmanr(sc.derived_ce, sc.ref_R_mapped)[0]), 1.0, 2e-3)
# X1-D
raw = pd.read_csv(REPO / "research/confirmatory/X1-D/results/latency_raw.csv")
w = raw[raw.series == "evaluator_warm"].ms.to_numpy()
chk("X1-D warm evaluator n", float(len(w)), 100.0, 0); chk("X1-D warm evaluator median", float(np.percentile(w, 50)), 236.129, 5e-4)
chk("X1-D SQLite write median", float(np.percentile(raw[raw.series == "sqlite_write"].ms.to_numpy(), 50)), 12.697, 5e-4)
root = ET.parse(REPO / "research/confirmatory/X1-D/results/junit.xml").getroot(); ts = root if root.tag == "testsuite" else root.find("testsuite")
chk("X1-D junit tests", float(ts.get("tests")), 226.0, 0); chk("X1-D junit failures", float(ts.get("failures")), 1.0, 0)
rep = "# Phase 4 T2 verification (independent recomputation)\n\n| Check | Recomputed | Stored/claimed | Tolerance | Result |\n|---|---|---|---|---|\n" + "\n".join(lines) + f"\n\nRESULT: {'PASS' if bad == 0 else 'FAIL'} ({bad} failures)\n"
rm.write_new(REPO / "research/analysis/PHASE4_T2_VERIFICATION.md", rep); print(rep)
