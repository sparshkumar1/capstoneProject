"""E3 — grounding probe of the Qwen feedback validator on CONSTRUCTED outputs (protocol ADCOM-E1..E3 v1, section 7)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import harness as H
from services.qwen.app import FeedbackRequest, _validate_feedback_output

import os
OUT = Path(os.environ.get("ADCOM_RESULTS") or Path(__file__).parents[1] / "results")
CATS = ["C0_faithful", "C1_verbatim_missing_as_correct", "C2_verbatim_incorrect_as_correct",
        "C3_narrative_correctly_explained_missing", "C4_truncated_paraphrase_credit", "C5_score_leak", "C6_generic_fluff"]


def build(cat, ev):
    correct = [str(c) for c in ev.get("correct_claims", [])]
    missing = [str(m) for m in ev.get("missing_concepts", [])]
    incorrect = [str(m) for m in ev.get("incorrect_claims", [])]
    base = {"what_was_correct": list(correct), "what_candidate_said": "(answer)",
            "how_to_answer": "State the mechanism first, then the complexity, then an edge case.",
            "narrative_feedback": "You covered part of the expected reasoning; the gaps listed above should be addressed next."}
    if cat == "C0_faithful":
        return base, True
    if cat == "C1_verbatim_missing_as_correct":
        if not missing: return None, None
        base["what_was_correct"] = correct + [missing[0]]; return base, False
    if cat == "C2_verbatim_incorrect_as_correct":
        if not incorrect: return None, None
        base["what_was_correct"] = correct + [incorrect[0]]; return base, False
    if cat == "C3_narrative_correctly_explained_missing":
        if not missing: return None, None
        base["narrative_feedback"] = f"You correctly explained {missing[0].lower()} and the rest of the approach was sound."; return base, False
    if cat == "C4_truncated_paraphrase_credit":
        if not missing: return None, None
        part = " ".join(missing[0].split()[:5])
        base["narrative_feedback"] = f"Your treatment of {part.lower()} was spot on and left nothing to add."; return base, False
    if cat == "C5_score_leak":
        base["narrative_feedback"] = "Score: 0.62 overall, so the answer is acceptable but not complete."; return base, False
    if cat == "C6_generic_fluff":
        base["narrative_feedback"] = "Good answer"; return base, False
    raise ValueError(cat)


def main():
    out = OUT / "e3_grounding.json"
    if out.exists():
        sys.exit("write-once")
    by_q = H.load_cases()
    payloads = [c["raw_eval"] | {"case_id": c["case_id"], "qid": c["qid"]} for v in by_q.values() for c in v]
    res = {}
    for cat in CATS:
        acc = rej = excl = 0
        wrong_by_q = {}
        for ev in payloads:
            data, expect_accept = build(cat, ev)
            if data is None:
                excl += 1; continue
            req = FeedbackRequest(question_text="q", structured_evaluation=ev)
            accepted = bool(_validate_feedback_output(data, req))
            acc += accepted; rej += (not accepted)
            if accepted != expect_accept:
                wrong_by_q[ev["qid"]] = wrong_by_q.get(ev["qid"], 0) + 1
        res[cat] = {"applicable": acc + rej, "accepted": acc, "rejected": rej, "excluded_no_applicable_evidence": excl,
                    "disagree_with_intended_label": sum(wrong_by_q.values()), "by_question": wrong_by_q}
    out.write_text(json.dumps(res, indent=1, sort_keys=True))
    for c, r in res.items():
        print(f"{c:45s} applicable={r['applicable']:3d} accepted={r['accepted']:3d} rejected={r['rejected']:3d} excluded={r['excluded_no_applicable_evidence']}")

if __name__ == "__main__":
    main()
