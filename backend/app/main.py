"""
WEBMORPH — FastAPI Application Entry Point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import runs
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # Startup
    yield
    # Shutdown
    from app.database import engine

    await engine.dispose()


app = FastAPI(
    title="WEBMORPH",
    description="A reliability layer for web data. The web changes. Your data shouldn't.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow Next.js frontend in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(runs.router)


@app.get("/api/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "ok",
        "service": "webmorph",
        "version": "0.1.0",
        "environment": settings.app_env,
    }
