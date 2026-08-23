# WebMorph MVP Demo Flow

This document outlines the end-to-end journey for demonstrating WebMorph during the hackathon presentation. The demo flows from a stable state, through failure, AI-driven healing, human approval, and final verification.

## 1. Initial State: The Healthy Collector
**What to show:**
- The WebMorph Dashboard displaying the "Demo Ecommerce Price Monitor".
- The Collector state is `ACTIVE`.
- The Data Contract version is `v1`.
- The Health Score is currently high (e.g. `98.0`), showing successful historical scrapes.

**Narrative:**
"WebMorph is currently monitoring pricing data. It strictly enforces a predefined schema ensuring the 'price' field is a valid number. Everything is running smoothly."

## 2. The Incident: Schema Drift Detected
**What to show:**
- A simulated target website change occurs (price changes from `51.77` to `"$51.77"`).
- A collection job runs and the pipeline detects a schema validation failure.
- A new Incident is generated with `severity: HIGH`.
- The Incident dashboard shows: `Price schema drift detected (TYPE_MISMATCH)`.
- The Collector's health score plummets.

**Narrative:**
"The target e-commerce site suddenly updated their DOM, prepending a dollar sign to the price. Our strict schema validation instantly catches this mismatch, halting bad data from entering the database and creating a high-severity incident."

## 3. AI Diagnosis & Healing Proposal
**What to show:**
- The Incident transitions to `AWAITING_APPROVAL`.
- The AI Agent generates a `HealingEvent` containing:
  - **AI Diagnosis:** "The target website changed its price formatting from a raw number to a string prefixed with '$'."
  - **Root Cause:** DOM element parsing logic returned a string.
  - **Confidence Score:** 98.5%
  - **Proposed Fix (Code diff):**
    ```javascript
    - const price = $('#price').text();
    - return parseFloat(price);
    + const rawPrice = $('#price').text();
    + return parseFloat(rawPrice.replace('$', '').trim());
    ```

**Narrative:**
"Instead of waking up an engineer, WebMorph's AI immediately analyzes the DOM snapshot, identifies the exact string manipulation required, and proposes a precise code fix with 98.5% confidence."

## 4. Human-in-the-Loop Approval
**What to show:**
- The UI presents an "Approve" or "Reject" button on the Healing Proposal.
- Click **Approve** (this hits `POST /api/incidents/{id}/approve`).

**Narrative:**
"Because this is a critical data pipeline, we have a human-in-the-loop step. The operator reviews the AI's logic, sees it's safe and correct, and clicks Approve."

## 5. Verification & Recovery
**What to show:**
- The Incident briefly transitions to `HEALING`, then `VERIFYING`.
- WebMorph pushes the new parsing logic to the Bright Data collector.
- A verification run is triggered using the new code against the live site.
- The validation passes. The incident state becomes `RECOVERED`.

**Narrative:**
"WebMorph deploys the fix to Bright Data via CLI, runs a verification scrape, confirms the new data matches the contract, and successfully closes the incident."

## 6. Audit Timeline
**What to show:**
- The Incident details page showing the full timeline of events (from `audit_events`):
  1. `INCIDENT_DETECTED`
  2. `HEAL_PROPOSED`
  3. `HEALING_EVENT_STATE_CHANGED` -> `HEALING`
  4. `INCIDENT_STATE_CHANGED` -> `VERIFYING`
  5. `RUN_SUCCEEDED`
  6. `INCIDENT_STATE_CHANGED` -> `RECOVERED`

**Narrative:**
"Every state change and AI decision is fully audited, giving teams complete visibility and trust into how the system self-healed in production."
