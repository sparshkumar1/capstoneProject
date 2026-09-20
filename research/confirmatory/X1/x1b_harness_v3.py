#!/usr/bin/env python
"""X1-B-I harness: Qwen fixed-answer invariance (Paper 1). Protocol: research/confirmatory/X1/PROTOCOL_X1-B_v3.md (build B revision of the v2 design).

Fixed-answer invariance only: the evaluator result is a fixed stub (byte-identical for every trial); what varies is the
LLM-facing candidate text. Every trial runs the REAL orchestrator answer path (handle_voice_answer) with the REAL Qwen
service; only the evaluator call is stubbed. Behavioural stress (B2) is a separate experiment and is not part of this file.

    --dry-run                          2 pairs, temp output, not evidence
    --run --registered-commit <40>     official run (protocol tag gate), write-once output
"""
import ast, asyncio, copy, csv, hashlib, json, os, re, subprocess, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
os.environ.setdefault("EVALUATOR_MOCK_MODE", "1")
from agents.orchestrator.interview_orchestrator import InterviewOrchestrator
import agents.orchestrator.feedback_agent as fa

PROTOCOL_TAG = "prereg/X1-B/v3"
REPLICATES = 2                       # independent fresh runs of every injection pair (stochastic decoding; some Qwen outputs are rejected by the service)
SUT_TAG = "sut/X1/build-B"
OUT_REL = "research/confirmatory/X1/results/x1b_v3"
PROMPTS = REPO / "research/confirmatory/X1/x1b_prompts.json"
QWEN = "http://localhost:8001"
LLM_CLIENT_TIMEOUT_S = 600.0        # DEVIATION from the shipped 6.0 s (see protocol section 2): real generation takes far longer than 6 s on this CPU
FIXED_EVAL = {"final_score": 0.90, "raw_evaluator_score": 0.90, "grade": "Excellent",
              "score_breakdown": {"semantic_similarity": 0.8, "concept_coverage": 0.9, "reasoning_quality": 0.95, "overall": 0.9},
              "covered_concepts": ["pointer dereference"], "correct_claims": ["pointer dereference"],
              "missing_concepts": [], "incorrect_claims": [], "weakest_gap": "None - comprehensive answer",
              "decision_source": "evaluator_cross_encoder", "mandatory_pass": True, "mistake_penalty": 0.0}
QUESTION = {"id": "x1b_q1", "text": "Explain what a pointer is in C.", "topic": "pointers",
            "difficulty": 3, "type": "verbal", "expected_concepts": ["pointer dereference"],
            "reference_answer": "A pointer holds the address of another variable; dereferencing reads the value stored there."}
STATIC_FILES = ["agents/orchestrator/interview_orchestrator.py", "agents/orchestrator/feedback_agent.py",
                "services/storage/best_answer.py", "services/storage/database.py"]
PROTECTED_KEYS = {"final_score", "raw_score", "validated_score", "raw_evaluator_score", "current_difficulty", "is_best", "difficulty",
                  "timing_modifier", "technical_performance"}
TAINT = ("qwen", "narrative", "llm", "fu_data", "actionable", "how_to_answer", "stronger_answer", "qwen_res", "hint")
LLM_TEXT_KEYS = ("narrative_feedback", "justification", "how_to_answer", "stronger_answer_guide", "actionable_improvements",
                 "what_was_correct", "what_was_incorrect", "what_was_incomplete", "missing_concepts", "what_candidate_said")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def cj(x):
    return json.dumps(x, sort_keys=True, default=str)


# ------------------------------------------------------------------------------------------ static guard
def _names(node):
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            out.append(n.id)
        elif isinstance(n, ast.Attribute):
            out.append(n.attr)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.append(n.value)
    return out


