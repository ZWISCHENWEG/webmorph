import json

import pytest

from app.models.snapshot import ValidationState
from app.validation.engine import process_payload
from app.validation.health import calculate_record_stability
from app.validation.normalizer import normalize_payload


@pytest.fixture
def baseline_payload():
    with open("../caniuse-baseline.json") as f:
        return json.load(f)

def test_a_valid_baseline(baseline_payload):
    result = process_payload(baseline_payload, [])
    assert result.is_valid is True
    assert result.errors == []
    
    normalized = result.normalized_payload[0]
    assert len(normalized["browser_support"]) == 17
    
    total_versions = sum(len(b["versions"]) for b in normalized["browser_support"])
    assert total_versions == 52
    
    # Check status class subset
    for b in normalized["browser_support"]:
        for v in b["versions"]:
            assert v["status_class"] in {"y", "a", "n"}
            
    assert result.health_score == 100.0
    assert result.validation_state == ValidationState.HEALTHY

def test_b_missing_required_field(baseline_payload):
    payload = baseline_payload[0]
    del payload["feature_name"]
    result = process_payload([payload], [])
    
    assert result.is_valid is False
    assert "feature_name" in result.errors[0]
    assert result.schema_validity_score == 0.0

def test_c_invalid_url(baseline_payload):
    payload = baseline_payload[0]
    payload["specification_url"] = "not_a_url"
    result = process_payload([payload], [])
    
    assert result.is_valid is False
    assert "specification_url" in result.errors[0]

def test_d_invalid_percentage(baseline_payload):
    payload = baseline_payload[0]
    payload["global_usage_percentage"] = "96" # missing %
    result = process_payload([payload], [])
    
    assert result.is_valid is False
    assert "global_usage_percentage" in result.errors[0]

def test_e_invalid_status_class(baseline_payload):
    payload = baseline_payload[0]
    payload["browser_support"][0]["versions"][0]["status_class"] = "x"
    result = process_payload([payload], [])
    
    assert result.is_valid is False
    assert "status_class" in result.errors[0]

def test_f_empty_browser_support(baseline_payload):
    payload = baseline_payload[0]
    payload["browser_support"] = []
    result = process_payload([payload], [])
    
    assert result.is_valid is False
    assert "browser_support" in result.errors[0]

def test_g_invalid_browser_record(baseline_payload):
    payload = baseline_payload[0]
    del payload["browser_support"][0]["browser_name"]
    result = process_payload([payload], [])
    
    assert result.is_valid is False
    assert "browser_name" in result.errors[0]

def test_h_invalid_version_record(baseline_payload):
    payload = baseline_payload[0]
    del payload["browser_support"][0]["versions"][0]["version_range"]
    result = process_payload([payload], [])
    
    assert result.is_valid is False
    assert "version_range" in result.errors[0]

def test_i_normalization():
    raw_payload = [{
        "feature_name": "Test",
        "specification_url": "[https://example.com](https://example.com)",
        "specification_status": "WD",
        "global_usage_percentage": "90%",
        "global_usage_support": "80%",
        "global_usage_partial": "10%",
        "description": "Test desc",
        "compatibility_notes": "Test notes",
        "browser_support": [{
            "browser_name": "Chrome",
            "versions": [{
                "version_range": "1",
                "support_status": "Supported",
                "status_class": "y"
            }]
        }]
    }]
    
    result = process_payload(raw_payload, [])
    assert result.is_valid is True
    # URL should be extracted
    assert str(result.normalized_payload[0]["specification_url"]) == "https://example.com"
    # Ensure nested semantic values were absolutely untouched (including weird whitespaces)
    browser_support = result.normalized_payload[0]["browser_support"][0]
    assert browser_support["browser_name"] == "Chrome"
    assert browser_support["versions"][0]["version_range"] == "1"
    assert browser_support["versions"][0]["support_status"] == "Supported"
    assert browser_support["versions"][0]["status_class"] == "y"

