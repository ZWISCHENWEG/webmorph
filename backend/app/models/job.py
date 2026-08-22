"""
WEBMORPH — Job Model.

Represents an asynchronous WEBMORPH job.
Technical-Spec.md: Job: id, operation_type, status, attempt_count, related_entity_ref,
    created_at, updated_at.
Job Lifecycle: QUEUED -> RUNNING -> SUCCEEDED | FAILED | TIMED_OUT | CANCELLED
"""

import enum

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class JobOperationType(enum.StrEnum):
    COLLECTION = "COLLECTION"
    HEAL_REQUEST = "HEAL_REQUEST"
    HEAL_APPROVE = "HEAL_APPROVE"
    VERIFICATION = "VERIFICATION"


class JobStatus(enum.StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    CANCELLED = "CANCELLED"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operation_type: Mapped[JobOperationType] = mapped_column(Enum(JobOperationType), nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus), nullable=False, default=JobStatus.QUEUED, index=True
    )
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    related_entity_ref: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Reference to the related entity, e.g. 'collector:1' or 'incident:5'",
    )
    error_message: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
