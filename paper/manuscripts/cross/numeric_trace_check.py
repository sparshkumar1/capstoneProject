"""Numeric traceability check for the three draft manuscripts (read-only).

For each manuscript, every decimal number with >= 3 decimals and every 'a/b' or 'a of b' count
is looked up in the text of the frozen source files listed for that paper. Numbers not found are
reported for manual review. This checks presence, not correct attribution; correct attribution
was checked by hand against the claim ledgers.
"""
import re, sys, io, os

ROOT = r"C:\Users\spars\Downloads\PrepAIred"
R = os.path.join(ROOT, "research")

SRC = {
    "paper1": [
        "evidence/final/PAPER1_FINAL_CLAIM_MATRIX.md",
        "evidence/final/manuscript/paper1/FINAL_RESULTS_TABLES.md",
        "evidence/final/manuscript/paper1/FINAL_ABSTRACT_FACTS.md",
        "confirmatory/X1/results/x1b_v3/summary.json",
        "confirmatory/X1/results/x1c_v2/environment_and_verdicts.json",
        "confirmatory/X1/PROTOCOL_X1-B_v3.md",
        "literature/claude_web_research/QUOTE_AUDIT.md",
    ],
    "paper2": [
        "results/paper2/paper2_summary_results.csv",
        "results/paper2/paper2_ablation_results.csv",
        "results/paper2/paper2_case_level_results.csv",
        "results/paper2/paper2_metamorphic_results.csv",
        "results/paper2/paper2_adversarial_results.csv",
        "analysis/phase1/x2_a/x2a_agreement.csv",
        "analysis/phase1/x2_a/x2a_bootstrap_rho.csv",
        "analysis/phase1/x2_a/x2a_bootstrap_rho_diff.csv",
        "analysis/phase1/x2_a/x2a_within_question.csv",
        "analysis/phase1/x2_a/x2a_per_question.csv",
        "analysis/phase1/x2_a/x2a_per_category.csv",
        "analysis/phase1/x2_a/x2a_loqo.csv",
        "analysis/phase1/x2_a/x2a_overlap.csv",
        "analysis/phase1/x2_a/x2a_auroc.csv",
        "analysis/phase1/x2_a/x2a_false_accept.csv",
        "analysis/phase1/x2_a/x2a_rater_loo.csv",
        "confirmatory/X2-B/results/metrics_point_ci.csv",
        "confirmatory/X2-B/results/paired_differences.csv",
        "confirmatory/X2-B/results/permutation_null.csv",
        "audit/HUMAN_GATE_3_COMPLETION.md",
        "audit/P0_1_CROSSENCODER_FORENSIC.md",
        "audit/P0_7_HUMAN_ETHICS_FORENSIC.md",
        "evidence/final/manuscript/paper2/FINAL_RESULTS_TABLES.md",
    ],
    "paper3": [
        "confirmatory/X3-A/results/x3a_decision.json",
        "confirmatory/X3-A/results/x3a_secondary_contrasts.csv",
        "confirmatory/X3-A/results/x3a_condition_summary.csv",
        "confirmatory/X3-A/results/x3a_primary_and_secondary_metrics.csv",
        "confirmatory/X3-A/x3a_config.json",
        "analysis/x3a_o7/results/x3a_o7_report.md",
        "analysis/x3a_o7/O7_INTERPRETATION.md",
        "analysis/phase1/x3_0/x3_0c_facts.json",
        "analysis/phase1/x3_0/x3_0c_replay_summary.csv",
        "analysis/phase1/x3_0/x3_0c_followup.json",
        "analysis/phase1/x3_0/x3_0a_training_action_shares.csv",
        "analysis/phase1/x3_0/X3_0A_REPORT.md",
        "audit/P0_4_GUARDRAIL_FORENSIC.md",
        "experiments/paper3/frozen_config.yaml",
        "evidence/final/PAPER3_FINAL_CLAIM_MATRIX.md",
        "literature/claude_web_research/QUOTE_AUDIT.md",
    ],
}


def rd(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def variants(num):
    """Return string forms under which a number may appear in a source (unsigned, trimmed zeros)."""
    n = num.lstrip("+-\u2212")
    out = {n}
    if "." in n:
        out.add(n.rstrip("0").rstrip("."))
        out.add(n.lstrip("0"))
        try:
            v = float(n)
            for d in range(2, 7):
                out.add(f"{v:.{d}f}")
                out.add(f"{v:.{d}f}".rstrip("0").rstrip("."))
        except ValueError:
            pass
    return {x for x in out if x}


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
grand_missing = 0
for paper, files in SRC.items():
    corpus = "\n".join(rd(os.path.join(R, f)) for f in files if os.path.exists(os.path.join(R, f)))
    missing_files = [f for f in files if not os.path.exists(os.path.join(R, f))]
    text = rd(os.path.join(ROOT, "paper", "manuscripts", paper, "manuscript.md"))
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S).split("## References")[0]
    text = text.replace("\u2212", "-")
    nums = sorted(set(re.findall(r"(?<![\w.])[-+]?\d+\.\d{3,}(?![\d])", text)))
    miss = []
    for n in nums:
        if not any(v in corpus for v in variants(n)):
            miss.append(n)
    print(f"== {paper}: {len(nums)} distinct decimals (>=3 dp); not found in listed sources: {len(miss)}")
    if missing_files:
        print("   source files missing:", missing_files)
    for m in miss:
        ctx = re.search(r".{0,60}" + re.escape(m) + r".{0,40}", text)
        print("   ", m, "|", ctx.group(0).replace("\n", " ") if ctx else "")
    grand_missing += len(miss)
print("total unmatched:", grand_missing)
