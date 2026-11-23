"""XD: grounding probe rebuilt to separate genuine validator behaviour from an evaluator-evidence artefact (protocol MA-XA-XB v1).

Evidence class: SYNTHETIC / AUTHORED outputs (constructed feedback texts) checked by the real lexical validator
`services.qwen.app._validate_feedback_output`, against the 64 recorded production-evaluator payloads (REPLAY inputs).
No LLM is involved. The validator is deterministic, so there is no sampling variance: intervals describe the finite payload set.

Subsets (fixed before running):
  ALL            all 64 payloads, identical to the earlier E3 accounting (recomputed here and compared with the stored E3 result)
  NO_OVERLAP     payloads whose covered, missing and incorrect lists share no string (removes the evidence contradiction)
  RELABELLED     all 64 payloads with every placeholder concept text ("... core principle") given a unique number, as the evaluator now
                 does (services/evaluator/app.py::_label_concepts); the stored payloads themselves are not modified on disk
(A planned NO_PLACEHOLDER subset was dropped before the real run: a structural check showed that all 64 stored payloads contain
 placeholder text, so that subset is empty.)
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ma_common as C  # noqa: E402
sys.path.insert(0, str(C.REPO / "paper/adcom2027/experiments"))
from e3_grounding_probe import CATS, build  # noqa: E402
from scipy.stats import beta  # noqa: E402
from services.qwen.app import FeedbackRequest, _validate_feedback_output  # noqa: E402

PLACEHOLDER = re.compile(r"core principle(?: \(\d+\))?$", re.I)


def cp(k, n, a=0.05):
    if n == 0:
        return (None, None)
    lo = 0.0 if k == 0 else beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - a / 2, k + 1, n - k)
    return (round(float(lo), 4), round(float(hi), 4))


def overlap(ev):
    sets = [set(map(str, ev.get(k, []))) for k in ("correct_claims", "missing_concepts", "incorrect_claims")]
    return bool((sets[0] & sets[1]) or (sets[0] & sets[2]) or (sets[1] & sets[2]))


def has_placeholder(ev):
    return any(PLACEHOLDER.search(str(c)) for k in ("correct_claims", "missing_concepts") for c in ev.get(k, []))


def relabel(ev):
    """Number every placeholder occurrence in covered/missing so no string is shared between lists (deterministic, per payload)."""
    ev = json.loads(json.dumps(ev))
    n = 0
    for key in ("correct_claims", "missing_concepts"):
        out = []
        for c in ev.get(key, []):
            if PLACEHOLDER.search(str(c)):
                n += 1
                base = re.sub(r" \(\d+\)$", "", str(c))
                c = f"{base} ({n})"
            out.append(c)
        ev[key] = out
    return ev


def run(payloads):
    out = {}
    for cat in CATS:
        acc = rej = dis = excl = 0
        for ev in payloads:
            data, expect = build(cat, ev)
            if data is None:
                excl += 1
                continue
            accepted = bool(_validate_feedback_output(data, FeedbackRequest(question_text="q", structured_evaluation=ev)))
            acc += accepted
            rej += (not accepted)
            dis += (accepted != expect)
        n = acc + rej
        out[cat] = {"applicable": n, "accepted": acc, "rejected": rej, "excluded": excl,
                    "disagree_with_intended_label": dis, "disagree_ci95": cp(dis, n)}
    return out


def main(out_dir: Path):
    gs = C.git_state()
    by_q = C.H.load_cases()
    payloads = [c["raw_eval"] | {"case_id": c["case_id"], "qid": c["qid"]} for v in by_q.values() for c in v]
    subsets = {"ALL": payloads, "NO_OVERLAP": [p for p in payloads if not overlap(p)],
               "RELABELLED": [relabel(p) for p in payloads]}
    res = {name: {"n_payloads": len(ps), "categories": run(ps)} for name, ps in subsets.items()}
    stored = json.loads((C.REPO / "paper/adcom2027/results/e3_grounding.json").read_text())
    same = all(res["ALL"]["categories"][c][k] == stored[c][k] for c in CATS
               for k in ("applicable", "accepted", "rejected"))
    res["_checks"] = {"ALL_equals_stored_E3": same, "payloads_with_overlap": sum(overlap(p) for p in payloads),
                      "payloads_with_placeholder": sum(has_placeholder(p) for p in payloads),
                      "overlap_and_placeholder": sum(overlap(p) and has_placeholder(p) for p in payloads)}
    meta = {"protocol": "MA-XA-XB-v1", "git": gs, "validator": "services.qwen.app._validate_feedback_output",
            "input_sha256": C.sha256_file(C.H.RAW)}
    C.write_once(out_dir / "xd_grounding.json", json.dumps({"meta": meta, **res}, indent=1, sort_keys=True))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    main(Path(ap.parse_args().out))
