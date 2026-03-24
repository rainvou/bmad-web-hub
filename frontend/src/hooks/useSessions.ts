import { useCallback, useEffect, useState } from 'react';
import type { Session } from '../api/types';
import { api } from '../api/client';

export function useSessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(() => {
    setLoading(true);
    api.sessions
      .list()
      .then(setSessions)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    refresh();
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
