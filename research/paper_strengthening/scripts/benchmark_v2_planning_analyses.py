"""
Planning-only analyses for SYNTHETIC_EVALUATOR_BENCHMARK_PROTOCOL_V2.md.

Two pieces, both re-analysis of already-frozen/already-existing data. No
model is called, no new score is generated, no frozen file is modified.

1. Eligibility audit of data/rubrics/rubrics_final_clean.json against a
   disclosed, stricter-than-loose criterion for supporting all 7 answer
   categories without ambiguous/artificial construction.
2. A bootstrap precision projection: using the existing 8-question,
   64-item paired error data (full composite vs. R-only) from
   research/results/paper2/paper2_case_level_results.csv, project how the
   95% CI on the paired mean difference would narrow at larger candidate
   sample sizes (K = 8/16/32/64/107), ASSUMING new questions have a
   similar effect/variance structure to the observed 8 (a disclosed
   assumption, not a guarantee).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]


def word_count(s: str) -> int:
    return len(s.split())


def eligibility_audit():
    with open(ROOT / "data/rubrics/rubrics_final_clean.json", encoding="utf-8") as f:
        d = json.load(f)

    eligible, excluded = [], []
    for x in d:
        qid = x["qid"]
        mand = x.get("logic_markers", {}).get("mandatory", []) or []
        groups = x.get("logic_markers", {}).get("concept_groups", []) or []
        mistakes = x.get("common_mistakes", []) or []
        sem = x.get("semantic_targets", []) or []

        reasons = []
        if len(mand) < 2:
            reasons.append("mandatory<2 (cannot construct a meaningful partial-omission)")
        if len(groups) < 2:
            reasons.append("concept_groups<2 (insufficient distinct concepts for keyword-stuffed list)")
        if len(sem) < 2:
            reasons.append("semantic_targets<2 (insufficient content for a genuine paraphrase)")
        good_mistakes = [m for m in mistakes if word_count(m) >= 4]
        if not good_mistakes:
            reasons.append("no phraseable (>=4 word) common_mistakes entry for misconception construction")
        long_mand = [m for m in mand if word_count(m) > 10]
        if long_mand:
            reasons.append("mandatory phrase too long (>10 words) to flatten into a clean keyword list")

        if reasons:
            excluded.append({"qid": qid, "topic": x.get("topic"), "reasons": reasons})
        else:
            eligible.append({"qid": qid, "topic": x.get("topic"), "type": x.get("type")})

    return eligible, excluded


def precision_projection(seed=20260921, n_boot=3000):
    df = pd.read_csv(ROOT / "research/results/paper2/paper2_case_level_results.csv")
    err_full = (df["final_score"] - df["human_gold_score"]).abs()
    err_r = (df["R"] - df["human_gold_score"]).abs()
    df["d"] = err_full - err_r
    per_q = df.groupby("qid")["d"].mean()

    rng = np.random.default_rng(seed)
    out = {}
    for K in [8, 16, 32, 64, 107]:
        boots = []
        for _ in range(n_boot):
            sampled = rng.choice(per_q.values, size=K, replace=True)
            boots.append(float(sampled.mean()))
        arr = np.array(boots)
        lo, hi = np.percentile(arr, [2.5, 97.5])
        out[K] = {"ci95_low": round(float(lo), 4), "ci95_high": round(float(hi), 4),
                   "half_width": round(float((hi - lo) / 2), 4)}
    return out


if __name__ == "__main__":
    eligible, excluded = eligibility_audit()
    print(f"Eligible: {len(eligible)} / {len(eligible) + len(excluded)}")
    print("Excluded:")
    for e in excluded:
        print(" ", e)

    proj = precision_projection()
    print("\nPrecision projection (assumption-dependent; see protocol §4.4):")
    for k, v in proj.items():
        print(f"  K={k:4d}  CI95=[{v['ci95_low']}, {v['ci95_high']}]  half-width={v['half_width']}")

    out_path = Path(__file__).resolve().parents[1] / "results" / "benchmark_v2_planning.json"
    out_path.write_text(json.dumps({
        "eligible_count": len(eligible),
        "excluded": excluded,
        "eligible_topics": sorted(set(e["topic"] for e in eligible)),
        "precision_projection": proj,
    }, indent=2))
    print(f"\nWritten: {out_path}")
