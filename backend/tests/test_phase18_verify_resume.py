import contextlib
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.main import app
from app.models.collector import Collector
from app.models.healing_event import ApprovalStatus, HealingEvent, HealingStatus
from app.models.incident import Incident, IncidentStatus
from app.models.job import Job, JobOperationType, JobStatus
from app.models.run import Run
from app.models.snapshot import ValidationState
from app.workers.verify_worker import process_verify_job


@pytest_asyncio.fixture
async def collector(db_session: AsyncSession):
    c = Collector(bright_data_collector_id="c_test_verify", current_contract_version=1)
    db_session.add(c)
    await db_session.flush()
    return c


@pytest_asyncio.fixture
async def run(db_session: AsyncSession, collector):
    r = Run(collector_id=collector.id, contract_version=1)
    db_session.add(r)
    await db_session.flush()
    return r


@pytest_asyncio.fixture
async def incident_verifying(db_session: AsyncSession, collector, run):
    # Setup incident in VERIFYING state
    inc = Incident(
        collector_id=collector.id,
        trigger_run_id=run.id,
        status=IncidentStatus.VERIFYING,
    )
    db_session.add(inc)
    await db_session.flush()

    # Create approved healing event
    he = HealingEvent(
        incident_id=inc.id,
        status=HealingStatus.VERIFYING,
        approval_status=ApprovalStatus.APPROVED,
        proposal={"test": "proposal"},
    )
    db_session.add(he)
    await db_session.commit()

    return inc


@pytest_asyncio.fixture
async def mock_session_factory(db_session: AsyncSession):
    @contextlib.asynccontextmanager
    async def _mock_factory():
        yield db_session

    return _mock_factory


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    app.dependency_overrides[get_session] = lambda: db_session
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_api_verify_missing_incident(async_client: AsyncClient):
    response = await async_client.post("/api/incidents/9999/verify")

    assert response.status_code == 404
    data = response.json()
    err_code = data.get("detail", {}).get("error", {}).get("code") or data.get("error", {}).get(
        "code"
    )
    assert err_code == "ERR_NOT_FOUND"


@pytest.mark.asyncio
async def test_api_verify_invalid_state(
    async_client: AsyncClient, db_session: AsyncSession, incident_verifying
):
    # Change status to something invalid
    incident_verifying.status = IncidentStatus.APPROVED
    await db_session.commit()

    response = await async_client.post(f"/api/incidents/{incident_verifying.id}/verify")
    print("DEBUG:", response.json())

    assert response.status_code == 400
    data = response.json()
    err_code = data.get("detail", {}).get("error", {}).get("code") or data.get("error", {}).get(
        "code"
    )
    assert err_code in ("ERR_INVALID_STATE", "ERR_HTTP_400")


@pytest.mark.asyncio
async def test_api_verify_duplicate_job(
    async_client: AsyncClient, db_session: AsyncSession, incident_verifying
):
    job = Job(
        operation_type=JobOperationType.VERIFICATION,
        related_entity_ref=f"incident:{incident_verifying.id}",
        status=JobStatus.QUEUED,
    )
    db_session.add(job)
    await db_session.commit()

    response = await async_client.post(f"/api/incidents/{incident_verifying.id}/verify")

    assert response.status_code == 409
    data = response.json()
    err_code = data.get("detail", {}).get("error", {}).get("code") or data.get("error", {}).get(
        "code"
    )
    assert err_code in ("ERR_CONFLICT", "ERR_HTTP_409")


@pytest.mark.asyncio
async def test_api_verify_success(
    async_client: AsyncClient, db_session: AsyncSession, incident_verifying
):
    response = await async_client.post(f"/api/incidents/{incident_verifying.id}/verify")

    assert response.status_code == 202
    data = response.json()
    assert "job_" in data["job_id"]

    # Verify Job is created
    job_id = int(data["job_id"].split("_")[1])
    job = await db_session.get(Job, job_id)
    assert job is not None
    assert job.operation_type == JobOperationType.VERIFICATION


