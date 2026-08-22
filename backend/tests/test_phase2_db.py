import pytest
from sqlalchemy import exc

from app.models.collector import Collector
from app.models.healing_event import HealingEvent, HealingStatus
from app.models.incident import Incident, IncidentStatus
from app.models.run import Run
from app.models.snapshot import Snapshot, ValidationState


@pytest.mark.asyncio
async def test_collector_and_snapshot_creation(db_session):
    collector = Collector(bright_data_collector_id="c_test_123")
    db_session.add(collector)
    await db_session.commit()

    # Create run
    run = Run(collector_id=collector.id, contract_version=1)
    db_session.add(run)
    await db_session.commit()

    # Create snapshot
    snapshot = Snapshot(
        bright_data_snapshot_id="j_test_abc",
        collector_id=collector.id,
        run_id=run.id,
        contract_version=1,
        raw_payload={},
        normalized_payload={},
        record_count=10,
        validation_state=ValidationState.PENDING,
        health_score=100
    )
    db_session.add(snapshot)
    await db_session.commit()

    assert snapshot.id is not None

    # Idempotency constraint test
    snapshot2 = Snapshot(
        bright_data_snapshot_id="j_test_abc",
        collector_id=collector.id,
        run_id=run.id,
        contract_version=1,
        raw_payload={},
        normalized_payload={},
        record_count=10,
        validation_state=ValidationState.PENDING,
        health_score=100
    )
    db_session.add(snapshot2)
    with pytest.raises(exc.IntegrityError):
        await db_session.commit()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_healing_event_unique_active_constraint(db_session):
    collector = Collector(bright_data_collector_id="c_test_456")
    db_session.add(collector)
    await db_session.commit()

    run = Run(collector_id=collector.id, contract_version=1)
    db_session.add(run)
    await db_session.commit()

    incident = Incident(
        collector_id=collector.id, 
        trigger_run_id=run.id,
        status=IncidentStatus.DRIFT_DETECTED
    )
    db_session.add(incident)
    await db_session.commit()

    h1 = HealingEvent(
        incident_id=incident.id,
        status=HealingStatus.PROPOSED
    )
    db_session.add(h1)
    await db_session.commit()

    inc_id = incident.id

    h2 = HealingEvent(
        incident_id=inc_id,
        status=HealingStatus.AWAITING_APPROVAL
    )
    db_session.add(h2)
    with pytest.raises(exc.IntegrityError):
        await db_session.commit()
    await db_session.rollback()

    # terminal state doesn't block another active event
    h1.status = HealingStatus.FAILED
    db_session.add(h1)
    await db_session.commit()

    h3 = HealingEvent(
        incident_id=inc_id,
        status=HealingStatus.PROPOSED
    )
    db_session.add(h3)
    await db_session.commit()
    assert h3.id is not None
