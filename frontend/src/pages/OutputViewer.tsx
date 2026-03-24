import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { api } from '../api/client';

interface OutputFile {
  path: string;
  name: string;
  category: string;
  size: number;
  modified: number;
}

export default function OutputViewer() {
  const [files, setFiles] = useState<OutputFile[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.outputs
      .list()
      .then(setFiles)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selected) {
      setContent('');
      return;
    }
    api.outputs.get(selected).then(setContent);
  }, [selected]);

  const grouped = files.reduce<Record<string, OutputFile[]>>((acc, f) => {
    if (!acc[f.category]) acc[f.category] = [];
    acc[f.category].push(f);
    return acc;
  }, {});

  return (
    <div className="flex h-full">
      {/* File list */}
      <div className="w-72 border-r border-border overflow-y-auto p-4 shrink-0">
        <h2 className="text-sm font-semibold text-text-bright mb-4">Output Artifacts</h2>
        {loading ? (
          <p className="text-text-dim text-sm">Loading...</p>
        ) : files.length === 0 ? (
          <p className="text-text-dim text-sm">No outputs yet.</p>
        ) : (
          Object.entries(grouped).map(([cat, catFiles]) => (
            <div key={cat} className="mb-4">
              <p className="text-xs text-text-dim uppercase tracking-wider mb-2">{cat}</p>
              <ul className="space-y-1">
                {catFiles.map((f) => (
                  <li key={f.path}>
                    <button
                      onClick={() => setSelected(f.path)}
                      className={`w-full text-left text-sm px-2 py-1.5 rounded transition-colors ${
                        selected === f.path
                          ? 'bg-primary/20 text-accent'
                          : 'text-text hover:bg-surface-lighter'
                      }`}
                    >
                      {f.name}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ))
        )}
      </div>

      {/* Content viewer */}
      <div className="flex-1 overflow-y-auto p-8">
        {content ? (
          <div className="max-w-3xl mx-auto markdown-content">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="text-text-dim">Select an output to view</p>
          </div>
        )}
      </div>
    </div>
  );
}
