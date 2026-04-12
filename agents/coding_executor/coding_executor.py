import multiprocessing as mp
import traceback

from .sandbox_policy import validate_source_safety


SAFE_BUILTINS = {
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "float": float,
    "int": int,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "range": range,
    "reversed": reversed,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
}


def _run_single_case(code: str, case: dict, queue: mp.Queue) -> None:
    env = {"__builtins__": SAFE_BUILTINS}
    try:
        exec(code, env, env)

        if "function" in case:
            fn_name = case["function"]
            if fn_name not in env or not callable(env[fn_name]):
                raise ValueError(f"Function '{fn_name}' not defined")
            args = case.get("args", case.get("input", []))
            if not isinstance(args, (list, tuple)):
                args = [args]
            kwargs = case.get("kwargs", {})
            result = env[fn_name](*args, **kwargs)
        elif "call" in case:
            result = eval(case["call"], env, env)
        else:
            raise ValueError("Test case must define 'function' or 'call'")

        expected = case.get("expected")
        passed = result == expected
        queue.put(
            {
                "status": "ok",
                "passed": passed,
                "expected": expected,
                "actual": result,
            }
        )
    except Exception as exc:
        queue.put(
            {
                "status": "runtime_error",
                "passed": False,
                "error": str(exc),
                "traceback": traceback.format_exc(limit=3),
            }
        )


def _execute_with_timeout(code: str, case: dict, timeout_sec: float) -> dict:
    queue = mp.Queue()
    proc = mp.Process(target=_run_single_case, args=(code, case, queue))
    proc.start()
    proc.join(timeout=timeout_sec)

    if proc.is_alive():
        proc.terminate()
        proc.join()
        return {
            "status": "timeout",
            "passed": False,
            "error": f"Execution timed out after {timeout_sec}s",
        }

    if queue.empty():
        return {
            "status": "runtime_error",
            "passed": False,
            "error": "No result returned from executor",
        }

    return queue.get()


def evaluate_code_submission(
    code: str,
    test_cases: list[dict] | None,
    timeout_sec: float = 2.0,
) -> dict:
    test_cases = test_cases or []

    safe, reasons = validate_source_safety(code)
    if not safe:
        return {
            "status": "policy_blocked",
            "coding_score": 0.0,
            "tests_total": len(test_cases),
            "tests_passed": 0,
            "test_results": [],
            "policy_reasons": reasons,
        }

    if not test_cases:
        return {
            "status": "no_tests",
            "coding_score": None,
            "tests_total": 0,
            "tests_passed": 0,
            "test_results": [],
            "policy_reasons": [],
        }

    results = []
    passed_count = 0

    for idx, case in enumerate(test_cases, start=1):
        out = _execute_with_timeout(code, case, timeout_sec=timeout_sec)
        out["test_id"] = case.get("id", f"test_{idx}")
        results.append(out)
        if out.get("passed"):
            passed_count += 1

    total = len(test_cases)
    score = passed_count / total if total else 0.0

    if passed_count == total:
        status = "ok"
    elif any(r.get("status") == "timeout" for r in results):
        status = "timeout"
    elif any(r.get("status") in {"runtime_error"} for r in results):
        status = "runtime_error"
    else:
        status = "failed"

    return {
        "status": status,
        "coding_score": round(float(score), 4),
        "tests_total": total,
        "tests_passed": passed_count,
        "test_results": results,
        "policy_reasons": [],
    }
