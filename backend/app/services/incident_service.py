import asyncio
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.audit_event import AuditEvent
from app.models.collector import Collector
from app.models.healing_event import ApprovalStatus, HealingEvent, HealingStatus
from app.models.incident import Incident, IncidentStatus
from app.models.job import Job, JobStatus
from app.models.run import Run, RunStatus
from app.models.snapshot import Snapshot, ValidationState
from app.services.brightdata_service import BrightDataService, BrightDataServiceError
from app.validation.engine import process_payload

logger = logging.getLogger(__name__)


class AuditEventService:
    @staticmethod
    async def log_event(
        session: AsyncSession,
        event_type: str,
        related_entity_ref: str,
        actor_source: str = "system",
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """
        Creates an immutable audit event for a state transition.
        """
        event = AuditEvent(
            event_type=event_type,
            related_entity_ref=related_entity_ref,
            actor_source=actor_source,
            metadata_json=metadata,
        )
        session.add(event)
        return event


class DiagnosisService:
    @staticmethod
    async def diagnose_incident(
        session: AsyncSession, incident: Incident, snapshot: Snapshot
    ) -> Incident:
        """
        Deterministically diagnoses an incident based on the snapshot's validation details.
        Transitions the incident to DIAGNOSING -> HEAL_PROPOSED -> AWAITING_APPROVAL.
        Creates a HealingEvent.
        """
        if incident.status != IncidentStatus.DRIFT_DETECTED:
            raise ValueError(f"Cannot diagnose incident in state {incident.status}")

        # Transition to DIAGNOSING
        incident.status = IncidentStatus.DIAGNOSING
        await AuditEventService.log_event(
            session,
            "INCIDENT_STATE_CHANGED",
            f"incident:{incident.id}",
            metadata={"new_state": IncidentStatus.DIAGNOSING.value},
        )
        # Flush to persist state change before continuing
        await session.flush()

        # Guard: Ensure we are in DIAGNOSING before moving to HEAL_PROPOSED
        if incident.status != IncidentStatus.DIAGNOSING:
            raise ValueError(f"Incident {incident.id} is not in DIAGNOSING state.")

        # Deterministic Diagnosis
        details = snapshot.validation_details or {}
        missing_fields = details.get("missing_fields", [])
        schema_errors = details.get("schema_errors", [])
        stability_issues = details.get("stability_issues", [])

        completeness_score = snapshot.completeness_score or 0.0
        schema_validity_score = snapshot.schema_validity_score or 0.0
        stability_score = snapshot.stability_score or 0.0

        diagnosis_payload = {
            "root_cause": "DRIFT_DETECTED",
            "missing_fields": missing_fields,
            "schema_errors": schema_errors,
            "stability_issues": stability_issues,
            "health_breakdown": {
                "completeness": completeness_score,
                "schema_validity": schema_validity_score,
                "stability": stability_score,
                "overall": snapshot.health_score,
            },
            "snapshot_id": snapshot.id,
            "run_id": snapshot.run_id,
        }

        incident.diagnosis = diagnosis_payload

        # Stop at DIAGNOSING per Phase 5 scope
        await session.flush()

        return incident


class IncidentService:
    @staticmethod
    async def evaluate_snapshot(session: AsyncSession, snapshot: Snapshot) -> Incident | None:
        """
        Evaluates a snapshot and creates an incident if health < 80 (DRIFT_DETECTED).
        Does NOT create an incident for HEALTHY (>= 90) or DEGRADED (80-89.99).
        """
        health = snapshot.health_score
        if health is None:
            return None

        if health < 80.0:
            # We must create an incident.
            incident = Incident(
                collector_id=snapshot.collector_id,
                trigger_run_id=snapshot.run_id,
                status=IncidentStatus.DRIFT_DETECTED,
            )
            session.add(incident)
            await session.flush()

            await AuditEventService.log_event(
                session,
                "INCIDENT_CREATED",
                f"incident:{incident.id}",
                metadata={
                    "collector_id": snapshot.collector_id,
                    "run_id": snapshot.run_id,
                    "health": health,
                },
            )

            # Immediately trigger deterministic diagnosis
            await DiagnosisService.diagnose_incident(session, incident, snapshot)

            return incident

        # For DEGRADED or HEALTHY, no incident is created per specifications.
        return None

    @staticmethod
    async def process_human_approval(
        session: AsyncSession, incident_id: int, approved: bool
    ) -> HealingEvent:
        """
        Processes human approval or rejection for an AWAITING_APPROVAL incident.
        """
        # Fetch incident with active healing event
        stmt = select(Incident).where(Incident.id == incident_id)
        result = await session.execute(stmt)
        incident = result.scalar_one_or_none()

        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        if incident.status != IncidentStatus.AWAITING_APPROVAL:
            raise ValueError(
                f"Incident {incident_id} is in state {incident.status}, must be AWAITING_APPROVAL"
            )

        # Get active healing event
        stmt_he = select(HealingEvent).where(
            HealingEvent.incident_id == incident_id,
            HealingEvent.status == HealingStatus.AWAITING_APPROVAL,
        )
        result_he = await session.execute(stmt_he)
        healing_event = result_he.scalar_one_or_none()

        if not healing_event:
            raise ValueError(f"No active HealingEvent awaiting approval for incident {incident_id}")

        if approved:
            incident.status = IncidentStatus.APPROVED
            healing_event.approval_status = ApprovalStatus.APPROVED
            healing_event.status = HealingStatus.APPROVED
        else:
            incident.status = IncidentStatus.REJECTED
            healing_event.approval_status = ApprovalStatus.REJECTED
            healing_event.status = HealingStatus.REJECTED

        await AuditEventService.log_event(
            session,
            "INCIDENT_STATE_CHANGED",
            f"incident:{incident.id}",
            actor_source="operator",
            metadata={"new_state": incident.status.value, "healing_event_id": healing_event.id},
        )
        await AuditEventService.log_event(
            session,
            "HEALING_EVENT_STATE_CHANGED",
            f"healing_event:{healing_event.id}",
            actor_source="operator",
            metadata={"new_state": healing_event.status.value},
        )

        await session.flush()
        return healing_event

    @staticmethod
    async def execute_verification(
        session: AsyncSession,
        incident: Incident,
        healing_event: HealingEvent,
        job: Job,
        collector: Collector,
    ):
        """
        Executes the verification stage for an incident in the VERIFYING state.
        This includes triggering a Bright Data collector run, performing validation,
        and evaluating the recovery thresholds.
        """

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
        verification_attempts = 0
        target_url = settings.bright_data_target_url

        while True:
            verification_attempts += 1
            job.attempt_count += 1
            await session.commit()

            try:
                snapshot_id, raw_payload = await BrightDataService.run_collector(
                    collector.bright_data_collector_id, target_url
                )
                run.status = RunStatus.SUCCEEDED
                break
            except BrightDataServiceError as e:
                if e.retryable and verification_attempts < 3:
                    logger.warning(
                        f"Retryable error running verification collector "
                        f"(attempt {verification_attempts}/3): {str(e)}"
                    )
                    await asyncio.sleep(2 * (2 ** (verification_attempts - 1)))
                    continue

                run.status = RunStatus.FAILED
                await fail_incident(
                    IncidentStatus.VERIFICATION_FAILED, HealingStatus.FAILED, str(e)
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

        logger.info(f"DEBUG raw_payload: {raw_payload}")
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
            validation_details={
                "is_valid": validation_result.is_valid,
                "validation_state": validation_result.validation_state.value,
                "health_score": validation_result.health_score,
                "completeness_score": validation_result.completeness_score,
                "schema_validity_score": validation_result.schema_validity_score,
                "stability_score": validation_result.stability_score,
                "errors": validation_result.errors,
            },
        )
        session.add(snapshot)
        await session.flush()

        # Strict Recovery Evaluation Criteria
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
