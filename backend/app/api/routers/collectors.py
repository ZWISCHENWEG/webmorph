from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import CollectorListResponse, CollectorSchema
from app.database import get_session
from app.models.collector import Collector

router = APIRouter(prefix="/api/collectors", tags=["collectors"])


@router.get("", response_model=CollectorListResponse)
async def get_collectors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),  # noqa: B008
):
    """List collectors."""
    stmt = select(Collector).order_by(Collector.id).offset(skip).limit(limit)
    collectors = (await session.execute(stmt)).scalars().all()
    return {"data": collectors}


@router.get("/{collector_id}", response_model=CollectorSchema)
async def get_collector(
    collector_id: int,
    session: AsyncSession = Depends(get_session),  # noqa: B008
):
    """Get a single collector by ID."""
    collector = await session.get(Collector, collector_id)
    if not collector:
        raise HTTPException(status_code=404, detail="Collector not found")
    return collector
