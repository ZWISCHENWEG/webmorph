# WebMorph - Phase 19 Deployment Checklist

This document details the exact configuration required to deploy WebMorph to Render successfully.

## 1. Prerequisites

### Database (Neon PostgreSQL)
1. Create a Neon PostgreSQL database.
2. Copy the connection string.
3. Replace the `postgres://` prefix with `postgresql+asyncpg://` if it is not already set.

### Bright Data
1. Ensure your Bright Data API Token is valid.
2. Ensure you have the Target URL and Collector ID ready.

---

## 2. Environment Variables
Both the Web Service and Background Worker require these environment variables to be set in the Render dashboard:

| Variable | Description | Example |
|---|---|---|
| `APP_ENV` | Application environment (set to production) | `production` |
| `DATABASE_URL` | Neon DB connection string with asyncpg | `postgresql+asyncpg://user:pass@ep-cool...` |
| `BRIGHT_DATA_API_TOKEN` | Your Bright Data API Token | `...` |
| `BRIGHT_DATA_COLLECTOR_ID` | Your Bright Data Collector ID | `c_mt45pt...` |
| `BRIGHT_DATA_TARGET_URL` | The URL you are monitoring | `https://books.toscrape.com/` |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed frontend domains. Defaults to `*` if left empty. | `https://your-vercel-app.vercel.app` |

---

## 3. Web Service Configuration (FastAPI)

Create a **New Web Service** on Render connected to this repository.

- **Root Directory:** `backend`
- **Language:** Python
- **Python Version:** 3.12 (Set via `PYTHON_VERSION` env var if `.python-version` isn't detected)
- **Build Command:** `curl -LsSf https://astral.sh/uv/install.sh | sh && uv sync`
- **Start Command:** `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path:** `/health`

*Note: Migrations are not executed automatically on startup. See section 5.*

---

## 4. Background Worker Configuration

Create a **New Background Worker** on Render connected to this repository.

- **Root Directory:** `backend`
- **Language:** Python
- **Build Command:** `curl -LsSf https://astral.sh/uv/install.sh | sh && uv sync`
- **Start Command:** `uv run python worker_entry.py`

---

## 5. Executing Database Migrations

Since migrations are not tied to the startup command to prevent conflicts during horizontal scaling or rapid restarts, you must run migrations manually upon initial deployment.

From the Render dashboard for your Web Service:
1. Go to the **Shell** tab (if available on your plan) and run:
   ```bash
   uv run python run_migrations.py
   ```
2. **OR (for Free Tier without Shell):** Temporarily change your Web Service **Start Command** to:
   ```bash
   uv run python run_migrations.py && uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
   Deploy the service to execute the migration, and then revert the Start Command back to the standard one.
