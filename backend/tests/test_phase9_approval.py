import contextlib
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.main import app
from app.models.audit_event import AuditEvent
from app.models.collector import Collector
from app.models.healing_event import ApprovalStatus, HealingEvent, HealingStatus
from app.models.incident import Incident, IncidentStatus
from app.models.job import Job, JobOperationType, JobStatus
from app.models.run import Run
from app.services.brightdata_service import BrightDataServiceError
from app.workers.approve_worker import process_approve_job


@pytest_asyncio.fixture
async def collector(db_session: AsyncSession):
    c = Collector(bright_data_collector_id="c_test_approve", current_contract_version=1)
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
async def incident_awaiting(db_session: AsyncSession, collector, run):
    incident = Incident(
        collector_id=collector.id,
        trigger_run_id=run.id,
        status=IncidentStatus.AWAITING_APPROVAL,
    )
    db_session.add(incident)
    await db_session.flush()

    he = HealingEvent(
        incident_id=incident.id,
        status=HealingStatus.AWAITING_APPROVAL,
        approval_status=ApprovalStatus.PENDING,
        proposal={"steps": ["add selector"]},
    )
    db_session.add(he)
    await db_session.commit()
    await db_session.refresh(incident)
    return incident


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    app.dependency_overrides[get_session] = lambda: db_session
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def mock_session_factory(db_session):
    @contextlib.asynccontextmanager
    async def _mock_factory():
        yield db_session

    return _mock_factory


