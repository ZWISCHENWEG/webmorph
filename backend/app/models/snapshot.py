"""
WEBMORPH — Snapshot Model.

Represents a single Bright Data execution result (j_xxxxx).
Technical-Spec.md: Snapshot: id, bright_data_snapshot_id (j_xxxxx), collector_id,
    run_id, contract_version, normalized_payload_ref, record_count,
    validation_state, health_score, created_at.

IDEMPOTENCY: bright_data_snapshot_id has a unique constraint to prevent
duplicate persistence of the same Bright Data result.
"""

import enum

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ValidationState(enum.StrEnum):
    PENDING = "PENDING"
    HEALTHY = "HEALTHY"
    INVALID = "INVALID"
    DEGRADED = "DEGRADED"
    DRIFT_DETECTED = "DRIFT_DETECTED"


class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bright_data_snapshot_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
        index=True,
        comment="Bright Data execution result identifier (j_xxxxx). "
        "Unique constraint prevents duplicate snapshots.",
    )
    collector_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("collectors.id"), nullable=False, index=True
    )
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("runs.id"), nullable=False, index=True)
    contract_version: Mapped[int] = mapped_column(Integer, nullable=False)

    # Raw payload preserved for provenance/auditability
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Normalized payload for validation
    normalized_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    record_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    validation_state: Mapped[ValidationState] = mapped_column(
        Enum(ValidationState), nullable=False, default=ValidationState.PENDING
    )
    health_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Per-component health scores for observability
    completeness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    schema_validity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    stability_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Validation details (which fields failed, etc.)
    validation_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    collector: Mapped["Collector"] = relationship(back_populates="snapshots")  # type: ignore[name-defined] # noqa: F821
    run: Mapped["Run"] = relationship(back_populates="snapshot")  # type: ignore[name-defined] # noqa: F821
