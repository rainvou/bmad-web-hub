import { useCallback, useEffect, useRef, useState } from 'react';
import type { Message, WSIncoming, Session } from '../api/types';

interface UseWebSocketReturn {
  messages: Message[];
  streamingText: string;
  isConnected: boolean;
  isStreaming: boolean;
  session: Session | null;
  activeTool: string | null;
  sendMessage: (content: string) => void;
  cancel: () => void;
  usage: { cost_usd?: number; duration_ms?: number } | null;
}

export function useWebSocket(sessionId: string | undefined): UseWebSocketReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [streamingText, setStreamingText] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [session, setSession] = useState<Session | null>(null);
  const [usage, setUsage] = useState<{ cost_usd?: number; duration_ms?: number } | null>(null);
  const [activeTool, setActiveTool] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/${sessionId}`);
    wsRef.current = ws;

    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => {
      setIsConnected(false);
      setIsStreaming(false);
      setActiveTool(null);
    };
    ws.onerror = () => {
      console.error('WebSocket connection error');
    };

    ws.onmessage = (event) => {
      try {
        const data: WSIncoming = JSON.parse(event.data);

        switch (data.type) {
          case 'session_init':
            setSession(data.session);
            setMessages(data.messages);
            break;

          case 'assistant_start':
            setIsStreaming(true);
            setStreamingText('');
            setActiveTool(null);
            break;

          case 'assistant_chunk':
            setActiveTool(null);
            setStreamingText((prev) => prev + data.text);
            break;

          case 'assistant_end':
            setIsStreaming(false);
            setActiveTool(null);
            setUsage(data.usage);
            if (data.content) {
              setMessages((prev) => [
                ...prev,
                {
                  id: Math.random().toString(36).slice(2) + Date.now().toString(36),
                  session_id: sessionId,
                  role: 'assistant',
                  content: data.content,
                  created_at: new Date().toISOString(),
                },
              ]);
            }
            setStreamingText('');
            break;

          case 'tool_use':
            setActiveTool(data.tool);
            break;

          case 'title_updated':
            setSession((prev) => prev ? { ...prev, title: data.title } : prev);
            break;

          case 'error':
            setIsStreaming(false);
            setActiveTool(null);
            setStreamingText('');
            console.error('WS Error:', data.message);
            setMessages((prev) => [
              ...prev,
              {
                id: Math.random().toString(36).slice(2) + Date.now().toString(36),
                session_id: sessionId,
                role: 'system',
                content: `Error: ${data.message}`,
                created_at: new Date().toISOString(),
              },
            ]);
            break;

          case 'output_detected':
            setMessages((prev) => [
              ...prev,
              {
                id: Math.random().toString(36).slice(2) + Date.now().toString(36),
                session_id: sessionId,
                role: 'system',
                content: `New output: ${data.file} (${data.category})`,
                created_at: new Date().toISOString(),
              },
            ]);
            break;
        }
      } catch (e) {
        console.error('Failed to parse WS message:', e);
      }
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [sessionId]);

  const sendMessage = useCallback(
    (content: string) => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

      setMessages((prev) => [
        ...prev,
        {
          id: Math.random().toString(36).slice(2) + Date.now().toString(36),
          session_id: sessionId || '',
          role: 'user',
          content,
          created_at: new Date().toISOString(),
        },
      ]);

      wsRef.current.send(JSON.stringify({ type: 'user_message', content }));
    },
    [sessionId],
  );

  const cancel = useCallback(() => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    wsRef.current.send(JSON.stringify({ type: 'cancel' }));
  }, []);

  return { messages, streamingText, isConnected, isStreaming, session, activeTool, sendMessage, cancel, usage };
}
