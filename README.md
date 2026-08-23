# WEBMORPH

> The web changes. Your data shouldn't.

WEBMORPH is a reliability layer for web data, built for the **Into the Scrape-Verse 2026** hackathon by WeMakeDevs × Bright Data.

## Overview
Web data powers downstream intelligence, but DOM changes frequently cause extraction degradation. Traditional scrapers break silently, corrupting pipelines and losing critical intelligence.

WebMorph solves this by treating extracted web data as a **Versioned Data Contract**. It provides autonomous extraction monitoring that detects when a scraper's output structure drifts from expected shapes. By integrating with Bright Data Scraper Studio, WebMorph acts as a reliability layer that evaluates data health, creates incidents, requests AI-driven heal proposals, and orchestrates a human-in-the-loop approval workflow to recover broken scrapers autonomously.

## Features
- **Bright Data Integration**: First-class integration with Bright Data Scraper Studio.
- **Schema Validation**: Deterministic payload validation against a defined Data Contract.
- **Health Scoring**: Calculation of extraction health based on completeness, stability, and schema validity.
- **Drift Detection**: Automatic inference of structural drift when health scores degrade.
- **Incident Lifecycle**: Comprehensive state machine to manage incidents from creation to recovery.
- **AI Healing Proposal**: Request autonomous scraper fixes using Bright Data's AI capabilities.
- **Human Approval Workflow**: Mandated human-in-the-loop step to approve collector modifications securely.
- **Verification and Recovery**: Robust execution runs to verify the fix and formally recover the incident state.

## Architecture
WebMorph utilizes a robust, modern multi-tier architecture to orchestrate asynchronous scrape jobs and state transitions.

**Frontend:**
- Next.js (App Router)
- React
- TypeScript
- Tailwind CSS

**Backend:**
- FastAPI (Python)
- SQLAlchemy (Async)
- Pydantic
- Background Workers (Run, Approve, Verify)

**External:**
- Bright Data Scraper Studio

**Database:**
- PostgreSQL/SQLite schema supporting `Collector`, `Snapshot`, `Incident`, `HealingEvent`, `Job`, and `AuditEvent` entities.

### Data Flow
```text
Collection
↓
Normalization
↓
Validation
↓
Health Calculation
↓
Drift Detection
↓
Incident Creation
↓
Healing Proposal
↓
Human Approval
↓
Verification
↓
Recovery
```

## Local Development Setup

### Backend

1. **Install dependencies:**
   ```bash
   cd backend
   uv sync
   ```

2. **Environment setup:**
   Create a `.env` file in the `backend/` directory:
   ```env
   BRIGHT_DATA_API_TOKEN=your_token_here
   BRIGHT_DATA_COLLECTOR_ID=your_collector_id_here
   BRIGHT_DATA_TARGET_URL=your_target_url_here
   DEMO_MODE=false
   ```

3. **Database setup:**
   ```bash
   uv run alembic upgrade head
   ```

4. **Run backend:**
   ```bash
   uv run uvicorn app.main:app --reload
   ```

### Frontend

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Environment setup:**
   Create a `.env.local` file in the `frontend/` directory (if required).

3. **Run frontend:**
   ```bash
   npm run dev
   ```

## Environment Variables
The following environment variables are required in the backend `.env` file:
- `BRIGHT_DATA_API_TOKEN` - The Bright Data API authorization token.
- `BRIGHT_DATA_COLLECTOR_ID` - The target Scraper Studio Collector ID.
- `BRIGHT_DATA_TARGET_URL` - The URL targeted by the collector.
- `DEMO_MODE` - Set to `true` or `false` to enable local mutation of collected output for testing drift detection.

*(Important: Never commit real token values. Keep `.env` out of version control.)*

## Demo Flow
1. **Collector running normally**: The baseline collector successfully extracts data matching the Versioned Data Contract.
2. **Extraction degradation introduced**: The target website DOM changes (or Mode B intentional degradation), omitting required fields.
3. **Validation detects schema drift**: The validation engine evaluates the snapshot and identifies missing schema requirements, lowering the health score.
4. **Incident created**: An incident triggers and enters `DIAGNOSING`.
5. **Diagnosis generated**: A breakdown of the failure is created.
6. **Healing proposal created**: The system issues a `bdata scraper heal` request. Incident moves to `HEAL_PROPOSED` and awaits a fix.
7. **Human approval required**: An operator reviews the Bright Data fix in the WebMorph UI and approves it.
8. **Verification executed**: A background worker requests a fresh collection to verify the new collector template.
9. **Collector recovered**: The snapshot passes validation and the incident is marked `RECOVERED`.

## Deployment
*(Note: Not currently deployed. Documentation is for future reference only.)*

- **Backend hosting**: Dockerized FastAPI service deployed on a scalable compute platform (e.g., Render, Railway, AWS ECS).
- **Database requirement**: Managed PostgreSQL database instance.
- **Frontend hosting**: Vercel or Netlify for static site and serverless Next.js functions.
- **Environment variables**: Must be configured securely in the hosting provider's secrets management system.

## Screenshots

- **Dashboard Screenshot**
  *(TODO: Add UI screenshot here)*

- **Incident Workflow Screenshot**
  *(TODO: Add UI screenshot here)*

- **Healing Approval Screenshot**
  *(TODO: Add UI screenshot here)*

- **Recovery Screenshot**
  *(TODO: Add UI screenshot here)*

## Target Website
Status: SELECTED ✅
URL: https://caniuse.com/css-sticky
Collector ID: `c_mt45ptkn297h5onaf7`
Why selected: Public data, no login/paywall/personal/gov data, sufficient structural complexity.

## Hackathon Compliance
- [x] Public web data only
- [x] No login-protected data
- [x] No paywalled data
- [x] No personal/private data
- [x] No government websites
- [x] Custom Scraper Studio scraper
- [x] Real create/run flow
- [x] Self-healing demonstration
- [x] Public repository
- [x] README
- [x] Example structured output
- [x] Demo video (Pending)
- [x] Bright Data usage explanation
- [x] AI usage disclosure
