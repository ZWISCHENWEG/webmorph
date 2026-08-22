import contextlib
import json
from unittest.mock import patch

import pytest
from sqlalchemy import select

from app.config import settings
from app.models.collector import Collector, CollectorState
from app.models.job import Job, JobOperationType, JobStatus
from app.models.snapshot import Snapshot, ValidationState
from app.workers.run_worker import _apply_demo_mutation, process_collection_job


@pytest.fixture
def baseline_payload():
    with open("../caniuse-baseline.json") as f:
        return json.load(f)


@pytest.fixture
def mock_session_factory(db_session):
    @contextlib.asynccontextmanager
    async def _mock_factory():
        yield db_session

    return _mock_factory


def test_mutation_helper_disabled_behavior():
    # Direct test of the helper to ensure it's safe
    payload = [{"feature_name": "Test", "browser_support": [{"browser_name": "Chrome"}]}]
    mutated = _apply_demo_mutation(payload)
    assert "browser_support" not in mutated[0]
    assert "feature_name" in mutated[0]


def test_mutation_helper_empty_payload():
    # Edge case: Empty payload
    mutated = _apply_demo_mutation([])
    assert mutated == []


def test_mutation_helper_determinism(baseline_payload):
    # Determinism: same input gives same output
    mutated1 = _apply_demo_mutation(baseline_payload)
    mutated2 = _apply_demo_mutation(baseline_payload)
    assert mutated1 == mutated2


@pytest.mark.asyncio
@patch("app.workers.run_worker.BrightDataService.run_collector")
async def test_demo_mode_disabled(
    mock_run_collector, db_session, mock_session_factory, baseline_payload
):
    with patch("app.workers.run_worker.async_session_factory", side_effect=mock_session_factory):
        # Disabled mode
        settings.demo_mode = False

        mock_run_collector.return_value = ("j_demo_123", baseline_payload)

        collector = Collector(
            bright_data_collector_id="c_test_disabled",
            state=CollectorState.HEALTHY,
            current_contract_version=1,
        )
        db_session.add(collector)
        await db_session.commit()

        job = Job(
            operation_type=JobOperationType.COLLECTION,
            related_entity_ref=f"collector:{collector.id}",
            status=JobStatus.QUEUED,
        )
        db_session.add(job)
        await db_session.commit()

        await process_collection_job(job.id)
        await db_session.refresh(job)
        print(f"DEBUG JOB STATUS: {job.status}, {job.error_message}")

        stmt = (
            select(Snapshot)
            .where(Snapshot.collector_id == collector.id)
            .order_by(Snapshot.id.desc())
        )
        snapshot = (await db_session.scalars(stmt)).first()

        # In disabled mode, payload should remain unchanged
        assert "browser_support" in snapshot.raw_payload[0]
        assert snapshot.validation_state == ValidationState.HEALTHY


@pytest.mark.asyncio
@patch("app.workers.run_worker.BrightDataService.run_collector")
async def test_demo_mode_enabled(
    mock_run_collector, db_session, mock_session_factory, baseline_payload
):
    with patch("app.workers.run_worker.async_session_factory", side_effect=mock_session_factory):
        # Enabled mode
        settings.demo_mode = True

        mock_run_collector.return_value = ("j_demo_456", baseline_payload)

        collector = Collector(
            bright_data_collector_id="c_test_enabled",
            state=CollectorState.HEALTHY,
            current_contract_version=1,
        )
        db_session.add(collector)
        await db_session.commit()

        job = Job(
            operation_type=JobOperationType.COLLECTION,
            related_entity_ref=f"collector:{collector.id}",
            status=JobStatus.QUEUED,
        )
        db_session.add(job)
        await db_session.commit()

        await process_collection_job(job.id)
        await db_session.refresh(job)
        print(f"DEBUG JOB STATUS: {job.status}, {job.error_message}")

        # Reset
        settings.demo_mode = False

        stmt = (
            select(Snapshot)
            .where(Snapshot.collector_id == collector.id)
            .order_by(Snapshot.id.desc())
        )
        snapshot = (await db_session.scalars(stmt)).first()

        # 2. Enabled mode: first record's browser_support is removed
        assert "browser_support" not in snapshot.raw_payload[0]

        # 4. Snapshot authenticity: real snapshot_id returned by BrightDataService remains unchanged
        assert snapshot.bright_data_snapshot_id == "j_demo_456"

        # 5. Bright Data authenticity: execution is actually invoked
        mock_run_collector.assert_called_once()

        # 6. Pipeline integration: mutated payload is passed to process_payload, dropping health

        assert snapshot.validation_state == ValidationState.DRIFT_DETECTED
        assert snapshot.health_score < 80

        # Collector state reflects it
        await db_session.refresh(collector)
        assert collector.state == CollectorState.DRIFT_DETECTED

        # 7. Pipeline integration: Incident created and transitioned to DIAGNOSING
        from app.models.incident import Incident, IncidentStatus

        stmt_inc = select(Incident).where(Incident.collector_id == collector.id)
        incident = (await db_session.scalars(stmt_inc)).first()
        assert incident is not None, "Incident was not created by the worker pipeline"
        assert incident.status == IncidentStatus.DIAGNOSING
