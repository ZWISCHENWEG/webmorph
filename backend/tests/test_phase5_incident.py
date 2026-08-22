import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_event import AuditEvent
from app.models.collector import Collector
from app.models.healing_event import ApprovalStatus, HealingEvent, HealingStatus
from app.models.incident import Incident, IncidentStatus
from app.models.run import Run, RunStatus
from app.models.snapshot import Snapshot, ValidationState
from app.services.incident_service import DiagnosisService, IncidentService


@pytest_asyncio.fixture
async def collector(db_session: AsyncSession):
    c = Collector(bright_data_collector_id="c_test_inc", current_contract_version=1)
    db_session.add(c)
    await db_session.flush()
    return c


@pytest_asyncio.fixture
async def run(db_session: AsyncSession, collector):
    r = Run(collector_id=collector.id, contract_version=1, status=RunStatus.SUCCEEDED)
    db_session.add(r)
    await db_session.flush()
    return r


@pytest.mark.asyncio
async def test_incident_not_created_for_healthy(db_session: AsyncSession, collector, run):
    """HEALTHY snapshots (>= 90) must not create incidents."""
    snapshot = Snapshot(
        bright_data_snapshot_id="j_healthy",
        collector_id=collector.id,
        run_id=run.id,
        contract_version=1,
        health_score=100.0,
        validation_state=ValidationState.HEALTHY,
    )
    db_session.add(snapshot)
    await db_session.flush()

    incident = await IncidentService.evaluate_snapshot(db_session, snapshot)
    assert incident is None

    stmt = select(Incident).where(Incident.trigger_run_id == run.id)
    result = await db_session.execute(stmt)
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_incident_not_created_for_degraded(db_session: AsyncSession, collector, run):
    """DEGRADED snapshots (80 <= health < 90) must not create incidents."""
    snapshot = Snapshot(
        bright_data_snapshot_id="j_degraded",
        collector_id=collector.id,
        run_id=run.id,
        contract_version=1,
        health_score=80.0,
        validation_state=ValidationState.DEGRADED,
    )
    db_session.add(snapshot)
    await db_session.flush()

    incident = await IncidentService.evaluate_snapshot(db_session, snapshot)
    assert incident is None


@pytest.mark.asyncio
async def test_incident_trigger_drift_detected(db_session: AsyncSession, collector, run):
    """DRIFT_DETECTED snapshots (< 80) must create an incident."""
    snapshot = Snapshot(
        bright_data_snapshot_id="j_drift",
        collector_id=collector.id,
        run_id=run.id,
        contract_version=1,
        health_score=79.99,
        validation_state=ValidationState.DRIFT_DETECTED,
        validation_details={"failed_fields": ["feature_name"]},
        completeness_score=50.0,
        schema_validity_score=100.0,
        stability_score=100.0,
    )
    db_session.add(snapshot)
    await db_session.flush()

    incident = await IncidentService.evaluate_snapshot(db_session, snapshot)
    assert incident is not None
    assert incident.collector_id == collector.id
    assert incident.trigger_run_id == run.id

    # It should have passed through DIAGNOSING, HEAL_PROPOSED, to AWAITING_APPROVAL
    assert incident.status == IncidentStatus.AWAITING_APPROVAL

    # Verify diagnosis provenance
    assert incident.diagnosis is not None
    assert incident.diagnosis["snapshot_id"] == snapshot.id
    assert incident.diagnosis["run_id"] == run.id
    assert incident.diagnosis["failing_fields"] == ["feature_name"]
    assert incident.diagnosis["health_breakdown"]["completeness"] == 50.0
    assert incident.diagnosis["root_cause"] == "DRIFT_DETECTED"

    # Verify HealingEvent
    stmt = select(HealingEvent).where(HealingEvent.incident_id == incident.id)
    result = await db_session.execute(stmt)
    healing_event = result.scalar_one()

    assert healing_event.status == HealingStatus.AWAITING_APPROVAL
    assert healing_event.approval_status == ApprovalStatus.PENDING

    # Verify AuditEvents (INCIDENT_CREATED, INCIDENT_STATE_CHANGED x3, HEALING_EVENT_CREATED)
    stmt_audit = select(AuditEvent).where(
        AuditEvent.related_entity_ref == f"incident:{incident.id}"
    )
    audits = (await db_session.execute(stmt_audit)).scalars().all()

    event_types = [a.event_type for a in audits]
    assert "INCIDENT_CREATED" in event_types
    assert "INCIDENT_STATE_CHANGED" in event_types
    assert len([e for e in event_types if e == "INCIDENT_STATE_CHANGED"]) == 3


