"""
PrepAIred — Live Qwen 1.5B GGUF Inference Verification Harness
==============================================================
Runs an end-to-end local generation test using llama.cpp / llama-cpp-python
to prove that Qwen 1.5B GGUF is executing genuine neural inference on CPU
rather than relying on fallback heuristics.

Run with:
    python scripts/verify_qwen_live.py
"""

import sys
import time
import asyncio
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.qwen.app import ModelRegistry, generate_followup, FollowupRequest, GGUF_MODEL_PATH


async def test_qwen_live():
    print("=" * 70)
    print("PREPAIRED — LIVE QWEN 1.5B GGUF INFERENCE VERIFICATION")
    print("=" * 70)
    print(f"Target GGUF Path: {GGUF_MODEL_PATH}")

    # Check 1: File Existence
    if not GGUF_MODEL_PATH.exists():
        print("[FAIL] Model file missing!")
        print("Please run: python scripts/download_qwen_model.py")
        return False

    size_mb = GGUF_MODEL_PATH.stat().st_size / (1024 * 1024)
    print(f"[OK] Found GGUF file: {size_mb:.1f} MB")

    # Check 2: Load Model via llama.cpp
    print("\n[INFO] Loading model into llama.cpp CPU engine...")
    t0 = time.time()
    registry = ModelRegistry.get()
    try:
        registry.load_gguf_model("qwen_1b", GGUF_MODEL_PATH)
    except Exception as exc:
        print(f"[FAIL] Could not load model: {exc}")
        return False
    load_time = time.time() - t0
    print(f"[OK] Model loaded in {load_time:.2f}s")

    # Check 3: Execute Live Generation
    print("\n[INFO] Submitting test follow-up generation prompt...")
    req = FollowupRequest(
        original_question="What is a hash table and how do you handle collisions?",
        candidate_answer="A hash table maps keys to values using a hash code. I forgot how to resolve collisions.",
        correct_concepts=["hash code", "key value mapping"],
        missing_concepts=["chaining", "open addressing", "linear probing"],
        current_difficulty=3,
    )

    t_gen = time.time()
    res = await generate_followup(req)
    gen_time = time.time() - t_gen

    print("\n" + "-" * 70)
    print(f"GENERATED FOLLOW-UP PROBE:\n\"{res.followup}\"")
    print(f"\nREASONING:\n\"{res.reason}\"")
    print(f"\nTARGET CONCEPTS:\n{res.target_concepts}")
    print(f"\nDECISION SOURCE:\n{res.decision_source}")
    print(f"LLM STATUS:\n{res.llm_status}")
    print(f"GENERATION LATENCY:\n{gen_time:.2f}s")
    print("-" * 70)

    # Check 4: Attribution Verification
    is_qwen = (res.decision_source == "qwen_1.5b_llm" and res.llm_status == "available")
    is_not_fallback = (res.decision_source != "non_llm_structured_recovery")
    has_text = len(res.followup.strip()) > 15

    if is_qwen and is_not_fallback and has_text:
        print("\n" + "=" * 70)
        print("VERDICT: [PASS] — GENUINE QWEN 1.5B GGUF INFERENCE CONFIRMED")
        print("=" * 70)
        print("1. Model loaded cleanly via llama.cpp.")
        print("2. Response was generated dynamically by the neural model.")
        print(f"3. Attribution correctly tagged: '{res.decision_source}'.")
        print("4. Deterministic fallback was NOT used.")
        return True
    else:
        print("\n" + "=" * 70)
        print("VERDICT: [FAIL] — FALLBACK DETECTED OR ATTRIBUTION MISMATCH")
        print("=" * 70)
        return False


def main():
    success = asyncio.run(test_qwen_live())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
