from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.main import app
from app.models.collector import Collector
from app.models.incident import Incident, IncidentStatus
from app.models.job import Job, JobOperationType, JobStatus
from app.models.run import Run, RunStatus
from app.workers.run_worker import process_collection_job


@pytest_asyncio.fixture
async def sample_collector(db_session: AsyncSession):
    c = Collector(bright_data_collector_id="c_test_123", current_contract_version=1)
    db_session.add(c)
    await db_session.flush()
    return c


@pytest_asyncio.fixture
async def sample_run(db_session: AsyncSession, sample_collector):
    r = Run(collector_id=sample_collector.id, contract_version=1, status=RunStatus.SUCCEEDED)
    db_session.add(r)
    await db_session.flush()
    return r


@pytest_asyncio.fixture
async def sample_incident(db_session: AsyncSession, sample_collector, sample_run):
    inc = Incident(
        collector_id=sample_collector.id,
        trigger_run_id=sample_run.id,
        status=IncidentStatus.DRIFT_DETECTED,
        diagnosis={"issue": "test"},
    )
    db_session.add(inc)
    await db_session.flush()
    return inc


@pytest_asyncio.fixture
async def sample_job(db_session: AsyncSession):
    j = Job(
        operation_type=JobOperationType.COLLECTION,
        status=JobStatus.QUEUED,
        related_entity_ref="collector:1",
    )
    db_session.add(j)
    await db_session.flush()
    return j


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    app.dependency_overrides[get_session] = lambda: db_session
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_collectors_success(async_client: AsyncClient, sample_collector):
    response = await async_client.get("/api/collectors")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 1
    collector_data = data["data"][0]
    assert collector_data["id"] == sample_collector.id
    assert collector_data["bright_data_collector_id"] == "c_test_123"
    assert collector_data["state"] == "HEALTHY"


@pytest.mark.asyncio
async def test_get_collector_by_id_returns_schema(async_client: AsyncClient, sample_collector):
    response = await async_client.get(f"/api/collectors/{sample_collector.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_collector.id
    assert data["bright_data_collector_id"] == "c_test_123"


@pytest.mark.asyncio
async def test_get_incidents_success(async_client: AsyncClient, sample_incident):
    response = await async_client.get("/api/incidents")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == sample_incident.id
    assert data["data"][0]["status"] == "DRIFT_DETECTED"


@pytest.mark.asyncio
async def test_get_incident_by_id_includes_nested_events(
    async_client: AsyncClient, sample_incident
):
    response = await async_client.get(f"/api/incidents/{sample_incident.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_incident.id
    assert "healing_events" in data
    assert "audit_events" in data
    assert isinstance(data["healing_events"], list)
    assert isinstance(data["audit_events"], list)
    assert data["diagnosis"] == {"issue": "test"}


@pytest.mark.asyncio
async def test_get_job_success(async_client: AsyncClient, sample_job):
    response = await async_client.get(f"/api/jobs/job_{sample_job.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == f"job_{sample_job.id}"
    assert data["status"] == "QUEUED"


@pytest.mark.asyncio
async def test_api_get_job_malformed_id(async_client: AsyncClient):
    invalid_ids = ["1", "abc", "invalid_1", "job_", "job_abc", "job_-1"]
    for i_id in invalid_ids:
        response = await async_client.get(f"/api/jobs/{i_id}")
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "ERR_NOT_FOUND"


@pytest.mark.asyncio
async def test_api_get_job_missing_id(async_client: AsyncClient):
    response = await async_client.get("/api/jobs/job_999999")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "ERR_NOT_FOUND"


@pytest.mark.asyncio
async def test_api_404_normalized_error(async_client: AsyncClient):
    response = await async_client.get("/api/collectors/99999")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "ERR_NOT_FOUND"
    assert data["error"]["message"] == "Collector not found"
    assert data["error"]["retryable"] is False

    # Also test generic 404 for unmapped route
    response2 = await async_client.get("/api/does_not_exist")
    assert response2.status_code == 404
    data2 = response2.json()
    assert data2["error"]["code"] == "ERR_NOT_FOUND"


@pytest.mark.asyncio
async def test_api_422_normalized_to_400_error(async_client: AsyncClient):
    # Pass a string where an int is expected
    response = await async_client.get("/api/collectors/not_an_int")
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "ERR_VALIDATION"
    assert data["error"]["retryable"] is False


@pytest.mark.asyncio
async def test_api_500_redacts_stack_trace(async_client: AsyncClient, db_session: AsyncSession):
    # Force a 500 by mocking the db session to raise an exception
    with patch("app.api.routers.collectors.select") as mock_select:
        mock_select.side_effect = RuntimeError("SECRET_DATABASE_PASSWORD")
        response = await async_client.get("/api/collectors")

        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "ERR_INTERNAL"
        assert "SECRET_DATABASE_PASSWORD" not in data["error"]["message"]
        assert data["error"]["retryable"] is True


@pytest.mark.asyncio
async def test_post_run_returns_202_and_dispatches_worker(
    async_client: AsyncClient, db_session: AsyncSession, sample_collector
):
    with patch("fastapi.BackgroundTasks.add_task") as mock_add_task:
        response = await async_client.post(f"/api/collectors/{sample_collector.id}/runs")
        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert data["job_id"].startswith("job_")
        assert data["status"] == "QUEUED"

        # Verify the background task was dispatched
        mock_add_task.assert_called_once()
        args = mock_add_task.call_args[0]
        assert args[0] == process_collection_job
        assert isinstance(args[1], int)  # the job_id
