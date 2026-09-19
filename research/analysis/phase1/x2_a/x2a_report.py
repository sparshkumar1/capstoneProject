"""Builds X2A_REPORT.md from the stored X2-A CSV outputs (no new computation; numbers are read, not typed)."""
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "research" / "tools"))
import run_manifest as rm  # noqa: E402

OUT = Path(__file__).resolve().parent


def rd(n):
    with open(OUT / f"x2a_{n}.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def by(rows, key, val):
    return [r for r in rows if r[key] == val][0]


bo, bd = rd("bootstrap_rho"), rd("bootstrap_rho_diff")
c, r = by(bo, "scorer", "composite"), by(bo, "scorer", "R_only")
d_cr = by(bd, "contrast", "composite - R_only")
lq = rd("loqo")
lqc = [float(x["composite"]) for x in lq]
rl = rd("rater_loo")
rl_all = [x for x in rl if x["items"] == "all 64 items" and x["omitted_rater"].startswith("R")]
rl_54 = [x for x in rl if x["items"] != "all 64 items" and x["omitted_rater"].startswith("R")]
ov = rd("overlap")
au = rd("auroc")
ad = rd("auroc_diff")[0]
fa = rd("false_accept")
ag = rd("agreement")[0]
wq = by(rd("within_question"), "scorer", "composite")
pq = rd("per_question")
frozen54 = by([x for x in rl if x["omitted_rater"].startswith("none")], "items", "54 non-adjudicated items")
f60 = by(fa, "rule", "fixed tau=0.6")
f75 = by(fa, "rule", "fixed tau=0.75")
m60 = {x["scorer"]: x for x in fa if x["rule"].endswith("tau=0.6")}
m75 = {x["scorer"]: x for x in fa if x["rule"].endswith("tau=0.75")}
mn, mx = min(lqc), max(lqc)

rep = f"""# X2-A report - old-benchmark sensitivity / descriptive / exploratory analyses (2026-09-19)

**Every number below is read from the stored X2-A CSV files (`x2a_*.csv`) by `x2a_report.py`.** Data: the frozen 64 constructed answers to 8 questions, whose primary results were already known; question set overlaps the pilot. **No analysis here is confirmatory.** Labels: SENS = sensitivity analysis of a frozen estimand; DESC = descriptive; EXPL = exploratory with a pre-specified rule (hypothesis-generating for X2-C H3). Configuration, seed (42) and B (10 000) were fixed and committed before the run; the analysis was run once (`manifest_X2-A.json`).

## 1. Question-cluster uncertainty for the composite (SENS)
Composite Spearman rho = {c['spearman']}. Two-level cluster bootstrap (resample 8 questions, then answers within question) 95 % percentile interval [{c['two_level_ci_low']}, {c['two_level_ci_high']}]; question-only resampling [{c['question_only_ci_low']}, {c['question_only_ci_high']}]. The frozen case-level interval [0.1575, 0.5774] treated the 64 answers as independent. R-only: {r['spearman']} [{r['two_level_ci_low']}, {r['two_level_ci_high']}] (two-level). Only 8 clusters: the interval is coarse. Composite minus R-only: {d_cr['point']} [{d_cr['two_level_ci_low']}, {d_cr['two_level_ci_high']}] (two-level); the interval includes zero, so the data neither establish nor exclude a difference.

## 2. Influence of single questions and raters (SENS)
- Leave-one-question-out composite rho ranges {mn:.4f} to {mx:.4f} across the 8 left-out questions (`x2a_loqo.csv`).
- Rater leave-one-out (gold = mean of the two remaining raters), composite rho: all 64 items {', '.join(x['rho_composite'] for x in rl_all)} (omitting R1, R2, R3); on the 54 non-adjudicated items {', '.join(x['rho_composite'] for x in rl_54)}; frozen gold on the 54 non-adjudicated items {frozen54['rho_composite']}. The frozen gold adjudicated 10 items; the leave-one-out golds do not.

## 3. Structure of the disagreement (DESC)
- Within-question (demeaned) composite rho = {wq['within_question_spearman_demeaned']}, higher than the pooled {c['spearman']}: much of the loss of agreement is between questions (composite means differ by question more than human means do; `x2a_per_question.csv`).
- Bias (composite minus human): Bland-Altman bias {ag['bland_altman_bias']} (95 % limits [{ag['loa_low']}, {ag['loa_high']}]); Lin's CCC {ag['lin_ccc']}. Spearman correlation of the residual with answer length (words) {ag['spearman_residual_vs_answer_words']}.
- Per-category means and signed bias: `x2a_per_category.csv` (n = 2 to 8 per category; within-category rho computed only for n >= 8 and not interpreted).

## 4. Pilot-overlap contrast (DESC; exploratory; not a held-out validation)
Composite rho on pilot-overlap questions {ov[0]['qids']} (n = {ov[0]['n']}): {ov[0]['rho_composite']}; other questions {ov[1]['qids']} (n = {ov[1]['n']}): {ov[1]['rho_composite']}. R-only: {ov[0]['rho_R_only']} vs {ov[1]['rho_R_only']}. Point estimates only; question difficulty also differs between the two sets; this pattern is compatible with, but does not establish, optimism from the pilot-based settings.

## 5. Adversarial false-accept analysis (EXPL; rule pre-specified, data already seen)
Adversarial set = keyword_stuffed, misconception, contradictory, incorrect, verbose_wrong (n = {au[0]['n_adversarial']}); correct-reference set = concise_correct, verbose_correct, suboptimal_correct, paraphrase (n = {au[0]['n_correct_reference']}); partial_incomplete excluded from both.
- Threshold-free AUROC (correct-reference vs adversarial), two-level bootstrap: composite {by(au,'scorer','composite')['AUROC_correct_vs_adversarial']} [{by(au,'scorer','composite')['ci_low']}, {by(au,'scorer','composite')['ci_high']}]; R-only {by(au,'scorer','R_only')['AUROC_correct_vs_adversarial']} [{by(au,'scorer','R_only')['ci_low']}, {by(au,'scorer','R_only')['ci_high']}]; S1+R {by(au,'scorer','S1_plus_R')['AUROC_correct_vs_adversarial']}; S1 {by(au,'scorer','S1')['AUROC_correct_vs_adversarial']}. Composite minus R-only {ad['point']} [{ad['ci_low']}, {ad['ci_high']}] (includes zero).
- Composite at the documented grade boundaries (no explicit accept threshold exists): tau = 0.60: {f60['n_false_accepts']} of {f60['n_adversarial']} adversarial answers accepted (false-accept rate {f60['false_accept_rate']}, cluster CI [{f60['fa_ci_low']}, {f60['fa_ci_high']}]) but only {f60['accept_rate_correct_reference']} of correct-reference answers accepted; tau = 0.75: {f75['n_false_accepts']} of {f75['n_adversarial']} accepted, {f75['accept_rate_correct_reference']} of correct-reference answers accepted.
- Matched to the composite's accept-rate on the correct-reference set, false accepts at tau = 0.60: R-only {m60['R_only']['n_false_accepts']}, S1+R {m60['S1_plus_R']['n_false_accepts']}, S1 {m60['S1']['n_false_accepts']}, S2_eff {m60['S2_eff']['n_false_accepts']} (composite {f60['n_false_accepts']}); at tau = 0.75: all {m75['R_only']['n_false_accepts']} for R-only.
- Reading (exploratory): on this seen, constructed set the composite is **not** observed to be safer than R-only or S1+R; H3 (composite false-accept < R-only) is not supported here and should be expected to be at risk in X2-C. The composite is also conservative on correct answers (low accept rate). Adversarial counts are small (34); intervals are wide.

## Not concluded / cautions
No claim of validity, replication or absence of effect follows from any X2-A output. Nothing here sets a parameter of X2-B or X2-C (tau rule, category sets, rho_min, sample size). Registry: only the two-level bootstrap interval is proposed as a scoped VALID sensitivity statement; everything else is DESC/EXPLORATORY.
"""
rm.write_new(OUT / "X2A_REPORT.md", rep)
print(rep)
