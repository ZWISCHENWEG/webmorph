import argparse
import asyncio
import os
import sys
from datetime import datetime, timezone

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory, engine
from app.models.audit_event import AuditEvent
from app.models.base import Base
from app.models.collector import Collector, CollectorState
from app.models.data_contract import ContractStatus, DataContract
from app.models.healing_event import ApprovalStatus, HealingEvent, HealingStatus
from app.models.incident import Incident, IncidentStatus
from app.models.job import Job, JobOperationType, JobStatus
from app.models.run import Run, RunStatus
from app.models.snapshot import Snapshot, ValidationState


async def reset_database():
    """Drops and recreates all tables. Use with caution."""
    print("⚠️ Resetting database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database reset complete.")


async def seed_data():
    """Seeds the database with a realistic ecommerce incident lifecycle."""
    print("🌱 Seeding realistic MVP demo data...")
    async with async_session_factory() as session:
        # Create Collector
        collector = Collector(
            bright_data_collector_id="c_demo_ecommerce_123",
            current_contract_version=1,
            state=CollectorState.AWAITING_APPROVAL,
            latest_health_score=45.0,
        )
        session.add(collector)
        await session.flush()
        print(f"Created Collector: {collector.id}")

        # Create Data Contract
        contract = DataContract(
            collector_id=collector.id,
            version=1,
            schema_json={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "price": {"type": "number", "minimum": 0},
                    "availability": {"type": "boolean"},
                },
                "required": ["title", "price", "availability"],
            },
            status=ContractStatus.ACTIVE,
        )
        session.add(contract)
        
        # Create a Job
        job = Job(
            operation_type=JobOperationType.COLLECTION,
            status=JobStatus.SUCCEEDED,
            related_entity_ref=f"collector:{collector.id}",
        )
        session.add(job)
        await session.flush()

        # Create a Run
        run = Run(
            collector_id=collector.id,
            contract_version=1,
            job_id=job.id,
            status=RunStatus.FAILED,
        )
        session.add(run)
        await session.flush()

        # Create a Snapshot
        snapshot = Snapshot(
            bright_data_snapshot_id="j_demo_123",
            collector_id=collector.id,
            run_id=run.id,
            contract_version=1,
            validation_state=ValidationState.INVALID,
            record_count=1,
            health_score=45.0,
            schema_validity_score=0.0,
            validation_details={
                "is_valid": False,
                "errors": [
                    {
                        "field": "price",
                        "error": "Expected number, got string '$51.77'",
                    }
                ],
            }
        )
        session.add(snapshot)
        await session.flush()

        # Create an Incident
        incident = Incident(
            collector_id=collector.id,
            trigger_run_id=run.id,
            status=IncidentStatus.AWAITING_APPROVAL,
            diagnosis={
                "severity": "HIGH",
                "message": "Price schema drift detected",
                "fields_affected": ["price"],
                "drift_type": "TYPE_MISMATCH"
            }
        )
        session.add(incident)
        await session.flush()

        # Create Healing Event
        healing_event = HealingEvent(
            incident_id=incident.id,
            status=HealingStatus.AWAITING_APPROVAL,
            approval_status=ApprovalStatus.PENDING,
            proposal={
                "ai_diagnosis": "The target website changed its price formatting from a raw number to a string prefixed with '$'.",
                "root_cause": "DOM element parsing for 'price' now includes the currency symbol.",
                "proposed_fix": "```javascript\n// Update parser logic\nconst rawPrice = $('#price').text();\nconst parsedPrice = parseFloat(rawPrice.replace('$', '').trim());\nreturn parsedPrice;\n```",
                "confidence_score": 98.5
            }
        )
        session.add(healing_event)

        # Create Heal Job (simulating previous AI heal request)
        heal_job = Job(
            operation_type=JobOperationType.HEAL_REQUEST,
            related_entity_ref=f"incident:{incident.id}",
            status=JobStatus.SUCCEEDED,
        )
        session.add(heal_job)

        # Add Audit Events
        audit_events = [
            AuditEvent(
                event_type="INCIDENT_DETECTED",
                related_entity_ref=f"incident:{incident.id}",
                metadata_json={"message": "Drift detected: Price schema mismatch.", "health_score": 45.0},
            ),
            AuditEvent(
                event_type="HEAL_PROPOSED",
                related_entity_ref=f"incident:{incident.id}",
                metadata_json={"message": "AI generated a high-confidence healing proposal.", "confidence": 98.5},
            ),
        ]
        session.add_all(audit_events)

        await session.commit()
        print("✅ Demo data successfully seeded!")


async def main():
    parser = argparse.ArgumentParser(description="Seed MVP Demo Data")
    parser.add_argument("--reset", action="store_true", help="Reset the database before seeding")
    args = parser.parse_args()

    if args.reset:
        await reset_database()
    else:
        # If not resetting, we create tables just in case they don't exist
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    await seed_data()


if __name__ == "__main__":
    asyncio.run(main())
