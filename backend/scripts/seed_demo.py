import argparse
import asyncio
import os
import sys
from datetime import UTC, datetime, timedelta

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models import (
    AuditEvent,
    Collector,
    DataContract,
    HealingEvent,
    Incident,
    Job,
    Run,
    Snapshot,
)
from app.models.collector import CollectorState
from app.models.data_contract import ContractStatus
from app.models.healing_event import ApprovalStatus, HealingStatus
from app.models.incident import IncidentStatus
from app.models.job import JobOperationType, JobStatus
from app.models.run import RunStatus
from app.models.snapshot import ValidationState


async def clear_demo_data(session: AsyncSession):
    """Safely removes only demo-related records based on a naming convention."""
    print("🧹 Clearing existing demo data...")
    
    # Find demo collectors
    result = await session.execute(
        select(Collector).where(Collector.bright_data_collector_id.like("c_demo_%"))
    )
    demo_collectors = result.scalars().all()
    collector_ids = [c.id for c in demo_collectors]

    if not collector_ids:
        print("   No demo data found to clear.")
        return

    print(f"   Found {len(collector_ids)} demo collectors. Deleting related records...")

    # We must delete in the correct order to respect foreign key constraints
    # 1. Healing Events & Audit Events
    incidents_result = await session.execute(
        select(Incident.id).where(Incident.collector_id.in_(collector_ids))
    )
    incident_ids = [row[0] for row in incidents_result.fetchall()]
    
    if incident_ids:
        await session.execute(delete(HealingEvent).where(HealingEvent.incident_id.in_(incident_ids)))
        # Delete incident-related audit events
        await session.execute(
            delete(AuditEvent).where(
                AuditEvent.related_entity_ref.in_([f"incident:{i}" for i in incident_ids])
            )
        )
    
    # 2. Incidents
    await session.execute(delete(Incident).where(Incident.collector_id.in_(collector_ids)))
    
    # 3. Snapshots
    await session.execute(delete(Snapshot).where(Snapshot.collector_id.in_(collector_ids)))
    
    # 4. Runs
    runs_result = await session.execute(
        select(Run.id).where(Run.collector_id.in_(collector_ids))
    )
    run_ids = [row[0] for row in runs_result.fetchall()]
    
    if run_ids:
        await session.execute(delete(Run).where(Run.id.in_(run_ids)))
        
    # 5. Data Contracts
    await session.execute(delete(DataContract).where(DataContract.collector_id.in_(collector_ids)))
    
    # 6. Delete collector-related audit events and jobs
    await session.execute(
        delete(AuditEvent).where(
            AuditEvent.related_entity_ref.in_([f"collector:{c}" for c in collector_ids])
        )
    )
    await session.execute(
        delete(Job).where(
            Job.related_entity_ref.in_([f"collector:{c}" for c in collector_ids])
        )
    )

    # 7. Finally, Collectors
    await session.execute(delete(Collector).where(Collector.id.in_(collector_ids)))
    
    await session.commit()
    print("✅ Demo data successfully cleared.")


