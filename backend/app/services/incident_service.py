import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_event import AuditEvent
from app.models.healing_event import ApprovalStatus, HealingEvent, HealingStatus
from app.models.incident import Incident, IncidentStatus
from app.models.snapshot import Snapshot

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

        # Transition to HEAL_PROPOSED
        incident.status = IncidentStatus.HEAL_PROPOSED
        await AuditEventService.log_event(
            session,
            "INCIDENT_STATE_CHANGED",
            f"incident:{incident.id}",
            metadata={"new_state": IncidentStatus.HEAL_PROPOSED.value},
        )
        await session.flush()

        # Create HealingEvent in PROPOSED state
        healing_event = HealingEvent(
            incident_id=incident.id,
            status=HealingStatus.PROPOSED,
            approval_status=ApprovalStatus.PENDING,
            proposal={"type": "human_assisted_heal", "diagnosis": diagnosis_payload},
        )
        session.add(healing_event)
        await session.flush()

        await AuditEventService.log_event(
            session,
            "HEALING_EVENT_CREATED",
            f"healing_event:{healing_event.id}",
            metadata={"incident_id": incident.id, "status": HealingStatus.PROPOSED.value},
        )

        # Guard: Ensure Incident is HEAL_PROPOSED
        if incident.status != IncidentStatus.HEAL_PROPOSED:
            raise ValueError(f"Incident {incident.id} is not in HEAL_PROPOSED state.")

        # Transition Incident and HealingEvent to AWAITING_APPROVAL
        incident.status = IncidentStatus.AWAITING_APPROVAL
        healing_event.status = HealingStatus.AWAITING_APPROVAL

        await AuditEventService.log_event(
            session,
            "INCIDENT_STATE_CHANGED",
            f"incident:{incident.id}",
            metadata={"new_state": IncidentStatus.AWAITING_APPROVAL.value},
        )
        await AuditEventService.log_event(
            session,
            "HEALING_EVENT_STATE_CHANGED",
            f"healing_event:{healing_event.id}",
            metadata={"new_state": HealingStatus.AWAITING_APPROVAL.value},
        )
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
