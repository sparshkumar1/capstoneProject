"""X2-B runner (old-benchmark exploratory arm): derived vs upstream CrossEncoder and lexical/length baselines.
Run in envs/LOCK-X2-2026-09-19:  envs/LOCK-X2-2026-09-19/Scripts/python.exe -B research/confirmatory/X2-B/x2b_run.py
Single run; refuses to start if results/ exists; verifies lock + protocol tag + hashes + gates before any upstream output is produced."""
import csv
import io
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from scipy.stats import kendalltau, rankdata  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "research" / "tools"))
import run_manifest as rm  # noqa: E402

CFG_PATH = HERE / "x2b_config.json"
CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
PREREG = REPO / "research" / "preregistration" / "X2-B"
SELFTEST = "--selftest" in sys.argv
OUT = (Path(os.environ["X2B_SELFTEST_DIR"]) if SELFTEST else HERE / "results")


class _StubManifest:
    def __init__(self, *a, **k): self.d = {"failures": []}
    def add_inputs(self, *a): pass
    def set_gate(self, *a): pass
    def note(self, *a, **k): print("NOTE", a)
    def finish(self, outs, status="completed"): return status + " (selftest, no manifest)"


def _write_new(path, text):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        raise FileExistsError(p)
    p.write_text(text, encoding="utf-8")
    return p


def sha(p):
    return rm.sha256_file(p)


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()


def verify_lock():
    import importlib.metadata as md
    lock = json.loads((REPO / CFG["lock_files"]["lock_json"]).read_text(encoding="utf-8"))
    req = (REPO / CFG["lock_files"]["requirements"]).read_text(encoding="utf-8")
    assert sha(REPO / CFG["lock_files"]["requirements"]) == lock["requirements_sha256"]
    norm = lambda n: re.sub(r"[-_.]+", "-", n).lower()
    have = {norm(d.metadata["Name"]): d.version for d in md.distributions()}
    bad = [(m.group(1), m.group(2), have.get(norm(m.group(1)))) for m in re.finditer(r"^([A-Za-z0-9_.\-]+)==([^\s\\]+)", req, flags=re.M) if have.get(norm(m.group(1))) != m.group(2)]
    assert not bad, f"installed packages differ from lock: {bad}"
    return sha(REPO / CFG["lock_files"]["lock_json"])


def verify_protocol():
    man = json.loads((PREREG / "protocol_manifest.json").read_text(encoding="utf-8"))
    for rel, h in man["files"].items():
        assert sha(REPO / rel) == h, f"protocol dependency changed: {rel}"
    tag = CFG["protocol_tag"]
    tc = git("rev-list", "-n", "1", tag)
    assert tc, f"tag {tag} missing"
    assert subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", tc, "HEAD"]).returncode == 0
    msg = git("tag", "-l", "--format=%(contents)", tag)
    assert sha(PREREG / "PROTOCOL.md") in msg and sha(PREREG / "protocol_manifest.json") in msg
    return {"type": "prereg_git_tag", "tag": tag, "tag_commit": tc, "protocol_path": "research/preregistration/X2-B/PROTOCOL.md",
            "protocol_sha256": sha(PREREG / "PROTOCOL.md"), "protocol_manifest_sha256": sha(PREREG / "protocol_manifest.json")}


# ---------------------------------------------------------------- statistics
def spear(x, y):
    if np.ptp(x) == 0 or np.ptp(y) == 0:
        return float("nan")
    return float(np.corrcoef(rankdata(x), rankdata(y))[0, 1])


def kend(x, y):
    if np.ptp(x) == 0 or np.ptp(y) == 0:
        return float("nan")
    return float(kendalltau(x, y)[0])


def auroc(pos, neg):
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    r = rankdata(np.concatenate([pos, neg]))
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2.0) / (len(pos) * len(neg)))


def metric_controls():
    x = np.arange(20.0)
    ok = abs(spear(x, x) - 1) < 1e-12 and abs(spear(x, -x) + 1) < 1e-12 and abs(kend(x, x) - 1) < 1e-12
    ok &= abs(auroc(np.array([2.0, 3.0]), np.array([0.0, 1.0])) - 1) < 1e-12 and abs(auroc(np.array([1.0]), np.array([1.0])) - 0.5) < 1e-12
    ok &= math.isnan(spear(np.ones(5), x[:5]))
    return bool(ok)


def tok(s):
    return re.findall(r"[a-z0-9]+", s.lower())


