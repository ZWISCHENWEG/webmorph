"""
WEBMORPH — Collector Model.

Represents a persistent Bright Data scraper definition.
Technical-Spec.md: Collector: id, bright_data_collector_id (c_xxxxx), current_contract_version.
"""

import enum

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CollectorState(enum.StrEnum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    DRIFT_DETECTED = "DRIFT_DETECTED"
    DIAGNOSING = "DIAGNOSING"
    HEAL_PROPOSED = "HEAL_PROPOSED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    HEALING = "HEALING"
    VERIFYING = "VERIFYING"
    RECOVERED = "RECOVERED"
    REJECTED = "REJECTED"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    HEAL_FAILED = "HEAL_FAILED"
    MANUAL_INTERVENTION = "MANUAL_INTERVENTION"


class Collector(Base):
    __tablename__ = "collectors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bright_data_collector_id: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    current_contract_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )
    state: Mapped[CollectorState] = mapped_column(
        Enum(CollectorState), nullable=False, default=CollectorState.HEALTHY
    )
    latest_health_score: Mapped[float | None] = mapped_column(default=None)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    contracts: Mapped[list["DataContract"]] = relationship(back_populates="collector")  # type: ignore[name-defined] # noqa: F821
    runs: Mapped[list["Run"]] = relationship(back_populates="collector")  # type: ignore[name-defined] # noqa: F821
    snapshots: Mapped[list["Snapshot"]] = relationship(back_populates="collector")  # type: ignore[name-defined] # noqa: F821
    incidents: Mapped[list["Incident"]] = relationship(back_populates="collector")  # type: ignore[name-defined] # noqa: F821
