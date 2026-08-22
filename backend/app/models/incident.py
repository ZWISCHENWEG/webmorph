"""
WEBMORPH — Incident Model.

Represents a drift detection incident triggered when health < 80.
Technical-Spec.md: Incident: id, collector_id, trigger_run_id, status.
"""

import enum

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class IncidentStatus(enum.StrEnum):
    DRIFT_DETECTED = "DRIFT_DETECTED"
    DIAGNOSING = "DIAGNOSING"
    HEAL_PROPOSED = "HEAL_PROPOSED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    HEALING = "HEALING"
    VERIFYING = "VERIFYING"
    RECOVERED = "RECOVERED"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    HEAL_FAILED = "HEAL_FAILED"
    MANUAL_INTERVENTION = "MANUAL_INTERVENTION"


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    collector_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("collectors.id"), nullable=False, index=True
    )
    trigger_run_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("runs.id"), nullable=False
    )
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus), nullable=False, default=IncidentStatus.DRIFT_DETECTED, index=True
    )
    # Diagnosis details: which fields failed, health breakdown
    diagnosis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    resolved_at: Mapped[str | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    collector: Mapped["Collector"] = relationship(back_populates="incidents")  # type: ignore[name-defined] # noqa: F821
    trigger_run: Mapped["Run"] = relationship()  # type: ignore[name-defined] # noqa: F821
    healing_events: Mapped[list["HealingEvent"]] = relationship(back_populates="incident")  # type: ignore[name-defined] # noqa: F821
