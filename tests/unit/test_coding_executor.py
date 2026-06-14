import textwrap

from agents.coding_executor.coding_executor import evaluate_code_submission
from agents.coding_executor.sandbox_policy import validate_source_safety


def test_validate_source_safety_blocks_dangerous_imports():
    safe, reasons = validate_source_safety("import os\nprint('hi')")
    assert safe is False
    assert any("Blocked import: os" in reason for reason in reasons)


def test_evaluate_code_submission_accepts_safe_function():
    result = evaluate_code_submission(
        textwrap.dedent(
            """
            def square(x):
                return x * x
            """
        ),
        [{"function": "square", "args": [3], "expected": 9}],
        timeout_sec=1.0,
    )

    assert result["status"] == "ok"
    assert result["tests_passed"] == 1
    assert result["tests_total"] == 1
    assert result["test_results"][0]["passed"] is True


def test_evaluate_code_submission_times_out():
    result = evaluate_code_submission(
        textwrap.dedent(
            """
            def spin():
                while True:
                    pass
            """
        ),
        [{"function": "spin", "args": [], "expected": None}],
        timeout_sec=0.1,
    )

    assert result["status"] == "timeout"
    assert result["tests_passed"] == 0
