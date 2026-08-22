def calculate_completeness(records: list[dict]) -> float:
    required_fields = [
        "feature_name",
        "specification_url",
        "specification_status",
        "global_usage_percentage",
        "global_usage_support",
        "global_usage_partial",
        "description",
        "compatibility_notes",
        "browser_support",
    ]

    total_records = len(records)
    if total_records == 0:
        return 0.0

    field_completeness_list = []

    for field in required_fields:
        successful = sum(
            1 for r in records if r.get(field) is not None and str(r.get(field)).strip() != ""
        )
        field_completeness = (successful / max(1, total_records)) * 100.0
        field_completeness_list.append(field_completeness)

    if not field_completeness_list:
        return 0.0

    return sum(field_completeness_list) / len(field_completeness_list)


def calculate_schema_validity(valid_records: int, total_records: int) -> float:
    if total_records == 0:
        return 0.0
    return (valid_records / max(1, total_records)) * 100.0


def calculate_record_stability(current_count: int, healthy_baseline_counts: list[int]) -> float:
    N = current_count

    if not healthy_baseline_counts:
        # A. First run with records
        if N > 0:
            return 100.0
        # B. First run with zero records
        return 0.0

    baselines = healthy_baseline_counts[-5:]
    mean_count = sum(baselines) / len(baselines)

    if mean_count == 0 and N == 0:
        # C
        return 100.0
    elif mean_count == 0 and N > 0:
        # D
        deviation = (N - 0) / N
    else:
        # E
        deviation = abs(N - mean_count) / mean_count

    stability = max(0.0, 100.0 - (deviation * 100.0))
    return stability


def calculate_health_score(completeness: float, schema_validity: float, stability: float) -> float:
    return (completeness * 0.60) + (schema_validity * 0.20) + (stability * 0.20)
