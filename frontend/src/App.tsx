import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { LangProvider } from './hooks/useLang';
import ErrorBoundary from './components/ErrorBoundary';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import SessionView from './pages/SessionView';
import OutputViewer from './pages/OutputViewer';

export default function App() {
  return (
    <ErrorBoundary>
      <LangProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<Layout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/sessions/:id" element={<SessionView />} />
              <Route path="/outputs" element={<OutputViewer />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </LangProvider>
    </ErrorBoundary>
  );
}
