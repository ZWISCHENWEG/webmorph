# Deployment Readiness Audit

## Current Deployment Blockers
- None. The backend natively supports dynamic configuration via environment variables, the database layer natively supports `DATABASE_URL` (including `postgresql+asyncpg`), and the frontend safely uses `NEXT_PUBLIC_API_URL`.

## Required Environment Variables
**Backend (Render):**
- `DATABASE_URL`: Connection string to PostgreSQL (e.g., `postgresql+asyncpg://user:pass@host/db`).
- `BRIGHT_DATA_API_TOKEN`: Official Bright Data Scraper Studio API key.
- `BRIGHT_DATA_COLLECTOR_ID`: The deployed Scraper Studio collector ID.
- `BRIGHT_DATA_TARGET_URL`: The target URL for extraction.
- `APP_ENV`: Set to `production`.
- `DEMO_MODE`: Set to `false`.

**Frontend (Vercel):**
- `NEXT_PUBLIC_API_URL`: URL pointing to the deployed Render backend (e.g., `https://webmorph-backend.onrender.com`).

## Required Service Configuration
- **Backend Service**: Requires running `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`. The `/api/health` endpoint is already exposed for zero-downtime checks.
- **Frontend Service**: Next.js requires the standard `npm run build` and `npm start` (Vercel handles this automatically).
- **Worker Service**: A separate `backend/worker_entry.py` has been created to poll the database and dispatch async processes without coupling execution strictly to the web service event loop.

## Database Compatibility Status
- Fully compatible. The system defaults to `sqlite+aiosqlite` for local development. By configuring `DATABASE_URL` in production, SQLAlchemy automatically loads the `asyncpg` dialect. The `asyncpg` library has been explicitly added to the primary dependency manifest in `pyproject.toml`.

## Worker Deployment Requirements
- The background worker requires a standard Python execution environment running `uv run python worker_entry.py`. It requires the same environment variables as the backend web service (including `DATABASE_URL` and Bright Data credentials).
