"""Empirical authority matrix: which role changes which part of session state, observed on real runs.

Method: the orchestrator's role-specific methods are wrapped; the session state (plus the question queue) is
snapshotted at every role-boundary and changes are attributed to the innermost active role.  Descriptive probe on
the 8 replay sessions (64 recorded answers); no hypothesis is tested.
"""
import asyncio, copy, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import harness as H

ROLE_OF = {
    "_evaluate_verbal": "Evaluator+Validator",
    "_generate_feedback": "FeedbackAgent",
    "_adapt_difficulty": "DifficultyPolicy(PPO+guardrails)",
    "_decide_and_inject_followup": "FollowUpAgent",
    "_update_session_state": "Hub:state-commit",
    "_select_and_send_question": "Hub:question-dispatch",
    "_rebuild_remaining_questions": "QuestionSelector",
    "_fail_closed_evaluator_unavailable": "Hub:fail-closed",
    "_finalize_session": "Hub:report",
}
VOLATILE = {"created_at", "id"}


def snap(o):
    s = copy.deepcopy(o._state)
    s["question_queue"] = [q.get("id") for q in o._question_queue]
    s["attempt_counts"] = dict(o._attempt_counts)
    return s


def changed(a, b):
    out = set()
    for k in set(a) | set(b):
        if k in VOLATILE:
            continue
        if json.dumps(a.get(k), sort_keys=True, default=str) != json.dumps(b.get(k), sort_keys=True, default=str):
            out.add(k)
    return out


class Tracer:
    def __init__(self, o):
        self.o, self.stack, self.last = o, ["Hub:other"], snap(o)
        self.counts = defaultdict(Counter)       # key -> role -> n
        self.calls = Counter()
        for name, role in ROLE_OF.items():
            self._wrap(name, role)

    def _flush(self):
        now = snap(self.o)
        for k in changed(self.last, now):
            self.counts[k][self.stack[-1]] += 1
        self.last = now

    def _wrap(self, name, role):
        o, orig, tr = self.o, getattr(self.o, name), self
        if asyncio.iscoroutinefunction(orig):
            async def w(*a, **k):
                tr._flush(); tr.stack.append(role); tr.calls[role] += 1
                try:
                    return await orig(*a, **k)
                finally:
                    tr._flush(); tr.stack.pop()
        else:
            def w(*a, **k):
                tr._flush(); tr.stack.append(role); tr.calls[role] += 1
                try:
                    return orig(*a, **k)
                finally:
                    tr._flush(); tr.stack.pop()
        setattr(o, name, w)


async def main():
    by_q, qs = H.load_cases(), H.load_questions()
    total, calls = defaultdict(Counter), Counter()
    n_turns = n_fu = 0
    for k in range(8):
        questions, answers, cases = H.session_plan(k, by_q, qs)
        ev = H.ReplayEvaluator(cases)
        o = H.new_orchestrator(k, questions, ev)
        tr = Tracer(o)
        with H.fixed_timer(), H.qwen_mode("down"):
            turns = await H.drive(o, answers)
        tr._flush()
        for key, c in tr.counts.items():
            for role, n in c.items():
                total[key][role] += n
        calls.update(tr.calls)
        n_turns += len(turns); n_fu += sum(t["is_followup"] for t in turns)
    roles = sorted({r for c in total.values() for r in c})
    out = {"sessions": 8, "turns": n_turns, "followup_turns": n_fu, "role_invocations": dict(calls),
           "writes": {k: dict(c) for k, c in sorted(total.items())}}
    p = Path(__file__).parents[1] / "results" / "trace_state_writes.json"
    p.write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({"turns": n_turns, "followups": n_fu, "calls": dict(calls)}, indent=1))
    print(f"{'state key':32s}" + "".join(f"{r[:14]:>16s}" for r in roles))
    for k, c in sorted(total.items()):
        print(f"{k:32s}" + "".join(f"{c.get(r,0):>16d}" for r in roles))

if __name__ == "__main__":
    asyncio.run(main())