async def seed_data(session: AsyncSession):
    """Seeds realistic, robust MVP demo data without dropping tables."""
    print("🌱 Seeding realistic demo data...")
    now = datetime.now(UTC)
    
    # =========================================================================
    # 1. Healthy Collector (Tech Blog Scraper)
    # =========================================================================
    healthy_collector = Collector(
        bright_data_collector_id="c_demo_tech_blog_123",
        current_contract_version=1,
        state=CollectorState.HEALTHY,
        latest_health_score=99.5,
    )
    session.add(healthy_collector)
    await session.flush()
    
    healthy_contract = DataContract(
        collector_id=healthy_collector.id,
        version=1,
        schema_json={"title": "string", "author": "string", "date": "string"},
        status=ContractStatus.ACTIVE,
    )
    session.add(healthy_contract)
    
    healthy_job = Job(
        operation_type=JobOperationType.COLLECTION,
        status=JobStatus.SUCCEEDED,
        related_entity_ref=f"collector:{healthy_collector.id}",
    )
    session.add(healthy_job)
    await session.flush()

    healthy_run = Run(
        collector_id=healthy_collector.id,
        contract_version=1,
        job_id=healthy_job.id,
        status=RunStatus.SUCCEEDED,
        created_at=now - timedelta(hours=2),
        updated_at=now - timedelta(hours=1.9),
    )
    session.add(healthy_run)
    await session.flush()
    
    healthy_snapshot = Snapshot(
        bright_data_snapshot_id="j_demo_tech_blog_999",
        collector_id=healthy_collector.id,
        run_id=healthy_run.id,
        contract_version=1,
        record_count=150,
        validation_state=ValidationState.HEALTHY,
        health_score=99.5,
        completeness_score=100.0,
        schema_validity_score=100.0,
        stability_score=98.5,
        created_at=now - timedelta(hours=1.9),
    )
    session.add(healthy_snapshot)

    # =========================================================================
    # 2. Drift Detected Collector (Ecommerce Price Monitor)
    # =========================================================================
    incident_collector = Collector(
        bright_data_collector_id="c_demo_ecommerce_123",
        current_contract_version=1,
        state=CollectorState.AWAITING_APPROVAL,
        latest_health_score=65.0,
    )
    session.add(incident_collector)
    await session.flush()
    
    incident_contract = DataContract(
        collector_id=incident_collector.id,
        version=1,
        schema_json={"product_name": "string", "price": "number", "in_stock": "boolean"},
        status=ContractStatus.ACTIVE,
    )
    session.add(incident_contract)
    
    incident_job = Job(
        operation_type=JobOperationType.COLLECTION,
        status=JobStatus.SUCCEEDED,
        related_entity_ref=f"collector:{incident_collector.id}",
    )
    session.add(incident_job)
    await session.flush()

    incident_run = Run(
        collector_id=incident_collector.id,
        contract_version=1,
        job_id=incident_job.id,
        status=RunStatus.FAILED,
        created_at=now - timedelta(minutes=45),
        updated_at=now - timedelta(minutes=40),
    )
    session.add(incident_run)
    await session.flush()
    
    incident_snapshot = Snapshot(
        bright_data_snapshot_id="j_demo_ecommerce_888",
        collector_id=incident_collector.id,
        run_id=incident_run.id,
        contract_version=1,
        record_count=200,
        validation_state=ValidationState.DRIFT_DETECTED,
        health_score=65.0,
        completeness_score=100.0,
        schema_validity_score=0.0,  # Schema drift on 'price'
        stability_score=90.0,
        validation_details={
            "is_valid": False,
            "errors": [
                {
                    "field": "price",
                    "error": "Expected number, got string '$51.77'"
                }
            ]
        },
        created_at=now - timedelta(minutes=40),
    )
    session.add(incident_snapshot)
    await session.flush()
    
    incident = Incident(
        collector_id=incident_collector.id,
        trigger_run_id=incident_run.id,
        status=IncidentStatus.AWAITING_APPROVAL,
        diagnosis={
            "severity": "HIGH",
            "message": "Schema Drift Detected: Price",
            "fields_affected": ["price"],
            "drift_type": "TYPE_MISMATCH",
            "ai_diagnosis": "Detected website structure change. Target changed price format from primitive numeric to nested object."
        },
        created_at=now - timedelta(minutes=35),
        updated_at=now - timedelta(minutes=30),
    )
    session.add(incident)
    await session.flush()
    
    healing_event = HealingEvent(
        incident_id=incident.id,
        status=HealingStatus.AWAITING_APPROVAL,
        approval_status=ApprovalStatus.PENDING,
        proposal={
            "ai_diagnosis": "Detected website structure change. Generated repair with 98.5% confidence.",
            "root_cause": "Website UI update migrated price from a primitive numeric value to a localized currency object.",
            "proposed_fix": "```javascript\n// BEFORE:\n// price: 199\n\n// AFTER:\n// price: {\n//   value: 199,\n//   currency: \"USD\"\n// }\n\nconst rawPriceNode = $('.product-price');\nreturn {\n  value: parseFloat(rawPriceNode.attr('data-price-value')),\n  currency: rawPriceNode.attr('data-currency')\n};\n```",
            "confidence_score": 98.5
        },
        created_at=now - timedelta(minutes=30),
        updated_at=now - timedelta(minutes=30),
    )
    session.add(healing_event)

    audit_events = [
        AuditEvent(
            event_type="INCIDENT_DETECTED",
            related_entity_ref=f"incident:{incident.id}",
            metadata_json={"message": "Drift detected: Price schema mismatch.", "health_score": 65.0},
        ),
        AuditEvent(
            event_type="HEAL_PROPOSED",
            related_entity_ref=f"incident:{incident.id}",
            metadata_json={"message": "AI generated a high-confidence healing proposal.", "confidence": 98.5},
        ),
    ]
    session.add_all(audit_events)

    # =========================================================================
    # 3. Recovered Collector (Real Estate Scraper)
    # =========================================================================
    recovered_collector = Collector(
        bright_data_collector_id="c_demo_realestate_123",
        current_contract_version=2,
        state=CollectorState.HEALTHY,
        latest_health_score=98.0,
    )
    session.add(recovered_collector)
    await session.flush()
    
    rec_contract_v1 = DataContract(
        collector_id=recovered_collector.id,
        version=1,
        schema_json={"address": "string", "sqft": "number"},
        status=ContractStatus.SUPERSEDED,
    )
    rec_contract_v2 = DataContract(
        collector_id=recovered_collector.id,
        version=2,
        schema_json={"address": "string", "sqft": "number", "agent": "string"},
        status=ContractStatus.ACTIVE,
    )
    session.add_all([rec_contract_v1, rec_contract_v2])
    
    rec_job = Job(
        operation_type=JobOperationType.COLLECTION,
        status=JobStatus.SUCCEEDED,
        related_entity_ref=f"collector:{recovered_collector.id}",
    )
    session.add(rec_job)
    await session.flush()

    rec_run = Run(
        collector_id=recovered_collector.id,
        contract_version=1,
        job_id=rec_job.id,
        status=RunStatus.FAILED,
        created_at=now - timedelta(days=1),
        updated_at=now - timedelta(days=1, minutes=-5),
    )
    session.add(rec_run)
    await session.flush()
    
    rec_incident = Incident(
        collector_id=recovered_collector.id,
        trigger_run_id=rec_run.id,
        status=IncidentStatus.RECOVERED,
        diagnosis={
            "severity": "MEDIUM",
            "message": "Missing 'agent' field due to layout change"
        },
        created_at=now - timedelta(days=1, minutes=-10),
        resolved_at=now - timedelta(days=1, minutes=-60),
    )
    session.add(rec_incident)
    await session.flush()
    
    rec_heal = HealingEvent(
        incident_id=rec_incident.id,
        status=HealingStatus.RECOVERED,
        approval_status=ApprovalStatus.APPROVED,
        proposal={
            "ai_diagnosis": "Targeted new agent div class",
            "confidence_score": 92.0
        },
        created_at=now - timedelta(days=1, minutes=-15),
    )
    session.add(rec_heal)

    await session.commit()
    print("✅ Demo data successfully seeded!")


async def main():
    parser = argparse.ArgumentParser(description="Seed WebMorph database with demo data safely.")
    parser.add_argument("--reset", action="store_true", help="Clear existing demo data before seeding")
    args = parser.parse_args()

    async with async_session_factory() as session:
        if args.reset:
            await clear_demo_data(session)
        
        await seed_data(session)

if __name__ == "__main__":
    asyncio.run(main())
