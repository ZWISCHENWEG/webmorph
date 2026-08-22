"""
WEBMORPH — Run Model.

Represents an internal WEBMORPH execution attempt.
Technical-Spec.md: Run: id, collector_id, contract_version, status.
"""

import enum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RunStatus(enum.StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    collector_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("collectors.id"), nullable=False, index=True
    )
    contract_version: Mapped[int] = mapped_column(Integer, nullable=False)
    job_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("jobs.id"), nullable=True
    )
    status: Mapped[RunStatus] = mapped_column(
        Enum(RunStatus), nullable=False, default=RunStatus.PENDING, index=True
    )
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    collector: Mapped["Collector"] = relationship(back_populates="runs")  # type: ignore[name-defined] # noqa: F821
    snapshot: Mapped["Snapshot | None"] = relationship(back_populates="run", uselist=False)  # type: ignore[name-defined] # noqa: F821
    job: Mapped["Job | None"] = relationship()  # type: ignore[name-defined] # noqa: F821
