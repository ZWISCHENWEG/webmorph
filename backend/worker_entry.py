import asyncio
import logging

from sqlalchemy import select

from app.database import async_session_factory
from app.models.job import Job, JobOperationType, JobStatus
from app.workers.approve_worker import process_heal_approve_job
from app.workers.heal_worker import process_heal_request_job

# Import the actual worker logic functions
from app.workers.run_worker import process_collection_job
from app.workers.verify_worker import process_verification_job

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker_entry")


async def poll_jobs():
    """Continuously poll the database for queued jobs and process them."""
    logger.info("Starting background worker polling loop...")
    while True:
        try:
            async with async_session_factory() as session:
                # Find queued jobs
                stmt = (
                    select(Job)
                    .where(Job.status == JobStatus.QUEUED)
                    .order_by(Job.created_at.asc())
                    .limit(5)
                )
                result = await session.execute(stmt)
                jobs = result.scalars().all()

                for job in jobs:
                    logger.info(f"Picked up job {job.id} ({job.operation_type})")
                    if job.operation_type == JobOperationType.COLLECTION:
                        asyncio.create_task(process_collection_job(job.id))
                    elif job.operation_type == JobOperationType.HEAL_REQUEST:
                        asyncio.create_task(process_heal_request_job(job.id))
                    elif job.operation_type == JobOperationType.HEAL_APPROVE:
                        asyncio.create_task(process_heal_approve_job(job.id))
                    elif job.operation_type == JobOperationType.VERIFICATION:
                        asyncio.create_task(process_verification_job(job.id))

        except Exception as e:
            logger.error(f"Error in polling loop: {e}")

        await asyncio.sleep(5)  # Poll interval


if __name__ == "__main__":
    asyncio.run(poll_jobs())