@pytest.mark.asyncio
async def test_human_approval_success(db_session: AsyncSession, collector, run):
    """Test the approval path correctly updates the incident and healing event."""
    snapshot = Snapshot(
        bright_data_snapshot_id="j_drift_appr",
        collector_id=collector.id,
        run_id=run.id,
        contract_version=1,
        health_score=50.0,
    )
    db_session.add(snapshot)
    await db_session.flush()

    incident = await IncidentService.evaluate_snapshot(db_session, snapshot)

    he = await IncidentService.process_human_approval(db_session, incident.id, approved=True)

    assert incident.status == IncidentStatus.APPROVED
    assert he.status == HealingStatus.APPROVED
    assert he.approval_status == ApprovalStatus.APPROVED

    stmt_audit = select(AuditEvent).where(
        AuditEvent.related_entity_ref == f"incident:{incident.id}",
        AuditEvent.event_type == "HEAL_APPROVED",
    )
    audit = (await db_session.execute(stmt_audit)).scalar_one_or_none()
    assert audit is not None
    assert audit.actor_source == "operator"


@pytest.mark.asyncio
async def test_human_approval_rejection(db_session: AsyncSession, collector, run):
    """Test the rejection path correctly updates the incident and healing event."""
    snapshot = Snapshot(
        bright_data_snapshot_id="j_drift_rej",
        collector_id=collector.id,
        run_id=run.id,
        contract_version=1,
        health_score=50.0,
    )
    db_session.add(snapshot)
    await db_session.flush()

    incident = await IncidentService.evaluate_snapshot(db_session, snapshot)

    he = await IncidentService.process_human_approval(db_session, incident.id, approved=False)

    assert incident.status == IncidentStatus.REJECTED
    assert he.status == HealingStatus.REJECTED
    assert he.approval_status == ApprovalStatus.REJECTED


@pytest.mark.asyncio
async def test_invalid_approval_state(db_session: AsyncSession, collector, run):
    """Test that approving an incident not in AWAITING_APPROVAL fails."""
    incident = Incident(
        collector_id=collector.id, trigger_run_id=run.id, status=IncidentStatus.DRIFT_DETECTED
    )
    db_session.add(incident)
    await db_session.flush()

    with pytest.raises(ValueError, match="must be AWAITING_APPROVAL"):
        await IncidentService.process_human_approval(db_session, incident.id, approved=True)


@pytest.mark.asyncio
async def test_one_active_healing_constraint(db_session: AsyncSession, collector, run):
    """Test that only one active healing event can exist per incident."""
    incident = Incident(
        collector_id=collector.id, trigger_run_id=run.id, status=IncidentStatus.AWAITING_APPROVAL
    )
    db_session.add(incident)
    await db_session.flush()

    he1 = HealingEvent(
        incident_id=incident.id,
        status=HealingStatus.AWAITING_APPROVAL,
        approval_status=ApprovalStatus.PENDING,
    )
    db_session.add(he1)
    await db_session.flush()

    he2 = HealingEvent(
        incident_id=incident.id,
        status=HealingStatus.PROPOSED,
        approval_status=ApprovalStatus.PENDING,
    )
    db_session.add(he2)

    # This should trigger a unique constraint violation on flush
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_transaction_rollback_preserves_state(db_session: AsyncSession, collector, run):
    """Test that if diagnosis fails partway through, the transaction can be rolled back safely."""
    incident = Incident(
        collector_id=collector.id,
        trigger_run_id=run.id,
        status=IncidentStatus.APPROVED,  # Invalid state for diagnosis
    )
    db_session.add(incident)
    await db_session.flush()

    snapshot = Snapshot(
        bright_data_snapshot_id="j_rollback_test",
        collector_id=collector.id,
        run_id=run.id,
        contract_version=1,
        health_score=50.0,
    )
    db_session.add(snapshot)
    await db_session.flush()

    with pytest.raises(ValueError, match="Cannot diagnose incident in state"):
        await DiagnosisService.diagnose_incident(db_session, incident, snapshot)

    # Incident status should still be APPROVED
    assert incident.status == IncidentStatus.APPROVED
