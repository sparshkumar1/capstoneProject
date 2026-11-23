"""
V3 planning computations. Re-analysis / inspection of already-existing files
only. No model call, no new score, no frozen file modified.

1. Eligibility audit (same criteria as V2/V3 protocol §1).
2. A concrete, seeded, topic-imbalance-aware development/confirmatory split
   (protocol §2), with the 3 oversized topics capped at 8 questions each
   and deliberately reserved for the confirmatory set (not drawn into
   development), so confirmatory retains multi-item topic depth.
3. Inspection of research/results/paper2/paper2_metamorphic_results.csv for
   the TOST margin re-justification (protocol §4) and the existing MG-5
   keyword-injection failures.
4. A precision projection recomputed at the corrected, realistic scale.
"""
import json
import collections
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
SEED = 20260921
CAP = 8


def word_count(s: str) -> int:
    return len(s.split())


def eligibility_audit():
    with open(ROOT / "data/rubrics/rubrics_final_clean.json", encoding="utf-8") as f:
        d = json.load(f)
    eligible = []
    for x in d:
        mand = x.get("logic_markers", {}).get("mandatory", []) or []
        groups = x.get("logic_markers", {}).get("concept_groups", []) or []
        mistakes = x.get("common_mistakes", []) or []
        sem = x.get("semantic_targets", []) or []
        ok = (
            len(mand) >= 2
            and len(groups) >= 2
            and len(sem) >= 2
            and any(word_count(m) >= 4 for m in mistakes)
            and all(word_count(m) <= 10 for m in mand)
        )
        if ok:
            eligible.append(x)
    return eligible


def build_split(eligible, large_reserved=("C_Programming", "DSA_Theory", "Arrays")):
    by_topic = collections.defaultdict(list)
    for x in eligible:
        by_topic[x["topic"]].append(x["qid"])

    rng = np.random.default_rng(SEED)
    capped_pool, dev_reserve = {}, {}
    for t, qids in by_topic.items():
        qs = sorted(qids, key=str)
        if len(qs) > CAP:
            idx = rng.choice(len(qs), size=CAP, replace=False)
            chosen = sorted([qs[i] for i in idx], key=str)
            capped_pool[t] = chosen
            dev_reserve[t] = [q for q in qs if q not in chosen]
        else:
            capped_pool[t] = qs

    dev_candidates = sorted(
        t for t, v in capped_pool.items() if len(v) >= 3 and t not in large_reserved
    )
    idx = rng.choice(len(dev_candidates), size=6, replace=False)
    dev_topics = sorted([dev_candidates[i] for i in idx])
    confirmatory_topics = sorted(t for t in capped_pool if t not in dev_topics)

    return {
        "dev_topics": dev_topics,
        "dev_n_questions": sum(len(capped_pool[t]) for t in dev_topics),
        "confirmatory_topics": confirmatory_topics,
        "confirmatory_n_questions": sum(len(capped_pool[t]) for t in confirmatory_topics),
        "confirmatory_topic_sizes": {t: len(capped_pool[t]) for t in confirmatory_topics},
        "cap_excess_reserved_for_dev_only": {t: len(v) for t, v in dev_reserve.items()},
    }


def metamorphic_margin_check():
    df = pd.read_csv(ROOT / "research/results/paper2/paper2_metamorphic_results.csv")
    mg1 = df[df["relation"].str.contains("MG-1")]
    mg5 = df[df["relation"].str.contains("MG-5")]
    return {
        "MG1_paraphrase_deltas": mg1["delta"].round(4).tolist(),
        "MG1_criterion": mg1["criterion"].iloc[0] if len(mg1) else None,
        "MG5_keyword_injection_scores": mg5["transformed_score"].round(4).tolist(),
        "MG5_n_failed": int((~mg5["passed"]).sum()),
        "MG5_n_total": int(len(mg5)),
    }


def precision_projection(K_values=(8, 31, 67), n_boot=3000):
    df = pd.read_csv(ROOT / "research/results/paper2/paper2_case_level_results.csv")
    err_full = (df["final_score"] - df["human_gold_score"]).abs()
    err_r = (df["R"] - df["human_gold_score"]).abs()
    df["d"] = err_full - err_r
    per_q = df.groupby("qid")["d"].mean()
    rng = np.random.default_rng(SEED)
    out = {}
    for K in K_values:
        boots = [float(rng.choice(per_q.values, size=K, replace=True).mean()) for _ in range(n_boot)]
        lo, hi = np.percentile(boots, [2.5, 97.5])
        out[K] = {"ci95": [round(float(lo), 4), round(float(hi), 4)], "half_width": round(float((hi - lo) / 2), 4)}
    return out


if __name__ == "__main__":
    eligible = eligibility_audit()
    split = build_split(eligible)
    margin = metamorphic_margin_check()
    proj = precision_projection()

    result = {
        "n_eligible": len(eligible),
        "split": split,
        "metamorphic_margin_check": margin,
        "precision_projection_illustrative_only": proj,
    }
    print(json.dumps(result, indent=2))
    out_path = Path(__file__).resolve().parents[1] / "results" / "benchmark_v3_planning.json"
    out_path.write_text(json.dumps(result, indent=2))
    print(f"\nWritten: {out_path}")
