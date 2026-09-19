"""X2-A - sensitivity / descriptive / exploratory re-analysis of the frozen 64-case benchmark.

Configuration: x2a_config.json (hashed in the manifest). Pre-run note: X2A_PRERUN_NOTE.md.
Reads stored files only; executes no evaluator, loads no model. Single run.
Run: python -B research/analysis/phase1/x2_a/x2a_analysis.py            (real run; writes outputs)
     python -B research/analysis/phase1/x2_a/x2a_analysis.py --selftest  (synthetic data; writes nothing)
"""
import csv
import io
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import kendalltau, rankdata, spearmanr

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "research" / "tools"))
OUT = Path(__file__).resolve().parent
CFG = OUT / "x2a_config.json"
NOTE = OUT / "X2A_PRERUN_NOTE.md"


# ------------------------------------------------------------------ statistics
def spear(x, y):
    if np.ptp(x) == 0 or np.ptp(y) == 0:
        return np.nan
    rx, ry = rankdata(x), rankdata(y)
    return float(np.corrcoef(rx, ry)[0, 1])


def auroc(pos, neg):
    """P(pos score > neg score) + 0.5 P(tie); pos = correct-reference, neg = adversarial."""
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    r = rankdata(np.concatenate([pos, neg]))
    u = r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2.0
    return float(u / (len(pos) * len(neg)))


def accept_rate(scores, tau):
    return float(np.mean(scores >= tau)) if len(scores) else np.nan


def matched_threshold(sc_correct, target_rate):
    """largest observed value t with accept-rate(correct) >= target_rate."""
    vals = np.unique(sc_correct)[::-1]
    for t in vals:
        if np.mean(sc_correct >= t) >= target_rate - 1e-12:
            return float(t)
    return float(vals[-1])


def ccc(x, y):
    mx, my = x.mean(), y.mean()
    vx, vy = x.var(), y.var()
    cov = np.mean((x - mx) * (y - my))
    return float(2 * cov / (vx + vy + (mx - my) ** 2))


def pct(a, q=(2.5, 97.5)):
    a = np.asarray(a, float)
    a = a[~np.isnan(a)]
    return [float(np.percentile(a, q[0])), float(np.percentile(a, q[1]))], int(len(a))


def two_level_draw(rng, q_index):
    qs = rng.integers(0, len(q_index), len(q_index))
    return np.concatenate([rng.choice(q_index[q], size=len(q_index[q]), replace=True) for q in qs])


def question_only_draw(rng, q_index):
    qs = rng.integers(0, len(q_index), len(q_index))
    return np.concatenate([q_index[q] for q in qs])


