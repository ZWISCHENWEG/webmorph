from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.schemas import IncidentDetailSchema, IncidentListResponse
from app.database import get_session
from app.models.healing_event import HealingEvent, HealingStatus
from app.models.incident import Incident, IncidentStatus
from app.models.job import Job, JobOperationType, JobStatus
from app.workers.heal_worker import process_heal_job

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


class JobAcceptedResponse(BaseModel):
    job_id: str
    status: str


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


@router.post(
    "/{incident_id}/heal", response_model=JobAcceptedResponse, status_code=status.HTTP_202_ACCEPTED
)
async def request_heal(
    incident_id: int,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),  # noqa: B008
):
    """Trigger a heal request for an incident in DIAGNOSING state."""
    stmt = select(Incident).where(Incident.id == incident_id)
    incident = (await session.execute(stmt)).scalar_one_or_none()

    if not incident:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "ERR_NOT_FOUND",
                    "message": "Incident not found",
                    "retryable": False,
                }
            },
        )

    if incident.status != IncidentStatus.DIAGNOSING:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "ERR_INVALID_STATE",
                    "message": f"Incident must be DIAGNOSING, got {incident.status.value}",
                    "retryable": False,
                }
            },
        )

    # Duplicate protection - Active Healing Event
    he_stmt = select(HealingEvent).where(
        HealingEvent.incident_id == incident_id,
        HealingEvent.status.not_in(
            [HealingStatus.RECOVERED, HealingStatus.REJECTED, HealingStatus.FAILED]
        ),
    )
    existing_he = (await session.execute(he_stmt)).scalar_one_or_none()
    if existing_he:
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": "ERR_CONFLICT",
                    "message": "Active healing event already exists for this incident",
                    "retryable": False,
                }
            },
        )

    # Duplicate protection - Active Job
    job_stmt = select(Job).where(
        Job.related_entity_ref == f"incident:{incident_id}",
        Job.operation_type == JobOperationType.HEAL_REQUEST,
        Job.status.in_([JobStatus.QUEUED, JobStatus.RUNNING]),
    )
    existing_job = (await session.execute(job_stmt)).scalar_one_or_none()
    if existing_job:
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": "ERR_CONFLICT",
                    "message": "Active heal request job already exists for this incident",
                    "retryable": False,
                }
            },
        )

    # Create Job
    job = Job(
        operation_type=JobOperationType.HEAL_REQUEST,
        related_entity_ref=f"incident:{incident.id}",
        status=JobStatus.QUEUED,
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    background_tasks.add_task(process_heal_job, job.id)

    return {"job_id": f"job_{job.id}", "status": "QUEUED"}
