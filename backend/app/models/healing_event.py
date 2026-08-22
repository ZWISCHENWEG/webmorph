"""
WEBMORPH — HealingEvent Model.

Represents a healing attempt for an Incident.
Technical-Spec.md: HealingEvent: id, incident_id, status, approval_status, proposal.
    Unique active constraint per Incident.
"""

import enum

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Index, Integer, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class HealingStatus(enum.StrEnum):
    PROPOSED = "PROPOSED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    HEALING = "HEALING"
    VERIFYING = "VERIFYING"
    RECOVERED = "RECOVERED"
    FAILED = "FAILED"


class ApprovalStatus(enum.StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class HealingEvent(Base):
    __tablename__ = "healing_events"
    __table_args__ = (
        Index(
            "ix_active_healing_event_per_incident",
            "incident_id",
            unique=True,
            sqlite_where=text("status NOT IN ('RECOVERED', 'REJECTED', 'FAILED')"),
            postgresql_where=text("status NOT IN ('RECOVERED', 'REJECTED', 'FAILED')"),
        ),
    )


    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    incident_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("incidents.id"), nullable=False, index=True
    )
    status: Mapped[HealingStatus] = mapped_column(
        Enum(HealingStatus), nullable=False, default=HealingStatus.PROPOSED
    )
    approval_status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus), nullable=False, default=ApprovalStatus.PENDING
    )
    proposal: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    verification_run_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("runs.id"), nullable=True
    )
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    incident: Mapped["Incident"] = relationship(back_populates="healing_events")  # type: ignore[name-defined] # noqa: F821
