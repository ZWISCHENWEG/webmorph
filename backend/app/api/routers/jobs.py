from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import JobSchema
from app.database import get_session
from app.models.job import Job

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobSchema)
async def get_job(
    job_id: str,
    session: AsyncSession = Depends(get_session),  # noqa: B008
):
    """Get a single job by ID."""
    if not job_id.startswith("job_"):
        raise HTTPException(status_code=404, detail="Job not found")

    id_str = job_id[4:]
    if not id_str.isdigit():
        raise HTTPException(status_code=404, detail="Job not found")

    db_job_id = int(id_str)

    job = await session.get(Job, db_job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response_data = {
        "id": f"job_{job.id}",
        "operation_type": job.operation_type,
        "status": job.status,
        "error_message": job.error_message,
        "attempt_count": job.attempt_count,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }
    return response_data
