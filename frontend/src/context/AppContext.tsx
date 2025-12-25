import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Message, AppConfig } from '../types';

interface AppState {
  // 配置
  config: AppConfig;
  setConfig: (config: AppConfig) => void;
  
  // 会话
  currentSessionId: string | null;
  setCurrentSessionId: (id: string | null) => void;
  switchSession: (id: string | null) => void;  // 切换会话，保留消息
  
  // 消息
  messages: Message[];
  addMessage: (message: Message) => void;
  clearMessages: () => void;
  setMessages: (messages: Message[]) => void;
  
  // 流式控制
  isStreaming: boolean;
  setIsStreaming: (streaming: boolean) => void;
  stopStreaming: boolean;
  setStopStreaming: (stop: boolean) => void;
}

const AppContext = createContext<AppState | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [config, setConfig] = useState<AppConfig>({
    apiBase: 'http://localhost:8000'
  });
  
  const [currentSessionId, setCurrentSessionIdState] = useState<string | null>(null);
  const [messages, setMessagesState] = useState<Message[]>([]);
  // 会话消息缓存：保存每个会话的消息列表
  const [sessionMessages, setSessionMessages] = useState<Record<string, Message[]>>({});
  
  const [isStreaming, setIsStreaming] = useState(false);
  const [stopStreaming, setStopStreaming] = useState(false);
  
  const addMessage = (message: Message) => {
    setMessagesState(prev => {
      const newMessages = [...prev, message];
      // 同时更新缓存
      if (currentSessionId) {
        setSessionMessages(cache => ({
          ...cache,
          [currentSessionId]: newMessages
        }));
      }
      return newMessages;
    });
  };
  
  const clearMessages = () => {
    setMessagesState([]);
    // 清空当前会话的缓存
    if (currentSessionId) {
      setSessionMessages(cache => ({
        ...cache,
        [currentSessionId]: []
      }));
    }
  };
  
  const setMessages = (newMessages: Message[]) => {
    setMessagesState(newMessages);
    // 更新缓存
    if (currentSessionId) {
      setSessionMessages(cache => ({
        ...cache,
        [currentSessionId]: newMessages
      }));
    }
  };

  // 设置当前会话（不切换消息）
  const setCurrentSessionId = (id: string | null) => {
    setCurrentSessionIdState(id);
  };

  // 切换会话（保留消息）
  const switchSession = (id: string | null) => {
    // 保存当前会话的消息
    if (currentSessionId && messages.length > 0) {
      setSessionMessages(cache => ({
        ...cache,
        [currentSessionId]: messages
      }));
    }
    
    // 切换到新会话
    setCurrentSessionIdState(id);
    
    // 加载新会话的消息（如果有缓存）
    if (id && sessionMessages[id]) {
      setMessagesState(sessionMessages[id]);
    } else {
      setMessagesState([]);
    }
  };
  
  const value: AppState = {
    config,
    setConfig,
    currentSessionId,
    setCurrentSessionId,
    switchSession,
    messages,
    addMessage,
    clearMessages,
    setMessages,
    isStreaming,
    setIsStreaming,
    stopStreaming,
    setStopStreaming,
  };
  
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

export const useAppContext = (): AppState => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
};
