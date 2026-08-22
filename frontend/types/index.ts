export interface ErrorDetail {
  code: string;
  message: string;
  retryable: boolean;
}

export interface ErrorResponse {
  error: ErrorDetail;
}

export interface Collector {
  id: number;
  bright_data_collector_id: string;
  current_contract_version: number;
  state: 'HEALTHY' | 'DEGRADED' | 'DRIFT_DETECTED' | 'DIAGNOSING' | 'HEAL_PROPOSED' | 'AWAITING_APPROVAL' | 'APPROVED' | 'REJECTED';
  latest_health_score: number | null;
  created_at: string;
  updated_at: string;
}

export interface CollectorListResponse {
  data: Collector[];
}

export interface Job {
  id: string;
  operation_type: string;
  status: 'QUEUED' | 'RUNNING' | 'SUCCEEDED' | 'FAILED' | 'TIMED_OUT' | 'CANCELLED';
  error_message: string | null;
  attempt_count: number;
  created_at: string;
  updated_at: string;
}

export interface JobTriggerResponse {
  job_id: string;
  status: string;
}

export interface AuditEvent {
  id: number;
  event_type: string;
  related_entity_ref: string;
  actor_source: string;
  metadata_json: Record<string, unknown> | null;
  created_at: string;
}

export interface HealProposal {
  changes?: string[];
  risk_level?: string;
  impact_assessment?: string;
  [key: string]: unknown;
}

export interface HealingEvent {
  id: number;
  incident_id: number;
  status: 'PENDING' | 'PROPOSED' | 'APPLIED' | 'FAILED';
  approval_status: 'PENDING' | 'APPROVED' | 'REJECTED';
  proposal: HealProposal | null;
  created_at: string;
  updated_at: string;
}

export interface Diagnosis {
  issue?: string;
  missing_fields?: string[];
  [key: string]: unknown;
}

export interface IncidentSummary {
  id: number;
  collector_id: number;
  trigger_run_id: number;
  status: 'DRIFT_DETECTED' | 'DIAGNOSING' | 'HEAL_PROPOSED' | 'AWAITING_APPROVAL' | 'APPROVED' | 'HEALING' | 'VERIFYING' | 'RECOVERED' | 'REJECTED' | 'MANUAL_INTERVENTION';
  diagnosis: Diagnosis | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
}

export interface IncidentDetail extends IncidentSummary {
  healing_events: HealingEvent[];
  audit_events: AuditEvent[];
}

export interface IncidentListResponse {
  data: IncidentSummary[];
}

export interface Snapshot {
  id: number;
  bright_data_snapshot_id: string;
  collector_id: number;
  run_id: number;
  contract_version: number;
  normalized_payload: Record<string, unknown> | null;
  record_count: number;
  validation_state: 'PENDING' | 'HEALTHY' | 'INVALID' | 'DEGRADED' | 'DRIFT_DETECTED';
  health_score: number | null;
  completeness_score: number | null;
  schema_validity_score: number | null;
  stability_score: number | null;
  validation_details: Record<string, unknown> | null;
  created_at: string;
}

export interface SnapshotListResponse {
  data: Snapshot[];
}
