import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.main import app
from app.models.collector import Collector
from app.models.run import Run
from app.models.snapshot import Snapshot, ValidationState


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    app.dependency_overrides[get_session] = lambda: db_session
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_snapshots_missing_collector(async_client: AsyncClient):
    response = await async_client.get("/api/collectors/9999/snapshots")
    assert response.status_code == 404
    assert response.json()["error"]["message"] == "Collector not found"


@pytest.mark.asyncio
async def test_get_snapshots_empty(async_client: AsyncClient, db_session: AsyncSession):
    collector = Collector(bright_data_collector_id="c_empty_test")
    db_session.add(collector)
    await db_session.commit()
    await db_session.refresh(collector)

    response = await async_client.get(f"/api/collectors/{collector.id}/snapshots")
    assert response.status_code == 200
    assert response.json()["data"] == []


@pytest.mark.asyncio
async def test_get_snapshots_pagination_schema_and_ordering(
    async_client: AsyncClient, db_session: AsyncSession
):
    collector = Collector(bright_data_collector_id="c_snap_test")
    db_session.add(collector)
    await db_session.commit()
    await db_session.refresh(collector)

    run = Run(collector_id=collector.id, contract_version=1)
    db_session.add(run)
    await db_session.commit()
    await db_session.refresh(run)

    for i in range(3):
        snap = Snapshot(
            bright_data_snapshot_id=f"j_test_{i}",
            collector_id=collector.id,
            run_id=run.id,
            contract_version=1,
            raw_payload={"secret": "raw_data"},
            normalized_payload={"clean": "data", "id": i},
            record_count=1,
            validation_state=ValidationState.HEALTHY,
            health_score=100.0,
            completeness_score=100.0,
            schema_validity_score=100.0,
            stability_score=100.0,
            validation_details={"fields": "ok"},
        )
        db_session.add(snap)
    await db_session.commit()

    # Get all 3 snapshots
    res = await async_client.get(f"/api/collectors/{collector.id}/snapshots")
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data) == 3

    # Check deterministic ordering (descending by created_at and id)
    # The last inserted should be first.
    assert data[0]["bright_data_snapshot_id"] == "j_test_2"
    assert data[1]["bright_data_snapshot_id"] == "j_test_1"
    assert data[2]["bright_data_snapshot_id"] == "j_test_0"

    # Check schema and raw_payload absence
    first = data[0]
    assert "id" in first
    assert "bright_data_snapshot_id" in first
    assert "raw_payload" not in first
    assert first["normalized_payload"] == {"clean": "data", "id": 2}
    assert first["health_score"] == 100.0

    # Pagination test
    res_limit = await async_client.get(f"/api/collectors/{collector.id}/snapshots?limit=2&skip=0")
    assert res_limit.status_code == 200
    assert len(res_limit.json()["data"]) == 2

    res_skip = await async_client.get(f"/api/collectors/{collector.id}/snapshots?limit=2&skip=2")
    assert res_skip.status_code == 200
    assert len(res_skip.json()["data"]) == 1
    assert res_skip.json()["data"][0]["bright_data_snapshot_id"] == "j_test_0"
