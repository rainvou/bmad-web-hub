import { useNavigate } from 'react-router-dom';
import { useSkills } from '../hooks/useSkills';
import { api } from '../api/client';
import type { SkillMeta } from '../api/types';

const MODULE_LABELS: Record<string, string> = {
  core: 'Core',
  bmm: 'BMM (Development Workflow)',
  cis: 'CIS (Creative Intelligence)',
  tea: 'TEA (Test Architecture)',
  wds: 'WDS (Workflow Design)',
};

export default function SkillPicker() {
  const { grouped, loading, error } = useSkills();
  const navigate = useNavigate();

  const handleSelect = async (skill: SkillMeta) => {
    const session = await api.sessions.create({ skill_name: skill.name });
    navigate(`/sessions/${session.id}`);
  };

  if (loading) return <div className="p-8 text-center text-text-dim">Loading skills...</div>;
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

        return (
          <div key={mod}>
            <h3 className="text-sm font-semibold text-text-dim uppercase tracking-wider mb-3">
              {MODULE_LABELS[mod] || mod}
            </h3>

            {agents.length > 0 && (
              <div className="mb-3">
                <p className="text-xs text-text-dim mb-2">Agents</p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {agents.map((skill) => (
                    <SkillCard key={skill.name} skill={skill} onSelect={handleSelect} />
                  ))}
                </div>
              </div>
            )}

            {nonAgents.length > 0 && (
              <div>
                {agents.length > 0 && <p className="text-xs text-text-dim mb-2">Skills</p>}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {nonAgents.map((skill) => (
                    <SkillCard key={skill.name} skill={skill} onSelect={handleSelect} />
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

function SkillCard({ skill, onSelect }: { skill: SkillMeta; onSelect: (s: SkillMeta) => void }) {
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
      <p className="text-xs text-text-dim mt-1.5 line-clamp-2">
        {skill.description || 'No description'}
      </p>
    </button>
  );
}
