import { CollectorListResponse, JobTriggerResponse, Job, ErrorResponse } from '../types';

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
