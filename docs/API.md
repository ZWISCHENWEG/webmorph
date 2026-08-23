# API Documentation

## Collectors

### `POST /api/collectors/{id}/run`
Triggers an asynchronous scrape execution for the specified Bright Data Collector.
- **Purpose**: Queues a background job to run the collector via `bdata scraper run`.
- **Response**: `202 Accepted` with a Job ID for tracking.

## Incidents

### `POST /api/incidents/{id}/heal`
Requests an AI-generated heal proposal from Bright Data for an active incident in the `DIAGNOSING` state.
- **Purpose**: Creates an idempotent job that requests an external fix from Scraper Studio and transitions the incident to `AWAITING_APPROVAL`.
- **Response**: `202 Accepted` with a Job ID.

### `POST /api/incidents/{id}/approve`
Approves the received healing proposal, moving it to production execution.
- **Purpose**: Initiates the `bdata scraper approve` command to promote a Bright Data development template into production, transitioning the incident to `HEALING` and subsequently to `VERIFYING`.
- **Response**: `202 Accepted` with a Job ID.

### `POST /api/incidents/{id}/verify`
Safely resumes the verification phase of a successfully approved incident.
- **Purpose**: Dispatches the `VerifyWorker` to run a new data collection through the healed scraper, validating the results against the Data Contract to confirm the fix before moving to `RECOVERED`.
- **Response**: `202 Accepted` with a Job ID.

## Jobs
### `GET /api/jobs/{id}`
Returns the real-time execution status of any queued asynchronous background task (e.g., runs, heals, approvals, verification).
