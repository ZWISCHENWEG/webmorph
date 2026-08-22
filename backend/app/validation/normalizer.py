import re
from typing import Any


def normalize_url(val: str) -> str:
    if not isinstance(val, str):
        return val
    # Extract from markdown [URL](URL) if present
    match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", val)
    if match:
        return match.group(2).strip()
    return val.strip()


def normalize_record(record: dict) -> dict:
    normalized = dict(record)
    for key, value in normalized.items():
        if isinstance(value, str):
            if "url" in key.lower():
                normalized[key] = normalize_url(value)
            else:
                normalized[key] = value.strip()
    return normalized


def normalize_payload(raw_payload: Any) -> list[dict]:
    """
    Normalizes the raw Bright Data JSON payload.
    Expected to be a list of records.
    """
    if not isinstance(raw_payload, list):
        if isinstance(raw_payload, dict):
            raw_payload = [raw_payload]
        else:
            return []

    return [normalize_record(r) for r in raw_payload if isinstance(r, dict)]