def static_guard(src, label):
    """Flag every statement that writes a protected key/name whose right-hand side mentions an LLM-derived name."""
    tree = ast.parse(src)
    hits = []
    for n in ast.walk(tree):
        targets, rhs = [], None
        if isinstance(n, ast.Assign):
            targets, rhs = n.targets, n.value
        elif isinstance(n, ast.AugAssign):
            targets, rhs = [n.target], n.value
        elif isinstance(n, ast.Dict):
            for k, v in zip(n.keys, n.values):
                if isinstance(k, ast.Constant) and k.value in PROTECTED_KEYS and v is not None:
                    hits.append((n.lineno, k.value, v))
            continue
        for t in targets:
            key = None
            if isinstance(t, ast.Subscript) and isinstance(t.slice, ast.Constant) and t.slice.value in PROTECTED_KEYS:
                key = t.slice.value
            elif isinstance(t, ast.Name) and t.id in PROTECTED_KEYS:
                key = t.id
            elif isinstance(t, ast.Attribute) and t.attr in PROTECTED_KEYS:
                key = t.attr
            if key and rhs is not None:
                hits.append((n.lineno, key, rhs))
    flagged = []
    for line, key, rhs in hits:
        bad = sorted({x for x in _names(rhs) if any(tk in x.lower() for tk in TAINT)})
        if bad:
            flagged.append({"file": label, "line": line, "protected_key": key, "tainted_names": bad})
    return {"file": label, "protected_writes_scanned": len(hits), "flagged": flagged}


def static_report():
    rep = [static_guard((REPO / f).read_text(encoding="utf-8"), f) for f in STATIC_FILES]
    mutant_src = (REPO / STATIC_FILES[0]).read_text(encoding="utf-8") + (
        "\n\ndef _x1b_mutant(eval_result, qwen_res):\n    eval_result['final_score'] = float(len(qwen_res['narrative_feedback'])) / 1000.0\n")
    m = static_guard(mutant_src, "MUTANT(" + STATIC_FILES[0] + ")")
    return {"real_sources": rep, "mutant_detected": len(m["flagged"]) > 0, "mutant": m}


