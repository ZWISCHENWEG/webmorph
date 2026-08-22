from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# -------------------------------------------------------------------------
# Base / Common
# -------------------------------------------------------------------------


class PaginationResponse(BaseModel):
    data: list[Any]


class ErrorDetail(BaseModel):
    code: str
    message: str
    retryable: bool


class ErrorResponse(BaseModel):
    error: ErrorDetail


# -------------------------------------------------------------------------
# Collector
# -------------------------------------------------------------------------


class CollectorSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bright_data_collector_id: str
    current_contract_version: int
    state: str
    latest_health_score: float | None
    created_at: datetime
    updated_at: datetime


class CollectorListResponse(BaseModel):
    data: list[CollectorSchema]


# -------------------------------------------------------------------------
# Job
# -------------------------------------------------------------------------


class JobSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str  # We will map `id` to `job_{id}` in the router
    operation_type: str
    status: str
    error_message: str | None
    attempt_count: int
    created_at: datetime
    updated_at: datetime


class JobTriggerResponse(BaseModel):
    job_id: str
    status: str


# -------------------------------------------------------------------------
# Audit & Healing Events (For Nested Incident Responses)
# -------------------------------------------------------------------------


class AuditEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    related_entity_ref: str
    actor_source: str
    metadata_json: dict | None = Field(alias="metadata_json")
    created_at: datetime


class HealingEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    status: str
    approval_status: str
    proposal: dict | None
    created_at: datetime
    updated_at: datetime


# -------------------------------------------------------------------------
# Incident
# -------------------------------------------------------------------------


class IncidentSummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    collector_id: int
    trigger_run_id: int
    status: str
    diagnosis: dict | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None


class IncidentDetailSchema(IncidentSummarySchema):
    healing_events: list[HealingEventSchema] = []
    audit_events: list[AuditEventSchema] = []


class IncidentListResponse(BaseModel):
    data: list[IncidentSummarySchema]
