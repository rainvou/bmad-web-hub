import type { SkillMeta, Session, Message } from './types';

const BASE = '/api';

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  skills: {
    list: (params?: { module?: string; type?: string }) => {
      const qs = new URLSearchParams();
      if (params?.module) qs.set('module', params.module);
      if (params?.type) qs.set('type', params.type);
      const query = qs.toString();
      return fetchJSON<SkillMeta[]>(`/skills${query ? '?' + query : ''}`);
    },
    get: (name: string) => fetchJSON<SkillMeta>(`/skills/${name}`),
  },

  sessions: {
    list: () => fetchJSON<Session[]>('/sessions'),
    get: (id: string) => fetchJSON<Session>(`/sessions/${id}`),
    create: (data: { skill_name: string; title?: string }) =>
      fetchJSON<Session>('/sessions', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      fetchJSON<void>(`/sessions/${id}`, { method: 'DELETE' }),
    messages: (id: string) => fetchJSON<Message[]>(`/sessions/${id}/messages`),
  },

  outputs: {
    list: () => fetchJSON<{ path: string; name: string; category: string; size: number; modified: number }[]>('/outputs'),
    get: (path: string) =>
      fetch(`${BASE}/outputs/${path}`).then((r) => {
        if (!r.ok) throw new Error('Output not found');
        return r.text();
      }),
  },
};
