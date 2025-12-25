import React from 'react';
import { Card } from 'antd';
import { Message } from '../types';
import ReactMarkdown from 'react-markdown';
import type { Components } from 'react-markdown';

interface Props {
  messages: Message[];
  streamingMessage?: string;
}

// 清理文本中的多余空行和格式问题
const cleanContent = (content: string): string => {
  return content
    // 移除连续的空行（2个或更多换行符变为1个）
    .replace(/\n{2,}/g, '\n')
    // 移除行尾空格
    .replace(/[ \t]+$/gm, '')
    // 移除开头和结尾的空白
    .trim();
};

// 自定义Markdown组件渲染，优化间距
const markdownComponents: Components = {
  // 段落：无间距
  p: ({ children }) => <p style={{ margin: 0, padding: 0 }}>{children}</p>,
  // 列表项：无间距
  li: ({ children }) => <li style={{ margin: 0, padding: 0, lineHeight: 1.4 }}>{children}</li>,
  // 标题：最小间距
  h1: ({ children }) => <h1 style={{ margin: '4px 0 2px 0', fontSize: '1.5em', fontWeight: 600, lineHeight: 1.2 }}>{children}</h1>,
  h2: ({ children }) => <h2 style={{ margin: '4px 0 2px 0', fontSize: '1.3em', fontWeight: 600, lineHeight: 1.2 }}>{children}</h2>,
  h3: ({ children }) => <h3 style={{ margin: '4px 0 2px 0', fontSize: '1.1em', fontWeight: 600, lineHeight: 1.2 }}>{children}</h3>,
  // 列表：最小间距
  ol: ({ children }) => <ol style={{ margin: '2px 0', paddingLeft: '20px' }}>{children}</ol>,
  ul: ({ children }) => <ul style={{ margin: '2px 0', paddingLeft: '20px' }}>{children}</ul>,
};

const MessageList: React.FC<Props> = ({ messages, streamingMessage }) => {
  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', width: '100%' }}>
      {messages.map((msg, index) => (
        <div
          key={index}
          style={{
            display: 'flex',
            justifyContent: 'center',
            marginBottom: '6px',
          }}
        >
          <Card
            className={`chat-message ${msg.role}`}
            style={{
              width: '100%',
              background: msg.role === 'user'
                ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                : '#f0f2f6',
              color: msg.role === 'user' ? 'white' : '#262730',
              borderRadius: '8px',
            }}
            bodyStyle={{ padding: '12px 16px' }}
          >
            <div className="chat-message-content">
              <ReactMarkdown components={markdownComponents}>
                {cleanContent(msg.content)}
              </ReactMarkdown>
            </div>
            <div className="chat-message-time">{msg.timestamp}</div>
          </Card>
        </div>
      ))}
      
      {streamingMessage && (
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '6px' }}>
          <Card
            className="chat-message assistant"
            style={{
              width: '100%',
              background: '#f0f2f6',
              color: '#262730',
              borderRadius: '8px',
            }}
            bodyStyle={{ padding: '12px 16px' }}
          >
            <div className="chat-message-content">
              <ReactMarkdown components={markdownComponents}>
                {cleanContent(streamingMessage)}
              </ReactMarkdown>
            </div>
            {streamingMessage !== '🤔 正在思考中...' && (
              <span className="thinking-indicator">●</span>
            )}
          </Card>
        </div>
      )}
    </div>
  );
};

export default MessageList;
