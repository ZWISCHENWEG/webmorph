from typing import Any

from pydantic import ValidationError

from app.models.snapshot import ValidationState
from app.validation.health import (
    calculate_completeness,
    calculate_health_score,
    calculate_record_stability,
    calculate_schema_validity,
)
from app.validation.normalizer import normalize_payload
from app.validation.schema import CanIUseFeature


class ValidationResult:
    def __init__(
        self,
        is_valid: bool,
        normalized_payload: list[dict],
        validation_state: ValidationState,
        health_score: float,
        completeness_score: float,
        schema_validity_score: float,
        stability_score: float,
        errors: list[str],
    ):
        self.is_valid = is_valid
        self.normalized_payload = normalized_payload
        self.validation_state = validation_state
        self.health_score = health_score
        self.completeness_score = completeness_score
        self.schema_validity_score = schema_validity_score
        self.stability_score = stability_score
        self.errors = errors


def process_payload(raw_payload: Any, healthy_baseline_counts: list[int]) -> ValidationResult:
    """
    Processes the raw payload deterministically:
    1. Normalizes
    2. Validates against DataContract v1
    3. Calculates Health
    """
    normalized_records = normalize_payload(raw_payload)
    total_records = len(normalized_records)

    valid_records = 0
    errors = []

    for i, record in enumerate(normalized_records):
        try:
            CanIUseFeature.model_validate(record)
            valid_records += 1
        except ValidationError as e:
            errors.append(f"Record {i} validation failed: {str(e)}")

    is_valid = (valid_records == total_records) and (total_records > 0)

    # Calculate components
    completeness = calculate_completeness(normalized_records)
    schema_validity = calculate_schema_validity(valid_records, total_records)
    stability = calculate_record_stability(total_records, healthy_baseline_counts)

    health_score = calculate_health_score(completeness, schema_validity, stability)

    # State mapping based on Technical-Spec.md
    if health_score >= 90:
        state = ValidationState.HEALTHY
    elif health_score >= 80:
        state = ValidationState.DEGRADED
    else:
        state = ValidationState.DRIFT_DETECTED

    return ValidationResult(
        is_valid=is_valid,
        normalized_payload=normalized_records,
        validation_state=state,
        health_score=health_score,
        completeness_score=completeness,
        schema_validity_score=schema_validity,
        stability_score=stability,
        errors=errors,
    )
