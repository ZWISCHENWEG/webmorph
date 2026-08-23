import {
  CollectorListResponse,
  Collector,
  JobTriggerResponse,
  Job,
  ErrorResponse,
  IncidentListResponse,
  IncidentDetail,
  SnapshotListResponse
} from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  public code: string;
  public retryable: boolean;

  constructor(message: string, code: string, retryable: boolean) {
    super(message);
    this.code = code;
    this.retryable = retryable;
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    if (errorData && errorData.error) {
      const { code, message, retryable } = (errorData as ErrorResponse).error;
      throw new ApiError(message, code, retryable);
    }
    throw new ApiError(`HTTP Error: ${response.status}`, 'ERR_INTERNAL', true);
  }
  return response.json();
}

export async function getCollectors(): Promise<CollectorListResponse> {
  const response = await fetch(`${API_BASE_URL}/api/collectors`, {
    cache: 'no-store'
  });
  return handleResponse<CollectorListResponse>(response);
}

export async function getCollector(id: number): Promise<Collector> {
  const response = await fetch(`${API_BASE_URL}/api/collectors/${id}`, {
    cache: 'no-store'
  });
  return handleResponse<Collector>(response);
}

export async function getCollectorSnapshots(id: number, skip: number = 0, limit: number = 100): Promise<SnapshotListResponse> {
  const response = await fetch(`${API_BASE_URL}/api/collectors/${id}/snapshots?skip=${skip}&limit=${limit}`, {
    cache: 'no-store'
  });
  return handleResponse<SnapshotListResponse>(response);
}

export async function triggerRun(collectorId: number): Promise<JobTriggerResponse> {
  const response = await fetch(`${API_BASE_URL}/api/collectors/${collectorId}/runs`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  return handleResponse<JobTriggerResponse>(response);
}

export async function getJobStatus(jobId: string): Promise<Job> {
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}`, {
    cache: 'no-store'
  });
  return handleResponse<Job>(response);
}

export async function getIncidents(): Promise<IncidentListResponse> {
  const response = await fetch(`${API_BASE_URL}/api/incidents`, {
    cache: 'no-store'
  });
  return handleResponse<IncidentListResponse>(response);
}

export async function getIncident(id: number): Promise<IncidentDetail> {
  const response = await fetch(`${API_BASE_URL}/api/incidents/${id}`, {
    cache: 'no-store'
  });
  return handleResponse<IncidentDetail>(response);
}

export async function proposeHeal(incidentId: number): Promise<JobTriggerResponse> {
  const response = await fetch(`${API_BASE_URL}/api/incidents/${incidentId}/heal`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  return handleResponse<JobTriggerResponse>(response);
}

export async function approveHeal(incidentId: number, approved: boolean): Promise<{status: string, job_id?: string}> {
  const response = await fetch(`${API_BASE_URL}/api/incidents/${incidentId}/approve`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ approved })
  });
  return handleResponse<{status: string, job_id?: string}>(response);
}

export async function verifyHeal(incidentId: number): Promise<JobTriggerResponse> {
  const response = await fetch(`${API_BASE_URL}/api/incidents/${incidentId}/verify`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  return handleResponse<JobTriggerResponse>(response);
}
