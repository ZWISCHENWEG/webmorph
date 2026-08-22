from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.collector import Collector
from app.models.job import Job, JobOperationType, JobStatus
from app.workers.run_worker import process_collection_job

router = APIRouter(prefix="/api/collectors", tags=["runs"])


@router.post("/{collector_id}/runs", status_code=status.HTTP_202_ACCEPTED)
async def trigger_run(
    collector_id: int,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),  # noqa: B008
):
    """
    Triggers a collection run for a specific Collector.
    Returns a Job ID immediately (202 Accepted).
    """
    collector = await session.get(Collector, collector_id)
    if not collector:
        raise HTTPException(status_code=404, detail="Collector not found")

    job = Job(
        operation_type=JobOperationType.COLLECTION,
        status=JobStatus.QUEUED,
        related_entity_ref=f"collector:{collector.id}",
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    background_tasks.add_task(process_collection_job, job.id)

    return {"job_id": f"job_{job.id}", "status": job.status.value}