# ------------------------------------------------------------------ analysis
def analyse(d, raters, cfg, B, seed):
    """d: dict of numpy arrays keyed by column; raters: dict r-> {item_id: score}; returns dict of result tables."""
    n = len(d["qid"])
    qids = np.unique(d["qid"])
    q_index = [np.where(d["qid"] == q)[0] for q in qids]
    gold = d["human_gold_score"]
    S = {"composite": d["final_score"], "R_only": d["R"], "S1": d["S1"], "S2_eff": d["S2_eff"],
         "S1_plus_R": cfg["scorers"]["S1_plus_R"]["S1"] * d["S1"] + cfg["scorers"]["S1_plus_R"]["R"] * d["R"]}
    cat = d["category"]
    A_set, C_set = set(cfg["category_sets"]["adversarial"]), set(cfg["category_sets"]["correct_reference"])
    isA = np.array([c in A_set for c in cat])
    isC = np.array([c in C_set for c in cat])
    res = {}

    # 1 point estimates
    point = []
    for name, s in S.items():
        point.append({"scorer": name, "spearman": round(spear(s, gold), 4),
                      "kendall_tau_b": round(float(kendalltau(s, gold)[0]), 4)})
    res["point"] = point

    # 2 bootstrap (one RNG stream, fixed order of use)
    rng = np.random.default_rng(seed)
    taus = cfg["false_accept"]["tau_values"]
    names = list(S)
    rho2 = {k: [] for k in names}
    rho1 = {k: [] for k in names}
    au = {k: [] for k in names}
    far_fixed = {t: [] for t in taus}
    acc_c_fixed = {t: [] for t in taus}
    far_matched = {(k, t): [] for k in names if k != "composite" for t in taus}
    for _ in range(B):
        idx = two_level_draw(rng, q_index)
        g = gold[idx]
        for k in names:
            rho2[k].append(spear(S[k][idx], g))
        A_i, C_i = idx[isA[idx]], idx[isC[idx]]
        for k in names:
            au[k].append(auroc(S[k][C_i], S[k][A_i]))
        for t in taus:
            far_fixed[t].append(accept_rate(S["composite"][A_i], t))
            acc_c_fixed[t].append(accept_rate(S["composite"][C_i], t))
            tgt = accept_rate(S["composite"][C_i], t)
            for k in names:
                if k == "composite":
                    continue
                thr = matched_threshold(S[k][C_i], tgt) if len(C_i) else np.nan
                far_matched[(k, t)].append(accept_rate(S[k][A_i], thr) if len(C_i) else np.nan)
        idx1 = question_only_draw(rng, q_index)
        for k in names:
            rho1[k].append(spear(S[k][idx1], gold[idx1]))

    boot = []
    for k in names:
        ci2, n2 = pct(rho2[k])
        ci1, n1 = pct(rho1[k])
        boot.append({"scorer": k, "spearman": round(spear(S[k], gold), 4),
                     "two_level_ci_low": round(ci2[0], 4), "two_level_ci_high": round(ci2[1], 4), "two_level_valid_reps": n2,
                     "question_only_ci_low": round(ci1[0], 4), "question_only_ci_high": round(ci1[1], 4), "question_only_valid_reps": n1,
                     "share_two_level_reps_le_0": round(float(np.mean(np.array(rho2[k])[~np.isnan(rho2[k])] <= 0)), 4)})
    res["bootstrap_rho"] = boot
    diffs = []
    for a, b in (("composite", "R_only"), ("composite", "S1_plus_R"), ("R_only", "S1_plus_R")):
        dd = np.array(rho2[a]) - np.array(rho2[b])
        ci, nn = pct(dd)
        diffs.append({"contrast": f"{a} - {b}", "point": round(spear(S[a], gold) - spear(S[b], gold), 4),
                      "two_level_ci_low": round(ci[0], 4), "two_level_ci_high": round(ci[1], 4), "valid_reps": nn})
    res["bootstrap_rho_diff"] = diffs

    # 3 LOQO
    lo = []
    for i, q in enumerate(qids):
        keep = np.setdiff1d(np.arange(n), q_index[i])
        lo.append({"left_out_qid": int(q), "n": int(len(keep)), "composite": round(spear(S["composite"][keep], gold[keep]), 4),
                   "R_only": round(spear(S["R_only"][keep], gold[keep]), 4)})
    res["loqo"] = lo

    # 4 per-question, per-category, within-question
    pq = []
    for i, q in enumerate(qids):
        ii = q_index[i]
        pq.append({"qid": int(q), "n": int(len(ii)), "mean_human": round(float(gold[ii].mean()), 4), "mean_composite": round(float(S["composite"][ii].mean()), 4),
                   "rho_composite": round(spear(S["composite"][ii], gold[ii]), 4), "rho_R_only": round(spear(S["R_only"][ii], gold[ii]), 4)})
    res["per_question"] = pq
    pc = []
    for c in sorted(set(cat)):
        ii = np.where(cat == c)[0]
        row = {"category": c, "n": int(len(ii)), "mean_human": round(float(gold[ii].mean()), 4),
               "mean_composite": round(float(S["composite"][ii].mean()), 4),
               "signed_bias_composite_minus_human": round(float((S["composite"][ii] - gold[ii]).mean()), 4),
               "mean_R": round(float(S["R_only"][ii].mean()), 4)}
        row["rho_composite"] = round(spear(S["composite"][ii], gold[ii]), 4) if len(ii) >= cfg["per_category"]["rho_computed_only_if_n_ge"] else "not computed (n<%d)" % cfg["per_category"]["rho_computed_only_if_n_ge"]
        pc.append(row)
    res["per_category"] = pc
    dem = lambda x: x - np.array([x[q_index[list(qids).index(qq)]].mean() for qq in d["qid"]])
    res["within_question"] = [{"scorer": k, "within_question_spearman_demeaned": round(spear(dem(S[k]), dem(gold)), 4)} for k in ("composite", "R_only", "S1_plus_R")]

    # 5 rater leave-one-out
    adj = d["gold_method"] != "mean_of_three"
    rl = []
    ids = d["case_id"]
    for r in sorted(raters):
        others = [o for o in sorted(raters) if o != r]
        g_r = np.array([np.mean([raters[o][i] for o in others]) for i in ids])
        for lab, mask in (("all 64 items", np.ones(n, bool)), ("54 non-adjudicated items", ~adj)):
            rl.append({"omitted_rater": r, "items": lab, "n": int(mask.sum()),
                       "rho_composite": round(spear(S["composite"][mask], g_r[mask]), 4),
                       "rho_R_only": round(spear(S["R_only"][mask], g_r[mask]), 4)})
    for lab, mask in (("all 64 items", np.ones(n, bool)), ("54 non-adjudicated items", ~adj)):
        rl.append({"omitted_rater": "none (frozen gold)", "items": lab, "n": int(mask.sum()),
                   "rho_composite": round(spear(S["composite"][mask], gold[mask]), 4),
                   "rho_R_only": round(spear(S["R_only"][mask], gold[mask]), 4)})
    res["rater_loo"] = rl

    # 6 overlap / non-overlap
    ov = []
    for lab, qs in (("pilot-overlap qids", cfg["pilot_overlap"]["pilot_qids"]), ("other qids", cfg["pilot_overlap"]["other_qids"])):
        m = np.isin(d["qid"], qs)
        ov.append({"set": lab, "qids": " ".join(map(str, qs)), "n": int(m.sum()),
                   "rho_composite": round(spear(S["composite"][m], gold[m]), 4), "rho_R_only": round(spear(S["R_only"][m], gold[m]), 4)})
    res["overlap"] = ov

    # 7 false accept
    fa = []
    for k in names:
        ci, nn = pct(au[k])
        fa.append({"scorer": k, "AUROC_correct_vs_adversarial": round(auroc(S[k][isC], S[k][isA]), 4),
                   "ci_low": round(ci[0], 4), "ci_high": round(ci[1], 4), "valid_reps": nn,
                   "n_correct_reference": int(isC.sum()), "n_adversarial": int(isA.sum())})
    res["auroc"] = fa
    dd = np.array(au["composite"]) - np.array(au["R_only"])
    ci, nn = pct(dd)
    res["auroc_diff"] = [{"contrast": "composite - R_only", "point": round(auroc(S["composite"][isC], S["composite"][isA]) - auroc(S["R_only"][isC], S["R_only"][isA]), 4),
                          "ci_low": round(ci[0], 4), "ci_high": round(ci[1], 4), "valid_reps": nn}]
    ff = []
    for t in taus:
        a_pt = accept_rate(S["composite"][isA], t)
        c_pt = accept_rate(S["composite"][isC], t)
        ca, _ = pct(far_fixed[t])
        cc, _ = pct(acc_c_fixed[t])
        ff.append({"scorer": "composite", "rule": f"fixed tau={t}", "threshold": t, "false_accept_rate": round(a_pt, 4), "fa_ci_low": round(ca[0], 4), "fa_ci_high": round(ca[1], 4),
                   "accept_rate_correct_reference": round(c_pt, 4), "acc_ci_low": round(cc[0], 4), "acc_ci_high": round(cc[1], 4),
                   "n_false_accepts": int(np.sum(S["composite"][isA] >= t)), "n_adversarial": int(isA.sum())})
        for k in names:
            if k == "composite":
                continue
            thr = matched_threshold(S[k][isC], c_pt)
            cm, _ = pct(far_matched[(k, t)])
            ff.append({"scorer": k, "rule": f"matched to composite accept-rate on correct-reference at tau={t}", "threshold": round(thr, 4),
                       "false_accept_rate": round(accept_rate(S[k][isA], thr), 4), "fa_ci_low": round(cm[0], 4), "fa_ci_high": round(cm[1], 4),
                       "accept_rate_correct_reference": round(accept_rate(S[k][isC], thr), 4), "acc_ci_low": "", "acc_ci_high": "",
                       "n_false_accepts": int(np.sum(S[k][isA] >= thr)), "n_adversarial": int(isA.sum())})
    res["false_accept"] = ff

    # 8 agreement, bias, length
    diff = S["composite"] - gold
    sd = float(diff.std(ddof=1))
    res["agreement"] = [{"scorer": "composite", "lin_ccc": round(ccc(S["composite"], gold), 4), "bland_altman_bias": round(float(diff.mean()), 4),
                         "loa_low": round(float(diff.mean() - 1.96 * sd), 4), "loa_high": round(float(diff.mean() + 1.96 * sd), 4),
                         "spearman_residual_vs_answer_words": round(spear(diff, d["answer_words"]), 4)},
                        {"scorer": "R_only", "lin_ccc": round(ccc(S["R_only"], gold), 4), "bland_altman_bias": round(float((S["R_only"] - gold).mean()), 4),
                         "loa_low": "", "loa_high": "", "spearman_residual_vs_answer_words": round(spear(S["R_only"] - gold, d["answer_words"]), 4)}]
    res["meta"] = {"B": B, "seed": seed, "n": int(n), "n_questions": int(len(qids)), "n_adversarial": int(isA.sum()), "n_correct_reference": int(isC.sum()),
                   "n_excluded_from_both": int(n - isA.sum() - isC.sum()), "n_adjudicated": int(adj.sum())}
    return res


