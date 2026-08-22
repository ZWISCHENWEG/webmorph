# Data Contract v1: Can I Use — CSS position:sticky

## Contract Metadata
- **Contract Version:** 1
- **Target URL:** https://caniuse.com/css-sticky
- **Collector ID:** `c_mt45ptkn297h5onaf7`
- **Feature Scope:** Single Can I Use feature page (CSS position:sticky)
- **Approved:** STOP GATE C

---

## Required Top-Level Fields

| Field | Type | Required | Validation Rule |
|-------|------|----------|-----------------|
| `feature_name` | string | ✅ | Non-empty |
| `specification_url` | string | ✅ | Valid HTTP(S) URL after normalization |
| `specification_status` | string | ✅ | Non-empty |
| `global_usage_percentage` | string | ✅ | Parseable numeric percentage (e.g. `"96%"`) |
| `global_usage_support` | string | ✅ | Parseable numeric percentage (e.g. `"95.65%"`) |
| `global_usage_partial` | string | ✅ | Parseable numeric percentage (e.g. `"0.35%"`) |
| `description` | string | ✅ | Non-empty |
| `compatibility_notes` | string | ✅ | Non-empty |
| `browser_support` | array | ✅ | Non-empty array of browser records |

## Required Browser Record Fields

Each element in `browser_support` must contain:

| Field | Type | Required | Validation Rule |
|-------|------|----------|-----------------|
| `browser_name` | string | ✅ | Non-empty |
| `versions` | array | ✅ | Non-empty array of version records |

## Required Version Record Fields

Each element in `versions` must contain:

| Field | Type | Required | Validation Rule |
|-------|------|----------|-----------------|
| `version_range` | string | ✅ | Non-empty |
| `support_status` | string | ✅ | Non-empty |
| `status_class` | string | ✅ | One of: `y`, `a`, `n` |

### status_class Semantics (from Can I Use source)
- `y` = Supported
- `a` = Partial support
- `n` = Not supported / disabled by default

No additional source semantics are invented.

---

## Normalization Rules

The Bright Data CLI returns RAW JSON output. WEBMORPH MUST:

1. **Preserve the raw Bright Data payload** for provenance, auditability, and debugging. The raw payload is stored as-is before any transformation.
2. **Create a normalized representation** before canonical validation.

### URL Normalization
Bright Data may return URL fields as Markdown link representations:

```
[https://example.com](https://example.com)
```

The normalizer MUST extract the actual HTTP(S) URL:

```
https://example.com
```

This applies to any field expected to contain a URL (e.g., `specification_url`).

### Processing Pipeline

```text
RAW BRIGHT DATA OUTPUT
        ↓
    PRESERVATION (store raw payload)
        ↓
    NORMALIZATION (URL extraction, whitespace trimming)
        ↓
    CANONICAL SNAPSHOT
        ↓
    VALIDATION (against this Data Contract)
        ↓
    HEALTH CALCULATION (Technical-Spec formula)
        ↓
    VERIFIED / REJECTED
```

---

## Validation Rules (Deterministic)

The following rules are evaluated deterministically. No machine learning, no fuzzy matching, no AI-based inference.

1. **Required-field completeness:** All 9 top-level required fields must be present and non-null.
2. **Schema/type validity:** Each field must match its declared type (string, array).
3. **Non-empty `browser_support`:** The `browser_support` array must contain at least 1 browser record.
4. **Non-empty `versions`:** Each browser record must contain at least 1 version record.
5. **Required version fields:** Each version record must contain `version_range`, `support_status`, and `status_class`.
6. **Valid specification URL:** After normalization, `specification_url` must be a valid HTTP or HTTPS URL.
7. **Parseable percentages:** `global_usage_percentage`, `global_usage_support`, and `global_usage_partial` must be parseable as numeric percentages (strip `%`, parse as float).
8. **Valid `status_class`:** Each `status_class` must be one of: `y`, `a`, `n`.
9. **Non-empty `support_status`:** Each `support_status` string must be non-empty.
10. **Non-empty `browser_name`:** Each `browser_name` string must be non-empty.
11. **Non-empty `version_range`:** Each `version_range` string must be non-empty.

---

## Health Model

Uses the locked Technical-Spec deterministic health formula without modification:

- **Required Field Completeness:** 60% weight
- **Schema Validity:** 20% weight
- **Record Stability:** 20% weight

Thresholds (unchanged):
- `100 >= health >= 90`: HEALTHY
- `90 > health >= 80`: DEGRADED
- `health < 80`: DRIFT_DETECTED

Recovery governed by existing Technical-Spec recovery criteria (all conditions must pass).

---

## Initial Observed Baseline

Recorded from the first successful Bright Data collection on 2026-08-22.

| Metric | Observed Value |
|--------|---------------|
| `feature_name` | CSS position:sticky |
| `specification_url` | https://w3c.github.io/csswg-drafts/css-position/#sticky-pos |
| `specification_status` | - WD |
| `global_usage_percentage` | 96% |
| `global_usage_support` | 95.65% |
| `global_usage_partial` | 0.35% |
| Browser count in `browser_support` | 17 |
| Total version records across all browsers | ~50+ |
| All `status_class` values observed | `y`, `a`, `n` |

This baseline is evidence from the initial verified source state. It is NOT permanently hardcoded truth — future verified snapshots update the baseline pool (up to 5 most recent HEALTHY runs per Technical-Spec).

---

## Collector Metadata

- **Target URL:** https://caniuse.com/css-sticky
- **Collector ID:** `c_mt45ptkn297h5onaf7`
- **Source:** Bright Data Scraper Studio (custom collector)
- **Integration:** `bdata scraper run c_mt45ptkn297h5onaf7 https://caniuse.com/css-sticky`
