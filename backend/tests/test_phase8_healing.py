import contextlib
from unittest.mock import AsyncMock, MagicMock, patch

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
from app.workers.heal_worker import process_heal_job


@pytest_asyncio.fixture
async def collector(db_session: AsyncSession):
    c = Collector(bright_data_collector_id="c_test_heal")
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
async def incident_diagnosing(db_session: AsyncSession, collector, run):
    incident = Incident(
        collector_id=collector.id,
        trigger_run_id=run.id,
        status=IncidentStatus.DIAGNOSING,
        diagnosis={
            "missing_fields": ["price"],
            "schema_errors": [{"loc": ["rating"], "msg": "not a float"}],
            "stability_issues": ["record count dropped"],
        },
    )
    db_session.add(incident)
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
async def test_api_missing_incident(async_client: AsyncClient):
    response = await async_client.post("/api/incidents/999999/heal")
    assert response.status_code == 404
    data = response.json()
    err_code = data.get("detail", {}).get("error", {}).get("code") or data.get("error", {}).get(
        "code"
    )
    assert err_code == "ERR_NOT_FOUND"


@pytest.mark.asyncio
async def test_api_invalid_state(
    async_client: AsyncClient, db_session: AsyncSession, incident_diagnosing
):
    incident_diagnosing.status = IncidentStatus.APPROVED
    await db_session.commit()

    response = await async_client.post(f"/api/incidents/{incident_diagnosing.id}/heal")
    assert response.status_code == 400
    data = response.json()
    err_code = data.get("detail", {}).get("error", {}).get("code") or data.get("error", {}).get(
        "code"
    )
    assert err_code == "ERR_HTTP_400"


@pytest.mark.asyncio
async def test_api_duplicate_protection_job(
    async_client: AsyncClient, db_session: AsyncSession, incident_diagnosing
):
    job = Job(
        operation_type=JobOperationType.HEAL_REQUEST,
        related_entity_ref=f"incident:{incident_diagnosing.id}",
        status=JobStatus.QUEUED,
    )
    db_session.add(job)
    await db_session.commit()

    response = await async_client.post(f"/api/incidents/{incident_diagnosing.id}/heal")
    assert response.status_code == 409
    data = response.json()
    err_code = data.get("detail", {}).get("error", {}).get("code") or data.get("error", {}).get(
        "code"
    )
    assert err_code == "ERR_HTTP_409"


@pytest.mark.asyncio
async def test_api_duplicate_protection_healing_event(
    async_client: AsyncClient, db_session: AsyncSession, incident_diagnosing
):
    he = HealingEvent(incident_id=incident_diagnosing.id, status=HealingStatus.PROPOSED)
    db_session.add(he)
    await db_session.commit()

    response = await async_client.post(f"/api/incidents/{incident_diagnosing.id}/heal")
    assert response.status_code == 409
    data = response.json()
    err_code = data.get("detail", {}).get("error", {}).get("code") or data.get("error", {}).get(
        "code"
    )
    assert err_code == "ERR_HTTP_409"


@pytest.mark.asyncio
async def test_api_success_queue(
    async_client: AsyncClient, db_session: AsyncSession, incident_diagnosing
):
    response = await async_client.post(f"/api/incidents/{incident_diagnosing.id}/heal")
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["job_id"].startswith("job_")
    assert data["status"] == "QUEUED"

    # Verify Job is created in DB
    job_id = int(data["job_id"][4:])
    job = await db_session.get(Job, job_id)
    assert job is not None
    assert job.status == JobStatus.QUEUED
    assert job.operation_type == JobOperationType.HEAL_REQUEST
    assert job.related_entity_ref == f"incident:{incident_diagnosing.id}"


@pytest.mark.asyncio
async def test_worker_success(db_session: AsyncSession, incident_diagnosing, mock_session_factory):
    # Setup job
    job = Job(
        operation_type=JobOperationType.HEAL_REQUEST,
        related_entity_ref=f"incident:{incident_diagnosing.id}",
        status=JobStatus.QUEUED,
    )
    db_session.add(job)
    await db_session.commit()

    mock_proposal = {"steps": ["add selector"], "confidence": 0.95}

    with patch(
        "app.services.brightdata_service.BrightDataService.request_heal", return_value=mock_proposal
    ) as mock_req:
        with patch(
            "app.workers.heal_worker.async_session_factory", side_effect=mock_session_factory
        ):
            await process_heal_job(job.id)

        mock_req.assert_called_once()
        args, kwargs = mock_req.call_args
        # collector_id
        assert args[0] == "c_test_heal"
        # what_broke string check
        what_broke = args[1]
        assert "Missing fields: price" in what_broke
        assert "Schema errors: not a float" in what_broke
        assert "Stability issues: record count dropped" in what_broke

    await db_session.refresh(job)
    await db_session.refresh(incident_diagnosing)

    assert job.status == JobStatus.SUCCEEDED
    assert incident_diagnosing.status == IncidentStatus.AWAITING_APPROVAL

    # Verify HealingEvent created
    stmt = select(HealingEvent).where(HealingEvent.incident_id == incident_diagnosing.id)
    he = (await db_session.execute(stmt)).scalar_one()
    assert he.status == HealingStatus.AWAITING_APPROVAL
    assert he.approval_status == ApprovalStatus.PENDING
    assert he.proposal == mock_proposal

    # Verify Audit Events
    stmt_audit = select(AuditEvent).where(
        AuditEvent.related_entity_ref.in_(
            [f"incident:{incident_diagnosing.id}", f"healing_event:{he.id}"]
        )
    )
    audits = (await db_session.execute(stmt_audit)).scalars().all()
    event_types = [a.event_type for a in audits]

    # 2 incident state changes, 1 HE creation, 1 HE state change
    assert "HEALING_EVENT_CREATED" in event_types
    assert "HEALING_EVENT_STATE_CHANGED" in event_types
    assert event_types.count("INCIDENT_STATE_CHANGED") >= 2