def load_real(cfg):
    import pandas as pd
    cl = pd.read_csv(REPO / cfg["inputs"]["case_level"])
    gd = pd.read_csv(REPO / cfg["inputs"]["gold"])
    assert list(cl.case_id) == list(gd.case_id)
    assert np.allclose(cl.human_gold_score, gd.final_gold_score, atol=1e-9)
    raters, words = {}, {}
    for i, p in enumerate(cfg["inputs"]["raters"], 1):
        with open(REPO / p, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        raters[f"R{i}"] = {r["item_id"]: float(r["score_0_to_1"]) for r in rows}
        if i == 1:
            words = {r["item_id"]: len(r["candidate_answer"].split()) for r in rows}
        assert set(raters[f"R{i}"]) == set(cl.case_id)
    d = {c: cl[c].to_numpy() for c in ("case_id", "qid", "category", "human_gold_score", "gold_method", "S1", "S2_eff", "R", "final_score")}
    d["answer_words"] = np.array([words[i] for i in cl.case_id], float)
    return d, raters


def write_tables(res, rm, outs):
    for key, rows in res.items():
        if key == "meta":
            continue
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
        outs.append(rm.write_new(OUT / f"x2a_{key}.csv", buf.getvalue()))


def selftest():
    cfg = json.load(open(CFG))
    rng = np.random.default_rng(0)
    n = 64
    cats = (cfg["category_sets"]["adversarial"] + cfg["category_sets"]["correct_reference"] + ["partial_incomplete"]) * 8
    d = {"case_id": np.array([f"C{i}" for i in range(n)]), "qid": np.repeat([1, 3, 7, 10, 15, 22, 41, 50], 8),
         "category": np.array(cats[:n]), "human_gold_score": rng.random(n), "gold_method": np.array(["mean_of_three"] * 54 + ["expert_adjudication"] * 10),
         "S1": rng.random(n), "S2_eff": rng.random(n), "R": rng.random(n), "final_score": rng.random(n), "answer_words": rng.integers(10, 80, n).astype(float)}
    raters = {r: {i: float(rng.random()) for i in d["case_id"]} for r in ("R1", "R2", "R3")}
    res = analyse(d, raters, cfg, 200, 1)
    assert res["meta"]["n"] == 64 and len(res["bootstrap_rho"]) == 5 and len(res["false_accept"]) > 4
    # ranks/AUROC sanity
    assert abs(auroc(np.array([2.0, 3.0]), np.array([0.0, 1.0])) - 1.0) < 1e-12 and abs(auroc(np.array([1.0]), np.array([1.0])) - 0.5) < 1e-12
    assert abs(spear(np.arange(10.0), np.arange(10.0)) - 1.0) < 1e-12
    assert matched_threshold(np.array([0.9, 0.8, 0.7, 0.6]), 0.5) == 0.8
    print("selftest ok:", json.dumps(res["meta"]))


def main():
    import run_manifest as rm
    cfg = json.load(open(CFG))
    m = rm.Manifest("X2-A", OUT, __file__, config_path=CFG, note_path=NOTE,
                    seeds={"bootstrap": cfg["rng"]["seed"], "B": cfg["rng"]["bootstrap_B"]})
    m.add_inputs([REPO / cfg["inputs"]["case_level"], REPO / cfg["inputs"]["gold"]] + [REPO / p for p in cfg["inputs"]["raters"]])
    d, raters = load_real(cfg)
    res = analyse(d, raters, cfg, cfg["rng"]["bootstrap_B"], cfg["rng"]["seed"])
    outs = []
    write_tables(res, rm, outs)
    outs.append(rm.write_new(OUT / "x2a_meta.json", json.dumps(res["meta"], indent=2)))
    st = m.finish(outs)
    print("manifest:", st, m.d["failures"], m.d["deviations"])
    print(json.dumps(res["meta"]))


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        main()
