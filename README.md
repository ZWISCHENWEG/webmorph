# WEBMORPH

> The web changes. Your data shouldn't.

WEBMORPH is a reliability layer for web data, built for the **Into the Scrape-Verse 2026** hackathon by WeMakeDevs × Bright Data.

## Problem
Data engineers and analysts rely on web data for downstream intelligence. However, DOM changes cause extraction degradation. Traditional scrapers break silently, corrupting pipelines and losing critical intelligence.

## Solution
WEBMORPH treats extracted web data as a **Versioned Data Contract**. It manages Bright Data Collector executions, detects extraction degradation, requests heal proposals, requires human-in-the-loop approval, and strictly verifies recovery—ensuring the data pipeline survives structural drift without requiring a new Collector ID. Downstream Continuous Intelligence only consumes verified snapshots.

## Architecture
- **Frontend:** Next.js (React)
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL (SQLAlchemy 2.x + Alembic)
- **Execution Engine:** Internal asynchronous job queue executing secure subprocesses (triggered by API/UI, no autonomous schedulers)
- **Extraction & Healing:** Bright Data Scraper Studio (via official CLI `bdata scraper`)

## Core Workflow
1. **Data Contract:** Define expected schema.
2. **Collection:** Execute asynchronously via Bright Data CLI (triggered by operator).
3. **Validation:** Check Snapshot payload against the contract deterministically.
4. **Drift Detection:** Identify inferred structural drift upon degradation (`Health < 80`).
5. **Diagnosis:** Generate an incident report.
6. **Heal Proposal:** Request a fix from Bright Data.
7. **Approval:** Human-in-the-loop review.
8. **Heal:** Bright Data applies the fix.
9. **Verification:** Rerun and check all recovery criteria (ALL conditions must pass).
10. **Continuous Intelligence:** Domain-specific derived metrics flow reliably, operating continuously over the historical stream of ONLY verified snapshots.

## Screenshots
*(TODO: Add UI screenshots here)*

## Target Website
Status: SELECTED ✅
URL: https://caniuse.com/css-sticky
Collector ID: `c_mt45ptkn297h5onaf7`
Why selected: Public data, no login/paywall/personal/gov data, sufficient structural complexity (nested browser/version arrays), well-known developer resource.

## Hackathon Compliance
- [ ] Public web data only
- [ ] No login-protected data
- [ ] No paywalled data
- [ ] No personal/private data
- [ ] No government websites
- [ ] Custom Scraper Studio scraper
- [ ] Real create/run flow
- [ ] Self-healing demonstration
- [ ] Public repository
- [ ] README
- [ ] Example structured output
- [ ] Demo video
- [ ] Bright Data usage explanation
- [ ] AI usage disclosure

## Setup & Deployment
*(TODO: Add environment variables, testing, and deployment instructions)*

---

### Documentation Status:
**WEBMORPH DOCUMENTATION V4.1.2**
**FINAL / IMPLEMENTATION-READY**

**DOCUMENTATION COMPLETE.**

**IMPLEMENTATION IS BLOCKED UNTIL STOP GATE G IS AUTHORIZED.**

- **STOP GATE B** — ✅ Target website selected and manually verified.
- **STOP GATE C** — ✅ Versioned Data Contract v1 approved.
- **STOP GATE D** — ✅ Real Bright Data Collector created (`c_mt45ptkn297h5onaf7`).
- **STOP GATE E** — ✅ Real structured output validated against Data Contract v1.
- **STOP GATE F** — ✅ Collector ID manually confirmed.
- **STOP GATE G** — ❌ Human has NOT authorized implementation.
