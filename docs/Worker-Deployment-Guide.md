# Phase 19.2: Worker Deployment Guide

WebMorph utilizes an asynchronous polling worker to process background jobs (data collection, AI heal requests, heal approvals, and verifications).

## Deployment Architecture
- **Type**: Background Worker (Render)
- **Framework**: Python `asyncio` with SQLAlchemy ORM
- **Entrypoint**: `worker_entry.py`

## Deployment Instructions on Render

1. **Create a New Background Worker**:
   - In the Render Dashboard, select **New** -> **Background Worker**.
   - Connect the GitHub repository.

2. **Configuration Details**:
   - **Name**: `webmorph-worker`
   - **Environment**: `Python`
   - **Root Directory**: `backend` (Important!)
   - **Build Command**: `curl -LsSf https://astral.sh/uv/install.sh | sh && uv sync`
   - **Start Command**: `uv run python worker_entry.py`

3. **Environment Variables Required**:
   Must match the web service exactly to share state.
   - `DATABASE_URL`: Your Neon PostgreSQL Connection String
   - `OPENAI_API_KEY`: For AI Healing jobs
   - `GEMINI_API_KEY`: Alternative AI Provider (if used)
   - `PYTHONPATH`: `.`
   - `DEMO_MODE`: `1` (if running in mock/demo mode to prevent hitting external Bright Data API)

## How the Worker Operates
The worker utilizes an infinite `while True` loop that executes every 5 seconds.
1. It queries the `Job` table for up to 5 jobs with `JobStatus.QUEUED`.
2. It processes jobs asynchronously using `asyncio.create_task()` depending on `job.operation_type`:
   - `COLLECTION` -> `process_collection_job`
   - `HEAL_REQUEST` -> `process_heal_request_job`
   - `HEAL_APPROVE` -> `process_heal_approve_job`
   - `VERIFICATION` -> `process_verification_job`

This simple but effective architecture avoids external dependencies like Redis or Celery, keeping the infrastructure lean for the MVP/Hackathon.