@pytest.mark.asyncio
async def test_api_approve_missing_incident(async_client: AsyncClient):
    response = await async_client.post("/api/incidents/999999/approve", json={"approved": True})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_api_approve_invalid_state(
    async_client: AsyncClient, db_session: AsyncSession, incident_awaiting
):
    incident_awaiting.status = IncidentStatus.DIAGNOSING
    await db_session.commit()

    response = await async_client.post(
        f"/api/incidents/{incident_awaiting.id}/approve", json={"approved": True}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_api_approve_reject(
    async_client: AsyncClient, db_session: AsyncSession, incident_awaiting
):
    response = await async_client.post(
        f"/api/incidents/{incident_awaiting.id}/approve", json={"approved": False}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "REJECTED"

    await db_session.refresh(incident_awaiting)
    assert incident_awaiting.status == IncidentStatus.REJECTED

    stmt = select(HealingEvent).where(HealingEvent.incident_id == incident_awaiting.id)
    he = (await db_session.execute(stmt)).scalar_one()
    assert he.status == HealingStatus.REJECTED
    assert he.approval_status == ApprovalStatus.REJECTED


@pytest.mark.asyncio
async def test_api_approve_success(
    async_client: AsyncClient, db_session: AsyncSession, incident_awaiting
):
    response = await async_client.post(
        f"/api/incidents/{incident_awaiting.id}/approve", json={"approved": True}
    )
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "QUEUED"

    await db_session.refresh(incident_awaiting)
    assert incident_awaiting.status == IncidentStatus.APPROVED

    stmt = select(HealingEvent).where(HealingEvent.incident_id == incident_awaiting.id)
    he = (await db_session.execute(stmt)).scalar_one()
    assert he.status == HealingStatus.APPROVED
    assert he.approval_status == ApprovalStatus.APPROVED


@pytest.mark.asyncio
async def test_worker_success(db_session: AsyncSession, incident_awaiting, mock_session_factory):
    # Transition manually as the API would
    incident_awaiting.status = IncidentStatus.APPROVED
    stmt = select(HealingEvent).where(HealingEvent.incident_id == incident_awaiting.id)
    he = (await db_session.execute(stmt)).scalar_one()
    he.status = HealingStatus.APPROVED
    he.approval_status = ApprovalStatus.APPROVED
    await db_session.commit()

    job = Job(
        operation_type=JobOperationType.HEAL_APPROVE,
        related_entity_ref=f"incident:{incident_awaiting.id}",
        status=JobStatus.QUEUED,
    )
    db_session.add(job)
    await db_session.commit()

    # Mock approval and run_collector
    with (
        patch("app.services.brightdata_service.BrightDataService.approve_heal") as mock_approve,
        patch("app.services.brightdata_service.BrightDataService.run_collector") as mock_run,
        patch("app.workers.approve_worker.async_session_factory", side_effect=mock_session_factory),
        patch("app.workers.approve_worker.process_payload") as mock_process,
    ):
        # Setup mock process_payload return for strict recovery criteria
        mock_validation = MagicMock()
        mock_validation.health_score = 95.0
        mock_validation.schema_validity_score = 100.0
        mock_validation.stability_score = 95.0
        mock_validation.completeness_score = 100.0
        mock_validation.validation_state = "HEALTHY"
        mock_validation.normalized_payload = [{"price": 10.0}]
        mock_validation.model_dump.return_value = {}
        mock_process.return_value = mock_validation

        mock_run.return_value = ("snap_123", [{"price": 10.0}])

        await process_approve_job(job.id)

        mock_approve.assert_called_once_with("c_test_approve")
        mock_run.assert_called_once()

    await db_session.refresh(job)
    await db_session.refresh(incident_awaiting)
    await db_session.refresh(he)

    assert job.status == JobStatus.SUCCEEDED
    assert incident_awaiting.status == IncidentStatus.RECOVERED
    assert he.status == HealingStatus.RECOVERED
    assert he.verification_run_id is not None


@pytest.mark.asyncio
async def test_worker_approval_failure(
    db_session: AsyncSession, incident_awaiting, mock_session_factory
):
    incident_awaiting.status = IncidentStatus.APPROVED
    stmt = select(HealingEvent).where(HealingEvent.incident_id == incident_awaiting.id)
    he = (await db_session.execute(stmt)).scalar_one()
    he.status = HealingStatus.APPROVED
    he.approval_status = ApprovalStatus.APPROVED
    await db_session.commit()

    job = Job(
        operation_type=JobOperationType.HEAL_APPROVE,
        related_entity_ref=f"incident:{incident_awaiting.id}",
        status=JobStatus.QUEUED,
    )
    db_session.add(job)
    await db_session.commit()

    with (
        patch(
            "app.services.brightdata_service.BrightDataService.approve_heal",
            side_effect=BrightDataServiceError("Approval failed", "ERR_CLI_FAILED", False),
        ),
        patch("app.workers.approve_worker.async_session_factory", side_effect=mock_session_factory),
    ):
        await process_approve_job(job.id)

    await db_session.refresh(job)
    await db_session.refresh(incident_awaiting)
    await db_session.refresh(he)

    assert job.status == JobStatus.FAILED
    assert incident_awaiting.status == IncidentStatus.MANUAL_INTERVENTION
    assert he.status == HealingStatus.FAILED

    stmt_audit = (
        select(AuditEvent)
        .where(
            AuditEvent.related_entity_ref == f"incident:{incident_awaiting.id}",
            AuditEvent.event_type == "INCIDENT_STATE_CHANGED",
        )
        .order_by(AuditEvent.id.desc())
    )
    latest_audit = (await db_session.execute(stmt_audit)).scalars().first()
    assert latest_audit.metadata_json["new_state"] == "MANUAL_INTERVENTION"


@pytest.mark.asyncio
async def test_worker_criteria_failure(
    db_session: AsyncSession, incident_awaiting, mock_session_factory
):
    incident_awaiting.status = IncidentStatus.APPROVED
    stmt = select(HealingEvent).where(HealingEvent.incident_id == incident_awaiting.id)
    he = (await db_session.execute(stmt)).scalar_one()
    he.status = HealingStatus.APPROVED
    he.approval_status = ApprovalStatus.APPROVED
    await db_session.commit()

    job = Job(
        operation_type=JobOperationType.HEAL_APPROVE,
        related_entity_ref=f"incident:{incident_awaiting.id}",
        status=JobStatus.QUEUED,
    )
    db_session.add(job)
    await db_session.commit()

    with (
        patch("app.services.brightdata_service.BrightDataService.approve_heal"),
        patch("app.services.brightdata_service.BrightDataService.run_collector") as mock_run,
        patch("app.workers.approve_worker.async_session_factory", side_effect=mock_session_factory),
        patch("app.workers.approve_worker.process_payload") as mock_process,
    ):
        # Setup mock process_payload return for failing recovery criteria (schema < 100)
        mock_validation = MagicMock()
        mock_validation.health_score = 95.0
        mock_validation.schema_validity_score = 90.0  # Fails strict 100% check
        mock_validation.stability_score = 95.0
        mock_validation.completeness_score = 100.0
        mock_validation.validation_state = "DEGRADED"
        mock_validation.normalized_payload = [{"price": 10.0}]
        mock_validation.model_dump.return_value = {}
        mock_process.return_value = mock_validation

        mock_run.return_value = ("snap_123", [{"price": 10.0}])

        await process_approve_job(job.id)

    await db_session.refresh(job)
    await db_session.refresh(incident_awaiting)
    await db_session.refresh(he)

    assert job.status == JobStatus.FAILED
    assert incident_awaiting.status == IncidentStatus.MANUAL_INTERVENTION
    assert he.status == HealingStatus.FAILED
