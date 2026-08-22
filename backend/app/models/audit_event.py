"""
WEBMORPH — AuditEvent Model.

Immutable, append-only record of important state transitions.
Technical-Spec.md: AuditEvent: id, event_type, related_entity_ref, actor_source,
    metadata_json, created_at.

All important transitions generate an AuditEvent per Technical-Spec constraints.
"""

from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        comment="E.g. COLLECTOR_STATE_CHANGED, INCIDENT_CREATED, HEAL_APPROVED, RUN_COMPLETED",
    )
    related_entity_ref: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Reference like 'collector:1', 'incident:3', 'run:12'"
    )
    actor_source: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        default="system",
        comment="Who/what triggered the event: 'system', 'operator', 'bright_data'",
    )
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
