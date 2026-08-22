from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.schemas import IncidentDetailSchema, IncidentListResponse
from app.database import get_session
from app.models.incident import Incident

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("", response_model=IncidentListResponse)
async def get_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),  # noqa: B008
):
    """List incidents."""
    stmt = select(Incident).order_by(Incident.id.desc()).offset(skip).limit(limit)
    incidents = (await session.execute(stmt)).scalars().all()
    return {"data": incidents}


@router.get("/{incident_id}", response_model=IncidentDetailSchema)
async def get_incident(
    incident_id: int,
    session: AsyncSession = Depends(get_session),  # noqa: B008
):
    """Get a single incident by ID including nested events."""
    stmt = (
        select(Incident)
        .options(selectinload(Incident.healing_events))
        .where(Incident.id == incident_id)
    )
    incident = (await session.execute(stmt)).scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Fetch audit events manually, as there's no defined relationship on the ORM models.
    from app.models.audit_event import AuditEvent

    audit_stmt = (
        select(AuditEvent)
        .where(AuditEvent.related_entity_ref == f"incident:{incident.id}")
        .order_by(AuditEvent.id)
    )
    audit_events = (await session.execute(audit_stmt)).scalars().all()

    # Construct the response dictionary matching IncidentDetailSchema
    response_data = incident.__dict__.copy()
    # Pydantic handles lists of SQLAlchemy objects correctly via from_attributes=True
    response_data["healing_events"] = incident.healing_events
    response_data["audit_events"] = audit_events

    return response_data
