"""
Qwen per-request latency measurement, separate from model load time.

Measures the real, unmodified `services.qwen.app.ModelRegistry.generate_full`
call (the actual in-process llama.cpp/GGUF inference path used by
`generate_followup`/`generate_feedback`), not the deterministic fallback.
Model loading happens once, outside the timed region, via one warm-up call.

No training, no new experiment design, no scoring-logic change -- this is a
timing harness around already-existing inference code, following the same
methodology as `research/results/paper1/paper1_latency_results.csv`
(warmed-up, N repetitions, mean/median/P95 reported, hardware disclosed).

Usage: python qwen_latency_measurement.py [n_reps]
"""
import json
import os
import platform
import statistics
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

os.environ.setdefault("EVALUATOR_MOCK_MODE", "0")

try:
    import psutil
    _HAVE_PSUTIL = True
except ImportError:
    _HAVE_PSUTIL = False

from services.qwen.app import (  # noqa: E402
    ModelRegistry,
    MOCK_MODE,
    GGUF_MODEL_PATH,
    FollowupRequest,
    FeedbackRequest,
    _build_followup_prompt,
    _build_feedback_prompt,
)

OUT_DIR = Path(__file__).resolve().parent.parent / "results" / "qwen_latency"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FOLLOWUP_REQ = FollowupRequest(
    original_question="Explain how a hash map resolves collisions.",
    topic="Data Structures",
    candidate_answer="A hash map maps keys to array indices using a hash function. When two keys hash to the same index, we handle the collision, usually with chaining or open addressing.",
    structured_evaluation={
        "final_score": 0.65,
        "grade": "Good",
        "correct_claims": ["hash function maps keys to indices"],
        "missing_concepts": ["load factor", "rehashing"],
        "incorrect_claims": [],
    },
)

FEEDBACK_REQ = FeedbackRequest(
    question_text="Explain how a hash map resolves collisions.",
    topic="Data Structures",
    candidate_answer="A hash map maps keys to array indices using a hash function. When two keys hash to the same index, we handle the collision, usually with chaining or open addressing.",
    structured_evaluation={
        "final_score": 0.65,
        "grade": "Good",
        "correct_claims": ["hash function maps keys to indices"],
        "missing_concepts": ["load factor", "rehashing"],
        "incorrect_claims": [],
    },
)


def percentile(values, p):
    s = sorted(values)
    k = (len(s) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    if f == c:
        return s[f]
    return s[f] + (s[c] - s[f]) * (k - f)


def summarize(label, timings_s):
    return {
        "label": label,
        "n": len(timings_s),
        "mean_ms": round(statistics.mean(timings_s) * 1000, 1),
        "median_ms": round(statistics.median(timings_s) * 1000, 1),
        "p95_ms": round(percentile(timings_s, 95) * 1000, 1),
        "min_ms": round(min(timings_s) * 1000, 1),
        "max_ms": round(max(timings_s) * 1000, 1),
        "raw_ms": [round(t * 1000, 1) for t in timings_s],
    }


def main():
    n_reps = int(sys.argv[1]) if len(sys.argv) > 1 else 8

    registry = ModelRegistry.get()

    # The real service loads this model in a FastAPI startup event
    # (services/qwen/app.py::_warm_models_background), which this standalone
    # script does not run. Replicate that one call directly -- same function,
    # same path, same key -- so the measured model is the real one, not a
    # substitute.
    load_s = None
    if "qwen_1b" not in registry.models and GGUF_MODEL_PATH.exists():
        t0 = time.perf_counter()
        registry.load_gguf_model("qwen_1b", GGUF_MODEL_PATH)
        load_s = time.perf_counter() - t0

    active_key = "qwen_7b" if "qwen_7b" in registry.models else ("qwen_1b" if "qwen_1b" in registry.models else None)

    env_info = {
        "gguf_model_path": str(GGUF_MODEL_PATH),
        "gguf_model_load_s": round(load_s, 2) if load_s is not None else None,
        "MOCK_MODE": MOCK_MODE,
        "active_model_key": active_key,
        "model_type": registry.model_types.get(active_key) if active_key else None,
        "models_loaded": list(registry.models.keys()),
        "python": sys.version,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
    }

    if MOCK_MODE or active_key is None:
        result = {
            "status": "SKIPPED_NOT_MEASURABLE",
            "reason": "MOCK_MODE is on or no in-process model is loaded; a real latency "
                      "measurement requires the actual GGUF/HF model, not the deterministic "
                      "fallback path.",
            "env": env_info,
        }
        out_path = OUT_DIR / "qwen_latency_results.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result, indent=2))
        return

    proc = psutil.Process(os.getpid()) if _HAVE_PSUTIL else None
    rss_before_load = proc.memory_info().rss / (1024 * 1024) if proc else None

    # ---- Model load (untimed for per-request latency; timed separately) ----
    t_load_start = time.perf_counter()
    warmup_prompt = _build_followup_prompt(FOLLOWUP_REQ)
    _ = registry.generate_full(active_key, warmup_prompt, 32)  # triggers lazy load + first-call warmup
    t_load_end = time.perf_counter()
    load_and_first_call_s = t_load_end - t_load_start

    rss_after_load = proc.memory_info().rss / (1024 * 1024) if proc else None

    # ---- Timed follow-up generation (model already warm) ----
    followup_times = []
    followup_prompt = _build_followup_prompt(FOLLOWUP_REQ)
    for _ in range(n_reps):
        t0 = time.perf_counter()
        registry.generate_full(active_key, followup_prompt, 128)
        followup_times.append(time.perf_counter() - t0)

    # ---- Timed feedback generation (model already warm) ----
    feedback_times = []
    feedback_prompt = _build_feedback_prompt(FEEDBACK_REQ)
    for _ in range(n_reps):
        t0 = time.perf_counter()
        registry.generate_full(active_key, feedback_prompt, 256)
        feedback_times.append(time.perf_counter() - t0)

    rss_after_run = proc.memory_info().rss / (1024 * 1024) if proc else None

    result = {
        "status": "MEASURED",
        "env": env_info,
        "load_plus_first_call_s": round(load_and_first_call_s, 2),
        "rss_before_load_mb": round(rss_before_load, 1) if rss_before_load else None,
        "rss_after_load_mb": round(rss_after_load, 1) if rss_after_load else None,
        "rss_after_run_mb": round(rss_after_run, 1) if rss_after_run else None,
        "followup_generation": summarize("followup (max_new_tokens=128)", followup_times),
        "feedback_generation": summarize("feedback (max_new_tokens=256)", feedback_times),
    }
    out_path = OUT_DIR / "qwen_latency_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
