export interface SkillMeta {
  name: string;
  display_name: string;
  description: string;
  type: 'skill' | 'agent';
  icon: string;
  module: string;
  role: string;
  capabilities: string;
  has_workflow: boolean;
}

export interface Session {
  id: string;
  type: string | null;
  skill_name: string | null;
  title: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
  status: string;
  claude_session_id: string | null;
  output_file: string | null;
  message_count: number;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

// WebSocket message types
export interface WSSessionInit {
  type: 'session_init';
  session: Session;
  messages: Message[];
}

export interface WSAssistantChunk {
  type: 'assistant_chunk';
  text: string;
}

export interface WSAssistantEnd {
  type: 'assistant_end';
  content: string;
  usage: {
    cost_usd?: number;
    duration_ms?: number;
  };
}

export interface WSError {
  type: 'error';
  message: string;
}

export interface WSOutputDetected {
  type: 'output_detected';
  file: string;
  category: string;
}

export interface WSAssistantStart {
  type: 'assistant_start';
}

export interface WSToolUse {
  type: 'tool_use';
  tool: string;
}

export type WSIncoming =
  | WSSessionInit
  | WSAssistantStart
  | WSAssistantChunk
  | WSAssistantEnd
  | WSError
  | WSOutputDetected
  | WSToolUse;
