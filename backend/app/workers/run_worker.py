import asyncio
import logging

from sqlalchemy import select

from app.config import settings
from app.database import async_session_factory
from app.models.audit_event import AuditEvent
from app.models.collector import Collector, CollectorState
from app.models.job import Job, JobStatus
from app.models.run import Run, RunStatus
from app.models.snapshot import Snapshot, ValidationState
from app.services.brightdata_service import BrightDataService, BrightDataServiceError
from app.validation.engine import process_payload

logger = logging.getLogger(__name__)


async def process_collection_job(job_id: int):
    """
    Background worker that orchestrates the Bright Data execution lifecycle.
    Job -> Run -> Execute CLI -> Normalize/Validate -> Snapshot -> DB Update.
    """
    async with async_session_factory() as session:
        job = await session.get(Job, job_id)
        if not job or job.status != JobStatus.QUEUED:
            return

        # Mark job as running
        job.status = JobStatus.RUNNING
        await session.commit()

        # Parse collector ID from related_entity_ref
        try:
            _, collector_id_str = job.related_entity_ref.split(":")
            collector_id = int(collector_id_str)
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = f"Invalid related_entity_ref: {e}"
            await session.commit()
            return

        collector = await session.get(Collector, collector_id)
        if not collector:
            job.status = JobStatus.FAILED
            job.error_message = "Collector not found"
            await session.commit()
            return

        # Create Run
        run = Run(
            collector_id=collector.id,
            contract_version=collector.current_contract_version,
            job_id=job.id,
            status=RunStatus.RUNNING,
        )
        session.add(run)
        await session.commit()
        await session.refresh(run)

        # Execute Bright Data CLI securely with retries
        operation_attempts = 0
        target_url = settings.bright_data_target_url

        while True:
            operation_attempts += 1
            job.attempt_count += 1
            await session.commit()

            try:
                snapshot_id, raw_payload = await BrightDataService.run_collector(
                    collector.bright_data_collector_id, target_url
                )
                run.status = RunStatus.SUCCEEDED
                break  # Success
            except BrightDataServiceError as e:
                if e.retryable and operation_attempts < 3:
                    logger.warning(
                        f"Retryable error running collector "
                        f"(attempt {operation_attempts}/3): {str(e)}"
                    )
                    await asyncio.sleep(2 * (2 ** (operation_attempts - 1)))
                    continue

                run.status = RunStatus.FAILED
                job.status = JobStatus.FAILED
                job.error_message = str(e)

                # Audit event for failure
                audit = AuditEvent(
                    event_type="RUN_FAILED",
                    related_entity_ref=f"run:{run.id}",
                    actor_source="SYSTEM",
                    metadata_json={"error": str(e), "code": e.code},
                )
                session.add(audit)
                await session.commit()
                return
            except Exception as e:
                run.status = RunStatus.FAILED
                job.status = JobStatus.FAILED
                job.error_message = f"Unexpected error: {str(e)}"
                await session.commit()
                return

        # Get baselines for stability calculation
        baseline_stmt = (
            select(Snapshot)
            .where(
                Snapshot.collector_id == collector.id,
                Snapshot.validation_state == ValidationState.HEALTHY,
            )
            .order_by(Snapshot.created_at.desc())
            .limit(5)
        )

        baseline_results = await session.scalars(baseline_stmt)
        baseline_counts = [s.record_count for s in baseline_results]

        # Pass through Phase 3 Validation Engine
        validation_result = process_payload(raw_payload, baseline_counts)

        # Create Snapshot preserving provenance
        snapshot = Snapshot(
            bright_data_snapshot_id=snapshot_id,
            collector_id=collector.id,
            run_id=run.id,
            contract_version=collector.current_contract_version,
            raw_payload=raw_payload,
            normalized_payload=validation_result.normalized_payload,
            record_count=len(validation_result.normalized_payload),
            validation_state=validation_result.validation_state,
            health_score=validation_result.health_score,
        )
        session.add(snapshot)

        # State transition on Collector
        old_state = collector.state
        if validation_result.validation_state == ValidationState.HEALTHY:
            collector.state = CollectorState.HEALTHY
        elif validation_result.validation_state == ValidationState.DEGRADED:
            # If it was healthy, it becomes degraded. If it was already diagnosing etc, keep it?
            # Specs say: if health >= 90 -> HEALTHY. 90 > health >= 80 -> DEGRADED.
            collector.state = CollectorState.DEGRADED
        else:
            collector.state = CollectorState.DRIFT_DETECTED

        collector.latest_health_score = validation_result.health_score

        # Audit lifecycle transition
        if old_state != collector.state:
            audit = AuditEvent(
                event_type="COLLECTOR_STATE_CHANGED",
                related_entity_ref=f"collector:{collector.id}",
                actor_source="SYSTEM",
                metadata_json={
                    "old_state": old_state.value,
                    "new_state": collector.state.value,
                    "health_score": validation_result.health_score,
                },
            )
            session.add(audit)

        job.status = JobStatus.SUCCEEDED
        await session.commit()
