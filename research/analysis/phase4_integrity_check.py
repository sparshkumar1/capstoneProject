"""Phase-1 integrity check (X3-0d): frozen hashes, key hashes, run manifests, registry T1 (artifact hashes), git tracked-file changes.
Read-only apart from writing PHASE1_INTEGRITY_REPORT.md. Run: python -B research/analysis/phase1/phase1_integrity_check.py"""
import csv, hashlib, json, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
A = REPO / "research/analysis/phase1"
ROOTS = [REPO / "research/analysis", REPO / "research/confirmatory"]
sys.path.insert(0, str(REPO / "research/tools"))
import run_manifest as rm
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
lines = []; bad = 0
# 1 frozen baseline
mism = []; n = 0
for l in open(A / "frozen_hashes_phase0_baseline.txt", encoding="utf-8"):
    h, p = l.rstrip("\n").split(" *", 1); n += 1
    if not (REPO / p).exists() or sha(REPO / p) != h: mism.append(p)
lines.append(f"1. Frozen-file baseline (Phase-0 snapshot): {n} files, mismatches: {len(mism)} {mism[:5]}"); bad += len(mism)
# 2 key hashes
key = {"research/data/evaluator_benchmark/final_human_gold.csv": "363dbe6d848a04fe18be5ef1d30b6bbf63b54248fe758e5e6bd4c27a26c06ce2",
       "services/evaluator/models/tuned_model2/model.safetensors": "6a241a55bef24355378db16a6380f03226fc9394312122afa648ec9e03a94450",
       "research/experiments/paper3/frozen_config.yaml": None, "research/experiments/paper3/checkpoints/seed_123/ppo_final.zip": "299437ea0dcdd7a5eed51326e80854bd3bb55341194420b619c5da3d675e24e0",
       "rl/checkpoints/seed_123/ppo_final.zip": "2ab8d514ca748abd0ac650d4a0b1676093530b21a16b1586c764b6db8ac54575"}
km = []
for p, h in key.items():
    got = sha(REPO / p)
    if h and got != h: km.append(p)
    if p.endswith("frozen_config.yaml") and not got.startswith("d3da2184"): km.append(p)
lines.append(f"2. Key artifact hashes (gold, CrossEncoder, Paper-3 config, two checkpoints): mismatches {km}"); bad += len(km)
# 3 manifests
ms = sorted(p for r in ROOTS for p in r.rglob("manifest_*.json") if "ABORTED" not in str(p) and "attempt" not in p.parent.name and "dryrun" not in str(p)); mrows = []
for m in ms:
    d = json.loads(m.read_text(encoding="utf-8")); probs = []
    if d["status"] != "completed": probs.append("status " + d["status"])
    if d["failures"]: probs.append(f"failures {d['failures']}")
    for i in d["inputs"]:
        if i["sha256_before"] != i["sha256_after"] or sha(REPO / i["path"]) != i["sha256_before"]: probs.append("input changed " + i["path"])
    for o in d["outputs"]:
        if sha(REPO / o["path"]) != o["sha256"]: probs.append("output changed " + o["path"])
    for md in d["models"]:
        if sha(REPO / md["path"]) != md["sha256"]: probs.append("model changed " + md["path"])
    mrows.append(f"   - {m.relative_to(REPO)}: status {d['status']}, {len(d['inputs'])} inputs, {len(d['outputs'])} outputs, gate {d['gate'].get('name')}={d['gate'].get('passed')}, problems: {probs or 'none'}"); bad += len(probs)
lines.append(f"3. Run manifests ({len(ms)}):\n" + "\n".join(mrows))
# 4 registry T1
reg = list(csv.DictReader(open(REPO / "research/claims/CLAIM_REGISTRY.csv", encoding="utf-8", newline="")))
t1 = 0; t1bad = []
for r in reg:
    if r["artifact_path"] and r["artifact_sha256"]:
        t1 += 1
        if sha(REPO / r["artifact_path"]) != r["artifact_sha256"]: t1bad.append(r["claim_id"])
from collections import Counter
lines.append(f"4. Registry: {len(reg)} rows, {len(set(r['claim_id'] for r in reg))} unique IDs, statuses {dict(Counter(r['status'] for r in reg))}; T1 artifact-hash check on {t1} rows, mismatches {t1bad}"); bad += len(t1bad)
pend = [r["claim_id"] for r in reg if r["status"] == "PENDING-REGISTRATION"]
lines.append(f"   PENDING-REGISTRATION rows remaining: {pend}")
badlab = [r["claim_id"] for r in reg if r["status"] in ("VALID", "EXPLORATORY") and r["claim_id"].startswith(("X2A", "P1S")) and not r["artifact_sha256"]]
lines.append(f"   Phase-1 rows without artifact hash: {badlab}"); bad += len(badlab)
# 5 git
st = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain"], capture_output=True, text=True).stdout.splitlines()
tracked = [s for s in st if not s.startswith("??")]
lines.append(f"5. Tracked-file modifications in working tree: {tracked} (expected: pre-existing ' M .env.example' plus any not-yet-committed report edits)")
pyc = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "--ignored", "research/scripts", "rl"], capture_output=True, text=True).stdout.splitlines()
lines.append("6. Ignored/cached files under research/scripts and rl (pre-existing pycache timestamps predate Phase 1): " + "; ".join(pyc))
lines.append(f"\nRESULT: {'PASS' if bad == 0 else 'FAIL'} ({bad} problems)")
rep = "# Phase 4 integrity report (all Phase 1-3 outputs)\n\n" + "\n".join(lines) + "\n"
rm.write_new(REPO / "research/analysis/PHASE4_INTEGRITY_REPORT.md", rep); print(rep)