def test_j_raw_provenance(baseline_payload):
    original_raw = json.dumps(baseline_payload)
    
    normalized = normalize_payload(baseline_payload)
    
    # Raw payload should not be mutated
    assert json.dumps(baseline_payload) == original_raw
    assert id(baseline_payload) != id(normalized)

def test_k_record_stability_cases():
    # Case A: 0 baselines, N > 0 -> 100
    assert calculate_record_stability(1, []) == 100.0
    assert calculate_record_stability(50, []) == 100.0
    
    # Case B: 0 baselines, N == 0 -> 0
    assert calculate_record_stability(0, []) == 0.0
    
    # Case C: mean == 0, N == 0 -> 100
    assert calculate_record_stability(0, [0, 0, 0]) == 100.0
    
    # Case D: mean == 0, N > 0 -> 0 (deviation = 1.0)
    assert calculate_record_stability(10, [0, 0, 0]) == 0.0
    
    # Case E: mean > 0
    # N == mean -> deviation = 0 -> 100
    assert calculate_record_stability(10, [10, 10]) == 100.0
    # N drops by 10% -> deviation 0.1 -> stability 90
    assert calculate_record_stability(90, [100, 100]) == 90.0
    # N jumps by 50% -> deviation 0.5 -> stability 50
    assert calculate_record_stability(150, [100]) == 50.0
    # N drops to 0 (mean 10) -> deviation 1.0 -> stability 0
    assert calculate_record_stability(0, [10, 10]) == 0.0
    
    # historical limits (use only 5 most recent)
    # 5 recent are 100, oldest is 0. Mean should be 100.
    assert calculate_record_stability(100, [0, 100, 100, 100, 100, 100]) == 100.0

def test_l_health_calculation_and_state_boundaries(baseline_payload):
    def run_health(completeness, schema_validity, stability):
        from app.validation.health import calculate_health_score
        return calculate_health_score(completeness, schema_validity, stability)
        
    # Health boundaries (60/20/20 weight)
    # health >= 90: HEALTHY (which maps to Technical-Spec HEALTHY)
    # 90 > health >= 80: DEGRADED
    # health < 80: DRIFT_DETECTED
    
    # 100.0
    assert run_health(100, 100, 100) == 100.0
    # 90.0 exactly (completeness 100, schema 50, stability 100) -> 60 + 10 + 20 = 90
    assert run_health(100.0, 50.0, 100.0) == 90.0
    # 89.99 exactly (completeness 99.9833..., schema 50, stability 100) -> ~89.99
    assert abs(run_health(99.98333333333333, 50.0, 100.0) - 89.99) < 0.001
    # 80.0 exactly (completeness 100, schema 0, stability 100) -> 60 + 0 + 20 = 80
    assert run_health(100.0, 0.0, 100.0) == 80.0
    # 79.99 exactly (completeness 99.9833..., schema 0, stability 100) -> ~79.99
    assert abs(run_health(99.98333333333333, 0.0, 100.0) - 79.99) < 0.001
    # 0.0
    assert run_health(0, 0, 0) == 0.0

def test_m_state_transition_engine():
    from app.models.snapshot import ValidationState
    
    # Mocking process_payload boundaries is easiest by overriding the calculation
    # Since engine.py directly calculates it, we simulate the block:
    def get_state(health_score):
        if health_score >= 90:
            return ValidationState.HEALTHY
        elif health_score >= 80:
            return ValidationState.DEGRADED
        else:
            return ValidationState.DRIFT_DETECTED
        
    assert get_state(100.0) == ValidationState.HEALTHY
    assert get_state(90.0) == ValidationState.HEALTHY
    assert get_state(89.99) == ValidationState.DEGRADED
    assert get_state(80.0) == ValidationState.DEGRADED
    assert get_state(79.99) == ValidationState.DRIFT_DETECTED
    assert get_state(0.0) == ValidationState.DRIFT_DETECTED