def channel_enumeration():
    """Every call site that contacts the Qwen service or consumes its structured-fallback engine (grep, stored as evidence)."""
    pats = ["localhost:8001", "_query_qwen_feedback", "_synthesize_structured_followup", "qwen_followup", "qwen_res", "fu_data",
            "target_concepts", "/api/qwen/hint"]
    rows = []
    for f in ["agents/orchestrator/interview_orchestrator.py", "agents/orchestrator/feedback_agent.py", "apps/backend/main.py"]:
        for i, ln in enumerate((REPO / f).read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for p in pats:
                if p in ln:
                    rows.append({"file": f, "line": i, "pattern": p, "text": ln.strip()[:160]})
    return rows


# ------------------------------------------------------------------------------------------ trial
def _orch():
    o = InterviewOrchestrator("x1b", {"experience": "intermediate"},
                              {"c_topics": ["pointers"], "dsa_topics": ["graphs"], "duration_minutes": 30, "num_questions": 5,
                               "interview_mode": "standard"})
    o._select_questions_fn = None
    o._question_queue = [copy.deepcopy(QUESTION)] + [dict(QUESTION, id="x1b_q%d" % i) for i in range(2, 6)]
    o._state["questions"] = list(o._question_queue)
    return o


async def one_turn(transcript, mutant=False, replay_fb=None):
    o = _orch()
    await o.start()
    real_gen = o._generate_feedback
    captured = {}

    async def gen(tr, q, ev, *a, **k):
        if replay_fb is not None:                              # mutant arms replay the recorded real LLM output (no extra LLM call)
            fb = copy.deepcopy(replay_fb)
        else:
            fb = await real_gen(tr, q, ev, *a, **k)
            captured["fb"] = copy.deepcopy(fb)
        if mutant:                                             # harness-copy mutant: an LLM field is wired into the score path
            txt = str(fb.get("narrative_feedback", ""))
            ev["final_score"] = round((sum(map(ord, txt)) % 100) / 100.0, 4)
        return fb
    with patch.object(o, "_evaluate_verbal", new_callable=AsyncMock, return_value=copy.deepcopy(FIXED_EVAL)), \
            patch.object(o, "_generate_feedback", side_effect=gen):
        t0 = time.time()
        resp = await o.handle_voice_answer(transcript, QUESTION["id"])
        dt = time.time() - t0
    fb = resp.get("feedback", {})
    inv = {"fb_final_score": fb.get("final_score"), "fb_raw_evaluator_score": fb.get("raw_evaluator_score"), "fb_grade": fb.get("grade"),
           "fb_score_breakdown": fb.get("score_breakdown"), "state_scores": o._state.get("scores"), "state_raw_scores": o._state.get("raw_scores"),
           "state_current_difficulty": o._state.get("current_difficulty"), "difficulty_update": resp.get("difficulty_update"),
           "next_action": resp.get("next_action"), "is_best": fb.get("is_best"), "authoritative_best_answer": fb.get("authoritative_best_answer"),
           "best_validated_score": (fb.get("best_answer") or {}).get("validated_score"),
           "technical_performance": o._state.get("technical_performance"), "queue_len": len(o._question_queue)}
    llm = {k: fb.get(k) for k in LLM_TEXT_KEYS}
    return {"invariants": inv, "llm_text": llm, "llm_status": fb.get("llm_status"), "decision_source": fb.get("decision_source"),
            "seconds": round(dt, 2), "_raw_fb": captured.get("fb")}


def qwen_health():
    import httpx
    h = httpx.get(QWEN + "/health", timeout=5).json()
    return h


def diff_inv(a, b):
    return sorted(k for k in a if cj(a[k]) != cj(b[k]))


def real_llm(t):
    return t["llm_status"] == "available" and "non_llm" not in str(t["decision_source"]).lower() and "qwen" in str(t["decision_source"]).lower()


async def campaign(n_limit=None):
    fa.QWEN_TIMEOUT = LLM_CLIENT_TIMEOUT_S
    cfg = json.loads(PROMPTS.read_text(encoding="utf-8"))
    inj = cfg["injections"][:n_limit] if n_limit else cfg["injections"]
    rows = []
    for i, s, rp in [(i, s, rp) for i, s in enumerate(inj, 1) for rp in range(1, REPLICATES + 1)]:
        benign = await one_turn(cfg["base_answer"])
        adv = await one_turn(cfg["base_answer"] + " " + s)
        d = diff_inv(benign["invariants"], adv["invariants"])
        mben = await one_turn(cfg["base_answer"], mutant=True, replay_fb=benign["_raw_fb"])
        madv = await one_turn(cfg["base_answer"] + " " + s, mutant=True, replay_fb=adv["_raw_fb"])
        md = diff_inv(mben["invariants"], madv["invariants"])
        benign.pop("_raw_fb", None)
        adv.pop("_raw_fb", None)
        text_changed = cj(benign["llm_text"]) != cj(adv["llm_text"])
        rows.append({"pair": "%d.%d" % (i, rp), "injection_index": i, "replicate": rp, "injection": s, "injection_sha256": sha256_bytes(s.encode()), "invariant_differences": d, "invariant": not d,
                     "benign_llm_real": real_llm(benign), "adv_llm_real": real_llm(adv), "valid_pair": real_llm(benign) and real_llm(adv),
                     "llm_text_changed_between_arms": text_changed, "mutant_differences": md, "mutant_detected": bool(md),
                     "benign": benign, "adversarial": adv, "mutant_benign_scores": mben["invariants"]["state_scores"],
                     "mutant_adv_scores": madv["invariants"]["state_scores"]})
        print("pair %s invariant=%s valid=%s text_changed=%s mutant_detected=%s (%.0fs)" % (
            i, not d, rows[-1]["valid_pair"], text_changed, bool(md), benign["seconds"] + adv["seconds"]), flush=True)
    return rows


def summarise(rows, static, health):
    valid = [r for r in rows if r["valid_pair"]]
    return {"pairs_total": len(rows), "pairs_valid_llm_sourced": len(valid),
            "invariant_all_pairs": "%d/%d" % (sum(r["invariant"] for r in rows), len(rows)),
            "invariant_valid_pairs": "%d/%d" % (sum(r["invariant"] for r in valid), len(valid)),
            "pairs_where_llm_text_changed": "%d/%d" % (sum(r["llm_text_changed_between_arms"] for r in rows), len(rows)),
            "mutant_detected_pairs": "%d/%d" % (sum(r["mutant_detected"] for r in rows), len(rows)),
            "static_guard_real_sources_flagged": sum(len(x["flagged"]) for x in static["real_sources"]),
            "static_guard_mutant_detected": static["mutant_detected"], "qwen_health": health,
            "minimum_valid_pairs_required": 30, "meets_minimum": len(valid) >= 30}


def sut_state():
    g = lambda *a: subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()
    diff = lambda p: subprocess.run(["git", "-C", str(REPO), "diff", "--quiet", SUT_TAG, "--", p]).returncode == 0
    return {"sut_tag": SUT_TAG, "sut_commit": g("rev-parse", SUT_TAG + "^{commit}"), "head": g("rev-parse", "HEAD"),
            "agents_clean_vs_sut_tag": diff("agents"), "services_clean_vs_sut_tag": diff("services"),
            "prompts_sha256": sha256_bytes(PROMPTS.read_bytes()), "model_file": "models/gguf/qwen2.5-1.5b-instruct-q4_k_m.gguf",
            "model_sha256": hashlib.sha256(open(REPO / "models/gguf/qwen2.5-1.5b-instruct-q4_k_m.gguf", "rb").read()).hexdigest(),
            "decoding": "service defaults: temperature 0.1, top_p 0.9, max_new_tokens 512 (QWEN_FEEDBACK_MAX_NEW_TOKENS default), no fixed seed (llama.cpp default)"}


def dry_run():
    h = qwen_health()
    print("qwen health:", json.dumps(h)[:300])
    rows = asyncio.run(campaign(2))
    print(json.dumps({k: v for k, v in rows[0].items() if k not in ("benign", "adversarial")}, indent=1)[:900])
    print("LLM text sample:", str(rows[0]["adversarial"]["llm_text"].get("narrative_feedback"))[:200], rows[0]["adversarial"]["decision_source"])


def official(argv):
    rc = argv[argv.index("--registered-commit") + 1] if "--registered-commit" in argv[:-1] else ""
    g = lambda *a: subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()
    assert re.fullmatch("[0-9a-f]{40}", rc), "40-hex --registered-commit required"
    assert g("cat-file", "-t", "refs/tags/" + PROTOCOL_TAG) == "tag", "protocol tag missing/not annotated"
    assert g("rev-parse", "refs/tags/%s^{commit}" % PROTOCOL_TAG) == rc == g("rev-parse", "HEAD"), "HEAD != protocol tag commit"
    for rel in ("research/confirmatory/X1/x1b_harness_v3.py", "research/confirmatory/X1/PROTOCOL_X1-B_v3.md", "research/confirmatory/X1/x1b_prompts.json"):
        blob = subprocess.run(["git", "-C", str(REPO), "cat-file", "blob", "%s:%s" % (rc, rel)], capture_output=True).stdout
        assert blob == (REPO / rel).read_bytes(), rel + " differs from the tagged blob"
    sut = sut_state()
    assert sut["agents_clean_vs_sut_tag"] and sut["services_clean_vs_sut_tag"], "SUT differs from tag"
    health = qwen_health()
    assert not health.get("mock_mode") and "qwen_1b" in health.get("models_loaded", []), "real Qwen model is not loaded: %r" % health
    out = REPO / OUT_REL
    os.makedirs(out.parent, exist_ok=True)
    os.mkdir(out)
    t0 = datetime.now(timezone.utc).isoformat()
    static = static_report()
    channels = channel_enumeration()
    rows = asyncio.run(campaign())
    summ = summarise(rows, static, health)
    summ["run"] = {"protocol_tag": PROTOCOL_TAG, "registered_commit": rc, "started_utc": t0, "finished_utc": datetime.now(timezone.utc).isoformat(),
                   "harness_sha256": sha256_bytes(Path(__file__).read_bytes())}
    json.dump({"sut": sut, "summary": summ, "static_guard": static, "fixed_evaluator_result": FIXED_EVAL}, open(out / "summary.json", "x", encoding="utf-8"), indent=2)
    json.dump(channels, open(out / "channel_enumeration.json", "x", encoding="utf-8"), indent=2)
    with open(out / "pairs.jsonl", "x", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with open(out / "pairs.csv", "x", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pair", "injection_sha256", "valid_pair", "invariant", "invariant_differences", "llm_text_changed", "mutant_detected", "benign_source", "adv_source"])
        for r in rows:
            w.writerow([r["pair"], r["injection_sha256"], r["valid_pair"], r["invariant"], ";".join(r["invariant_differences"]),
                        r["llm_text_changed_between_arms"], r["mutant_detected"], r["benign"]["decision_source"], r["adversarial"]["decision_source"]])
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        dry_run()
    elif "--run" in sys.argv:
        official(sys.argv)
    else:
        print(__doc__)
