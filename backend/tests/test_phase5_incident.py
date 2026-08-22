from unittest.mock import patch

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
from app.services.incident_service import AuditEventService, DiagnosisService, IncidentService


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
        validation_details={
            "missing_fields": ["feature_name"],
            "schema_errors": [],
            "stability_issues": [],
        },
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
    assert incident.diagnosis["missing_fields"] == ["feature_name"]
    assert incident.diagnosis["schema_errors"] == []
    assert incident.diagnosis["stability_issues"] == []
    assert incident.diagnosis["health_breakdown"]["completeness"] == 50.0
    assert incident.diagnosis["root_cause"] == "DRIFT_DETECTED"

    # Verify HealingEvent
    stmt = select(HealingEvent).where(HealingEvent.incident_id == incident.id)
    result = await db_session.execute(stmt)
    healing_event = result.scalar_one()

    assert healing_event.status == HealingStatus.AWAITING_APPROVAL
    assert healing_event.approval_status == ApprovalStatus.PENDING

    # Verify AuditEvents
    # (INCIDENT_CREATED, INCIDENT_STATE_CHANGED x4,
    # HEALING_EVENT_CREATED, HEALING_EVENT_STATE_CHANGED)
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

    # Verify AuditEvents order and metadata
    stmt_audit_all = (
        select(AuditEvent)
        .where(
            (AuditEvent.related_entity_ref == f"incident:{incident.id}")
            | (AuditEvent.related_entity_ref == f"healing_event:{he.id}")
        )
        .order_by(AuditEvent.id)
    )
    audits_all = (await db_session.execute(stmt_audit_all)).scalars().all()

    # Expected chronological flow:
    # 1. INCIDENT_CREATED (evaluate_snapshot)
    # 2. INCIDENT_STATE_CHANGED -> DIAGNOSING (diagnose_incident)
    # 3. INCIDENT_STATE_CHANGED -> HEAL_PROPOSED (diagnose_incident)
    # 4. HEALING_EVENT_CREATED -> PROPOSED (diagnose_incident)
    # 5. INCIDENT_STATE_CHANGED -> AWAITING_APPROVAL (diagnose_incident)
    # 6. HEALING_EVENT_STATE_CHANGED -> AWAITING_APPROVAL (diagnose_incident)
    # 7. INCIDENT_STATE_CHANGED -> APPROVED (process_human_approval)
    # 8. HEALING_EVENT_STATE_CHANGED -> APPROVED (process_human_approval)

    event_list = [
        (a.event_type, a.metadata_json.get("new_state", a.metadata_json.get("status")))
        for a in audits_all
        if a.metadata_json
    ]

    assert event_list[0][0] == "INCIDENT_CREATED"
    assert event_list[1] == ("INCIDENT_STATE_CHANGED", IncidentStatus.DIAGNOSING.value)
    assert event_list[2] == ("INCIDENT_STATE_CHANGED", IncidentStatus.HEAL_PROPOSED.value)
    assert event_list[3] == ("HEALING_EVENT_CREATED", HealingStatus.PROPOSED.value)
    assert event_list[4] == ("INCIDENT_STATE_CHANGED", IncidentStatus.AWAITING_APPROVAL.value)
    assert event_list[5] == ("HEALING_EVENT_STATE_CHANGED", HealingStatus.AWAITING_APPROVAL.value)
    assert event_list[6] == ("INCIDENT_STATE_CHANGED", IncidentStatus.APPROVED.value)
    assert event_list[7] == ("HEALING_EVENT_STATE_CHANGED", HealingStatus.APPROVED.value)

    # Check actor source for approval
    assert audits_all[-1].actor_source == "operator"
    assert audits_all[-2].actor_source == "operator"


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
    """Test that if diagnosis fails partway through, the transaction is completely rolled back."""
    incident = Incident(
        collector_id=collector.id,
        trigger_run_id=run.id,
        status=IncidentStatus.DRIFT_DETECTED,
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

    # We will mock log_event to fail on the third call (which is HEAL_PROPOSED transition)
    # The first call is INCIDENT_STATE_CHANGED (DIAGNOSING)
    # By failing on the third call, we prove partial DB state is rolled back.
    call_count = 0
    original_log_event = AuditEventService.log_event

    async def mock_log_event(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise RuntimeError("Injected database failure")
        return await original_log_event(*args, **kwargs)

    incident_id = incident.id
    
    with (
        patch.object(AuditEventService, "log_event", side_effect=mock_log_event),
        pytest.raises(RuntimeError, match="Injected database failure"),
    ):
        async with db_session.begin_nested():
            await DiagnosisService.diagnose_incident(db_session, incident, snapshot)
    
    # Expunge to ensure we read from DB, not the session identity map
    db_session.expunge_all()

    # In a new context, verify state using a fresh query
    stmt_inc = select(Incident).where(Incident.id == incident_id)
    refreshed_incident = (await db_session.execute(stmt_inc)).scalar_one()

    # Incident status should be back to DRIFT_DETECTED, not DIAGNOSING
    assert refreshed_incident.status == IncidentStatus.DRIFT_DETECTED
    assert refreshed_incident.diagnosis is None

    # Check that NO HealingEvent was created
    stmt_he = select(HealingEvent).where(HealingEvent.incident_id == incident_id)
    he = (await db_session.execute(stmt_he)).scalar_one_or_none()
    assert he is None
    
    # Check that NO AuditEvents for DIAGNOSING remain
    stmt_aud = select(AuditEvent).where(AuditEvent.related_entity_ref == f"incident:{incident_id}")
    auds = (await db_session.execute(stmt_aud)).scalars().all()
    assert len(auds) == 0


@pytest.mark.asyncio
async def test_invalid_transition_states(db_session: AsyncSession, collector, run):
    """Test explicit state guards and invalid initial states."""
    incident = Incident(
        collector_id=collector.id,
        trigger_run_id=run.id,
        status=IncidentStatus.DRIFT_DETECTED,
    )
    db_session.add(incident)
    await db_session.flush()

    snapshot = Snapshot(
        bright_data_snapshot_id="j_guard_test",
        collector_id=collector.id,
        run_id=run.id,
        contract_version=1,
        health_score=50.0,
    )
    db_session.add(snapshot)
    await db_session.flush()

    # Try diagnosing an incident that's not in DRIFT_DETECTED
    incident.status = IncidentStatus.DIAGNOSING
    await db_session.flush()

    with pytest.raises(ValueError, match="Cannot diagnose incident in state"):
        await DiagnosisService.diagnose_incident(db_session, incident, snapshot)

    incident.status = IncidentStatus.HEAL_PROPOSED
    await db_session.flush()

    with pytest.raises(ValueError, match="Cannot diagnose incident in state"):
        await DiagnosisService.diagnose_incident(db_session, incident, snapshot)
