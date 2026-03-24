import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '../api/types';

interface Props {
  message: Message;
}

export default function ChatMessage({ message }: Props) {
  if (message.role === 'system') {
    return (
      <div className="flex justify-center my-2">
        <div className="text-xs text-text-dim bg-surface-lighter px-3 py-1 rounded-full">
          {message.content}
        </div>
      </div>
    );
  }

  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-primary text-white rounded-br-sm'
            : 'bg-surface-light border border-border rounded-bl-sm'
        }`}
      >
        {isUser ? (
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="markdown-content text-sm">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}
        <p className={`text-[10px] mt-1 ${isUser ? 'text-white/60' : 'text-text-dim'}`}>
          {new Date(message.created_at).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}
