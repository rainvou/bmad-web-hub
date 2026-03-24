import SkillPicker from '../components/SkillPicker';

export default function Dashboard() {
  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-4xl mx-auto p-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-text-bright">Start a New Session</h2>
          <p className="text-text-dim mt-1">Choose a BMAD skill or agent to begin.</p>
        </div>
        <SkillPicker />
      </div>
    </div>
  );
}
