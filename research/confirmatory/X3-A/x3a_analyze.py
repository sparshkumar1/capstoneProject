"""X3-A frozen analysis. Usage:
  python -B x3a_analyze.py --results research/confirmatory/X3-A/results            (confirmatory; primary stratum 'grid')
  python -B x3a_analyze.py --results research/confirmatory/X3-A/dryrun --primary-stratum frozen   (pipeline test on the fixture)
Reads sessions.csv; writes new files next to it (never overwrites). Deterministic given the config seed."""
import argparse
import csv
import io
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "research" / "tools"))
import run_manifest as rm  # noqa: E402

CFG = json.loads((HERE / "x3a_config.json").read_text(encoding="utf-8"))
TSEEDS = [str(s) for s in CFG["training_seeds"]]
PRIM_A, PRIM_B = "PPO | G", "Constant-Same | G"
METRICS = {"mae": "tracking MAE", "volatility": "volatility", "oscillation": "oscillation rate", "oracle_agreement": "oracle agreement (raw action)",
           "activations": "rule activations / session", "overrides": "action overrides / session", "attempted_boundary": "attempted boundary actions / session"}


def load(path, stratum):
    rows = list(csv.DictReader(open(path, encoding="utf-8", newline="")))
    rows = [r for r in rows if r["stratum"] == stratum]
    personas = sorted({r["persona_id"] for r in rows})
    return rows, personas


def cells(rows, personas, metric):
    """dict condition -> array [n_personas, n_seeds or 1] of persona-level means over evaluation seeds"""
    acc = {}
    for r in rows:
        acc.setdefault((r["condition"], r["training_seed"], r["persona_id"]), []).append(float(r[metric]))
    out = {}
    conds = sorted({k[0] for k in acc})
    for c in conds:
        seeds = sorted({k[1] for k in acc if k[0] == c}, key=lambda x: (x == "-", int(x) if x != "-" else 0))
        out[c] = np.array([[np.mean(acc[(c, s, p)]) for s in seeds] for p in personas])
    return out


def diff(A, B):
    """persona x seed matrix of A - B (broadcast: seedless arrays broadcast over seeds)."""
    return A - B


def boot(D, rng, B):
    n, s = D.shape
    stats = np.empty(B)
    for b in range(B):
        pi = rng.integers(0, n, n)
        si = rng.integers(0, s, s) if s > 1 else np.zeros(1, dtype=int)
        stats[b] = D[np.ix_(pi, si)].mean()
    return stats


def summarize(D, rng, B):
    st = boot(D, rng, B)
    lo, hi = np.percentile(st, [2.5, 97.5])
    dp = D.mean(axis=1)
    dz = float(dp.mean() / dp.std(ddof=1)) if len(dp) > 1 and dp.std(ddof=1) > 0 else float("nan")
    return {"point": float(D.mean()), "ci_low": float(lo), "ci_high": float(hi), "n_personas": int(D.shape[0]), "n_train_seeds": int(D.shape[1]),
            "sd_persona_level": float(dp.std(ddof=1)) if len(dp) > 1 else float("nan"), "cohen_dz": dz}


def classify(lo, hi, cfg):
    d, m = cfg["primary"]["delta_equivalence"], cfg["primary"]["m_superiority"]
    if hi < -m:
        return "PPO-superior"
    if lo > d:
        return "PPO-adverse"
    if lo > -d and hi < d:
        return "Equivalent"
    return "Inconclusive"


