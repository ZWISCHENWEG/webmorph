# Architecture: WEBMORPH

## System Architecture

```text
                    ┌──────────────────────┐
                    │      Next.js UI      │
                    └──────────┬───────────┘
                               │ REST
                               ▼
                    ┌──────────────────────┐
                    │     FastAPI API      │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │    WEBMORPH Engine   │
                    │                      │
                    │ Validation           │
                    │ Drift Detection      │
                    │ Incident Manager     │
                    │ Healing Orchestrator │
                    │ Job Runner           │
                    └───────┬───────┬──────┘
                            │       │ Subprocess (Safe)
                 ┌──────────▼──┐ ┌─▼──────────────┐
                 │ PostgreSQL  │ │ Bright Data CLI│
                 │ Persistence │ │ (bdata scraper)│
                 └─────────────┘ └───────┬────────┘
                                         │ Raw JSON
                               ┌─────────▼──────────────┐
                               │ BrightDataResult       │
                               │ Normalizer             │
                               └─────────┬──────────────┘
                                         │ Normalized
                                   ┌─────▼──────────┐
                                   │ Bright Data    │
                                   │ Scraper Studio │
                                   └────────────────┘
```

## Architecture Principles
A robust, asynchronous job-oriented model. FastAPI exposes the API. The WEBMORPH Engine contains the core domain logic. PostgreSQL persists all state. Bright Data Scraper Studio handles actual extraction and self-healing. Next.js never communicates directly with Bright Data; all secrets and orchestration remain server-side.

## Bright Data Integration Strategy
The official Bright Data CLI is the canonical integration mechanism for the hackathon MVP. WEBMORPH orchestrates the CLI to interact with Bright Data. The `BrightDataService` manages these interactions safely:
- `runCollector()`: Executes `bdata scraper run <collector_id> <url>`
- `requestHeal()`: Executes `bdata scraper heal <collector_id> "<what broke>"`
- `approveHeal()`: Executes `bdata scraper approve <collector_id>`
- `verifyCollector()`: Reruns `bdata scraper run <collector_id> <url>`

*Note: The domain layer does not depend on raw CLI formatting. The `BrightDataResultNormalizer` extracts required identifiers/status/data mapping them into our internal models. WEBMORPH explicitly calls `approve` only after human approval. NEVER use `--auto-approve`.*

## Asynchronous Job Architecture
Operations trigger Jobs:
1. **HTTP Request:** Trigger collection or heal (triggered by operator/UI/API).
2. **Create Job:** Backend creates a Job record (`QUEUED`).
3. **Return 202:** Client receives `202 Accepted` and a `job_id`.
4. **Background Execution:** Job engine executes the Bright Data CLI. The MVP does not require autonomous scheduled scraping; execution is on-demand.
5. **JSON Capture & Normalization:** WEBMORPH captures machine-readable JSON and passes it through `BrightDataResultNormalizer`.
6. **Update State:** WEBMORPH persists normalized results (e.g., Snapshot `j_xxxxx`). Update Job/Run/Incident state.

## Continuous Intelligence
Verified Snapshot -> Historical Verified Data -> Domain-specific derived metrics -> Continuous Intelligence.
Continuous Intelligence operates continuously over the historical stream of VERIFIED snapshots. The intelligence layer must never consume an unverified degraded snapshot as trusted data. WEBMORPH protects downstream intelligence from corrupted extraction. The exact intelligence metric depends on the final selected target website and Data Contract. Scheduled/recurring collection may be added in the future without changing this core architecture.

## Security & Observability
- **CLI Security:** Subprocesses must be executed safely without `shell=True`, using structured `argv` arrays, timeouts, bounded output capture, and validation on `collector_id`.
- **Credentials:** The backend owns all Bright Data credentials via environment variables (`.env`). Credentials are never exposed to the browser or in API responses.
- **Logging:** Structured logs include request IDs, job IDs, and incident IDs. Secrets are redacted.

## Production Database
- **PostgreSQL** is the required persistence layer.
- ORM/Data layer: SQLAlchemy 2.x + Alembic.
- **SQLite** is allowed as a local development fallback only.
