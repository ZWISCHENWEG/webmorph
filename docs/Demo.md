# Demo Storyboard: WEBMORPH

## Overview
- **Target Duration:** 2:30–3:00
- **Message:** The website changed. The data pipeline didn't.
- **Goal:** Highlight the reliability layer WEBMORPH provides over Bright Data's self-healing Scraper Studio.

## Demo Execution Strategy: Two Distinct Modes
The demo relies on separating WEBMORPH's detection capabilities from Bright Data's healing capabilities. **A locally mutated payload MUST NOT be used to justify calling Bright Data for a real heal.**

---

### MODE A — DETECTION PROOF
**Purpose:** Demonstrate WEBMORPH's deterministic validation and drift-detection capabilities using a real Bright Data result with a local DEMO_MODE mutation.

1. **REAL** Bright Data Collection.
2. **REAL** structured output.
3. *SIMULATED* deterministic local mutation (via `DEMO_MODE` mutating the output).
4. **REAL** WEBMORPH validation.
5. **REAL** WEBMORPH drift detection (`health < 80`).
6. **REAL** WEBMORPH incident + diagnosis.

---

### MODE B — SELF-HEALING PROOF
**Purpose:** Demonstrate the actual Bright Data Scraper Studio self-healing workflow using a real Bright Data-visible degradation.

1. **REAL** Bright Data Collector.
2. **ACTUAL** extraction degradation visible to Bright Data (Target website structure changes).
3. **REAL** WEBMORPH diagnosis.
4. Call `bdata scraper heal`.
5. **REAL** Bright Data heal proposal.
6. **REAL** human approval in the UI.
7. Call `bdata scraper approve`.
8. **REAL** Bright Data rerun.
9. **REAL** WEBMORPH verification.
10. **REAL** recovery showing the same Collector ID (`c_xxxxx`).
11. **REAL** trusted downstream intelligence.

> **OPEN HUMAN DECISION:**
> Choose and prepare a reproducible real degradation scenario that is visible to Bright Data Scraper Studio while remaining compliant with the hackathon rules. Do not invent this scenario in code.

---

## Timeline Breakdown

### 0:00–0:20: Problem
- **Visuals:** A common web target changing its DOM structure.
- **Narration:** "When the DOM changes, traditional scrapers break. Data pipelines fail silently."

### 0:20–0:40: Healthy collector + real data
- **Visuals:** WEBMORPH dashboard showing a Collector (`c_xxxxxxxxx`) scoring `100 >= health >= 90`.
- **Action:** Execute collector asynchronously.
- **Narration:** "A healthy Collector extracts data matching our strict Versioned Data Contract."

### 0:40–1:05: MODE A - Deterministic degradation
- **Visuals:** Simulated failure (via DEMO_MODE mutating the valid output).
- **Action:** Collector runs. Health drops below 80.
- **Narration:** "If the layout changes and extraction degrades, WEBMORPH detects inferred structural drift and isolates the failing fields."

### *--- [CLEAR DEMO TRANSITION] ---*
- **Narration:** "Now, let's see how WEBMORPH handles a *real* Scraper Studio extraction failure."

### 1:05–1:25: MODE B - Real Incident + Diagnosis
- **Visuals:** A REAL degradation scenario triggers a real incident (`DRIFT_DETECTED` -> `DIAGNOSING`).
- **Action:** View the generated incident detailing what actually broke on Bright Data's side.

### 1:25–1:45: Real Bright Data heal proposal
- **Visuals:** UI shows `HEAL_PROPOSED`.
- **Action:** The UI displays the proposed repair returned from the real Bright Data CLI.
- **Narration:** "WEBMORPH fetches a heal proposal directly from Scraper Studio."

### 1:45–2:00: Human approval
- **Visuals:** State moves to `AWAITING_APPROVAL`.
- **Action:** User clicks "Approve".
- **Narration:** "WEBMORPH enforces human-in-the-loop safety. We explicitly approve the fix."

### 2:00–2:20: Healing + verification
- **Visuals:** State moves to `HEALING` then `VERIFYING`. A new Snapshot (`j_xxxxxxxxx`) is executed.
- **Result:** Validation passes ALL strict recovery criteria. Status turns to `RECOVERED`.
- **Narration:** "Bright Data applies the heal. WEBMORPH rigorously verifies the output against the contract."

### 2:20–2:35: Same Collector ID
- **Visuals:** Zoom in on the Collector ID.
- **Narration:** "Crucially, the Collector ID remains exactly the same. Zero code changes required."

### 2:35–2:50: Continuous Intelligence
- **Visuals:** Switch to Continuous Intelligence view (domain-specific derived metrics).
- **Narration:** "Because WEBMORPH protects the pipeline, downstream intelligence only consumes verified data."

### 2:50–3:00: Final Statement
- **Narration:** "The website changed. The data pipeline didn't."
