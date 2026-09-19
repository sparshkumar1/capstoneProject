"""Phase 4 registry update: appends rows for the completed new experiments (X3-A, X2-B old-benchmark arm, X1-D).
Every value is read from a stored result file and asserted; artifact hashes are computed here. Refuses a second run.
Run: python -B research/analysis/phase4_registry_update.py"""
import csv
import hashlib
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REG = REPO / "research" / "claims" / "CLAIM_REGISTRY.csv"
DATE = "2026-09-19"
HEAD = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def sha(p):
    return hashlib.sha256((REPO / p).read_bytes()).hexdigest()


def rd(p):
    with open(REPO / p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


with open(REG, encoding="utf-8", newline="") as f:
    rdr = csv.DictReader(f)
    FIELDS = rdr.fieldnames
    rows = list(rdr)
assert "X3A-C001" not in {r["claim_id"] for r in rows}, "already updated"
new = []


def tag_commit(t):
    return subprocess.run(["git", "-C", str(REPO), "rev-list", "-n", "1", t], capture_output=True, text=True).stdout.strip()


def add(cid, paper, status, wording, value, unit, ci, artifact, script, config, lock, seed, notes, tag, verify=None, label="NEW-FROZEN"):
    verify = verify or f"rerun {script} at the tagged commit in the locked environment and compare {artifact} (T3); T1: hash of the artifact"
    new.append({"claim_id": cid, "paper": paper, "status": status, "claim_wording": wording, "value": value, "unit_or_n": unit, "ci_or_spread": ci,
                "evidence_label": label, "artifact_path": artifact, "artifact_sha256": sha(artifact), "script_path": script,
                "script_commit": tag_commit(tag) if tag else HEAD, "config_path": config, "env_lock_sha256": lock, "seed_set": seed,
                "recompute_tier": "T3", "verify_cmd": verify, "superseded_by": "", "last_verified": DATE, "notes": notes})


# ------------------------------------------------------------------ X3-A
X3 = "research/confirmatory/X3-A/results/"
LOCK3 = sha("research/locks/LOCK-X3-2026-09-19.lock.json")
dec = json.loads((REPO / X3 / "x3a_decision.json").read_text(encoding="utf-8"))
assert dec["classification"] == "Equivalent" and dec["x3b_trigger_fires"] is False and dec["n_personas"] == 40 and dec["n_train_seeds"] == 5
KW = dict(script="research/confirmatory/X3-A/x3a_run.py", config="research/confirmatory/X3-A/x3a_config.json", lock=LOCK3,
          seed="training 42/123/456/789/999; evaluation 1001..20020 (20); bootstrap 42 B=10000", tag="prereg/X3-A/v1")
NOTE3 = "Confirmatory X3-A under tag prereg/X3-A/v1 (frozen checkpoints, 40 grid personas, simulation only; PPO trained on a single unseeded candidate with the shield in the loop, X3-0b). Run env LOCK-X3-2026-09-19; gate G-HARNESS 9/9. "
add("X3A-C001", "3", "VALID", f"Persona-level tracking-MAE difference PPO+G minus Constant-Same+G = {dec['point']:.4f} (two-way cluster bootstrap 95 percent CI [{dec['ci_low']:.4f}, {dec['ci_high']:.4f}]; 40 personas x 5 training seeds); classification EQUIVALENT within +/-0.12 MAE: no detectable PPO contribution beyond the shield in these checkpoints in this simulator.",
    f"{dec['point']:.4f}", "40 personas x 5 training seeds", f"[{dec['ci_low']:.4f}, {dec['ci_high']:.4f}]", X3 + "x3a_decision.json", verify="python -B x3a_analyze.py --results research/confirmatory/X3-A/results (needs sessions.csv from x3a_run.py)",
    notes=NOTE3 + "Pre-registered primary endpoint. Equivalence is not superiority; the CI touches but does not cross zero on the upper side (+0.0021). X3-B not triggered. Not a method-level PPO claim.", **KW)
sec = {(r["contrast"], r["metric"]): r for r in rd(X3 + "x3a_secondary_contrasts.csv")}
pm = {r["metric"]: r for r in rd(X3 + "x3a_primary_and_secondary_metrics.csv")}
v = pm["secondary volatility"]
o = pm["secondary oscillation rate"]
add("X3A-C002", "3", "VALID", f"Under the same shield PPO is more volatile than a constant Same action: volatility difference {v['point']} [{v['ci_low']}, {v['ci_high']}], oscillation difference {o['point']} [{o['ci_low']}, {o['ci_high']}] (PPO+G minus Constant-Same+G).",
    v["point"], "40 personas x 5 seeds", f"[{v['ci_low']}, {v['ci_high']}]", X3 + "x3a_primary_and_secondary_metrics.csv", notes=NOTE3 + "DESCRIPTIVE secondary endpoint (no error control); tracking MAE alone hides this (P3-C023).", **KW)
s1 = sec[("Constant-Same | G minus Constant-Same | off", "mae")]
cs = {r["condition"]: r for r in rd(X3 + "x3a_condition_summary.csv")}
add("X3A-C003", "3", "VALID", f"On the 40-persona grid the shield did not improve tracking of a constant Same action: MAE {float(cs['Constant-Same | G']['mae']):.3f} with shield vs {float(cs['Constant-Same | off']['mae']):.3f} without (difference {s1['point']} [{s1['ci_low']}, {s1['ci_high']}]); the frozen five-persona benefit (1.200 -> 0.673) does not generalise across this persona set.",
    s1["point"], "40 personas (persona bootstrap only)", f"[{s1['ci_low']}, {s1['ci_high']}]", X3 + "x3a_secondary_contrasts.csv", notes=NOTE3 + "DESCRIPTIVE; the interval includes zero; the effect of the shield is persona-set dependent.", **KW)
z, sh_ = sec[("PPO-state-zero | G minus PPO | G", "mae")], sec[("PPO-state-shuffle | G minus PPO | G", "mae")]
add("X3A-C004", "3", "VALID", f"PPO uses its state observation: replacing the observation by zeros raises MAE by {z['point']} [{z['ci_low']}, {z['ci_high']}] and by a partner persona's observation by {sh_['point']} [{sh_['ci_low']}, {sh_['ci_high']}] (shield on).",
    z["point"], "40 personas x 5 seeds", f"[{z['ci_low']}, {z['ci_high']}]", X3 + "x3a_secondary_contrasts.csv", notes=NOTE3 + "DESCRIPTIVE control; state use does not imply better tracking than Constant-Same+G (X3A-C001).", **KW)
h, c_, orc = sec[("PPO | G minus Heuristic | G", "mae")], sec[("PPO | G minus Controller | G", "mae")], sec[("PPO | G minus Oracle-rule | G", "mae")]
hg = sec[("Heuristic | G minus Constant-Same | G", "mae")]
add("X3A-C005", "3", "VALID", f"On the grid, PPO+G has lower MAE than the frozen heuristic+G ({h['point']} [{h['ci_low']}, {h['ci_high']}]) and the proportional controller+G ({c_['point']} [{c_['ci_low']}, {c_['ci_high']}]) and is not distinguishable from oracle-rule+G ({orc['point']} [{orc['ci_low']}, {orc['ci_high']}]); the heuristic is worse than Constant-Same+G ({hg['point']} [{hg['ci_low']}, {hg['ci_high']}]), unlike on the frozen five personas.",
    h["point"], "40 personas x 5 seeds", f"[{h['ci_low']}, {h['ci_high']}]", X3 + "x3a_secondary_contrasts.csv", notes=NOTE3 + "DESCRIPTIVE; the controller is an upper reference that exploits the persona-target rule.", **KW)
g1p, g1c = sec[("PPO | G-minus-G1 minus PPO | G", "mae")], sec[("Constant-Same | G-minus-G1 minus Constant-Same | G", "mae")]
add("X3A-C006", "3", "VALID", f"Rule ablation: removing G1 (overload protection) lowers MAE by {abs(float(g1p['point'])):.3f} for PPO+G [{g1p['ci_low']}, {g1p['ci_high']}] and {abs(float(g1c['point'])):.3f} for Constant-Same+G [{g1c['ci_low']}, {g1c['ci_high']}]; removing G2, G4, G5 or G6 changes MAE by less than 0.03.",
    g1p["point"], "40 personas", f"[{g1p['ci_low']}, {g1p['ci_high']}]", X3 + "x3a_secondary_contrasts.csv", notes=NOTE3 + "DESCRIPTIVE; intervals include zero for G1.", **KW)
fz = [r for r in rd(X3 + "x3a_strata_descriptive.csv") if r["subset"].startswith("frozen")][0]
add("X3A-C007", "3", "VALID", f"On the five frozen personas (already-seen stratum) the primary contrast is {fz['point']} [{fz['ci_low']}, {fz['ci_high']}], reproducing the X3-0 accounting; it is not part of the primary estimate.",
    fz["point"], "5 personas x 5 seeds x 20 evaluation seeds", f"[{fz['ci_low']}, {fz['ci_high']}]", X3 + "x3a_strata_descriptive.csv", notes=NOTE3 + "DESCRIPTIVE.", **KW)

# ------------------------------------------------------------------ X2-B
X2 = "research/confirmatory/X2-B/results/"
LOCK2 = sha("research/locks/LOCK-X2-2026-09-19.lock.json")
K2 = dict(script="research/confirmatory/X2-B/x2b_run.py", config="research/confirmatory/X2-B/x2b_config.json", lock=LOCK2, seed="bootstrap 42 (B=10000); permutation 43 (10000)", tag="prereg/X2-B/v2")
N2 = "X2-B old-benchmark EXPLORATORY arm (64 constructed answers, 8 questions; derived-model results already known) under tag prereg/X2-B/v2; env LOCK-X2-2026-09-19; gates G-MODEL-HASH, G-METRIC-CONTROLS, G-DERIVED-REPRO passed (max diff 0.0005). No composite/MAE for the upstream arm. Descriptive; no multiplicity control. "
met = {r["scorer"]: r for r in rd(X2 + "metrics_point_ci.csv")}
pdf = {(r["contrast"], r["metric"]): r for r in rd(X2 + "paired_differences.csv")}
pn = {r["scorer"]: r for r in rd(X2 + "permutation_null.csv")}
d, u, ln = met["derived_ce"], met["upstream_ce"], met["length_only"]
pr, pt, pa = pdf[("derived_ce - upstream_ce", "spearman")], pdf[("derived_ce - upstream_ce", "kendall_tau_b")], pdf[("derived_ce - upstream_ce", "auroc")]
assert float(pr["ci_low"]) > 0 and float(pa["ci_low"]) > 0
add("X2B-C001", "2", "EXPLORATORY", f"On the old 64-case benchmark the derived CrossEncoder agrees better with the human gold than the public upstream checkpoint on identical inputs: Spearman difference {pr['point']} [{pr['ci_low']}, {pr['ci_high']}], Kendall tau-b {pt['point']} [{pt['ci_low']}, {pt['ci_high']}], AUROC (correct vs adversarial) {pa['point']} [{pa['ci_low']}, {pa['ci_high']}] (two-level cluster bootstrap, 8 questions).",
    pr["point"], "64 answers / 8 questions", f"[{pr['ci_low']}, {pr['ci_high']}]", X2 + "paired_differences.csv", notes=N2 + "Primary mapping-independent comparison. Suggests the undocumented fine-tune is material on this data; leakage or shared construction cannot be excluded (tuning provenance unknown). Wording remains 'partially fine-tuned derivative with incomplete provenance'.", **K2)
add("X2B-C002", "2", "EXPLORATORY", f"Upstream CrossEncoder on the old benchmark: Spearman {u['spearman']} [{u['sp_ci_low']}, {u['sp_ci_high']}], AUROC {u['auroc_correct_vs_adversarial']} [{u['auc_ci_low']}, {u['auc_ci_high']}]; one-sided within-question permutation p {pn['upstream_ce']['one_sided_perm_p']} (null 95th percentile {pn['upstream_ce']['null_95th_percentile']}).",
    u["spearman"], "64 answers / 8 questions", f"[{u['sp_ci_low']}, {u['sp_ci_high']}]", X2 + "metrics_point_ci.csv", notes=N2, **K2)
dl = pdf[("derived_ce - length_only", "spearman")]
dla = pdf[("derived_ce - length_only", "auroc")]
add("X2B-C003", "2", "EXPLORATORY", f"A length-only baseline (candidate word count) matches or exceeds the derived CrossEncoder on this benchmark: Spearman {ln['spearman']} [{ln['sp_ci_low']}, {ln['sp_ci_high']}] vs derived {d['spearman']}; AUROC {ln['auroc_correct_vs_adversarial']} [{ln['auc_ci_low']}, {ln['auc_ci_high']}] vs derived {d['auroc_correct_vs_adversarial']}; derived minus length-only Spearman {dl['point']} [{dl['ci_low']}, {dl['ci_high']}], AUROC {dla['point']} [{dla['ci_low']}, {dla['ci_high']}].",
    ln["spearman"], "64 answers / 8 questions", f"[{ln['sp_ci_low']}, {ln['sp_ci_high']}]", X2 + "metrics_point_ci.csv", notes=N2 + "The old benchmark does not show that R (or the composite) beats a trivial length baseline; construction (correct answers longer) is a plausible confound. Any statement that R 'adds evidence beyond surface features' needs X2-C.", **K2)
b, t, to = met["bm25"], met["tfidf"], met["token_overlap"]
add("X2B-C004", "2", "EXPLORATORY", f"Lexical baselines on the old benchmark: BM25 Spearman {b['spearman']} (AUROC {b['auroc_correct_vs_adversarial']}); TF-IDF {t['spearman']} ({t['auroc_correct_vs_adversarial']}); reference-token overlap {to['spearman']} ({to['auroc_correct_vs_adversarial']}); derived CrossEncoder {d['spearman']} ({d['auroc_correct_vs_adversarial']}).",
    b["spearman"], "64 answers / 8 questions", "see metrics_point_ci.csv", X2 + "metrics_point_ci.csv", notes=N2, **K2)

# ------------------------------------------------------------------ X1-D (if the run completed)
X1 = "research/confirmatory/X1-D/results/"
if (REPO / X1 / "test_report_summary.json").exists():
    ts = json.loads((REPO / X1 / "test_report_summary.json").read_text(encoding="utf-8"))
    ls = {(r["series"], r["stat"]): r for r in rd(X1 + "latency_stats.csv")}
    raw = rd(X1 + "latency_raw.csv")
    first = [r for r in raw if r["series"] == "evaluator_first_request"][0]["ms"]
    load = [r for r in raw if r["series"] == "asset_load"][0]["ms"]
    K1 = dict(script="research/confirmatory/X1-D/x1d_run.py", config="research/confirmatory/X1-D/x1d_config.json", lock="NOT_LOCKED (SUT project .venv; versions in the run manifest)", seed="bootstrap 42", tag="prereg/X1-D/v1")
    N1 = "X1-D under tag prereg/X1-D/v1, SUT sut/X1/build-A; single machine; unlocked SUT environment. "
    add("X1D-C001", "1", "VALID", f"Full test suite at SUT build A (EVALUATOR_MOCK_MODE=1, no early stop): {ts['tests']} tests, {ts['failures']} failures, {ts['errors']} errors, {ts['skipped']} skipped; failed IDs: {'; '.join(ts['failed_tests']) or 'none'}.",
        f"{ts['tests']} / {ts['failures']} / {ts['errors']} / {ts['skipped']}", "tests / failures / errors / skipped", "", X1 + "test_report_summary.json", notes=N1 + "Stored JUnit XML and console output. Replaces the withdrawn '213 tests passed, 0 failed'. Mocked-failure tests are not fault-injection evidence.", label="NEW-FROZEN", **K1)
    m_, p95, p99 = ls[("evaluator_warm", "median")], ls[("evaluator_warm", "p95")], ls[("evaluator_warm", "p99")]
    add("X1D-C002", "1", "VALID", f"Warm evaluator latency (N=100 requests after one cold request; in-process): median {m_['value_ms']} ms [{m_['ci_low_ms']}, {m_['ci_high_ms']}], P95 {p95['value_ms']} ms [{p95['ci_low_ms']}, {p95['ci_high_ms']}], P99 {p99['value_ms']} ms; cold first request {float(first):.1f} ms and asset load {float(load):.1f} ms reported separately.",
        m_["value_ms"], "100 warm requests", f"[{m_['ci_low_ms']}, {m_['ci_high_ms']}]", X1 + "latency_stats.csv", notes=N1 + "Raw per-request values in latency_raw.csv; P99 with N=100 is set by the two largest samples; no SLA defined; scope: stored benchmark answers, one process.", label="NEW-FROZEN", **K1)
    w = ls[("sqlite_write", "median")]
    w95 = ls[("sqlite_write", "p95")]
    add("X1D-C003", "1", "VALID", f"Uncontended single-writer SQLite save_attempt latency (N=100): median {w['value_ms']} ms [{w['ci_low_ms']}, {w['ci_high_ms']}], P95 {w95['value_ms']} ms [{w95['ci_low_ms']}, {w95['ci_high_ms']}].",
        w["value_ms"], "100 sequential writes", f"[{w['ci_low_ms']}, {w['ci_high_ms']}]", X1 + "latency_stats.csv", notes=N1 + "Not a concurrency figure (see P1S rows for the frozen 25-session measurement).", label="NEW-FROZEN", **K1)

with open(REG, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS, quoting=csv.QUOTE_ALL, lineterminator="\n")
    w.writeheader()
    w.writerows(rows + new)
print(len(rows), "->", len(rows) + len(new), [r["claim_id"] for r in new])
