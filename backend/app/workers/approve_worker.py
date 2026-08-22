import logging

from sqlalchemy import select

from app.config import settings
from app.database import async_session_factory
from app.models.collector import Collector
from app.models.healing_event import HealingEvent, HealingStatus
from app.models.incident import Incident, IncidentStatus
from app.models.job import Job, JobStatus
from app.models.run import Run, RunStatus
from app.models.snapshot import Snapshot, ValidationState
from app.services.brightdata_service import BrightDataService, BrightDataServiceError
from app.services.incident_service import AuditEventService
from app.validation.engine import process_payload

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

        # Create Verification Run
        run = Run(
            collector_id=collector.id,
            contract_version=collector.current_contract_version,
            job_id=job.id,
            status=RunStatus.RUNNING,
        )
        session.add(run)
        await session.commit()
        await session.refresh(run)

        # Link verification run to healing event
        healing_event.verification_run_id = run.id
        await session.commit()

        # Execute Verification Scrape
        try:
            target_url = settings.bright_data_target_url
            snapshot_id, raw_payload = await BrightDataService.run_collector(
                collector.bright_data_collector_id, target_url
            )
            run.status = RunStatus.SUCCEEDED
        except BrightDataServiceError as e:
            run.status = RunStatus.FAILED
            await fail_incident(IncidentStatus.VERIFICATION_FAILED, HealingStatus.FAILED, str(e))
            # Cascade
            async with session.begin_nested():
                incident.status = IncidentStatus.HEAL_FAILED
                await AuditEventService.log_event(
                    session,
                    "INCIDENT_STATE_CHANGED",
                    f"incident:{incident.id}",
                    metadata={"new_state": IncidentStatus.HEAL_FAILED.value},
                )
            async with session.begin_nested():
                incident.status = IncidentStatus.MANUAL_INTERVENTION
                await AuditEventService.log_event(
                    session,
                    "INCIDENT_STATE_CHANGED",
                    f"incident:{incident.id}",
                    metadata={
                        "new_state": IncidentStatus.MANUAL_INTERVENTION.value,
                        "reason": "verification_run_failed",
                    },
                )
            await session.commit()
            return
        except Exception as e:
            run.status = RunStatus.FAILED
            await fail_incident(
                IncidentStatus.VERIFICATION_FAILED,
                HealingStatus.FAILED,
                f"Unexpected error: {str(e)}",
            )
            # Cascade
            async with session.begin_nested():
                incident.status = IncidentStatus.HEAL_FAILED
                await AuditEventService.log_event(
                    session,
                    "INCIDENT_STATE_CHANGED",
                    f"incident:{incident.id}",
                    metadata={"new_state": IncidentStatus.HEAL_FAILED.value},
                )
            async with session.begin_nested():
                incident.status = IncidentStatus.MANUAL_INTERVENTION
                await AuditEventService.log_event(
                    session,
                    "INCIDENT_STATE_CHANGED",
                    f"incident:{incident.id}",
                    metadata={
                        "new_state": IncidentStatus.MANUAL_INTERVENTION.value,
                        "reason": "verification_run_failed",
                    },
                )
            await session.commit()
            return
        
        # Calculate Stability
        baseline_stmt = (
            select(Snapshot)
            .where(
                Snapshot.collector_id == collector.id,
                Snapshot.validation_state == ValidationState.HEALTHY,
            )
            .order_by(Snapshot.created_at.desc())
            .limit(5)
        )
        baseline_results = await session.scalars(baseline_stmt)
        baseline_counts = [s.record_count for s in baseline_results]

        validation_result = process_payload(raw_payload, baseline_counts)

        snapshot = Snapshot(
            bright_data_snapshot_id=snapshot_id,
            collector_id=collector.id,
            run_id=run.id,
            contract_version=collector.current_contract_version,
            raw_payload=raw_payload,
            normalized_payload=validation_result.normalized_payload,
            record_count=len(validation_result.normalized_payload),
            validation_state=validation_result.validation_state,
            health_score=validation_result.health_score,
            completeness_score=validation_result.completeness_score,
            schema_validity_score=validation_result.schema_validity_score,
            stability_score=validation_result.stability_score,
            validation_details=validation_result.model_dump(),
        )
        session.add(snapshot)
        await session.flush()

        # Strict Recovery Evaluation Criteria:
        # - health_score >= RECOVERY_THRESHOLD (95)
        # - field completeness >= REQUIRED_FIELD_RECOVERY_THRESHOLD (95) for ALL required fields
        # - schema validity == 100
        # - record stability >= 90
        # - no critical validation errors (if any, already caught in schema validity)
        # - Bright Data run completed successfully (already checked)
        
        recovery_passed = True
        
        if validation_result.health_score < 95.0:
            recovery_passed = False
        
        if validation_result.schema_validity_score < 100.0:
            recovery_passed = False
            
        if validation_result.stability_score < 90.0:
            recovery_passed = False
            
        if validation_result.completeness_score < 95.0:
            recovery_passed = False

        if recovery_passed:
            async with session.begin_nested():
                incident.status = IncidentStatus.RECOVERED
                healing_event.status = HealingStatus.RECOVERED
                
                await AuditEventService.log_event(
                    session,
                    "INCIDENT_STATE_CHANGED",
                    f"incident:{incident.id}",
                    metadata={"new_state": IncidentStatus.RECOVERED.value},
                )
                await AuditEventService.log_event(
                    session,
                    "HEALING_EVENT_STATE_CHANGED",
                    f"healing_event:{healing_event.id}",
                    metadata={"new_state": HealingStatus.RECOVERED.value},
                )
            job.status = JobStatus.SUCCEEDED
            await session.commit()
        else:
            await fail_incident(
                IncidentStatus.VERIFICATION_FAILED,
                HealingStatus.FAILED,
                "Recovery criteria not met",
            )
            async with session.begin_nested():
                incident.status = IncidentStatus.HEAL_FAILED
                await AuditEventService.log_event(
                    session,
                    "INCIDENT_STATE_CHANGED",
                    f"incident:{incident.id}",
                    metadata={"new_state": IncidentStatus.HEAL_FAILED.value},
                )
            async with session.begin_nested():
                incident.status = IncidentStatus.MANUAL_INTERVENTION
                await AuditEventService.log_event(
                    session,
                    "INCIDENT_STATE_CHANGED",
                    f"incident:{incident.id}",
                    metadata={
                        "new_state": IncidentStatus.MANUAL_INTERVENTION.value,
                        "reason": "criteria_failed",
                    },
                )
            await session.commit()