def bm25_scores(ref_tokens, docs_tokens, k1=1.5, b=0.75):
    N = len(docs_tokens)
    avgdl = np.mean([len(d) for d in docs_tokens])
    q = sorted(set(ref_tokens))
    df = {t: sum(1 for d in docs_tokens if t in set(d)) for t in q}
    out = []
    for d in docs_tokens:
        tf = {}
        for t in d:
            tf[t] = tf.get(t, 0) + 1
        s = 0.0
        for t in q:
            if df[t] == 0 or t not in tf:
                continue
            idf = math.log(1 + (N - df[t] + 0.5) / (df[t] + 0.5))
            s += idf * tf[t] * (k1 + 1) / (tf[t] + k1 * (1 - b + b * len(d) / avgdl))
        out.append(s)
    return np.array(out)


def two_level_draw(rng, q_index):
    qs = rng.integers(0, len(q_index), len(q_index))
    return np.concatenate([rng.choice(q_index[q], size=len(q_index[q]), replace=True) for q in qs])


def wcsv(name, rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return (_write_new if SELFTEST else rm.write_new)(OUT / name, buf.getvalue())


def main():
    import pandas as pd
    if OUT.exists():
        raise SystemExit("refusing to run: results/ already exists (no silent reruns)")
    lock_hash = verify_lock()
    protocol = {"type": "selftest"} if SELFTEST else verify_protocol()
    m = (_StubManifest if SELFTEST else rm.Manifest)("X2-B-run", OUT, __file__, config_path=CFG_PATH, protocol=protocol, lock_id=CFG["lock_id"], env_lock_sha256=lock_hash,
                    seeds=CFG["seeds"], gate={"name": "G-DERIVED-REPRO", "passed": None, "details": "pending"})
    inp = CFG["inputs"]
    m.add_inputs([REPO / inp[k] for k in inp])
    dm = REPO / CFG["models"]["derived"]["dir"]
    um = Path(CFG["models"]["upstream"]["dir"])
    m.add_inputs([dm / "model.safetensors"])
    if not SELFTEST:  # the upstream weights live in the external HF cache (outside the repository): recorded as a model entry, not a repo input
        m.d["models"].append({"role": "upstream_ce (external HF cache, read-only)", "path": str(um / "model.safetensors"), "sha256": sha(um / "model.safetensors"), "training_seed": None})
    gates = []
    # G-MODEL-HASH
    h_der, h_up = sha(dm / "model.safetensors"), sha(um / "model.safetensors")
    g1 = h_der == CFG["models"]["derived"]["sha256_model"] and h_up.startswith(CFG["models"]["upstream"]["sha256_model_prefix"])
    gates.append({"gate": "G-MODEL-HASH", "passed": g1, "detail": f"derived {h_der[:12]}..., upstream {h_up[:12]}..."})
    g2 = metric_controls()
    gates.append({"gate": "G-METRIC-CONTROLS", "passed": g2, "detail": "monotone/reversed/constant synthetic controls"})
    outs = []
    if not (g1 and g2):
        outs.append(wcsv("gates.csv", gates))
        m.note("pre-scoring gate failed; no model output produced", failure=True)
        print(m.finish(outs, status="failed"))
        raise SystemExit(1)

    cl = pd.read_csv(REPO / inp["case_level"])
    with open(REPO / inp["texts"], encoding="utf-8-sig", newline="") as f:
        texts = {r["item_id"]: r for r in csv.DictReader(f)}
    rub = {str(r["qid"]): r for r in json.loads((REPO / inp["rubrics"]).read_text(encoding="utf-8"))}
    ref_texts, cands = [], []
    for _, r in cl.iterrows():
        t = texts[r["case_id"]]
        ans = str(rub[str(r["qid"])].get("answer") or rub[str(r["qid"])].get("reference_answer") or "")
        ref_texts.append((t["question"] + " " + ans).strip())
        cands.append(t["candidate_answer"])
    n = len(cl)
    if SELFTEST:
        # derived-model reproduction on the real items is allowed pre-tag (already-known values); everything else uses SYNTHETIC text
        from sentence_transformers import CrossEncoder as _CE
        _rd = np.array(_CE(str(dm)).predict(list(zip(ref_texts, cands)), batch_size=16, show_progress_bar=False), dtype=float)
        print("SELFTEST derived-repro max diff:", float(np.max(np.abs(np.clip((_rd - 0.2) / 0.7, 0, 1) - cl["R"].to_numpy()))))
        srng = np.random.default_rng(5)
        words = ["array", "hash", "stack", "queue", "tree", "graph", "sort", "loop", "cache", "index", "node", "pointer", "memory", "thread"]
        mk = lambda k: " ".join(srng.choice(words, size=k))
        ref_texts = [mk(12) for _ in range(n)]
        cands = [mk(int(srng.integers(5, 40))) for _ in range(n)]
        cl = cl.copy()
        cl["human_gold_score"] = srng.random(n)
        for c in ("R", "S1", "S2_eff", "final_score"):
            cl[c] = srng.random(n)
    gold = cl["human_gold_score"].to_numpy()

    from sentence_transformers import CrossEncoder
    raw_d = np.array(CrossEncoder(str(dm)).predict(list(zip(ref_texts, cands)), batch_size=16, show_progress_bar=False), dtype=float)
    R_map = np.clip((raw_d - 0.20) / 0.70, 0.0, 1.0)
    maxdiff = float(np.max(np.abs(R_map - cl["R"].to_numpy())))
    g3 = (maxdiff <= 0.002) or SELFTEST  # selftest: the real-data reproduction was printed above; synthetic items have no stored R
    gates.append({"gate": "G-DERIVED-REPRO", "passed": g3, "detail": f"max |mapped derived raw - stored R| = {maxdiff:.6f} (tolerance 0.002)"})
    m.set_gate("G-DERIVED-REPRO", bool(g3), f"max abs diff {maxdiff:.6f}")
    outs.append(wcsv("gates.csv", gates))
    if not g3:
        m.note("G-DERIVED-REPRO failed: model loading/pair construction not equivalent to the frozen evaluator; upstream arm NOT run", failure=True)
        print(m.finish(outs, status="failed"))
        raise SystemExit(1)
    raw_u = np.array(CrossEncoder(str(um)).predict(list(zip(ref_texts, cands)), batch_size=16, show_progress_bar=False), dtype=float)

    # lexical baselines
    from sklearn.feature_extraction.text import TfidfVectorizer
    uniq_refs = sorted(set(ref_texts))
    vec = TfidfVectorizer(lowercase=True, token_pattern=r"(?u)\b\w+\b", norm="l2").fit(cands + uniq_refs)
    Xc, Xr = vec.transform(cands), vec.transform(ref_texts)
    tfidf = np.asarray(Xc.multiply(Xr).sum(axis=1)).ravel()
    dt = [tok(c) for c in cands]
    bm = np.array([bm25_scores(tok(ref_texts[i]), dt)[i] for i in range(n)])
    overlap = np.array([len(set(dt[i]) & set(tok(ref_texts[i]))) / max(len(set(tok(ref_texts[i]))), 1) for i in range(n)])
    length = np.array([len(c.split()) for c in cands], float)
    S = {"derived_ce": raw_d, "upstream_ce": raw_u, "tfidf": tfidf, "bm25": bm, "token_overlap": overlap, "length_only": length,
         "ref_S1": cl["S1"].to_numpy(), "ref_S2_eff": cl["S2_eff"].to_numpy(), "ref_R_mapped": cl["R"].to_numpy(), "ref_composite_deployed": cl["final_score"].to_numpy()}
    outs.append(wcsv("scores.csv", [{"case_id": cl["case_id"][i], "qid": int(cl["qid"][i]), "category": cl["category"][i], "human_gold": gold[i], **{k: f"{v[i]:.8f}" for k, v in S.items()}} for i in range(n)]))

    cat = cl["category"].to_numpy()
    isC = np.array([c in set(CFG["labels"]["correct_reference"]) for c in cat])
    isA = np.array([c in set(CFG["labels"]["adversarial"]) for c in cat])
    qids = np.unique(cl["qid"].to_numpy())
    q_index = [np.where(cl["qid"].to_numpy() == q)[0] for q in qids]
    names = list(S)
    B = 200 if SELFTEST else 10000
    rng = np.random.default_rng(CFG["seeds"]["bootstrap"])
    rho = {k: [] for k in names}
    tau = {k: [] for k in names}
    auc = {k: [] for k in names}
    for _ in range(B):
        idx = two_level_draw(rng, q_index)
        g = gold[idx]
        Ai, Ci = idx[isA[idx]], idx[isC[idx]]
        for k in names:
            rho[k].append(spear(S[k][idx], g))
            tau[k].append(kend(S[k][idx], g))
            auc[k].append(auroc(S[k][Ci], S[k][Ai]))

    def ci(a):
        a = np.asarray(a, float)
        a = a[~np.isnan(a)]
        return float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5)), int(len(a))

    rows = []
    for k in names:
        r_lo, r_hi, r_n = ci(rho[k]); t_lo, t_hi, t_n = ci(tau[k]); a_lo, a_hi, a_n = ci(auc[k])
        rows.append({"scorer": k, "spearman": round(spear(S[k], gold), 4), "sp_ci_low": round(r_lo, 4), "sp_ci_high": round(r_hi, 4),
                     "kendall_tau_b": round(kend(S[k], gold), 4), "kt_ci_low": round(t_lo, 4), "kt_ci_high": round(t_hi, 4),
                     "auroc_correct_vs_adversarial": round(auroc(S[k][isC], S[k][isA]), 4), "auc_ci_low": round(a_lo, 4), "auc_ci_high": round(a_hi, 4), "valid_reps": min(r_n, t_n, a_n)})
    outs.append(wcsv("metrics_point_ci.csv", rows))
    pd_rows = []
    for other in ("upstream_ce", "tfidf", "bm25", "token_overlap", "length_only"):
        for lab, D, pt in (("spearman", rho, lambda k: spear(S[k], gold)), ("kendall_tau_b", tau, lambda k: kend(S[k], gold)), ("auroc", auc, lambda k: auroc(S[k][isC], S[k][isA]))):
            d = np.array(D["derived_ce"]) - np.array(D[other])
            lo, hi, nn = ci(d)
            pd_rows.append({"contrast": f"derived_ce - {other}", "metric": lab, "point": round(pt("derived_ce") - pt(other), 4), "ci_low": round(lo, 4), "ci_high": round(hi, 4), "valid_reps": nn,
                            "role": "PRIMARY (mapping-independent)" if other == "upstream_ce" else "secondary (descriptive)"})
    outs.append(wcsv("paired_differences.csv", pd_rows))
    # permutation null (within-question permutations of gold)
    prng = np.random.default_rng(CFG["seeds"]["permutation"])
    Pn = 200 if SELFTEST else 10000
    null = {k: np.empty(Pn) for k in names}
    rk = {k: rankdata(S[k]) for k in names}
    for i in range(Pn):
        pg = gold.copy()
        for ix in q_index:
            pg[ix] = gold[prng.permutation(ix)]
        rg = rankdata(pg)
        for k in names:
            null[k][i] = np.corrcoef(rk[k], rg)[0, 1] if np.ptp(rk[k]) > 0 else np.nan
    pn_rows = [{"scorer": k, "observed_spearman": round(spear(S[k], gold), 4), "null_95th_percentile": round(float(np.nanpercentile(null[k], 95)), 4),
                "one_sided_perm_p": round(float((1 + np.sum(null[k] >= spear(S[k], gold))) / (Pn + 1)), 5)} for k in names]
    outs.append(wcsv("permutation_null.csv", pn_rows))
    R = {r["scorer"]: r for r in rows}
    up = [r for r in pd_rows if r["contrast"] == "derived_ce - upstream_ce"]
    rep = f"""# X2-B report - old-benchmark exploratory arm (2026-09-19)

Protocol `prereg/X2-B/v1`; arm: the frozen 64 constructed answers to 8 questions (EXPLORATORY/SENSITIVITY; the derived model's results on these items were already known). **The X2-C (confirmatory) arm was not run** (blocked by the human/ethics gate). No categorical verdict is drawn; no MAE-type or composite metric is reported for the upstream arm. Gates passed: {', '.join(g['gate'] for g in gates if g['passed'])}; derived-reproduction max |mapped raw - stored R| = {maxdiff:.6f}.

| Scorer | Spearman [CI] | Kendall tau-b [CI] | AUROC correct vs adversarial [CI] |
|---|---|---|---|
""" + "\n".join(f"| {r['scorer']} | {r['spearman']} [{r['sp_ci_low']}, {r['sp_ci_high']}] | {r['kendall_tau_b']} [{r['kt_ci_low']}, {r['kt_ci_high']}] | {r['auroc_correct_vs_adversarial']} [{r['auc_ci_low']}, {r['auc_ci_high']}] |" for r in rows) + f"""

**Primary contrast (derived minus upstream, mapping-independent; two-level cluster bootstrap):** """ + "; ".join(f"{r['metric']} {r['point']} [{r['ci_low']}, {r['ci_high']}]" for r in up) + """.
Secondary contrasts against TF-IDF, BM25, token overlap and length-only are in `paired_differences.csv`; permutation-null reference in `permutation_null.csv` (within-question permutations of the human gold). All comparisons are descriptive; no multiplicity control. Cautions: 8 question clusters; constructed answers; labels are construction categories; the upstream model is a public MS MARCO ranking model applied to (question + reference, answer) pairs.
"""
    outs.append((_write_new if SELFTEST else rm.write_new)(OUT / "X2B_REPORT.md", rep))
    print(m.finish(outs), m.d["failures"])
    print(rep)


if __name__ == "__main__":
    main()
