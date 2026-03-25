import { useCallback, useEffect, useState } from 'react';
import type { Session } from '../api/types';
import { api } from '../api/client';

export function useSessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(() => {
    api.sessions
      .list()
      .then(setSessions)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    refresh();
    // Poll every 5s to pick up title updates from other tabs/sessions
    const interval = setInterval(refresh, 5000);
    return () => clearInterval(interval);
  }, [refresh]);

  const deleteSession = useCallback(
    async (id: string) => {
      await api.sessions.delete(id);
      refresh();
    },
    [refresh],
  );

  return { sessions, loading, refresh, deleteSession };
}