@pytest.mark.asyncio
async def test_worker_cli_failure(
    db_session: AsyncSession, incident_diagnosing, mock_session_factory
):
    job = Job(
        operation_type=JobOperationType.HEAL_REQUEST,
        related_entity_ref=f"incident:{incident_diagnosing.id}",
        status=JobStatus.QUEUED,
    )
    db_session.add(job)
    await db_session.commit()

    with (
        patch(
            "app.services.brightdata_service.BrightDataService.request_heal",
            side_effect=BrightDataServiceError("Timeout", "ERR_CLI_TIMEOUT", True),
        ),
        patch("app.workers.heal_worker.async_session_factory", side_effect=mock_session_factory),
    ):
        await process_heal_job(job.id)

    await db_session.refresh(job)
    await db_session.refresh(incident_diagnosing)

    assert job.status == JobStatus.FAILED
    assert job.error_message == "Timeout"
    assert incident_diagnosing.status == IncidentStatus.DIAGNOSING

    stmt = select(HealingEvent).where(HealingEvent.incident_id == incident_diagnosing.id)
    he = (await db_session.execute(stmt)).scalar_one_or_none()
    assert he is None


@pytest.mark.asyncio
async def test_worker_db_failure_rollback(
    db_session: AsyncSession, incident_diagnosing, mock_session_factory
):
    incident_id = incident_diagnosing.id
    job = Job(
        operation_type=JobOperationType.HEAL_REQUEST,
        related_entity_ref=f"incident:{incident_id}",
        status=JobStatus.QUEUED,
    )
    db_session.add(job)
    await db_session.commit()

    mock_proposal = {"steps": ["add selector"], "confidence": 0.95}

    call_count = 0
    from app.services.incident_service import AuditEventService

    original_log = AuditEventService.log_event

    async def mock_log(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise RuntimeError("Injected DB error")
        return await original_log(*args, **kwargs)

    with patch(
        "app.services.brightdata_service.BrightDataService.request_heal", return_value=mock_proposal
    ):
        with (
            patch.object(AuditEventService, "log_event", side_effect=mock_log),
            patch(
                "app.workers.heal_worker.async_session_factory", side_effect=mock_session_factory
            ),
        ):
            await process_heal_job(job.id)

        db_session.expunge_all()

        job_reloaded = await db_session.get(Job, job.id)
        assert job_reloaded.status == JobStatus.FAILED
        assert "Injected DB error" in job_reloaded.error_message

        inc_reloaded = await db_session.get(Incident, incident_id)
        assert inc_reloaded.status == IncidentStatus.DIAGNOSING

    stmt = select(HealingEvent).where(HealingEvent.incident_id == incident_id)
    he = (await db_session.execute(stmt)).scalar_one_or_none()
    assert he is None


@pytest.mark.asyncio
async def test_brightdata_service_request_heal():
    # Test shell is false, args are passed, and output is parsed
    import app.services.brightdata_service as bds

    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.wait = AsyncMock()

    # A fake stream reader that returns data on first call, empty on second
    class FakeStream:
        def __init__(self, data):
            self.data = data
            self.called = False

        async def read(self, n):
            if not self.called:
                self.called = True
                return self.data
            return b""

    mock_process.stdout = FakeStream(b'{"proposed": true}')
    mock_process.stderr = FakeStream(b"")

    with patch("asyncio.create_subprocess_exec", return_value=mock_process) as mock_exec:
        result = await bds.BrightDataService.request_heal("c_test", "broken")

        mock_exec.assert_called_once()
        args = mock_exec.call_args[0]
        # Ensure we didn't use shell
        assert "shell" not in mock_exec.call_args[1] or not mock_exec.call_args[1]["shell"]
        assert args[-4:] == ("scraper", "heal", "c_test", "broken")

        assert result == {"proposed": True}
