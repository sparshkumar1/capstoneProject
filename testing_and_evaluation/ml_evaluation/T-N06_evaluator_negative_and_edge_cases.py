"""
T-N06 — Negative/edge-case testing of the real evaluator (services/evaluator/app.py::evaluate).

Read-only. Calls the real, production evaluate() function (loads the real
SBERT/FAISS/CrossEncoder assets, same as the passing pytest suite) on a set
of edge-case inputs: empty transcript, whitespace-only, extremely long
repeated text, non-English/garbled text, and a normal correct answer as a
sanity control.

Objective: confirm the evaluator never crashes and always returns a score in
[0, 1] for malformed input, per the "fails gracefully" requirement.

Run: .venv/Scripts/python.exe testing_and_evaluation/ml_evaluation/T-N06_evaluator_negative_and_edge_cases.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

# Windows consoles default to cp1252, which cannot print Cyrillic/CJK/emoji.
# Reconfigure stdout to UTF-8 so printing the edge-case inputs themselves
# (Unicode/emoji test cases) doesn't raise UnicodeEncodeError in THIS script's
# own print() calls -- unrelated to whether evaluate() itself handles them.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from services.evaluator.app import evaluate, get_rubric  # noqa: E402

QID = "1"
QN = "Explain your logic to find the two indices in an array that sum up to a target value."

CASES = [
    ("empty_string", ""),
    ("whitespace_only", "   \n\t  "),
    ("single_word", "array"),
    ("extremely_long_repeated", ("hash map two pointer brute force " * 500)),
    ("garbled_non_english", "asdkjasldkj 1234 !@#$ лорем ипсум 的你好世界 random garbage text"),
    ("normal_correct_answer", "I would use a hash map. Iterate through the array, and for each element, check if target minus the current element exists in the map. If it does, return the pair of indices. Otherwise, insert the current element and its index into the map. This runs in O(n) time with O(n) space, compared to the O(n^2) brute-force approach."),
    ("sql_injection_like", "'; DROP TABLE questions; --"),
    ("html_script_tag", "<script>alert('xss')</script> use a hash map"),
    ("only_punctuation", "!!!...???,,,;;;"),
    ("unicode_emoji_spam", "🔥💯🚀" * 50),
]


def main() -> int:
    rubric = get_rubric(QID)
    if rubric is None:
        print(f"FATAL: no rubric found for qid={QID!r}; cannot proceed")
        return 2

    failures = []
    for label, text in CASES:
        try:
            result = evaluate(QN, text, rubric)
            score = result.get("final_score") if isinstance(result, dict) else None
            ok = isinstance(score, (int, float)) and 0.0 <= float(score) <= 1.0
            status = "OK" if ok else "FAIL"
            if not ok:
                failures.append((label, f"score out of range or missing: {score!r}"))
            preview = text[:40].replace("\n", " ")
            print(f"[{status}] {label}: input={preview!r}({len(text)} chars) -> final_score={score}")
        except Exception as exc:
            failures.append((label, f"EXCEPTION: {type(exc).__name__}: {exc}"))
            print(f"[FAIL] {label}: raised {type(exc).__name__}: {exc}")

    print()
    print(f"Cases run: {len(CASES)}  Failures (crash or out-of-range score): {len(failures)}")
    if failures:
        print("FAILURES:")
        for label, msg in failures:
            print(f"  - {label}: {msg}")
        return 1
    print("Evaluator did not crash and returned an in-range score for every edge-case input, including empty/whitespace/garbled/injection-like/emoji text.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
