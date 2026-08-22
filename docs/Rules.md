# Core Rules & Principles: WEBMORPH

## 1. Zero Implementation Phase
No implementation occurs until Documentation V4.1.2 is completed, reviewed, and STOP GATES are cleared.

## 2. Infrastructure Focus
WEBMORPH is a reliability infrastructure layer. It is not an AI agent, a generic dashboard, or a data platform.

## 3. Human-in-the-Loop Healing
Healing MUST NEVER be applied automatically in production.
The flow must strictly be: Drift Detected -> Diagnosis -> Heal Proposed -> Human Approval -> Heal Executed -> Verified.

## 4. Single Source of Truth & Identity
- **Collector ID (`c_xxxxx`):** The Bright Data template definition.
- **Snapshot ID (`j_xxxxx`):** The Bright Data execution result.
- **Run ID:** The internal WEBMORPH execution attempt.
- Never conflate them.

## 5. Strict Recovery & Health Thresholds
- `100 >= health >= 90`: **HEALTHY**
- `90 > health >= 80`: **DEGRADED**
- `80 > health`: **DRIFT_DETECTED** (Incident generated)
An incident is resolved ONLY if it passes the strict verification logic (Health >= 95, all required fields >= recovery threshold, schema valid, count stable).

## 6. Official Integrations & Subprocess Security
The Bright Data CLI (`bdata scraper`) is the canonical integration. `BrightDataResultNormalizer` ensures the domain does not tightly couple to raw JSON envelopes. All subprocess calls must be strictly parameterized (`shell=False`) and secure.

## 7. Demo Integrity (No Fake Healing)
There are two demonstration modes:
- **Mode A:** `DEMO_MODE` injects deterministic local mutation into validated output to test WEBMORPH drift detection.
- **Mode B:** Real Scraper Studio degradation must be triggered on a live target before invoking a real `bdata scraper heal`.
**Never claim a locally mutated payload creates a Bright Data-side failure that can be healed.**

## 8. Continuous Intelligence Trust
Downstream intelligence (domain-specific derived metrics) must ONLY consume validated, verified snapshots. Unverified degraded snapshots must be blocked from downstream usage.