def wcsv(out_dir, name, rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return rm.write_new(out_dir / name, buf.getvalue())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--primary-stratum", default="grid")
    a = ap.parse_args()
    out = Path(a.results).resolve()
    B, seed = CFG["bootstrap"]["B"], CFG["bootstrap"]["seed"]
    rng = np.random.default_rng(seed)
    man = rm.Manifest("X3-A-analysis" + ("" if a.primary_stratum == "grid" else "-fixture"), out, __file__, config_path=HERE / "x3a_config.json",
                      seeds={"bootstrap": seed, "B": B}, lock_id=CFG["lock_id"], protocol={"type": "prereg_git_tag" if a.primary_stratum == "grid" else "fixture", "tag": CFG["protocol_tag"]})
    man.add_inputs([out / "sessions.csv"])
    rows, personas = load(out / "sessions.csv", a.primary_stratum)
    C = {m: cells(rows, personas, m) for m in METRICS}
    outs = []

    # ---- primary
    A, Bm = C["mae"][PRIM_A], C["mae"][PRIM_B]
    D = diff(A, Bm)                     # broadcast (n,5) - (n,1)
    prim = summarize(D, rng, B)
    cls = classify(prim["ci_low"], prim["ci_high"], CFG)
    trigger = cls != "Equivalent"
    decision = {"primary_stratum": a.primary_stratum, "contrast": f"{PRIM_A} minus {PRIM_B}", "endpoint": "persona-level tracking MAE difference", **prim,
                "delta": CFG["primary"]["delta_equivalence"], "m": CFG["primary"]["m_superiority"], "classification": cls,
                "x3b_trigger_fires": trigger,
                "x3b_note": "if true, X3-B additionally requires decision D-N2 (user); otherwise no method-level PPO claim is made",
                "interpretation_rule": {"Equivalent": "no detectable PPO contribution beyond the shield in these checkpoints (equivalence within +/-0.12 MAE)",
                                        "PPO-superior": "claim about these checkpoints only; a method-level claim requires X3-B",
                                        "PPO-adverse": "PPO+G is worse than a state-blind action with the same shield; reported",
                                        "Inconclusive": "never reported as 'no effect'"}[cls]}
    outs.append(rm.write_new(out / "x3a_decision.json", json.dumps(decision, indent=2)))
    prim_rows = [{"metric": "PRIMARY tracking MAE", "point": round(prim["point"], 5), "ci_low": round(prim["ci_low"], 5), "ci_high": round(prim["ci_high"], 5),
                  "classification": cls, "n_personas": prim["n_personas"], "n_train_seeds": prim["n_train_seeds"], "sd_persona_level": round(prim["sd_persona_level"], 5), "cohen_dz": round(prim["cohen_dz"], 3)}]
    for m in ("volatility", "oscillation", "oracle_agreement", "activations", "overrides", "attempted_boundary"):
        s = summarize(diff(C[m][PRIM_A], C[m][PRIM_B]), rng, B)
        prim_rows.append({"metric": f"secondary {METRICS[m]}", "point": round(s["point"], 5), "ci_low": round(s["ci_low"], 5), "ci_high": round(s["ci_high"], 5),
                          "classification": "descriptive", "n_personas": s["n_personas"], "n_train_seeds": s["n_train_seeds"], "sd_persona_level": round(s["sd_persona_level"], 5), "cohen_dz": round(s["cohen_dz"], 3)})
    outs.append(wcsv(out, "x3a_primary_and_secondary_metrics.csv", prim_rows))

    # ---- secondary contrasts (MAE and volatility), descriptive
    sec = []
    for x, y in CFG["secondary_contrasts"]:
        for m in ("mae", "volatility"):
            s = summarize(diff(C[m][x], C[m][y]), rng, B)
            sec.append({"contrast": f"{x} minus {y}", "metric": m, "point": round(s["point"], 5), "ci_low": round(s["ci_low"], 5), "ci_high": round(s["ci_high"], 5), "n_personas": s["n_personas"], "n_train_seeds": s["n_train_seeds"], "label": "descriptive (no error control)"})
    for pol_a, pol_b in (("PPO", "Constant-Same"),):
        for r in CFG["conditions"]["ppo"]["ablation_rules"]:
            s = summarize(diff(C["mae"][f"PPO | G-minus-{r}"], C["mae"]["PPO | G"]), rng, B)
            sec.append({"contrast": f"PPO | G-minus-{r} minus PPO | G", "metric": "mae", "point": round(s["point"], 5), "ci_low": round(s["ci_low"], 5), "ci_high": round(s["ci_high"], 5), "n_personas": s["n_personas"], "n_train_seeds": s["n_train_seeds"], "label": "descriptive rule ablation"})
            s = summarize(diff(C["mae"][f"Constant-Same | G-minus-{r}"], C["mae"]["Constant-Same | G"]), rng, B)
            sec.append({"contrast": f"Constant-Same | G-minus-{r} minus Constant-Same | G", "metric": "mae", "point": round(s["point"], 5), "ci_low": round(s["ci_low"], 5), "ci_high": round(s["ci_high"], 5), "n_personas": s["n_personas"], "n_train_seeds": s["n_train_seeds"], "label": "descriptive rule ablation"})
    outs.append(wcsv(out, "x3a_secondary_contrasts.csv", sec))

    # ---- condition summary
    cs = []
    for c in sorted(C["mae"]):
        r = {"condition": c, "n_train_seeds": C["mae"][c].shape[1]}
        for m in METRICS:
            r[m] = round(float(C[m][c].mean()), 5)
        cs.append(r)
    outs.append(wcsv(out, "x3a_condition_summary.csv", cs))

    # ---- strata / persona types (descriptive) for the primary contrast
    pid_index = {p: i for i, p in enumerate(personas)}
    strata = []
    def sub(name, sel):
        idx = [pid_index[p] for p in personas if sel(p)]
        if not idx:
            return
        s = summarize(D[idx], rng, B)
        strata.append({"subset": name, "n_personas": len(idx), "point": round(s["point"], 5), "ci_low": round(s["ci_low"], 5), "ci_high": round(s["ci_high"], 5), "label": "descriptive; not part of the primary classification"})
    sub("all personas of the primary stratum", lambda p: True)
    sub("training-matched persona normal@0.60 only", lambda p: p == "normal@0.60")
    sub("all except normal@0.60", lambda p: p != "normal@0.60")
    for t in CFG["persona_generator"]["types"]:
        sub(f"persona type {t}", lambda p, t=t: p.startswith(t + "@"))
    for lo_s, hi_s, nm in ((0.2, 0.4, "skill 0.20-0.40"), (0.5, 0.7, "skill 0.50-0.70"), (0.8, 0.9, "skill 0.80-0.90")):
        sub(nm, lambda p, lo_s=lo_s, hi_s=hi_s: "@" in p and lo_s - 1e-9 <= float(p.split("@")[1]) <= hi_s + 1e-9)
    if a.primary_stratum == "grid":
        frows, fpers = load(out / "sessions.csv", "frozen")
        Cf = cells(frows, fpers, "mae")
        s = summarize(diff(Cf[PRIM_A], Cf[PRIM_B]), rng, B)
        strata.append({"subset": "frozen 5-persona stratum (already-seen personas)", "n_personas": len(fpers), "point": round(s["point"], 5), "ci_low": round(s["ci_low"], 5), "ci_high": round(s["ci_high"], 5), "label": "descriptive; reproduces the X3-0 accounting"})
    outs.append(wcsv(out, "x3a_strata_descriptive.csv", strata))

    rep = f"""# X3-A analysis report ({'CONFIRMATORY' if a.primary_stratum == 'grid' else 'PIPELINE-TEST FIXTURE - not a result'})

Primary contrast: {PRIM_A} minus {PRIM_B}; unit = persona ({prim['n_personas']} in stratum '{a.primary_stratum}'); training seed second random factor ({prim['n_train_seeds']} seeds); two-way cluster bootstrap B={B}, seed {seed}; 95 % percentile CI.

| Quantity | Value |
|---|---|
| Mean paired difference (MAE units) | {prim['point']:.5f} |
| 95 % CI | [{prim['ci_low']:.5f}, {prim['ci_high']:.5f}] |
| SD of persona-level differences | {prim['sd_persona_level']:.5f} |
| Cohen d_z (persona level) | {prim['cohen_dz']:.3f} |
| Equivalence margin delta / superiority margin m | {CFG['primary']['delta_equivalence']} / {CFG['primary']['m_superiority']} |
| **Classification** | **{cls}** |
| X3-B trigger fires | {trigger} |

Interpretation rule: {decision['interpretation_rule']}.
Secondary metrics, contrasts, rule ablations and strata are DESCRIPTIVE (no multiplicity control); see `x3a_primary_and_secondary_metrics.csv`, `x3a_secondary_contrasts.csv`, `x3a_condition_summary.csv`, `x3a_strata_descriptive.csv`.
"""
    outs.append(rm.write_new(out / "X3A_ANALYSIS_REPORT.md", rep))
    print(man.finish(outs))
    print(rep)


if __name__ == "__main__":
    main()
