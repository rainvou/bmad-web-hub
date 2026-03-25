import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useSessions } from '../hooks/useSessions';
import { useLang } from '../hooks/useLang';

export default function Layout() {
  const { sessions, loading, deleteSession } = useSessions();
  const { lang, toggle } = useLang();
  const navigate = useNavigate();

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-72 bg-surface-light border-r border-border flex flex-col shrink-0">
        <div className="p-4 border-b border-border flex items-center justify-between">
          <Link to="/" className="block">
            <h1 className="text-lg font-bold text-text-bright">BMAD Web Hub</h1>
            <p className="text-xs text-text-dim mt-0.5">
              {lang === 'ko' ? '브라우저 기반 BMAD 플랫폼' : 'Browser-based BMAD Platform'}
            </p>
          </Link>
          <button
            onClick={toggle}
            className="px-2 py-1 text-xs font-bold rounded border border-border hover:border-accent hover:text-accent text-text-dim transition-colors shrink-0"
            title={lang === 'ko' ? 'Switch to English' : '한국어로 전환'}
          >
            {lang === 'ko' ? 'ENG' : 'KOR'}
          </button>
        </div>

        <div className="p-3">
          <button
            onClick={() => navigate('/')}
            className="w-full py-2 px-3 bg-primary hover:bg-primary-dark text-white rounded-lg text-sm font-medium transition-colors"
          >
            {lang === 'ko' ? '+ 새 세션' : '+ New Session'}
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-2">
          {loading ? (
            <p className="text-center text-text-dim text-sm p-4">
              {lang === 'ko' ? '로딩 중...' : 'Loading...'}
            </p>
          ) : sessions.length === 0 ? (
            <p className="text-center text-text-dim text-sm p-4">
              {lang === 'ko' ? '세션이 없습니다' : 'No sessions yet'}
            </p>
          ) : (
            <ul className="space-y-1">
              {sessions.map((s) => (
                <li key={s.id}>
                  <Link
                    to={`/sessions/${s.id}`}
                    className="block p-2.5 rounded-lg hover:bg-surface-lighter transition-colors group"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-text-bright truncate">
                        {s.title || (lang === 'ko' ? '제목 없음' : 'Untitled')}
                      </span>
                      <button
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          deleteSession(s.id);
                        }}
                        className="opacity-0 group-hover:opacity-100 text-text-dim hover:text-error text-xs transition-opacity"
                      >
                        x
                      </button>
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`w-1.5 h-1.5 rounded-full ${s.status === 'in_progress' ? 'bg-success' : 'bg-text-dim'}`} />
                      <span className="text-xs text-text-dim truncate">{s.skill_name}</span>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </nav>

        <div className="p-3 border-t border-border">
          <Link
            to="/outputs"
            className="block text-center text-sm text-text-dim hover:text-accent transition-colors py-1"
          >
            {lang === 'ko' ? '산출물 보기' : 'View Outputs'}
          </Link>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}
