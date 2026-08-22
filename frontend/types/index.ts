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
