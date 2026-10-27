import type { ExtractionResponse, IntegrationStatus, PlanResponse, StudentRecord } from '../types';

async function responseJson<T>(response: Response): Promise<T> {
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(typeof body.detail === 'string' ? body.detail : `Request failed (${response.status})`);
  }
  return body as T;
}

export async function getIntegrationStatus(): Promise<IntegrationStatus> {
  return responseJson(await fetch('/api/integrations/status'));
}

export async function extractStudentRecord(files: File[]): Promise<ExtractionResponse> {
  const form = new FormData();
  files.forEach(file => form.append('files', file));
  return responseJson(await fetch('/api/student-records/extract', { method: 'POST', body: form }));
}

export async function createPlan(input: {
  prompt: string;
  confirmed: boolean;
  record: StudentRecord;
  target_session: 'Semester 1' | 'Semester 2';
  target_credit_points: number;
  pace: 'balanced' | 'accelerated';
  interests: string[];
}): Promise<PlanResponse> {
  return responseJson(await fetch('/api/plans', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input)
  }));
}
