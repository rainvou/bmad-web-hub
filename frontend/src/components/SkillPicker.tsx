import { useNavigate } from 'react-router-dom';
import { useSkills } from '../hooks/useSkills';
import { useLang } from '../hooks/useLang';
import { api } from '../api/client';
import type { SkillMeta } from '../api/types';

const MODULE_LABELS: Record<string, Record<string, string>> = {
  core: { en: 'Core', ko: 'Core (핵심)' },
  bmm: { en: 'BMM (Development Workflow)', ko: 'BMM (개발 워크플로우)' },
  cis: { en: 'CIS (Creative Intelligence)', ko: 'CIS (창의적 지능)' },
  tea: { en: 'TEA (Test Architecture)', ko: 'TEA (테스트 아키텍처)' },
  wds: { en: 'WDS (Workflow Design)', ko: 'WDS (워크플로우 디자인)' },
};

export default function SkillPicker() {
  const { grouped, loading, error } = useSkills();
  const { lang } = useLang();
  const navigate = useNavigate();

  const handleSelect = async (skill: SkillMeta) => {
    const session = await api.sessions.create({ skill_name: skill.name });
    navigate(`/sessions/${session.id}`);
  };

  if (loading)
    return (
      <div className="p-8 text-center text-text-dim">
        {lang === 'ko' ? '스킬 로딩 중...' : 'Loading skills...'}
      </div>
    );
  if (error) return <div className="p-8 text-center text-error">{error}</div>;

  const moduleOrder = ['core', 'bmm', 'cis', 'tea', 'wds'];
  const sortedModules = Object.keys(grouped).sort(
    (a, b) => moduleOrder.indexOf(a) - moduleOrder.indexOf(b),
  );

  return (
    <div className="space-y-6">
      {sortedModules.map((mod) => {
        const skills = grouped[mod];
        const agents = skills.filter((s) => s.type === 'agent');
        const nonAgents = skills.filter((s) => s.type !== 'agent');
        const label = MODULE_LABELS[mod]?.[lang] || mod;

        return (
          <div key={mod}>
            <h3 className="text-sm font-semibold text-text-dim uppercase tracking-wider mb-3">
              {label}
            </h3>

            {agents.length > 0 && (
              <div className="mb-3">
                <p className="text-xs text-text-dim mb-2">
                  {lang === 'ko' ? '에이전트' : 'Agents'}
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {agents.map((skill) => (
                    <SkillCard key={skill.name} skill={skill} lang={lang} onSelect={handleSelect} />
                  ))}
                </div>
              </div>
            )}

            {nonAgents.length > 0 && (
              <div>
                {agents.length > 0 && (
                  <p className="text-xs text-text-dim mb-2">
                    {lang === 'ko' ? '스킬' : 'Skills'}
                  </p>
                )}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {nonAgents.map((skill) => (
                    <SkillCard key={skill.name} skill={skill} lang={lang} onSelect={handleSelect} />
                  ))}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function SkillCard({
  skill,
  lang,
  onSelect,
}: {
  skill: SkillMeta;
  lang: string;
  onSelect: (s: SkillMeta) => void;
}) {
  const desc =
    lang === 'ko' && skill.description_ko
      ? skill.description_ko
      : skill.description || (lang === 'ko' ? '설명 없음' : 'No description');

  return (
    <button
      onClick={() => onSelect(skill)}
      className="text-left p-3 rounded-lg border border-border hover:border-primary hover:bg-surface-lighter transition-all group"
    >
      <div className="flex items-center gap-2">
        {skill.icon && <span className="text-lg">{skill.icon}</span>}
        <span className="text-sm font-medium text-text-bright group-hover:text-accent transition-colors">
          {skill.display_name}
        </span>
        {skill.type === 'agent' && (
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-primary/20 text-primary">
            agent
          </span>
        )}
      </div>
      <p className="text-xs text-text-dim mt-1.5 line-clamp-2">{desc}</p>
    </button>
  );
}
