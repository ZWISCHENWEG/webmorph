# Deployment Plan

*(Note: The system is not currently deployed. This document serves as the plan for Phase 19).*

## Backend

**Hosting Options:**
- Railway, Render, or Heroku for easy containerized deployment.
- AWS ECS or Google Cloud Run for scalable production environments.

**Environment Variables Required:**
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
BRIGHT_DATA_API_TOKEN=your_production_token
BRIGHT_DATA_COLLECTOR_ID=your_collector
BRIGHT_DATA_TARGET_URL=your_target_url
DEMO_MODE=false
```

**Migrations:**
- Upon deployment, execute `uv run alembic upgrade head` as a release phase command.

## Frontend

**Build & Deployment:**
- Standard Next.js deployment on **Vercel** or **Netlify**.
- Requires connecting the GitHub repository.
- Build command: `npm run build`
- Environment Variables Required: `NEXT_PUBLIC_API_URL` pointing to the hosted backend API.

## Database

**Production Database Migration:**
- Provision a managed PostgreSQL instance (e.g., Supabase, Neon, AWS RDS).
- Inject the connection string securely into the Backend environment via `DATABASE_URL`.
- Local SQLite (`webmorph.db`) will not be used in production.
