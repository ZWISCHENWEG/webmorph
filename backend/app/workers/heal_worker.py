import logging

from app.database import async_session_factory
from app.models.collector import Collector
from app.models.healing_event import ApprovalStatus, HealingEvent, HealingStatus
from app.models.incident import Incident, IncidentStatus
from app.models.job import Job, JobStatus
from app.services.brightdata_service import BrightDataService, BrightDataServiceError
from app.services.incident_service import AuditEventService

logger = logging.getLogger(__name__)


async def process_heal_job(job_id: int):
    """
    Background worker that orchestrates the Bright Data heal request lifecycle.
    Job -> request_heal -> Incident/HealingEvent state updates.
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

        incident = await session.get(Incident, incident_id)
        if not incident:
            job.status = JobStatus.FAILED
            job.error_message = "Incident not found"
            await session.commit()
            return

        if incident.status != IncidentStatus.DIAGNOSING:
            job.status = JobStatus.FAILED
            job.error_message = f"Incident in invalid state: {incident.status}"
            await session.commit()
            return

        collector = await session.get(Collector, incident.collector_id)
        if not collector:
            job.status = JobStatus.FAILED
            job.error_message = "Collector not found"
            await session.commit()
            return

        # Construct what_broke
        diagnosis = incident.diagnosis or {}
        missing_fields = diagnosis.get("missing_fields", [])
        schema_errors = diagnosis.get("schema_errors", [])
        stability_issues = diagnosis.get("stability_issues", [])

        parts = []
        if missing_fields:
            parts.append(f"Missing fields: {', '.join(missing_fields)}")
        if schema_errors:
            schema_err_strs = [
                err.get("msg", "schema err") if isinstance(err, dict) else str(err)
                for err in schema_errors
            ]
            parts.append(f"Schema errors: {', '.join(schema_err_strs)}")
        if stability_issues:
            parts.append(f"Stability issues: {', '.join(stability_issues)}")

        what_broke = ". ".join(parts)
        if not what_broke:
            what_broke = "Unknown degradation."

        # Execute CLI
        try:
            proposal = await BrightDataService.request_heal(
                collector.bright_data_collector_id, what_broke
            )
        except BrightDataServiceError as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            await session.commit()
            return
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = f"Unexpected error: {str(e)}"
            await session.commit()
            return

        # Success - transition states
        try:
            async with session.begin_nested():
                # Incident DIAGNOSING -> HEAL_PROPOSED
                incident.status = IncidentStatus.HEAL_PROPOSED
                await AuditEventService.log_event(
                    session,
                    "INCIDENT_STATE_CHANGED",
                    f"incident:{incident.id}",
                    metadata={"new_state": IncidentStatus.HEAL_PROPOSED.value},
                )

                # HealingEvent -> PROPOSED
                healing_event = HealingEvent(
                    incident_id=incident.id,
                    status=HealingStatus.PROPOSED,
                    approval_status=ApprovalStatus.PENDING,
                    proposal=proposal,
                )
                session.add(healing_event)
                await session.flush()

                await AuditEventService.log_event(
                    session,
                    "HEALING_EVENT_CREATED",
                    f"healing_event:{healing_event.id}",
                    metadata={"status": HealingStatus.PROPOSED.value},
                )

                # Incident HEAL_PROPOSED -> AWAITING_APPROVAL
                incident.status = IncidentStatus.AWAITING_APPROVAL
                await AuditEventService.log_event(
                    session,
                    "INCIDENT_STATE_CHANGED",
                    f"incident:{incident.id}",
                    metadata={
                        "new_state": IncidentStatus.AWAITING_APPROVAL.value,
                        "healing_event_id": healing_event.id,
                    },
                )

                # HealingEvent PROPOSED -> AWAITING_APPROVAL
                healing_event.status = HealingStatus.AWAITING_APPROVAL
                await AuditEventService.log_event(
                    session,
                    "HEALING_EVENT_STATE_CHANGED",
                    f"healing_event:{healing_event.id}",
                    metadata={"new_state": HealingStatus.AWAITING_APPROVAL.value},
                )

                job.status = JobStatus.SUCCEEDED

            await session.commit()
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = f"Persistence failure: {str(e)}"
            await session.commit()
            return
