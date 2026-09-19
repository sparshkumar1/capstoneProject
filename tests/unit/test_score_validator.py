"""
Unit and regression tests for ScoreValidator guardrails.
Tests out-of-range numeric values, missing scores, missing required fields,
malformed schemas, wrong types, and contradictory evaluator outputs.
"""

import math
import pytest
from agents.validation.score_validator import ScoreValidator, aggregate_scores


def test_validator_clamps_out_of_range_numeric():
    """ScoreValidator clamps scores > 1.0 down to 1.0 and scores < 0.0 up to 0.0."""
    validator = ScoreValidator()
    
    res_high = validator.validate(1.45, evidence={}, is_coding=False)
    assert res_high["validated_score"] == 1.0
    assert any(t["rule"] == "clamp_0_1" for t in res_high["validation_trace"])

    res_low = validator.validate(-0.25, evidence={}, is_coding=False)
    assert res_low["validated_score"] == 0.0
    assert any(t["rule"] == "clamp_0_1" for t in res_low["validation_trace"])

    res_extreme = validator.validate(999.0, evidence={}, is_coding=False)
    assert res_extreme["validated_score"] == 1.0


def test_validator_handles_missing_and_none_score():
    """ScoreValidator safely converts None score to 0.0 with explicit trace."""
    validator = ScoreValidator()
    res = validator.validate(None, evidence={}, is_coding=False)
    assert res["validated_score"] == 0.0
    assert any(t["rule"] == "missing_score" for t in res["validation_trace"])


def test_validator_handles_wrong_type_and_non_numeric():
    """ScoreValidator safely handles non-numeric strings, objects, and lists."""
    validator = ScoreValidator()
    
    res_str = validator.validate("invalid_score_string", evidence={}, is_coding=False)
    assert res_str["validated_score"] == 0.0
    assert any(t["rule"] == "type_error" for t in res_str["validation_trace"])

    res_list = validator.validate([0.85], evidence={}, is_coding=False)
    assert res_list["validated_score"] == 0.0
    assert any(t["rule"] == "type_error" for t in res_list["validation_trace"])


def test_validator_handles_nan_and_inf():
    """ScoreValidator replaces NaN and Inf with 0.0."""
    validator = ScoreValidator()
    
    res_nan = validator.validate(float("nan"), evidence={}, is_coding=False)
    assert res_nan["validated_score"] == 0.0
    assert any(t["rule"] == "non_finite_score" for t in res_nan["validation_trace"])

    res_inf = validator.validate(float("inf"), evidence={}, is_coding=False)
    assert res_inf["validated_score"] == 0.0
    assert any(t["rule"] == "non_finite_score" for t in res_inf["validation_trace"])


def test_validator_handles_malformed_and_none_evidence():
    """ScoreValidator does not crash when evidence is None, string, or non-dict."""
    validator = ScoreValidator()
    
    res_none = validator.validate(0.75, evidence=None, is_coding=False)
    assert res_none["validated_score"] == 0.75

    res_str_ev = validator.validate(0.75, evidence="malformed_string", is_coding=False)
    assert res_str_ev["validated_score"] == 0.75
    assert any(t["rule"] == "malformed_evidence" for t in res_str_ev["validation_trace"])


def test_validator_enforces_mandatory_cap_on_contradictory_evaluation():
    """When mandatory_pass is False, scores above 0.65 are capped at 0.65."""
    validator = ScoreValidator(mandatory_cap=0.65)
    
    # Contradictory output: raw score 0.95 despite failing mandatory concept
    res = validator.validate(0.95, evidence={"mandatory_pass": False}, is_coding=False)
    assert res["validated_score"] == 0.65
    assert any(t["rule"] == "mandatory_cap" for t in res["validation_trace"])

    # If raw score is already below cap, it is not modified
    res_low = validator.validate(0.50, evidence={"mandatory_pass": False}, is_coding=False)
    assert res_low["validated_score"] == 0.50
    assert not any(t["rule"] == "mandatory_cap" for t in res_low["validation_trace"])


def test_validator_applies_mistake_penalty():
    """Mistake penalties are subtracted up to max_mistake_penalty."""
    validator = ScoreValidator(max_mistake_penalty=0.25)
    
    res = validator.validate(0.80, evidence={"mistake_penalty": 0.15}, is_coding=False)
    assert res["validated_score"] == pytest.approx(0.65, abs=1e-4)

    # Penalty exceeding cap is bounded
    res_capped = validator.validate(0.80, evidence={"mistake_penalty": 0.50}, is_coding=False)
    assert res_capped["validated_score"] == pytest.approx(0.55, abs=1e-4)


def test_validator_penalizes_coding_failures():
    """Coding runtime errors, timeouts, or policy blocks scale down the score."""
    validator = ScoreValidator(coding_failure_multiplier=0.7)
    
    res_fail = validator.validate(0.80, evidence={"execution_status": "runtime_error"}, is_coding=True)
    assert res_fail["validated_score"] == pytest.approx(0.80 * 0.7, abs=1e-4)
    assert any(t["rule"] == "coding_execution_penalty" for t in res_fail["validation_trace"])

    # Passed execution receives no penalty
    res_pass = validator.validate(0.80, evidence={"execution_status": "accepted"}, is_coding=True)
    assert res_pass["validated_score"] == 0.80


def test_validator_distinguishes_infrastructure_failure_from_candidate_failure():
    """ScoreValidator explicitly flags infrastructure failure separately from candidate technical failure."""
    validator = ScoreValidator()

    # 1. Success case
    res_succ = validator.validate(0.85, evidence={"mandatory_pass": True}, is_coding=False)
    assert res_succ["evaluation_status"] == "success"
    assert res_succ["is_infrastructure_failure"] is False
    assert res_succ["validated_score"] == 0.85

    # 2. Candidate technical failure (answered poorly, low score)
    res_poor = validator.validate(0.15, evidence={"mandatory_pass": False}, is_coding=False)
    assert res_poor["evaluation_status"] == "success"
    assert res_poor["is_infrastructure_failure"] is False
    assert res_poor["validated_score"] == 0.15

    # 3. Evaluator unavailable (infrastructure failure)
    res_unavail = validator.validate(None, evidence={"evaluation_status": "unavailable"}, is_coding=False)
    assert res_unavail["evaluation_status"] == "unavailable"
    assert res_unavail["is_infrastructure_failure"] is True
    assert res_unavail["validated_score"] == 0.0

    # 4. Evaluator malformed response
    res_malformed = validator.validate(None, evidence={"evaluation_status": "malformed"}, is_coding=False)
    assert res_malformed["evaluation_status"] == "malformed"
    assert res_malformed["is_infrastructure_failure"] is True
    assert res_malformed["validated_score"] == 0.0
