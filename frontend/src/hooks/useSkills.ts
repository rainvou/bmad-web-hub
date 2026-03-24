import { useEffect, useState } from 'react';
import type { SkillMeta } from '../api/types';
import { api } from '../api/client';

export function useSkills() {
  const [skills, setSkills] = useState<SkillMeta[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.skills
      .list()
      .then(setSkills)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const grouped = skills.reduce<Record<string, SkillMeta[]>>((acc, skill) => {
    const mod = skill.module || 'core';
    if (!acc[mod]) acc[mod] = [];
    acc[mod].push(skill);
    return acc;
  }, {});

  return { skills, grouped, loading, error };
}
