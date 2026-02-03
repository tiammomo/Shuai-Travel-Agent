/**
 * MessageList 组件基本测试
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { useChatStore } from '@/stores/chat';
import type { Message } from '@/types';

describe('MessageList 基本测试', () => {
  beforeEach(() => {
    useChatStore.setState({
      messages: [],
      streamingMessage: '',
      streamingReasoning: '',
      isStreaming: false,
      isThinking: false,
      reasoningExpanded: {},
    });
  });

  describe('Store 测试', () => {
    it('addMessage 应该添加用户消息', () => {
      const message: Message = { role: 'user', content: 'Hello', timestamp: '10:00' };
      useChatStore.getState().addMessage(message);
      expect(useChatStore.getState().messages).toHaveLength(1);
      expect(useChatStore.getState().messages[0].content).toBe('Hello');
    });

    it('addMessage 应该添加助手消息', () => {
      const message: Message = { role: 'assistant', content: 'Hi there!', timestamp: '10:01' };
      useChatStore.getState().addMessage(message);
      expect(useChatStore.getState().messages).toHaveLength(1);
      expect(useChatStore.getState().messages[0].role).toBe('assistant');
    });

    it('addMessage 应该追加多条消息', () => {
      useChatStore.getState().addMessage({ role: 'user', content: '问题1', timestamp: '10:00' });
      useChatStore.getState().addMessage({ role: 'assistant', content: '回答1', timestamp: '10:01' });
      useChatStore.getState().addMessage({ role: 'user', content: '问题2', timestamp: '10:02' });
      expect(useChatStore.getState().messages).toHaveLength(3);
    });
  });

  describe('流式状态测试', () => {
    it('streamingMessage 应该可设置', () => {
      useChatStore.setState({ streamingMessage: '流式响应中...' });
      expect(useChatStore.getState().streamingMessage).toBe('流式响应中...');
    });

    it('streamingReasoning 应该可设置', () => {
      useChatStore.setState({ streamingReasoning: '思考中...' });
      expect(useChatStore.getState().streamingReasoning).toBe('思考中...');
    });

    it('isThinking 状态应该可切换', () => {
      useChatStore.setState({ isThinking: true });
      expect(useChatStore.getState().isThinking).toBe(true);
    });
  });

  describe('思考展开测试', () => {
    it('toggleReasoning 应该切换展开状态', () => {
      useChatStore.setState({ reasoningExpanded: {} });
      useChatStore.getState().toggleReasoning('msg-1');
      expect(useChatStore.getState().reasoningExpanded['msg-1']).toBe(true);

      useChatStore.getState().toggleReasoning('msg-1');
      expect(useChatStore.getState().reasoningExpanded['msg-1']).toBe(false);
    });

    it('不同消息的展开状态应该独立', () => {
      useChatStore.setState({ reasoningExpanded: {} });
      useChatStore.getState().toggleReasoning('msg-1');
      useChatStore.getState().toggleReasoning('msg-2');

      expect(useChatStore.getState().reasoningExpanded['msg-1']).toBe(true);
      expect(useChatStore.getState().reasoningExpanded['msg-2']).toBe(true);
    });

    it('展开一个不应该影响另一个', () => {
      useChatStore.setState({ reasoningExpanded: { 'msg-1': true } });
      useChatStore.getState().toggleReasoning('msg-2');

      expect(useChatStore.getState().reasoningExpanded['msg-1']).toBe(true);
      expect(useChatStore.getState().reasoningExpanded['msg-2']).toBe(true);
    });
  });

  describe('重置测试', () => {
    it('reset 应该清空所有状态', () => {
      useChatStore.setState({
        messages: [{ role: 'user', content: 'test', timestamp: '10:00' }],
        streamingMessage: '流式',
        streamingReasoning: '思考',
        isStreaming: true,
        isThinking: true,
        error: '错误',
      });

      useChatStore.getState().reset();

      expect(useChatStore.getState().messages).toHaveLength(0);
      expect(useChatStore.getState().streamingMessage).toBe('');
      expect(useChatStore.getState().streamingReasoning).toBe('');
      expect(useChatStore.getState().isStreaming).toBe(false);
      expect(useChatStore.getState().isThinking).toBe(false);
      expect(useChatStore.getState().error).toBeNull();
    });
  });
});
