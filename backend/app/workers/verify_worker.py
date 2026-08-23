"""
WEBMORPH — Verify Worker.

Handles idempotent resumption of the verification process for incidents
that are already in the VERIFYING state with an approved healing event.
"""

import logging

from sqlalchemy import select

from app.database import async_session_factory
from app.models.collector import Collector
from app.models.healing_event import ApprovalStatus, HealingEvent
from app.models.incident import Incident, IncidentStatus
from app.models.job import Job, JobStatus
from app.services.incident_service import IncidentService

logger = logging.getLogger(__name__)


async def process_verify_job(job_id: int):
    """
    Background worker that orchestrates safe verification resume.
    """
    async with async_session_factory() as session:
        job = await session.get(Job, job_id)
        if not job or job.status != JobStatus.QUEUED:
            return

        # Start job
        job.status = JobStatus.RUNNING
        await session.commit()

        try:
            # 1. Fetch Incident
            if not job.related_entity_ref or not job.related_entity_ref.startswith("incident:"):
                raise ValueError(
                    "Verification job must have a related_entity_ref pointing to an incident"
                )
            incident_id = int(job.related_entity_ref.split(":")[1])
            incident = await session.get(Incident, incident_id)
            if not incident:
                raise ValueError(f"Incident {incident_id} not found")

            if incident.status != IncidentStatus.VERIFYING:
                raise ValueError(
                    f"Incident {incident.id} is in {incident.status.value}, not VERIFYING"
                )

            # 2. Fetch Collector
            collector = await session.get(Collector, incident.collector_id)
            if not collector:
                raise ValueError(f"Collector {incident.collector_id} not found")

            # 3. Fetch active HealingEvent
            stmt = select(HealingEvent).where(
                HealingEvent.incident_id == incident.id,
                HealingEvent.status.notin_(["RECOVERED", "REJECTED", "FAILED"]),
            )
            healing_event = await session.scalar(stmt)

            if not healing_event:
                raise ValueError(f"No active HealingEvent for incident {incident.id}")

            if healing_event.approval_status != ApprovalStatus.APPROVED:
                raise ValueError(
                    f"HealingEvent {healing_event.id} approval_status is "
                    f"{healing_event.approval_status.value}, not APPROVED"
                )

            # 4. Delegate to Shared Verification Logic
            await IncidentService.execute_verification(
                session=session,
                incident=incident,
                healing_event=healing_event,
                job=job,
                collector=collector,
            )

        except ValueError as e:
            logger.error(f"Validation error in verify job {job_id}: {str(e)}")
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            await session.commit()
        except Exception as e:
            logger.exception(f"Unexpected error in verify job {job_id}")
            job.status = JobStatus.FAILED
            job.error_message = f"Unexpected error: {str(e)}"
            await session.commit()
