import type { CheatSheet } from '../types';

export async function createCheatSheet(files: File[], title: string): Promise<CheatSheet> {
  const form = new FormData();
  files.forEach(file => form.append('files', file));
  form.append('title', title);
  const response = await fetch('/api/cheat-sheets', { method: 'POST', body: form });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(typeof body.detail === 'string' ? body.detail : `Request failed (${response.status})`);
  }
  return response.json();
}
