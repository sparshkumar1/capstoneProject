"""Exploratory add-on to E3: how often the stored evaluator evidence contradicts itself (same string covered and missing/incorrect)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import harness as H
n = both_missing = both_incorrect = 0
by_q, cases = {}, []
for v in H.load_cases().values():
    for c in v:
        ev = c["raw_eval"]
        norm = lambda xs: {str(x).lower().strip() for x in xs if x}
        cor, mis, inc = norm(ev.get("correct_claims", [])), norm(ev.get("missing_concepts", [])), norm(ev.get("incorrect_claims", []))
        n += 1
        m = bool(cor & mis); i = bool(cor & inc)
        both_missing += m; both_incorrect += i
        if m or i:
            cases.append(c["case_id"]); by_q[c["qid"]] = by_q.get(c["qid"], 0) + 1
res = {"payloads": n, "covered_and_missing_same_string": both_missing, "covered_and_incorrect_same_string": both_incorrect,
       "payloads_with_any_overlap": len(cases), "by_question": by_q, "case_ids": cases}
(Path(__file__).parents[1] / "results" / "e3_evidence_overlap.json").write_text(json.dumps(res, indent=1, sort_keys=True))
print(res)
