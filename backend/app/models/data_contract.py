"""
WEBMORPH — DataContract Model.

Represents a versioned schema definition for a Collector.
Technical-Spec.md: DataContract: version, collector_id, schema_json
"""

import enum

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ContractStatus(enum.StrEnum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"


class DataContract(Base):
    __tablename__ = "data_contracts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    collector_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("collectors.id"), nullable=False
    )
    schema_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[ContractStatus] = mapped_column(
        Enum(ContractStatus), nullable=False, default=ContractStatus.ACTIVE
    )
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    collector: Mapped["Collector"] = relationship(back_populates="contracts")  # type: ignore[name-defined] # noqa: F821
