// 类型定义
export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface SessionInfo {
  session_id: string;
  message_count: number;
  last_active: string;
  name?: string;  // 会话名称（可选）
}

export interface AppConfig {
  apiBase: string;
}

export interface ChatRequest {
  message: string;
  session_id: string;
}

export interface ChatResponse {
  success: boolean;
  response?: string;
  error?: string;
  session_id?: string;
}
