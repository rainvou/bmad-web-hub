import { useLang } from '../hooks/useLang';
import SkillPicker from '../components/SkillPicker';

export default function Dashboard() {
  const { lang } = useLang();

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-4xl mx-auto p-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-text-bright">
            {lang === 'ko' ? '새 세션 시작' : 'Start a New Session'}
          </h2>
          <p className="text-text-dim mt-1">
            {lang === 'ko'
              ? 'BMAD 스킬 또는 에이전트를 선택하세요.'
              : 'Choose a BMAD skill or agent to begin.'}
          </p>
        </div>
        <SkillPicker />
      </div>
    </div>
  );
}
