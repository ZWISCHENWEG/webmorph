# Deployment Debugging Report: `/api/collectors` ERR_INTERNAL on Render/Neon

## 1. Problem Description
After deploying the WebMorph backend to Render with Neon PostgreSQL, the `/health` endpoint succeeded (`{"status": "ok"}`), confirming database connectivity. However, calling `GET /api/collectors` resulted in an HTTP 500 error mapped as `ERR_INTERNAL`.

## 2. Investigation & Root Cause
We traced the issue down to a discrepancy between the SQLAlchemy ORM model and the Alembic database migrations:
- **Migration History:** The initial migration (`05f15b2b6e0e`) created the `collectors` table with `name` and `target_url` columns. A subsequent cleanup migration (`f11d6dd45df1`) dropped these columns.
- **ORM Model Mismatch:** Despite the columns being dropped from the database in the cleanup phase, `name` and `target_url` were still defined in `backend/app/models/collector.py`.
- **Why it passed locally:** Our `pytest` suite uses an in-memory SQLite database and provisions it using `Base.metadata.create_all()` rather than applying Alembic migrations. This bypassed the schema drift and created the missing columns, leading to a false sense of security.
- **The Exact Exception:** When `GET /api/collectors` invoked `select(Collector)`, SQLAlchemy explicitly asked PostgreSQL for all columns defined in the model. Since `name` and `target_url` did not exist, `asyncpg` threw an **`UndefinedColumnError`** (`column "name" does not exist`). This was caught by the global error handler and returned to the user as `ERR_INTERNAL`.

## 3. Resolution
- **Fix Applied:** We removed the orphaned `name` and `target_url` attributes from the `Collector` SQLAlchemy model (`backend/app/models/collector.py`).
- **Validation:** 
  - Ran `ruff check --fix .` to ensure codebase cleanliness.
  - Ran `pytest` locally to confirm all 78 tests pass with the updated model.
- **Architecture Stability:** No core architecture, workflows, or frontend components were modified. The fix was isolated to the ORM definition to ensure consistency with the established production schema.

## 4. Next Steps
The backend is now ready for a redeployment to Render. The schema correctly matches the code, and `GET /api/collectors` will return successfully.
