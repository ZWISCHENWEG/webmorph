import logging

from sqlalchemy import select

from app.database import async_session_factory
from app.models.collector import Collector
from app.models.healing_event import HealingEvent, HealingStatus
from app.models.incident import Incident, IncidentStatus
from app.models.job import Job, JobStatus
from app.services.brightdata_service import BrightDataService, BrightDataServiceError
from app.services.incident_service import AuditEventService, IncidentService

logger = logging.getLogger(__name__)


async def process_approve_job(job_id: int):
    """
    Background worker that orchestrates Bright Data approval and verification.
    APPROVED -> HEALING -> VERIFYING -> RECOVERED
    VERIFICATION_FAILED -> HEAL_FAILED -> MANUAL_INTERVENTION
    """
    async with async_session_factory() as session:
        job = await session.get(Job, job_id)
        if not job or job.status != JobStatus.QUEUED:
            return

        job.status = JobStatus.RUNNING
        await session.commit()

        try:
            _, incident_id_str = job.related_entity_ref.split(":")
            incident_id = int(incident_id_str)
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = f"Invalid related_entity_ref: {e}"
            await session.commit()
            return

        stmt = select(Incident).where(Incident.id == incident_id)
        incident = (await session.execute(stmt)).scalar_one_or_none()
        if not incident:
            job.status = JobStatus.FAILED
            job.error_message = "Incident not found"
            await session.commit()
            return

        collector = await session.get(Collector, incident.collector_id)
        if not collector:
            job.status = JobStatus.FAILED
            job.error_message = "Collector not found"
            await session.commit()
            return

        stmt_he = select(HealingEvent).where(
            HealingEvent.incident_id == incident_id,
            HealingEvent.status == HealingStatus.APPROVED,
        )
        healing_event = (await session.execute(stmt_he)).scalar_one_or_none()
        if not healing_event:
            job.status = JobStatus.FAILED
            job.error_message = "No active approved HealingEvent found"
            await session.commit()
            return

        if incident.status != IncidentStatus.APPROVED:
            job.status = JobStatus.FAILED
            job.error_message = f"Incident not in APPROVED state, got {incident.status}"
            await session.commit()
            return

        # Helper for handling failure cascade
        async def fail_incident(
            failure_state: IncidentStatus, heal_status: HealingStatus, error_msg: str
        ):
            async with session.begin_nested():
                incident.status = failure_state
                healing_event.status = heal_status

                await AuditEventService.log_event(
                    session,
                    "INCIDENT_STATE_CHANGED",
                    f"incident:{incident.id}",
                    metadata={"new_state": failure_state.value, "error": error_msg},
                )
                await AuditEventService.log_event(
                    session,
                    "HEALING_EVENT_STATE_CHANGED",
                    f"healing_event:{healing_event.id}",
                    metadata={"new_state": heal_status.value},
                )
            job.status = JobStatus.FAILED
            job.error_message = error_msg

        # Transition to HEALING
        async with session.begin_nested():
            incident.status = IncidentStatus.HEALING
            healing_event.status = HealingStatus.HEALING
            await AuditEventService.log_event(
                session,
                "INCIDENT_STATE_CHANGED",
                f"incident:{incident.id}",
                metadata={"new_state": IncidentStatus.HEALING.value},
            )
            await AuditEventService.log_event(
                session,
                "HEALING_EVENT_STATE_CHANGED",
                f"healing_event:{healing_event.id}",
                metadata={"new_state": HealingStatus.HEALING.value},
            )
        await session.commit()

        # Execute Bright Data Approval
        job.attempt_count += 1
        await session.commit()
        try:
            await BrightDataService.approve_heal(collector.bright_data_collector_id)
        except BrightDataServiceError as e:
            # Failure transitions: VERIFICATION_FAILED -> HEAL_FAILED -> MANUAL_INTERVENTION
            # Note: skips VERIFICATION_FAILED and goes HEAL_FAILED
            await fail_incident(IncidentStatus.HEAL_FAILED, HealingStatus.FAILED, str(e))
            # And then MANUAL_INTERVENTION
            async with session.begin_nested():
                incident.status = IncidentStatus.MANUAL_INTERVENTION
                await AuditEventService.log_event(
                    session,
                    "INCIDENT_STATE_CHANGED",
                    f"incident:{incident.id}",
                    metadata={
                        "new_state": IncidentStatus.MANUAL_INTERVENTION.value,
                        "reason": "approve_failed",
                    },
                )
            await session.commit()
            return
        except Exception as e:
            await fail_incident(
                IncidentStatus.HEAL_FAILED, HealingStatus.FAILED, f"Unexpected error: {str(e)}"
            )
            async with session.begin_nested():
                incident.status = IncidentStatus.MANUAL_INTERVENTION
                await AuditEventService.log_event(
                    session,
                    "INCIDENT_STATE_CHANGED",
                    f"incident:{incident.id}",
                    metadata={
                        "new_state": IncidentStatus.MANUAL_INTERVENTION.value,
                        "reason": "approve_failed",
                    },
                )
            await session.commit()
            return

        # Transition to VERIFYING
        async with session.begin_nested():
            incident.status = IncidentStatus.VERIFYING
            healing_event.status = HealingStatus.VERIFYING
            await AuditEventService.log_event(
                session,
                "INCIDENT_STATE_CHANGED",
                f"incident:{incident.id}",
                metadata={"new_state": IncidentStatus.VERIFYING.value},
            )
            await AuditEventService.log_event(
                session,
                "HEALING_EVENT_STATE_CHANGED",
                f"healing_event:{healing_event.id}",
                metadata={"new_state": HealingStatus.VERIFYING.value},
            )
        await session.commit()

        await IncidentService.execute_verification(
            session=session,
            incident=incident,
            healing_event=healing_event,
            job=job,
            collector=collector,
        )
