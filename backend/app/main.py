"""
WEBMORPH — FastAPI Application Entry Point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.errors import setup_exception_handlers
from app.api.routers import collectors, incidents, jobs, runs
from app.config import settings
from app.database import get_session

# Setup structured logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("webmorph.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # Startup
    logger.info("Starting WebMorph Backend...")
    yield
    # Shutdown
    logger.info("Shutting down WebMorph Backend...")
    from app.database import engine

    await engine.dispose()


app = FastAPI(
    title="WebMorph API",
    description="Self-healing web intelligence and automated scraping platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Parse allowed origins from environment (comma-separated), defaulting to ["*"]
allowed_origins_list = [
    origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(collectors.router)
app.include_router(incidents.router)
app.include_router(jobs.router)
app.include_router(runs.router)

setup_exception_handlers(app)


@app.get("/")
async def root():
    """Root endpoint for basic service identification."""
    return {"service": "WebMorph Backend", "status": "running", "version": "1.0.0"}


@app.get("/health")
async def health_check_root(
    response: Response,
    session: AsyncSession = Depends(get_session),  # noqa: B008
):
    """Root health check for deployment services like Render."""
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check database connection failed: {e}")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "error", "database": "disconnected"}


@app.get("/api/health")
async def health_check(
    response: Response,
    session: AsyncSession = Depends(get_session),  # noqa: B008
):
    """Detailed health check endpoint."""
    db_status = "connected"
    try:
        await session.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Detailed health check DB failure: {e}")
        db_status = "disconnected"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ok" if db_status == "connected" else "error",
        "service": "webmorph",
        "version": "1.0.0",
        "environment": settings.app_env,
        "database": db_status,
    }
