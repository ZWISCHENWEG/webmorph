import contextlib
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select

from app.models.audit_event import AuditEvent
from app.models.collector import Collector, CollectorState
from app.models.healing_event import ApprovalStatus, HealingEvent, HealingStatus
from app.models.incident import Incident, IncidentStatus
from app.models.job import Job, JobOperationType, JobStatus
from app.models.run import Run, RunStatus
from app.services.brightdata_service import BrightDataServiceError
from app.workers.approve_worker import process_approve_job
from app.workers.run_worker import process_collection_job


@pytest.fixture
def mock_session_factory(db_session):
    @contextlib.asynccontextmanager
    async def _mock_factory():
        yield db_session

    return _mock_factory


@pytest.fixture
async def setup_test_data(db_session):
    collector = Collector(
        bright_data_collector_id="c_test_retry",
        state=CollectorState.HEALTHY,
        current_contract_version=1,
    )
    db_session.add(collector)
    await db_session.commit()
    await db_session.refresh(collector)

    run = Run(collector_id=collector.id, contract_version=1, status=RunStatus.SUCCEEDED)
    db_session.add(run)
    await db_session.commit()
    await db_session.refresh(run)

    incident = Incident(
        collector_id=collector.id,
        trigger_run_id=run.id,
        status=IncidentStatus.APPROVED,
        diagnosis={"issue": "test"},
    )
    db_session.add(incident)
    await db_session.commit()
    await db_session.refresh(incident)

    return collector, incident


@pytest.fixture
def mock_sleep():
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock:
        yield mock


