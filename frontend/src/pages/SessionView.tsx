import { useParams } from 'react-router-dom';
import { useWebSocket } from '../hooks/useWebSocket';
import MessageList from '../components/MessageList';
import ChatInput from '../components/ChatInput';

export default function SessionView() {
  const { id } = useParams<{ id: string }>();
  const { messages, streamingText, isConnected, isStreaming, session, activeTool, sendMessage, cancel, usage } =
    useWebSocket(id);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="border-b border-border px-4 py-3 bg-surface-light flex items-center justify-between shrink-0">
        <div>
          <h2 className="text-sm font-semibold text-text-bright">
            {session?.title || 'Loading...'}
          </h2>
          <p className="text-xs text-text-dim">{session?.skill_name}</p>
        </div>
        <div className="flex items-center gap-3">
          {usage?.cost_usd != null && (
            <span className="text-xs text-text-dim">
              ${usage.cost_usd.toFixed(4)}
            </span>
          )}
          <span
            className={`w-2 h-2 rounded-full ${isConnected ? 'bg-success' : 'bg-error'}`}
            title={isConnected ? 'Connected' : 'Disconnected'}
          />
        </div>
      </header>

      {/* Messages */}
      <MessageList
        messages={messages}
        streamingText={streamingText}
        isStreaming={isStreaming}
        activeTool={activeTool}
      />

      {/* Input */}
      <ChatInput
        onSend={sendMessage}
        onCancel={cancel}
        disabled={!isConnected || isStreaming}
        isStreaming={isStreaming}
      />
    </div>
  );
}
