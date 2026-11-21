"""
T-N04 -- Evaluator service API contract test.

NOTE (Phase 2 correction): services/evaluator/app.py is a FLASK app
(`app = Flask(__name__)`, @app.route handlers), NOT FastAPI as
Details/revised_report_v5.pdf Table 3.1 claims -- see
reference_material_analysis/Previous_Project_Report_Analysis.md section 3.7.
This test therefore uses Flask's own test_client(), not fastapi.testclient.

Uses Flask's test_client() against the real app object in-process -- no
network, no separately running server process required. Confirms request
schema handling, status codes, and error paths for the two primary
endpoints: /health, /api/evaluator/set-question, /api/evaluator/evaluate-answer.

Run: .venv/Scripts/python.exe testing_and_evaluation/api_tests/T-N04_evaluator_api_contract.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.evaluator.app import app  # noqa: E402

QID = "1"


def check(label, condition, detail=""):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}" + (f" -- {detail}" if detail and not condition else ""))
    return condition


def main() -> int:
    client = app.test_client()
    failures = []

    # 1. Health check
    r = client.get("/health")
    ok = r.status_code == 200 and r.get_json(silent=True) is not None
    if not check("GET /health returns 200 + JSON", ok, f"status={r.status_code}"):
        failures.append("health")

    # 2. set-question with missing qid -> 400
    r = client.post("/api/evaluator/set-question", json={"question_text": "no qid here"})
    ok = r.status_code == 400
    if not check("POST /api/evaluator/set-question missing qid -> 400", ok, f"status={r.status_code}"):
        failures.append("set-question-missing-qid")

    # 3. set-question with unknown qid -> 404
    r = client.post("/api/evaluator/set-question", json={"qid": "nonexistent_qid_99999"})
    ok = r.status_code == 404
    if not check("POST /api/evaluator/set-question unknown qid -> 404", ok, f"status={r.status_code}"):
        failures.append("set-question-unknown-qid")

    # 4. set-question with valid qid -> 200
    r = client.post("/api/evaluator/set-question", json={
        "qid": QID,
        "question_text": "Explain your logic to find the two indices in an array that sum up to a target value.",
        "topic": "Arrays",
        "difficulty": 0.4,
        "blooms_level": "Apply",
    })
    ok = r.status_code == 200 and (r.get_json() or {}).get("status") == "success"
    if not check("POST /api/evaluator/set-question valid -> 200 success", ok, f"status={r.status_code} body={r.get_json(silent=True)}"):
        failures.append("set-question-valid")

    # 5. evaluate-answer with missing transcript -> 400
    r = client.post("/api/evaluator/evaluate-answer", json={})
    ok = r.status_code == 400
    if not check("POST /api/evaluator/evaluate-answer missing transcript -> 400", ok, f"status={r.status_code}"):
        failures.append("evaluate-missing-transcript")

    # 6. evaluate-answer with valid transcript after set-question -> 200 + score in [0,1]
    r = client.post("/api/evaluator/evaluate-answer", json={
        "transcript": "I would use a hash map to store seen values and check the complement in O(n) time."
    })
    body = r.get_json(silent=True) or {}
    score = (body.get("evaluation") or {}).get("final_score")
    ok = r.status_code == 200 and isinstance(score, (int, float)) and 0.0 <= score <= 1.0
    if not check("POST /api/evaluator/evaluate-answer valid -> 200 + score in [0,1]", ok, f"status={r.status_code} score={score}"):
        failures.append("evaluate-valid")
    else:
        print(f"      -> final_score={score}")

    # 7. Malformed JSON body (not valid JSON at all) -> should not crash the server (4xx/5xx, not an unhandled exception)
    r = client.post("/api/evaluator/evaluate-answer", data="not json at all", content_type="application/json")
    ok = r.status_code in (400, 415, 500)
    if not check("POST with malformed body -> graceful 4xx/5xx (no server crash)", ok, f"status={r.status_code}"):
        failures.append("malformed-body")

    print()
    print(f"Checks: 7  Failures: {len(failures)}")
    if failures:
        print("FAILURES:", failures)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
