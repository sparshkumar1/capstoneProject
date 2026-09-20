#!/usr/bin/env python
"""Builds FINAL_HASH_MANIFEST.json: SHA-256 of every evidence artifact named below plus the tag -> commit map and git state.
Read-only over the repository; writes only the manifest next to this script."""
import hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "FINAL_HASH_MANIFEST.json"

GROUPS = {
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
    "F_engineering_validation_X1": [
        "research/confirmatory/X1/PROTOCOL_X1-A.md", "research/confirmatory/X1/x1a_harness.py", "research/confirmatory/X1/results/x1a/runs.jsonl",
        "research/confirmatory/X1/results/x1a/verdicts.json", "research/confirmatory/X1/run_records/x1a/RUN_RECORD.json", "research/confirmatory/X1/X1A_RESULT_NOTE.md",
        "research/confirmatory/X1/PROTOCOL_X1-B.md", "research/confirmatory/X1/x1b_harness.py", "research/confirmatory/X1/x1b_prompts.json",
        "research/confirmatory/X1/run_records/x1b_v1_aborted/x1b_v1_aborted_stdout.txt",
        "research/confirmatory/X1/PROTOCOL_X1-C.md", "research/confirmatory/X1/x1c_harness.py", "research/confirmatory/X1/results/x1c/runs.jsonl",
        "research/confirmatory/X1/results/x1c/results.csv", "research/confirmatory/X1/results/x1c/junit.xml",
        "research/confirmatory/X1/results/x1c/environment_and_verdicts.json", "research/confirmatory/X1/run_records/x1c/RUN_RECORD.json",
        "research/confirmatory/X1/X1C_RESULT_NOTE.md"],
    "H_simulation_and_preparation": [
        "research/confirmatory/X2C/precision_simulation.py", "research/confirmatory/X2C/precision_simulation_results.json",
        "research/confirmatory/X2C/X2C_GATE_STATUS_AND_PREPARATION.md", "research/evidence/final/PAPER3_FINAL_EVIDENCE.md"],
}
X1B_RESULTS = ["research/confirmatory/X1/results/x1b/summary.json", "research/confirmatory/X1/results/x1b/pairs.jsonl",
               "research/confirmatory/X1/results/x1b/pairs.csv", "research/confirmatory/X1/results/x1b/channel_enumeration.json",
               "research/confirmatory/X1/run_records/x1b/RUN_RECORD.json", "research/confirmatory/X1/X1B_RESULT_NOTE.md"]
GROUPS["F_engineering_validation_X1"] += [p for p in X1B_RESULTS if (REPO / p).exists()]


def sha(p):
    return hashlib.sha256((REPO / p).read_bytes()).hexdigest()


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()


def main():
    files, missing = {}, []
    for grp, lst in GROUPS.items():
        files[grp] = {}
        for p in lst:
            if (REPO / p).exists():
                files[grp][p] = sha(p)
            else:
                missing.append(p)
    tags = {}
    for t in git("tag", "-l").split():
        tags[t] = {"object_type": git("cat-file", "-t", t), "commit": git("rev-parse", t + "^{commit}")}
    out = {"generated_utc": datetime.now(timezone.utc).isoformat(), "head": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"),
           "categories_note": "keys are evidence-lineage categories: A frozen/pre-existing, E secondary sensitivity, F engineering validation, H simulation/preparation; D registered primary and B/C/G are represented by A/E/F and the per-paper packages",
           "files_sha256": files, "missing_files": missing, "tags": tags}
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", OUT, "files:", sum(len(v) for v in files.values()), "missing:", missing)


if __name__ == "__main__":
    main()
