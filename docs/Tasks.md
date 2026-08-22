# Implementation Tasks: WEBMORPH

*Every phase must follow the Quality Gate: IMPLEMENT → TEST → VERIFY → REVIEW → FREEZE*

## Phase 1: Pre-requisites & Human Stop Gates
1. Review documentation.
> **STOP GATE A:** Documentation V4.1.2 approved. ✅
2. Select target website manually (Must be public, no login/paywall/personal/gov).
> **STOP GATE B:** Target website selected and manually verified. ✅ `https://caniuse.com/css-sticky`
3. Define the versioned Data Contract.
> **STOP GATE C:** Data Contract v1 approved. ✅ See `docs/DataContract-v1.md`
4. Create a real Bright Data Collector using Scraper Studio.
> **STOP GATE D:** Real Bright Data Collector created. ✅ `c_mt45ptkn297h5onaf7`
5. Verify the Collector returns valid JSON data matching the contract.
> **STOP GATE E:** Real structured output verified against the Data Contract. ✅ PASSED
6. Note the Collector ID (`c_mt45ptkn297h5onaf7`).
> **STOP GATE F:** Collector ID manually confirmed. ✅
> **STOP GATE G:** Human explicitly authorizes implementation. ❌ NOT AUTHORIZED

## Phase 2: Database & Backend Initialization
1. Initialize FastAPI project.
2. Configure SQLAlchemy 2.x and Alembic (PostgreSQL).
3. Create models: `DataContract`, `Collector`, `Run`, `Snapshot`, `Incident`, `HealingEvent`, `Job`, `AuditEvent`.
4. Generate and apply migrations. (Add indexes on ID, status).

## Phase 3: Domain Logic - Health & Validation
1. Implement Data Contract validation logic.
2. Implement exact Health Formula (Completeness, Schema Validity, Record Stability edge cases).
3. Implement `HEALTHY` (90-100), `DEGRADED` (80-89.99), and `DRIFT_DETECTED` (<80) evaluations and incident triggers.

## PHASE 4 — FROZEN
- implementation complete
- strict audit passed
- real Bright Data integration verified
- tests passing
- no Phase 5 implementation

## Phase 5: Incident Management & Diagnosis
1. Generate diagnostic report isolating failing fields.
2. Trigger incident flow only when `health < 80` (`DRIFT_DETECTED` -> `DIAGNOSING`). DEGRADED is a warning state that does not automatically create an incident.
3. Fire audit events.

## PHASE 6 — FROZEN
- implementation complete
- strict audit passed
- tests passing
- no Phase 7 implementation

## PHASE 7 — FROZEN
- implementation complete
- strict audit passed
- tests passing
- no Phase 8 implementation

## Phase 8: Healing Proposal Integration
1. Implement `requestHeal()` using `bdata scraper heal <collector_id> "<what broke>"`.
2. Connect `POST /api/incidents/{id}/heal` (Async 202).
3. Parse CLI response. Transition: `DIAGNOSING` -> `HEAL_PROPOSED` -> `AWAITING_APPROVAL`.

## Phase 9: Human Approval & Verification
1. Implement `approveHeal()` using `bdata scraper approve <collector_id>`. (NEVER auto-approve).
2. Implement `verifyCollector()` by running the scraper again.
3. Evaluate recovery criteria strictly (ALL conditions must pass).
4. Transition state: `HEALING` -> `VERIFYING` -> `RECOVERED` (or `VERIFICATION_FAILED`).

## Phase 10: Idempotency & Job System Enforcement
1. Enforce unique constraints on active Healing Events.
2. Handle Job retries (up to 3 attempts, exponential backoff) for network failures.
3. Block re-approving and re-verifying.

## Phase 11-16: UI Refinement
1. Build Incident View & Heal Proposal Review View.
2. Build Continuous Intelligence View (domain-specific derived metrics, consuming ONLY verified data).
3. Polish visual design (geometry, layering, halftone). Ensure no characters/fan art.

## Phase 17: Demo Mode
1. Implement `DEMO_MODE` flag to mutate collected output deterministically for drift detection testing by removing the `browser_support` key from the first record of a real Bright Data payload. The mutation occurs after successful real Bright Data collection and before normalization/validation. DEMO_MODE must never fake Bright Data success or snapshot IDs.
2. Ensure `DEMO_MODE` does NOT fake Bright Data successes or IDs.

## Phase 18: End-to-End Real Integration Testing
Verify real executions using the dual-mode demo strategy:

1. REAL Bright Data collector run.
2. MODE A: DEMO_MODE locally mutates the validated output.
3. REAL WEBMORPH validation detects the deterministic degradation.
4. REAL WEBMORPH generates the incident and diagnosis.
5. Separately prepare MODE B: a REAL Bright Data-visible extraction degradation on the selected target.
6. REAL Bright Data heal proposal using `bdata scraper heal`.
7. REAL human approval in the WEBMORPH UI.
8. REAL Bright Data approval using `bdata scraper approve`.
9. REAL Bright Data verification rerun.
10. REAL WEBMORPH recovery verification.
11. Confirm the SAME Collector ID remains unchanged.
12. Confirm downstream Continuous Intelligence consumes only the verified recovered snapshot.

> **CRITICAL RULE:** DEMO_MODE MUST NEVER be used as evidence that Bright Data itself is broken and MUST NEVER be used as the justification for calling `bdata scraper heal`.

## Phase 19: Deployment
1. Deploy Backend + PostgreSQL.
2. Deploy Frontend.
3. Record 2:30–3:00 Demo Video.
