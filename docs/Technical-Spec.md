# Technical Specification

## Core Terminology
- **Collector ID (`c_xxxxx`):** Persistent Bright Data scraper definition.
- **Snapshot ID / Collection ID (`j_xxxxx`):** One execution/result snapshot from Bright Data.
- **WEBMORPH Run ID:** Internal database identifier linking a Collector to a Snapshot.
*These must never be conflated. A single Collector has many Runs. Each successful Run corresponds to one Snapshot ID.*

## Constants & Thresholds
```python
DEGRADED_THRESHOLD = 90
DRIFT_THRESHOLD = 80
RECOVERY_THRESHOLD = 95
REQUIRED_FIELD_RECOVERY_THRESHOLD = 95
```
**Threshold Semantics:**
- `100 >= health >= 90`: **HEALTHY**
- `90 > health >= 80`: **DEGRADED**
- `80 > health`: **DRIFT_DETECTED** (Incident generated)
*If a Collector is DEGRADED and a subsequent run scores >= 90, its state automatically returns to HEALTHY. A degraded run does NOT automatically create an incident.*

## Health Calculation (Deterministic Formula)
All metrics are normalized to a 0–100 scale, rounded to two decimal places. Division by zero yields 0 unless explicitly handled.

1. **Required Field Completeness (60% weight):**
   - For each required field: `field_completeness = (successful_non_null_values / max(1, total_records)) * 100`
   - `completeness = average of all required field_completeness values`
2. **Schema Validity (20% weight):**
   - `schema_validity = (valid_records / max(1, total_records)) * 100`
3. **Record Stability (20% weight):**
   Let `N` = current record count. Let `baselines` = up to 5 most recent `HEALTHY` runs.
   - **A. First run with records (`0 baselines, N > 0`):** `stability = 100` (Cold-start positive)
   - **B. First run with zero records (`0 baselines, N == 0`):** `stability = 0` (Zero records is a failure, not stable)
   - If 1–5 healthy baselines exist, use all available healthy baselines.
   - If more than 5 healthy baselines exist, use the 5 most recent healthy baselines.
      - Let `mean_count = sum(baseline counts) / len(baselines)`.
      - **C. Mean is zero, current is zero (`mean_count == 0, N == 0`):** `stability = 100`
      - **D. Mean is zero, current is not (`mean_count == 0, N > 0`):** `deviation = (N - 0) / N = 1.0`
      - **E. Mean is not zero:** `deviation = abs(N - mean_count) / mean_count`
      - `stability = max(0, 100 - (deviation * 100))`
4. **Overall Health:**
   `health_score = (completeness * 0.60) + (schema_validity * 0.20) + (stability * 0.20)`

### Worked Examples
- **First Zero-Record Run:** N=0, baselines=0 -> Completeness=0, Schema=0, Stability=0 -> Health=0 (DRIFT_DETECTED).
- **Record-count Collapse:** N=10, mean=100. deviation=0.9. Stability=10. Completeness=100. Schema=100. -> Health=82 (DEGRADED).

## Recovery Criteria
An incident can ONLY become `RECOVERED` if ALL conditions are true:
1. `health_score >= RECOVERY_THRESHOLD (95)`
2. `field_completeness >= REQUIRED_FIELD_RECOVERY_THRESHOLD (95)` for ALL required fields.
3. `schema_validity == 100`
4. Record stability is >= 90.
5. No critical validation errors exist.
6. Bright Data run completed successfully.
*(Never resolve an incident solely because health_score >= 95).*

## Healing State Machine
```text
HEALTHY
   ↓ (80 <= health < 90)
DEGRADED
   ├── health >= 90 → HEALTHY
   │
   └── health < 80 → DRIFT_DETECTED
                      ↓
                  DIAGNOSING
                      ↓
                  HEAL_PROPOSED
                      ↓
                  AWAITING_APPROVAL
                     ├── REJECTED (Terminal)
                     │
                     └── APPROVED
                            ↓
                         HEALING
                            ↓
                         VERIFYING
                            ├── RECOVERED (Terminal)
                            │
                            └── VERIFICATION_FAILED
                                      ↓
                                  HEAL_FAILED
                                      ↓
                               MANUAL_INTERVENTION (Terminal)
```
**Constraints & Guards:** Cannot approve without `AWAITING_APPROVAL`. All transitions generate an `AuditEvent`. Only health < 80 creates DRIFT_DETECTED and starts the incident flow.

## Bright Data Result Normalization
The CLI raw JSON output is parsed by a `BrightDataResultNormalizer` to extract identifiers (`j_xxxx`), payload data, status codes, and error messages into WEBMORPH's internal schema. Do not hardcode dependencies on raw CLI envelope specifics.

## CLI Execution Security
`subprocess.run(argv, shell=False, capture_output=True, timeout=TIMEOUT)`
Validate `collector_id`. Bound captured output size (e.g. 5MB max). Redact secrets.

## Job Lifecycle
`QUEUED` -> `RUNNING` -> `SUCCEEDED` | `FAILED` | `TIMED_OUT` | `CANCELLED`
Jobs have retryable mechanisms with exponential backoff for network errors (max 3 attempts).

## Data Model (SQLAlchemy 2.x)
- **DataContract:** `version`, `collector_id`, `schema_json`
- **Collector:** `id`, `bright_data_collector_id` (`c_xxxxx`), `current_contract_version`. Indexes: `bright_data_collector_id`.
- **Run:** `id`, `collector_id`, `contract_version`, `status`.
- **Snapshot:** `id`, `bright_data_snapshot_id` (`j_xxxxx`), `collector_id`, `run_id`, `contract_version`, `normalized_payload_ref`, `record_count`, `validation_state`, `health_score`, `created_at`.
- **Incident:** `id`, `collector_id`, `trigger_run_id`, `status`.
- **HealingEvent:** `id`, `incident_id`, `status`, `approval_status`, `proposal`. Unique active constraint per Incident.
- **Job:** `id`, `operation_type`, `status`, `attempt_count`, `related_entity_ref`, `created_at`, `updated_at`.
- **AuditEvent:** `id`, `event_type`, `related_entity_ref`, `actor_source`, `metadata_json`, `created_at`.

## API Contract (FastAPI)
All long-running operations return `202 Accepted` with a `job_id`.
```json
{ "job_id": "job_xxx", "status": "QUEUED" }
```
**Error Envelope:**
```json
{
  "error": { "code": "ERR_CLI_TIMEOUT", "message": "Execution timed out.", "retryable": true }
}
```

## Idempotency
- **Collection:** Same Snapshot ID must not duplicate Run or Snapshot records. The Bright Data snapshot identifier `bright_data_snapshot_id` (`j_xxxxx`) must have a unique constraint/index in the Snapshot table to prevent the same result from being persisted multiple times.
- **Healing:** Unique constraint on `HealingEvent(incident_id)` where status is active.
- **Approval:** `APPROVED` or `REJECTED` cannot accept another approval request.
