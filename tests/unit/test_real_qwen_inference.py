"""
Real Qwen-2.5-1.5B Local Model Verification Test
================================================
Verifies real neural inference on CPU with actual snapshot weights.
"""

import os
import json
import pytest
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from services.qwen.app import _extract_json_from_llm


@pytest.mark.real_model
def test_real_qwen_inference_misconception_followup():
    """Verify that real Qwen2.5-1.5B weights generate a gap-targeted follow-up."""
    snapshot_base = "models/qwen_1b/models--Qwen--Qwen2.5-1.5B-Instruct"
    if not os.path.exists(snapshot_base):
        pytest.skip("Local Qwen weights not present on disk")

    snapshot_path = None
    for root, dirs, files in os.walk(snapshot_base):
        if "config.json" in files:
            snapshot_path = root
            break

    if not snapshot_path:
        pytest.skip("No valid snapshot found in models/qwen_1b")

    tokenizer = AutoTokenizer.from_pretrained(snapshot_path, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        snapshot_path,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
        local_files_only=True,
    )
    model.eval()

    prompt = (
        "You are an expert technical interviewer conducting an adaptive technical interview.\n"
        "Generate ONE candidate-specific follow-up question strictly based on the candidate's actual answer and the automated evaluation breakdown.\n\n"
        "CONTEXT:\n"
        "- Topic: Hashing (Difficulty: 3/5)\n"
        "- Original Question: Explain how a hash table handles collisions.\n"
        "- Candidate Answer: \"It stores the key and value using a hash function. If there is a collision, I think the new value replaces the old one.\"\n\n"
        "EVALUATION BREAKDOWN:\n"
        "- Score: 0.35 (Grade: Poor)\n"
        "- Correct Concepts Asserted: Hash function mapping\n"
        "- Missing Concepts: Chaining, Open Addressing, Collision resolution strategies\n"
        "- Detected Misconceptions / Inaccurate Claims: Collision means replacement\n"
        "- Weakest Gap: Collision resolution strategies\n\n"
        "Output strictly a single JSON object with this format:\n"
        "{\n"
        '  "followup": "<question text>",\n'
        '  "reason": "<reasoning>",\n'
        '  "target_concepts": ["<concept1>"]\n'
        "}"
    )

    messages = [
        {"role": "system", "content": "You are a precise technical interviewer JSON API. Output strictly valid JSON without markdown fences or additional commentary."},
        {"role": "user", "content": prompt},
    ]

    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([text], return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=150, temperature=0.2, do_sample=False)

    raw_response = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)
    print("\n[REAL QWEN RAW OUTPUT]:\n", raw_response)

    parsed = _extract_json_from_llm(raw_response)
    assert parsed is not None, f"Failed to parse JSON from real Qwen output: {raw_response}"
    assert "followup" in parsed
    assert "reason" in parsed
    assert "target_concepts" in parsed

    fu_lower = parsed["followup"].lower()
    reason_lower = parsed["reason"].lower()

    # Real model should target collision resolution or the replacement misconception
    assert (
        "collision" in fu_lower
        or "replace" in fu_lower
        or "chain" in fu_lower
        or "address" in fu_lower
        or "handle" in fu_lower
        or "collision" in reason_lower
        or "misconception" in reason_lower
    )