@pytest.mark.asyncio
async def test_run_worker_retry_success(
    db_session, setup_test_data, mock_sleep, mock_session_factory
):
    """Test run_worker retries 2 times and succeeds on the 3rd attempt, with exact backoff."""
    collector, _ = setup_test_data
    
    job = Job(
        operation_type=JobOperationType.COLLECTION,
        status=JobStatus.QUEUED,
        related_entity_ref=f"collector:{collector.id}",
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    with patch(
        "app.services.brightdata_service.BrightDataService.run_collector",
        side_effect=[
            BrightDataServiceError("Timeout", code="ERR_CLI_TIMEOUT", retryable=True),
            BrightDataServiceError("Empty", code="ERR_CLI_EMPTY", retryable=True),
            ("j_success_run", [{"url": "http://example.com", "name": "Success"}]),
        ],
    ) as mock_run, patch(
        "app.workers.run_worker.async_session_factory", side_effect=mock_session_factory
    ):
        await process_collection_job(job.id)

    # Verifications
    await db_session.refresh(job)
    assert job.status == JobStatus.SUCCEEDED
    assert job.attempt_count == 3
    
    assert mock_run.call_count == 3
    assert mock_sleep.call_count == 2
    mock_sleep.assert_any_call(2)
    mock_sleep.assert_any_call(4)


@pytest.mark.asyncio
async def test_run_worker_retry_exhausted(
    db_session, setup_test_data, mock_sleep, mock_session_factory
):
    """Test run_worker fails after exhausting 3 attempts."""
    collector, _ = setup_test_data
    
    job = Job(
        operation_type=JobOperationType.COLLECTION,
        status=JobStatus.QUEUED,
        related_entity_ref=f"collector:{collector.id}",
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    with patch(
        "app.services.brightdata_service.BrightDataService.run_collector",
        side_effect=[
            BrightDataServiceError("Timeout", code="ERR_CLI_TIMEOUT", retryable=True),
            BrightDataServiceError("Timeout", code="ERR_CLI_TIMEOUT", retryable=True),
            BrightDataServiceError("Timeout", code="ERR_CLI_TIMEOUT", retryable=True),
        ],
    ) as mock_run, patch(
        "app.workers.run_worker.async_session_factory", side_effect=mock_session_factory
    ):
        await process_collection_job(job.id)

    await db_session.refresh(job)
    assert job.status == JobStatus.FAILED
    assert job.attempt_count == 3
    
    assert mock_run.call_count == 3
    assert mock_sleep.call_count == 2
    
    # AuditEvent should be exactly 1
    stmt = select(AuditEvent).where(AuditEvent.event_type == "RUN_FAILED")
    audits = (await db_session.execute(stmt)).scalars().all()
    assert len(audits) == 1


@pytest.mark.asyncio
async def test_run_worker_non_retryable(
    db_session, setup_test_data, mock_sleep, mock_session_factory
):
    """Test run_worker fails immediately on non-retryable error."""
    collector, _ = setup_test_data
    
    job = Job(
        operation_type=JobOperationType.COLLECTION,
        status=JobStatus.QUEUED,
        related_entity_ref=f"collector:{collector.id}",
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    with patch(
        "app.services.brightdata_service.BrightDataService.run_collector",
        side_effect=BrightDataServiceError("Fatal", code="ERR_CLI_MALFORMED", retryable=False),
    ) as mock_run, patch(
        "app.workers.run_worker.async_session_factory", side_effect=mock_session_factory
    ):
        await process_collection_job(job.id)

    await db_session.refresh(job)
    assert job.status == JobStatus.FAILED
    assert job.attempt_count == 1
    
    assert mock_run.call_count == 1
    assert mock_sleep.call_count == 0


@pytest.mark.asyncio
async def test_approve_worker_approval_non_retryable(
    db_session, setup_test_data, mock_sleep, mock_session_factory
):
    """Test approve_worker does not retry approval even if retryable."""
    collector, incident = setup_test_data
    
    incident.status = IncidentStatus.APPROVED
    db_session.add(incident)
    
    healing_event = HealingEvent(
        incident_id=incident.id,
        status=HealingStatus.APPROVED,
        approval_status=ApprovalStatus.APPROVED,
        proposal="Fix XYZ"
    )
    db_session.add(healing_event)
    
    job = Job(
        operation_type=JobOperationType.HEAL_APPROVE,
        status=JobStatus.QUEUED,
        related_entity_ref=f"incident:{incident.id}",
        max_attempts=4,
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    with patch(
        "app.services.brightdata_service.BrightDataService.approve_heal",
        side_effect=BrightDataServiceError("Timeout", code="ERR_CLI_TIMEOUT", retryable=True),
    ) as mock_approve, patch(
        "app.workers.approve_worker.async_session_factory", side_effect=mock_session_factory
    ):
        await process_approve_job(job.id)

    await db_session.refresh(job)
    assert job.status == JobStatus.FAILED
    assert job.attempt_count == 1  # Exactly 1 physical execution
    
    assert mock_approve.call_count == 1
    assert mock_sleep.call_count == 0


@pytest.mark.asyncio
async def test_approve_worker_composite_exhaustion(
    db_session, setup_test_data, mock_sleep, mock_session_factory
):
    """
    Test approve_worker executes approval 1 time,
    then exhausts verification 3 times -> attempt_count = 4.
    """
    collector, incident = setup_test_data
    
    incident.status = IncidentStatus.APPROVED
    db_session.add(incident)
    
    healing_event = HealingEvent(
        incident_id=incident.id,
        status=HealingStatus.APPROVED,
        approval_status=ApprovalStatus.APPROVED,
        proposal="Fix XYZ"
    )
    db_session.add(healing_event)
    
    job = Job(
        operation_type=JobOperationType.HEAL_APPROVE,
        status=JobStatus.QUEUED,
        related_entity_ref=f"incident:{incident.id}",
        max_attempts=4,
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    with patch(
        "app.services.brightdata_service.BrightDataService.approve_heal",
    ) as mock_approve, patch(
        "app.services.brightdata_service.BrightDataService.run_collector",
        side_effect=[
            BrightDataServiceError("Timeout", code="ERR_CLI_TIMEOUT", retryable=True),
            BrightDataServiceError("Timeout", code="ERR_CLI_TIMEOUT", retryable=True),
            BrightDataServiceError("Timeout", code="ERR_CLI_TIMEOUT", retryable=True),
        ],
    ) as mock_run, patch(
        "app.workers.approve_worker.async_session_factory", side_effect=mock_session_factory
    ):
        await process_approve_job(job.id)

    await db_session.refresh(job)
    assert job.status == JobStatus.FAILED
    assert job.attempt_count == 4  # 1 approval + 3 verifications
    
    assert mock_approve.call_count == 1
    assert mock_run.call_count == 3
    assert mock_sleep.call_count == 2
    mock_sleep.assert_any_call(2)
    mock_sleep.assert_any_call(4)
