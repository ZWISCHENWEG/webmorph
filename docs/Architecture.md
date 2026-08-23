# Architecture

WebMorph separates concerns across an API, asynchronous workers, domain validation logic, and an external integration layer.

## System Components
1. **API Router Layer (FastAPI)**: Restful entry points for the frontend and internal triggers. Handlers only return HTTP statuses, queue background tasks, or query the DB.
2. **Workers (BackgroundTasks)**: Three distinct workers decouple long-running Bright Data CLI operations from HTTP requests:
    - `run_worker.py`: Executes data collections, normalizes results, triggers the validation engine, and conditionally triggers incidents.
    - `approve_worker.py`: Integrates human approval with the `bdata scraper approve` command and transitions incidents to the verification stage.
    - `verify_worker.py`: Re-runs collection safely on an incident in the `VERIFYING` state to check if the healing was successful.
3. **Domain Engine (Validation & Health)**: Evaluates schemas, calculates completeness/stability, and detects drift.
4. **Service Layer**: Provides business logic aggregation (e.g. `IncidentService`, `BrightDataService`).
5. **Data Layer**: SQLAlchemy ORM tracking operations securely and idempotently.

## Data Flow
1. An operator or cron schedule triggers `/api/collectors/{id}/run`.
2. The `RunWorker` dispatches to `BrightDataService.run_collector`.
3. The raw JSON is normalized, stored as a `Snapshot`.
4. The snapshot payload is evaluated through `ValidationEngine`.
5. Health is calculated (`completeness`, `schema_validity`, `stability`).
6. If Health < 80%, an `Incident` is generated with `DRIFT_DETECTED`.
7. `IncidentService` calls Bright Data for a Heal Proposal.
8. State transitions to `AWAITING_APPROVAL`.
9. The Operator approves via the UI.
10. `ApproveWorker` runs `bdata scraper approve`.
11. `VerifyWorker` ensures drift is gone; moves incident to `RECOVERED`.

## Database Models
- **DataContract**: Defines the JSON schema for validation.
- **Collector**: External mapping to a Bright Data Scraper Studio ID.
- **Run**: Execution record of a single collection instance.
- **Snapshot**: The stored output JSON and evaluated Health.
- **Incident**: A lifecycle entity tracing extraction degradation over time.
- **HealingEvent**: The tracking entity for an AI heal proposal.
- **Job**: Enforces idempotency for all background asynchronous operations.
- **AuditEvent**: Historical timeline logic event sourcing.
