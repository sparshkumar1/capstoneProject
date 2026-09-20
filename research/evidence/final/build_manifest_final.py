#!/usr/bin/env python
"""Builds FINAL_HASH_MANIFEST_FINAL.json for the final evidence freeze: SHA-256 of every evidence artifact (explicit groups, globbed
result directories), the tag -> commit/object map and git state. Read-only over the repository; writes only the manifest next to this
script. The provisional manifest (FINAL_HASH_MANIFEST.json, tag freeze/EVIDENCE/2026-09-20) is not touched."""
import hashlib, json, subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "FINAL_HASH_MANIFEST_FINAL.json"

EXPLICIT = {
    "A_frozen_preexisting": [
        "research/data/evaluator_benchmark/final_human_gold.csv", "research/data/evaluator_benchmark/benchmark_dataset.csv",
        "research/confirmatory/X3-A/results/sessions.csv", "research/confirmatory/X3-A/results/x3a_decision.json",
        "research/confirmatory/X3-A/results/manifest_X3-A-run.json", "research/confirmatory/X3-A/results/manifest_X3-A-analysis.json",
        "research/locks/LOCK-X3-2026-09-19.lock.json", "research/locks/LOCK-X3-2026-09-19.requirements.txt",
        "research/analysis/RESULT_HASHES_phase3.txt", "research/claims/CLAIM_REGISTRY.csv"],
    "E_secondary_sensitivity_O7": [
        "research/analysis/x3a_o7/x3a_o7.py", "research/analysis/x3a_o7/O7_REGISTRATION.json", "research/audit/X3A_O7_SENSITIVITY_SPEC.md",
        "research/analysis/x3a_o7/results/r0_record.json", "research/analysis/x3a_o7/results/x3a_o7_results.json",
        "research/analysis/x3a_o7/results/x3a_o7_report.md", "research/analysis/x3a_o7/run_record/O7_RUN_RECORD.json",
        "research/analysis/x3a_o7/O7_INTERPRETATION.md"],
    "I_build_B_code_and_tests": [
        "agents/coding_executor/coding_executor.py", "agents/orchestrator/interview_orchestrator.py", "agents/orchestrator/feedback_agent.py",
        "services/qwen/app.py", "tests/unit/test_evaluator_outage_and_sandbox_cleanup.py"],
    "H_simulation_and_preparation": [
        "research/confirmatory/X2C/precision_simulation.py", "research/confirmatory/X2C/precision_simulation_results.json",
        "research/confirmatory/X2C/X2C_GATE_STATUS_AND_PREPARATION.md"],
    "J_audit_claims_literature": [
        "research/evidence/final/X1_METHOD_AUDIT.md", "research/evidence/final/DEFECT_DECISIONS_FLT03_FLT06.md",
        "research/evidence/final/PAPER1_FINAL_CLAIM_MATRIX.md", "research/evidence/final/PAPER2_FINAL_CLAIM_MATRIX.md",
        "research/evidence/final/PAPER3_FINAL_CLAIM_MATRIX.md", "research/evidence/final/PAPER3_FINAL_EVIDENCE.md",
        "research/evidence/final/X1_OLD_VS_NEW_SUMMARY.md", "research/evidence/final/X1-A-old-vs-new.md", "research/evidence/final/X1-C-old-vs-new.md",
        "research/evidence/final/X1-B-old-vs-new.md", "research/evidence/final/FINAL_PUBLICATION_READINESS.md",
        "research/literature/FINAL_RESEARCH_POSITIONING.md", "research/literature/FINAL_REFERENCE_GAP_MATRIX.md",
        "research/literature/FINAL_RESEARCH_POSITIONING_pass1_2026-09-20.md", "research/evidence/final/FINAL_CLAIM_AUDIT.md",
        "research/evidence/final/FINAL_STATISTICAL_AUDIT.md", "research/evidence/final/FINAL_EVIDENCE_FREEZE_FINAL.md", "research/evidence/final/X1_OLD_VS_NEW_SUMMARY.md",
        "research/evidence/final/X1_B2_DECISION.md",
        # first-pass literature files: present in the working tree but deliberately NOT committed (hashed here for traceability)
        "research/literature/LITERATURE_NOVELTY_MASTER_MATRIX.md", "research/literature/ALTERNATIVE_PAPER_POSITIONING.md", "research/literature/SECOND_PASS_CLAIM_AUDIT.md"],
}
GLOBS = {
    "F_X1_build_A_v1": ["research/confirmatory/X1/PROTOCOL_X1-[ABC].md", "research/confirmatory/X1/x1[abc]_harness.py", "research/confirmatory/X1/x1b_prompts.json",
                        "research/confirmatory/X1/X1[ABC]_RESULT_NOTE.md", "research/confirmatory/X1/results/x1a/*", "research/confirmatory/X1/results/x1b/*",
                        "research/confirmatory/X1/results/x1c/*", "research/confirmatory/X1/run_records/*/*"],
    "G_X1_build_B_v2_v3": ["research/confirmatory/X1/PROTOCOL_X1-*_v[23].md", "research/confirmatory/X1/x1[ac]_harness_v2.py", "research/confirmatory/X1/x1b_harness_v3.py",
                           "research/confirmatory/X1/X1*_v[23]_RESULT_NOTE.md", "research/confirmatory/X1/results/x1a_v2/*", "research/confirmatory/X1/results/x1b_v3/*",
                           "research/confirmatory/X1/results/x1c_v2/*", "research/confirmatory/X1/run_records/*_v[23]/*"],
    "K_manuscript_preparation": ["research/evidence/final/manuscript/paper[123]/*.md"],
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()


def main():
    files, missing = {}, []
    for grp, lst in EXPLICIT.items():
        files[grp] = {}
        for rel in lst:
            p = REPO / rel
            if p.is_file():
                files[grp][rel] = sha(p)
            else:
                missing.append(rel)
    for grp, pats in GLOBS.items():
        files.setdefault(grp, {})
        for pat in pats:
            for p in sorted(REPO.glob(pat)):
                if p.is_file():
                    files[grp][p.relative_to(REPO).as_posix()] = sha(p)
    tags = {t: {"object_type": git("cat-file", "-t", t), "commit": git("rev-parse", t + "^{commit}")} for t in git("tag", "-l").split()}
    out = {"generated_utc": datetime.now(timezone.utc).isoformat(), "head": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"),
           "note": "final evidence manifest; supersedes nothing (the provisional FINAL_HASH_MANIFEST.json stays as tagged)",
           "files_sha256": files, "missing_files": missing, "tags": tags}
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", OUT.name, "files:", sum(len(v) for v in files.values()), "tags:", len(tags), "missing:", missing)


if __name__ == "__main__":
    main()
