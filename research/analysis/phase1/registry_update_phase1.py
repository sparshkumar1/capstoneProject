"""Phase 1 registry update: appends new rows and applies the dated status changes below to
research/claims/CLAIM_REGISTRY.csv. Every value is read from a stored Phase-1 artifact and asserted;
artifact hashes are computed here. Run once (a second run refuses: the new IDs already exist).
Run: python -B research/analysis/phase1/registry_update_phase1.py
"""
import csv
import hashlib
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
REG = REPO / "research" / "claims" / "CLAIM_REGISTRY.csv"
A = REPO / "research" / "analysis" / "phase1"
DATE = "2026-09-19"
HEAD = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
LOCK = hashlib.sha256((REPO / "research/locks/replay-Lobs.lock.json").read_bytes()).hexdigest()


def sha(p):
    return hashlib.sha256((REPO / p).read_bytes()).hexdigest()


def rd(p):
    with open(REPO / p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


with open(REG, encoding="utf-8", newline="") as f:
    rdr = csv.DictReader(f)
    FIELDS = rdr.fieldnames
    rows = list(rdr)
ids = {r["claim_id"] for r in rows}
assert "X2A-C001" not in ids, "registry already updated"
by_id = {r["claim_id"]: r for r in rows}
new = []


def add(cid, paper, status, wording, value, unit, ci, label, artifact, script, tier, verify, notes, config="", env="", seed="", superseded=""):
    new.append({"claim_id": cid, "paper": paper, "status": status, "claim_wording": wording, "value": value, "unit_or_n": unit, "ci_or_spread": ci,
                "evidence_label": label, "artifact_path": artifact, "artifact_sha256": sha(artifact) if artifact else "", "script_path": script,
                "script_commit": HEAD if script else "", "config_path": config, "env_lock_sha256": env or "NOT_RECORDED", "seed_set": seed,
                "recompute_tier": tier, "verify_cmd": verify, "superseded_by": superseded, "last_verified": DATE, "notes": notes})


def upd(cid, **kw):
    r = by_id[cid]
    old = r["status"]
    for k, v in kw.items():
        r[k] = v
    r["notes"] = (r["notes"] + " " if r["notes"] else "") + f"[{DATE} Phase 1: status {old} -> {r['status']}]"


# ------------------------------------------------------------------ X3-0c (replay) and X3-0a
X3 = "research/analysis/phase1/x3_0/"
summ = rd(X3 + "x3_0c_replay_summary.csv")
pooled = {(r["condition"]): r for r in summ if r["training_seed"] == "pooled 5 seeds"}
cs = [r for r in summ if r["condition"] == "Constant-Same+G"][0]
hz = [r for r in summ if r["condition"] == "Heuristic"][0]
assert pooled["PPO raw"]["attempted_boundary_final_action"] == "136" and pooled["PPO+G"]["action_overrides"] == "99"
assert pooled["PPO+G"]["unchanged_activations"] == "464" and pooled["PPO+G"]["sessions_with_override"] == "41"
assert cs["mae"] == "0.6728" and cs["volatility"] == "0.08" and pooled["PPO+G"]["volatility"] == "0.1864"
gate = rd(X3 + "x3_0c_gate_G-REPRO.csv")
assert len(gate) == 32 and all(g["match"] == "True" for g in gate)
env = LOCK
REP = dict(script=X3 + "x3_0c_replay.py", env=env, seed="training 42/123/456/789/999; evaluation 1001-5005 (frozen)")
REPNOTE = "REPLAY of frozen code in envs/replay-Lobs (lock record research/locks/replay-Lobs.lock.json; wheel hashes not recorded); gate G-REPRO passed 32/32; simulation only; manifest research/analysis/phase1/x3_0/manifest_X3-0c.json."
for cid, tier in (("P3-C007", "T3"), ("P3-C008", "T3"), ("P3-C009", "T3")):
    pass
upd("P3-C007", status="VALID", evidence_label="PHASE1-REPLAY", artifact_path=X3 + "x3_0c_replay_summary.csv", artifact_sha256=sha(X3 + "x3_0c_replay_summary.csv"),
    script_path=REP["script"], script_commit=HEAD, env_lock_sha256=env, seed_set=REP["seed"], value="136", unit_or_n="1250 turns (10.9 percent)",
    verify_cmd="run x3_0c_replay.py in envs/replay-Lobs; compare x3_0c_replay_summary.csv row 'PPO raw, pooled 5 seeds'", notes="Registered from the stored replay. " + REPNOTE + " Attempted boundary action = executed action would leave [1,5] before clipping (frozen definition).")
upd("P3-C008", status="VALID", evidence_label="PHASE1-REPLAY", artifact_path=X3 + "x3_0c_replay_summary.csv", artifact_sha256=sha(X3 + "x3_0c_replay_summary.csv"),
    script_path=REP["script"], script_commit=HEAD, env_lock_sha256=env, seed_set=REP["seed"], value="99", unit_or_n="1250 guarded turns (7.9 percent); 464 of 563 activations unchanged; 41 of 125 sessions with >=1 override",
    verify_cmd="run x3_0c_replay.py; row 'PPO+G, pooled 5 seeds': action_overrides / unchanged_activations / sessions_with_override", notes="Registered from the stored replay. " + REPNOTE)
upd("P3-C009", status="VALID", evidence_label="PHASE1-REPLAY", artifact_path=X3 + "x3_0c_replay_summary.csv", artifact_sha256=sha(X3 + "x3_0c_replay_summary.csv"),
    script_path=REP["script"], script_commit=HEAD, env_lock_sha256=env, seed_set=REP["seed"], value="0.6728", unit_or_n="25 sessions (5 personas x 5 evaluation seeds); Constant-Same+G volatility 0.080 vs PPO+G 0.186",
    verify_cmd="run x3_0c_replay.py; row 'Constant-Same+G'", notes="Constant-Same + the same guardrails: MAE 0.6728 vs PPO+G pooled 0.6772 (per seed 0.6728-0.6874); PPO's contribution under guardrails is not identified by the frozen study. Diagnostic control constructed post hoc by stubbing the checkpoint's predict(); not a registered comparison; persona-level paired difference in P3-C022. " + REPNOTE)

add("P3-C020", "3", "VALID", "Five-seed guarded volatility 0.186: the stored spread '+/- 0.068' is a population SD (ddof=0); the sample SD is 0.076. MAE spread 0.006 is the sample SD.", "0.076 (ddof=1) / 0.068 (ddof=0)", "5 training seeds", "",
    "PHASE1-STORED", X3 + "x3_0a_spread_conventions.csv", X3 + "x3_0a_stored.py", "T2", "python -B x3_0a_stored.py (asserts)", "State the SD convention when quoting. Manifest manifest_X3-0a.json.")
add("P3-C021", "3", "VALID", "Stored seed-123 guardrail file: 101 rule activations, 12 changed the action (11.9 percent); historical-mismatch run 112 activations, 11 overrides. Stored attempted boundary actions for seed 123: raw 60, guarded 71 (the shield did not reduce attempted boundary actions for this seed).", "12 of 101", "seed 123, 25 sessions", "",
    "PHASE1-STORED", X3 + "x3_0a_guardrail_activations_vs_overrides.csv", X3 + "x3_0a_stored.py", "T2", "python -B x3_0a_stored.py", "Recomputed from stored rows only; the five-seed count (99) is P3-C008 (replay).")
add("P3-C017", "3", "VALID", "The frozen PPO checkpoints were trained against a single default simulated candidate (skill 0.6, persona 'normal'); no persona sampler exists in any training script; the four other evaluation personas are outside the training distribution.", "single candidate", "3 training scripts", "",
    "CODE", X3 + "X3_0B_STATIC_CODE_NOTE.md", "", "T3", "read execute_paper3_study.py:227-228; interview_env.py:165,297-306; simulated_candidate.py:22-27", "Static code reading (X3-0b, N1/N10); not re-executed.")
add("P3-C018", "3", "VALID", "The training candidate's noise generator is unseeded (RandomState(None)); retraining with the frozen training seeds would not regenerate the frozen checkpoints; do not claim 'same seeds reproduce the checkpoints'.", "unseeded", "", "",
    "CODE", X3 + "X3_0B_STATIC_CODE_NOTE.md", "", "T3", "read simulated_candidate.py:24; execute_paper3_study.py:240-252", "Static code reading (X3-0b, N2).")
add("P3-C019", "3", "VALID", "The training environment applied the canonical guardrails inside step() (guardrails_enabled defaults to True and is not disabled by train_ppo_seed): the frozen PPO policies were trained with the shield in the loop.", "guardrails on during training", "", "",
    "CODE", X3 + "X3_0B_STATIC_CODE_NOTE.md", "", "T3", "read interview_env.py:94,134,229-245,317-323", "Static code reading (X3-0b, N9). Whether the module import or the inline fallback copy ran in the training process is not recorded.")
pers = rd(X3 + "x3_0c_persona_paired.csv")
mean_row = [r for r in pers if r["persona"].startswith("MEAN")][0]
sd_row = [r for r in pers if r["persona"].startswith("SD")][0]
add("P3-C022", "3", "VALID", f"Persona-level paired difference in tracking MAE, PPO+G minus Constant-Same+G, averaged over the 5 training seeds: mean {mean_row['delta_ppoG_minus_constsameG']}, SD across the 5 frozen personas {sd_row['delta_ppoG_minus_constsameG']} (descriptive; n=5 personas; checkpoints trained on one candidate).",
    mean_row["delta_ppoG_minus_constsameG"], "5 personas", "SD " + sd_row["delta_ppoG_minus_constsameG"], "PHASE1-REPLAY", X3 + "x3_0c_persona_paired.csv", REP["script"], "T3", "run x3_0c_replay.py; persona_paired.csv", "DESCRIPTIVE only; no inference; input to the X3-A precision rationale. " + REPNOTE, env=env, seed=REP["seed"])
add("P3-C023", "3", "VALID", "Tracking MAE cannot distinguish trajectories that alternate between the two integer levels adjacent to a half-integer target: of 25 PPO+G sessions whose executed path differs from Constant-Same+G, only 5 differ in MAE (e.g. overconfident_fail, target 1.5).", "25 path-differing; 5 MAE-differing", "125 sessions", "",
    "PHASE1-REPLAY", X3 + "x3_0c_followup.json", X3 + "x3_0c_followup.py", "T2", "python -B x3_0c_followup.py (reads replay session log)", "Follow-up computed from the stored replay session log; addendum X3_0C_FOLLOWUP_ADDENDUM.md; env: replay (see P3-C007).", env=env)
add("P3-C024", "3", "VALID", "Constant-Same+G volatility 0.080 versus five-seed PPO+G 0.186 and heuristic 0.160: under the same shield, PPO is more volatile than a state-blind constant action.", "0.080 vs 0.186", "25 vs 125 sessions", "", "PHASE1-REPLAY", X3 + "x3_0c_replay_summary.csv", REP["script"], "T3", "run x3_0c_replay.py; replay_summary.csv", "DESCRIPTIVE; simulation only. " + REPNOTE, env=env, seed=REP["seed"])

# ------------------------------------------------------------------ X2-A
X2 = "research/analysis/phase1/x2_a/"
bo = {r["scorer"]: r for r in rd(X2 + "x2a_bootstrap_rho.csv")}
c = bo["composite"]
assert c["two_level_ci_low"] == "0.1529" and c["two_level_ci_high"] == "0.649" and c["question_only_ci_low"] == "0.3066" and c["question_only_ci_high"] == "0.5888"
X2SC = dict(script=X2 + "x2a_analysis.py", config=X2 + "x2a_config.json", seed="numpy default_rng(42); B=10000")
SENS = "SENSITIVITY analysis of the frozen estimand on the old 64-case benchmark (exploratory/initial evidence; not confirmatory). Manifest manifest_X2-A.json; pre-run note X2A_PRERUN_NOTE.md; committed before the run."
add("X2A-C001", "2", "VALID", "Composite Spearman rho 0.3812 has a two-level question-cluster bootstrap 95 percent percentile interval [0.1529, 0.6490] (8 questions; B=10000; seed 42); the frozen case-level interval [0.1575, 0.5774] treats answers as independent.", "0.3812", "64 answers / 8 questions", "[0.1529, 0.6490]",
    "PHASE1-X2A", X2 + "x2a_bootstrap_rho.csv", X2SC["script"], "T2", "python -B x2a_analysis.py (single run) ; compare x2a_bootstrap_rho.csv", SENS + " Only 8 clusters: coarse.", config=X2SC["config"], seed=X2SC["seed"])
add("X2A-C002", "2", "VALID", "Question-only cluster bootstrap (whole questions resampled) 95 percent interval for composite rho [0.3066, 0.5888]; this reproduces the earlier unstored diagnostic (approx [0.30, 0.59], P2-C012).", "0.3812", "8 questions", "[0.3066, 0.5888]",
    "PHASE1-X2A", X2 + "x2a_bootstrap_rho.csv", X2SC["script"], "T2", "as X2A-C001", SENS + " Narrower than the two-level interval because within-question sampling variability is not resampled.", config=X2SC["config"], seed=X2SC["seed"])
d = {r["contrast"]: r for r in rd(X2 + "x2a_bootstrap_rho_diff.csv")}["composite - R_only"]
add("X2A-C003", "2", "VALID", f"Composite minus R-only Spearman rho = {d['point']}, two-level 95 percent interval [{d['two_level_ci_low']}, {d['two_level_ci_high']}] (includes zero: the data neither establish nor exclude a difference).", d["point"], "8 questions", f"[{d['two_level_ci_low']}, {d['two_level_ci_high']}]",
    "PHASE1-X2A", X2 + "x2a_bootstrap_rho_diff.csv", X2SC["script"], "T2", "as X2A-C001", SENS, config=X2SC["config"], seed=X2SC["seed"])
lq = [float(r["composite"]) for r in rd(X2 + "x2a_loqo.csv")]
add("X2A-C004", "2", "VALID", f"Leave-one-question-out composite rho ranges {min(lq):.4f} to {max(lq):.4f} across the 8 left-out questions.", f"{min(lq):.4f}-{max(lq):.4f}", "8 leave-outs", "",
    "PHASE1-X2A", X2 + "x2a_loqo.csv", X2SC["script"], "T2", "as X2A-C001", SENS, config=X2SC["config"], seed=X2SC["seed"])
rl = rd(X2 + "x2a_rater_loo.csv")
a64 = [float(r["rho_composite"]) for r in rl if r["omitted_rater"].startswith("R") and r["items"] == "all 64 items"]
a54 = [float(r["rho_composite"]) for r in rl if r["omitted_rater"].startswith("R") and r["items"] != "all 64 items"]
add("X2A-C005", "2", "VALID", f"Rater leave-one-out (gold = mean of the two remaining raters): composite rho {min(a64):.4f}-{max(a64):.4f} on all 64 items and {min(a54):.4f}-{max(a54):.4f} on the 54 non-adjudicated items; the frozen gold on the 54 non-adjudicated items gives 0.4454 (ten items were adjudicated in the frozen gold).", f"{min(a64):.4f}-{max(a64):.4f}", "3 leave-outs", "",
    "PHASE1-X2A", X2 + "x2a_rater_loo.csv", X2SC["script"], "T2", "as X2A-C001", SENS, config=X2SC["config"], seed=X2SC["seed"])
ov = rd(X2 + "x2a_overlap.csv")
add("X2A-C006", "2", "EXPLORATORY", f"Composite rho on the pilot-overlap questions (1, 3, 10, 41; n=32) {ov[0]['rho_composite']} versus the other four questions (n=32) {ov[1]['rho_composite']}; R-only {ov[0]['rho_R_only']} vs {ov[1]['rho_R_only']}. Point estimates only; not a held-out validation.", ov[0]["rho_composite"], "32 vs 32", "",
    "PHASE1-X2A", X2 + "x2a_overlap.csv", X2SC["script"], "T2", "as X2A-C001", "DESCRIPTIVE/exploratory (pattern already seen; question difficulty also differs). Reproduces the earlier unstored diagnostic (P2-C012).", config=X2SC["config"], seed=X2SC["seed"])
wq = rd(X2 + "x2a_within_question.csv")[0]
ag = rd(X2 + "x2a_agreement.csv")[0]
add("X2A-C007", "2", "VALID", f"Within-question (demeaned) composite rho {wq['within_question_spearman_demeaned']} exceeds the pooled 0.3812; composite bias vs human {ag['bland_altman_bias']} (Bland-Altman 95 percent limits [{ag['loa_low']}, {ag['loa_high']}]); Lin's CCC {ag['lin_ccc']}; residual vs answer length Spearman {ag['spearman_residual_vs_answer_words']}.", wq["within_question_spearman_demeaned"], "64 answers", "",
    "PHASE1-X2A", X2 + "x2a_agreement.csv", X2SC["script"], "T2", "as X2A-C001", "DESCRIPTIVE (old benchmark, seen data).", config=X2SC["config"], seed=X2SC["seed"])
au = {r["scorer"]: r for r in rd(X2 + "x2a_auroc.csv")}
ad = rd(X2 + "x2a_auroc_diff.csv")[0]
add("X2A-C008", "2", "EXPLORATORY", f"Adversarial vs correct-reference AUROC (34 vs 22 answers): composite {au['composite']['AUROC_correct_vs_adversarial']} [{au['composite']['ci_low']}, {au['composite']['ci_high']}], R-only {au['R_only']['AUROC_correct_vs_adversarial']} [{au['R_only']['ci_low']}, {au['R_only']['ci_high']}]; composite minus R-only {ad['point']} [{ad['ci_low']}, {ad['ci_high']}].", au["composite"]["AUROC_correct_vs_adversarial"], "34 adversarial / 22 correct", "",
    "PHASE1-X2A", X2 + "x2a_auroc.csv", X2SC["script"], "T2", "as X2A-C001", "EXPLORATORY with pre-specified rule; hypothesis-generating for X2-C H3; not evidence that the composite is safer or less safe.", config=X2SC["config"], seed=X2SC["seed"])
fa = rd(X2 + "x2a_false_accept.csv")
f60 = [r for r in fa if r["rule"] == "fixed tau=0.6"][0]
f75 = [r for r in fa if r["rule"] == "fixed tau=0.75"][0]
add("X2A-C009", "2", "EXPLORATORY", f"Composite at the documented grade boundaries (no explicit accept threshold exists): tau=0.60 accepts {f60['n_false_accepts']} of 34 adversarial answers and {f60['accept_rate_correct_reference']} of correct-reference answers; tau=0.75 accepts {f75['n_false_accepts']} of 34 adversarial and {f75['accept_rate_correct_reference']} of correct-reference answers. At the matched accept-rate R-only accepted 0 adversarial answers.", f"{f60['n_false_accepts']}/34 ; {f75['n_false_accepts']}/34", "34 adversarial answers", "",
    "PHASE1-X2A", X2 + "x2a_false_accept.csv", X2SC["script"], "T2", "as X2A-C001", "EXPLORATORY (seen data; tau not chosen from results; both grade boundaries reported). Small counts. The composite is not observed to be safer than R-only on this set; H3 of X2-C is at risk.", config=X2SC["config"], seed=X2SC["seed"])
upd("P2-C012", status="HISTORICAL", superseded_by="X2A-C002;X2A-C006", notes="Unstored earlier diagnostic; reproduced as stored artifacts in X2-A (question-only interval [0.3066, 0.5888]; overlap 0.7092 vs 0.4249; per-question rho range 0.4364-0.9048).")

# ------------------------------------------------------------------ Paper 1 stored analysis (41 statements)
P1 = "research/analysis/phase1/paper1/"
surv = rd(P1 + "p1_claim_survival.csv")
assert len(surv) == 41
for i, s in enumerate(surv, 1):
    notes = f"Phase-1A claim survival row {s['row_id']}; evidence class {s['evidence_class']}; basis: {s['basis']}; check: {s['check_detail'] or 'n/a'}; X1 successor: {s['x1_successor']}."
    add(f"P1S-C{i:03d}", "1", s["status"], s["claim_as_stored"], "", "", "", "PHASE1-STORED", P1 + "p1_claim_survival.csv", P1 + "p1_stored_analysis.py", "T2" if s["check"] != "none" else "T1",
        "python -B p1_stored_analysis.py (asserts each check)", notes)
upd("P1-C009", status="DESIGN-ONLY", notes="Configuration only; effectiveness not measured by the frozen study (see P1S-C005).")
upd("P1-C003", evidence_label="PHASE1-STORED", artifact_sha256=sha("research/results/paper1/paper1_security_results.csv"), notes="Now checked from stored data: 4 of 9 observed_status equal expected_outcome (SEC-01/03/04/05); see P1S-C002/C003.")

# ------------------------------------------------------------------ write
rows_out = rows + new
with open(REG, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS, quoting=csv.QUOTE_ALL, lineterminator="\n")
    w.writeheader()
    w.writerows(rows_out)
from collections import Counter
print(len(rows), "->", len(rows_out), dict(Counter(r["status"] for r in rows_out)))