@pytest.mark.asyncio
async def test_worker_success(db_session: AsyncSession, incident_verifying, mock_session_factory):
    job = Job(
        operation_type=JobOperationType.VERIFICATION,
        related_entity_ref=f"incident:{incident_verifying.id}",
        status=JobStatus.QUEUED,
    )
    db_session.add(job)
    await db_session.commit()

    with (
        patch("app.services.brightdata_service.BrightDataService.run_collector") as mock_run,
        patch("app.workers.verify_worker.async_session_factory", side_effect=mock_session_factory),
        patch("app.services.incident_service.process_payload") as mock_process,
    ):
        # Strict recovery criteria: health >= 95, schema == 100, stability >= 90, completeness >= 95
        mock_validation = MagicMock()
        mock_validation.health_score = 96.0
        mock_validation.schema_validity_score = 100.0
        mock_validation.stability_score = 92.0
        mock_validation.completeness_score = 98.0
        mock_validation.validation_state = ValidationState.HEALTHY
        mock_validation.normalized_payload = [{"price": 10.0}]
        mock_validation.is_valid = True
        mock_validation.errors = []
        mock_process.return_value = mock_validation

        mock_run.return_value = ("snap_verify_1", [{"price": 10.0}])

        await process_verify_job(job.id)

    await db_session.refresh(job)
    await db_session.refresh(incident_verifying)
    stmt = select(HealingEvent).where(HealingEvent.incident_id == incident_verifying.id)
    he = (await db_session.scalars(stmt)).first()

    assert job.status == JobStatus.SUCCEEDED
    assert incident_verifying.status == IncidentStatus.RECOVERED
    assert he.status == HealingStatus.RECOVERED


@pytest.mark.asyncio
async def test_worker_criteria_failure(
    db_session: AsyncSession, incident_verifying, mock_session_factory
):
    job = Job(
        operation_type=JobOperationType.VERIFICATION,
        related_entity_ref=f"incident:{incident_verifying.id}",
        status=JobStatus.QUEUED,
    )
    db_session.add(job)
    await db_session.commit()

    with (
        patch("app.services.brightdata_service.BrightDataService.run_collector") as mock_run,
        patch("app.workers.verify_worker.async_session_factory", side_effect=mock_session_factory),
        patch("app.services.incident_service.process_payload") as mock_process,
    ):
        # Failing recovery criteria (schema < 100)
        mock_validation = MagicMock()
        mock_validation.health_score = 96.0
        mock_validation.schema_validity_score = 99.0  # < 100 causes failure
        mock_validation.stability_score = 92.0
        mock_validation.completeness_score = 98.0
        mock_validation.validation_state = ValidationState.INVALID
        mock_validation.normalized_payload = [{"price": 10.0}]
        mock_validation.is_valid = True
        mock_validation.errors = []
        mock_process.return_value = mock_validation

        mock_run.return_value = ("snap_verify_1", [{"price": 10.0}])

        await process_verify_job(job.id)

    await db_session.refresh(job)
    await db_session.refresh(incident_verifying)
    stmt = select(HealingEvent).where(HealingEvent.incident_id == incident_verifying.id)
    he = (await db_session.scalars(stmt)).first()

    assert job.status == JobStatus.FAILED
    assert incident_verifying.status == IncidentStatus.MANUAL_INTERVENTION
    assert he.status == HealingStatus.FAILED


@pytest.mark.asyncio
async def test_worker_invalid_state_rejected(
    db_session: AsyncSession, incident_verifying, mock_session_factory
):
    # Make healing event approval status PENDING (not APPROVED)
    stmt = select(HealingEvent).where(HealingEvent.incident_id == incident_verifying.id)
    he = (await db_session.scalars(stmt)).first()
    he.approval_status = ApprovalStatus.PENDING
    await db_session.commit()

    job = Job(
        operation_type=JobOperationType.VERIFICATION,
        related_entity_ref=f"incident:{incident_verifying.id}",
        status=JobStatus.QUEUED,
    )
    db_session.add(job)
    await db_session.commit()

    with patch("app.workers.verify_worker.async_session_factory", side_effect=mock_session_factory):
        await process_verify_job(job.id)

    await db_session.refresh(job)
    # Should safely fail the job
    assert job.status == JobStatus.FAILED
    assert "approval_status is PENDING, not APPROVED" in job.error_message
