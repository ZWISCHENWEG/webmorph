# Product Requirements Document (PRD): WEBMORPH

## 1. Product Summary
WEBMORPH is a reliability layer for web data.
Tagline: The web changes. Your data shouldn't.

## 2. Problem
Data engineers and analysts rely on web data for downstream intelligence. However, DOM changes cause extraction degradation. Traditional scrapers break silently, corrupting pipelines and losing critical intelligence.

## 3. Product Vision & Identity
WEBMORPH provides an infrastructure layer designed to protect the integrity of web data extraction over time through deterministic validation, drift detection, and strict recovery verification gates.
WEBMORPH is **NOT** a generic scraper, a scraping dashboard, a custom AI agent, or a generic data platform. Bright Data Scraper Studio handles actual extraction and self-healing.
WEBMORPH handles: Versioned Data Contracts, validation, drift inference, diagnosis, human approval, healing orchestration, and trusted downstream intelligence.

## 4. Core Product Workflow
```text
DATA CONTRACT
      ↓
COLLECTION
      ↓
VALIDATION
      ↓
DRIFT DETECTION
      ↓
DIAGNOSIS
      ↓
HEAL PROPOSAL
      ↓
APPROVAL
      ↓
HEAL
      ↓
VERIFICATION
      ↓
RECOVERY
      ↓
CONTINUOUS INTELLIGENCE
```

## 5. Core Features
- Data Contract Management (Versioned schemas).
- Collector Management (Collector IDs `c_xxxxx`).
- Asynchronous Execution & Snapshot Management (Snapshot IDs `j_xxxxx`).
- Validation & Deterministic Health Calculation (`100 >= Health >= 90` is HEALTHY, `90 > Health >= 80` is DEGRADED, `< 80` is DRIFT_DETECTED).
- Extraction Degradation / Inferred Structural Drift Detection.
- Incident Management & Diagnosis.
- Heal Proposal & Human-in-the-Loop Approval.
- Recovery Verification (Strict "all-conditions-must-pass" gate).
- Continuous Intelligence (Domain-specific derived metrics, powered ONLY by verified data).

## 6. MVP Scope
Validating a single Bright Data Collector, detecting drift, requesting a heal proposal via Bright Data CLI, routing human approval, and demonstrating recovery through continuous intelligence.

## 7. Functional Requirements
### MUST
- Register and store a Bright Data Collector ID (`c_xxxxx`).
- Register versioned Data Contracts.
- Execute asynchronously via Bright Data CLI and retrieve Snapshot IDs (`j_xxxxx`).
- Evaluate completeness, schema validity, and stability deterministically.
- Require explicit human approval for proposed heals.
- Rerun and strictly verify recovery before incident resolution.
- Maintain a comprehensive audit trail of state transitions.

### OUT OF SCOPE
- User authentication and multi-tenancy.
- Complex anomaly detection models (machine learning).
- Replacing Bright Data's extraction/healing engine.

## 8. Human-in-the-Loop Safety
Default model: Drift Detected -> Diagnosis -> Heal Proposed -> User Approves -> Heal Applied.
Healing MUST NEVER be applied automatically in production. The UI must explain the diagnosis and proposed repair before approval.

## 9. Constraints
- Must comply with all "Into the Scrape-Verse" hackathon rules.
- Must use publicly available web data (no logins, paywalls, personal data, or government sites).

## 10. MVP Execution Model & Continuous Intelligence
- **MVP Collection Model:** Collection and verification are asynchronous job operations triggered by the operator/UI/API. The MVP does not require autonomous scheduled scraping (no Redis, Celery, or cron infrastructure).
- **Continuous Intelligence:** The intelligence layer continuously operates over the historical stream of VERIFIED snapshots. Unverified or degraded snapshots are never trusted by downstream intelligence.
- **Future Extensibility:** Scheduled/recurring collection may be added later without changing the core validation, drift detection, healing, or verification architecture.
