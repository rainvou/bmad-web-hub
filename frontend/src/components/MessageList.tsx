import { useEffect, useRef } from 'react';
import type { Message } from '../api/types';
import ChatMessage from './ChatMessage';
import StreamingText from './StreamingText';

interface Props {
  messages: Message[];
  streamingText: string;
  isStreaming: boolean;
  activeTool: string | null;
}

export default function MessageList({ messages, streamingText, isStreaming, activeTool }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingText, activeTool]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      {messages.length === 0 && !isStreaming && (
        <div className="flex items-center justify-center h-full">
          <p className="text-text-dim text-sm">Send a message to start the conversation.</p>
        </div>
      )}

      {messages.map((msg) => (
        <ChatMessage key={msg.id} message={msg} />
      ))}

      {isStreaming && streamingText && <StreamingText text={streamingText} />}

      {isStreaming && !streamingText && (
        <div className="flex justify-start mb-4">
          <div className="rounded-2xl rounded-bl-sm px-4 py-3 bg-surface-light border border-border">
            <div className="flex items-center gap-2 text-sm text-text-dim">
              <span className="inline-block w-2 h-2 bg-accent rounded-full animate-pulse" />
              {activeTool ? (
                <span>Using <span className="text-accent font-mono">{activeTool}</span>...</span>
              ) : (
                <span>Thinking...</span>
              )}
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
