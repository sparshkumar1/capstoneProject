"""Write results/RUN_LEDGER.md: hashes of inputs, scripts and results, git state, tags, and the dated experiment ledger."""
import hashlib, subprocess, datetime
from pathlib import Path
ROOT = Path(__file__).parents[1]; REPO = ROOT.parents[1]
sh = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout.strip()
L = ["# Run ledger — ADCOM 2027 work", "", f"Generated {datetime.datetime.now(datetime.UTC).isoformat(timespec='seconds')}; branch `{git('branch','--show-current')}`; base `cb888f2`; HEAD `{git('rev-parse','HEAD')}`.", "",
     "## Tags (local, unpushed; no external timestamp)"]
for t in git("tag", "-l", "prereg/ADCOM*").splitlines():
    L.append(f"- `{t}` -> {git('rev-list','-n1',t)[:12]}; {git('tag','-l','-n1',t).split(None,1)[1] if ' ' in git('tag','-l','-n1',t) else ''}")
L += ["", "## Inputs (sha256)"]
for p in ["research/results/paper2/paper2_evaluator_raw.json", "research/data/evaluator_benchmark/benchmark_dataset.csv"]:
    L.append(f"- `{p}`: {sh(REPO/p)}")
ck = list((REPO/'research/experiments/paper3/checkpoints').glob('seed_123/*.zip')) + list((REPO/'rl/checkpoints').rglob('*seed_123*.zip'))
L += ["", "## Scripts and results (sha256)"]
for d in ["protocol", "experiments", "results", "figures", "verification"]:
    for p in sorted((ROOT/d).glob("*")):
        if p.is_file() and p.name != "RUN_LEDGER.md" and p.suffix not in (".png",):
            L.append(f"- `{d}/{p.name}`: {sh(p)}")
L += ["", "## Dated experiment ledger (2026-10-02, one working session)",
"| id | what | class | outcome |", "|---|---|---|---|",
"| T0 | state-write trace, 8 sessions / 186 turns, run before the protocol | replay, descriptive | evaluator/validator/feedback wrote 0 keys; follow-up 1 key; policy 14; hub commit 22 |",
"| T1 | existing 7 test files, first run | tests | 2 failures (one needed `python-multipart`, one `test_evaluator_failure_produces_structured_failure_without_fabrication` of unknown cause); two further runs 145 passed. The transient failure is unexplained. |",
"| H1 | harness bug: follow-up of a follow-up had no recorded answer (retry exhaustion) | harness | fixed before any registered run (root-question lookup); trace re-run |",
"| S1 | smoke runs of E1, E3, E2 (partial), E4, E5 into a scratch directory | smoke | harness checked; the E1 smoke path of V0/session 0 prompted the exploratory reversal metric (disclosed in amendment A1) |",
"| E1 | 752 sessions, 18 cells (protocol v1) | replay | 14/14 predictions matched; F2 seeds 0-19 produced 15/160 non-terminating V0 sessions (analytic expectation ~30% per session; seeds 0-19 drew few triple failures; not re-selected) |",
"| E3 | grounding probe on 64 payloads | constructed | faithful C0 accepted 47/64 (17 payloads have the same string covered and missing); C4 paraphrase accepted 40/57 |",
"| E4 | strict contract before/after (amendment A2) | replay | predictions (i)-(vi) held |",
"| E2 | hanging/refusing/healthy server, 24 turns | socket | 24.7 / 0.69 / 0.14 s median; server-side counter disagreed with client attempts (96 vs 80), not investigated |",
"| E5 | circuit breaker before/after (amendment A3) | socket | predictions (i)-(v) held; P120 equals P60 because cooldown (60 s) has elapsed at every turn |",
"| R1 | full test suite on the branch vs the cb888f2 snapshot | tests | baseline 23 failed, 306 passed, 36 errors; branch 23 failed, 329 passed, 36 errors; identical failing sets (Docker, faiss/HF not available). One existing test encoded the old None-score behaviour and was updated deliberately |",
"| X1 | first full-suite attempt used -x and stopped at a missing-faiss error; a second run was killed mid-way after source edits and discarded | tests | not used |"]
(ROOT/"results"/"RUN_LEDGER.md").write_text("\n".join(L) + "\n")
print("ledger written")
