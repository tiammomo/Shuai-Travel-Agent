"""Chat application service - 聊天服务模块

提供聊天功能的应用服务层实现，负责消息的保存、检索和流式响应生成。

主要组件:
- ChatService: 聊天服务类

功能特点:
- 消息的持久化存储
- 会话管理
- SSE流式响应生成
- 过期会话清理

使用示例:
    from src.services.chat_service import ChatService

    service = ChatService(repository=session_repository)

    # 保存消息
    await service.save_message(session_id, 'user', '你好')

    # 获取消息
    result = await service.get_messages(session_id)

    # 生成流式响应
    async for chunk in service.generate_chat_stream(session_id, message, agent):
        print(chunk)
"""

import uuid
from typing import Dict, Any, AsyncGenerator
from ..repositories.session_repository import SessionRepository


class ChatService:
    """
    聊天服务类

    提供聊天功能的应用服务层接口，负责协调消息存储和会话管理。
    采用依赖注入模式，通过SessionRepository进行数据持久化。

    服务职责:
        - 消息的创建、读取、更新
        - 会话的创建和管理
        - SSE流式响应的生成
        - 过期会话的清理

    事件类型 (SSE流式响应):
        - session_id: 会话ID分配事件
        - reasoning_start: 思考开始事件
        - reasoning_chunk: 思考内容事件
        - reasoning_end: 思考结束事件
        - answer_start: 答案开始事件
        - chunk: 答案内容块事件
        - done: 完成事件
    """

    def __init__(self, repository: SessionRepository):
        """
        初始化聊天服务

        Args:
            repository: SessionRepository 会话仓储实例
        """
        self._repository = repository

    async def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        reasoning: str = None
    ) -> Dict[str, Any]:
        """
        保存消息到会话

        Args:
            session_id: str 会话ID
            role: str 消息角色，'user'或'assistant'
            content: str 消息内容
            reasoning: str 可选的思考过程

        Returns:
            Dict: 操作结果 {'success': bool}
        """
        session = await self._repository.get(session_id)
        if not session:
            return {'success': False, 'error': '会话不存在'}

        message = {
            'role': role,
            'content': content,
            'reasoning': reasoning,
            'timestamp': self._get_timestamp(),
        }

        messages = session.get('messages', [])
        messages.append(message)
        session['messages'] = messages
        session['message_count'] = len(messages)
        session['last_active'] = self._get_timestamp()

        await self._repository.update(session_id, session)
        return {'success': True}

    async def get_messages(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话的所有消息

        Args:
            session_id: str 会话ID

        Returns:
            Dict: {'success': bool, 'messages': [...]}
        """
        session = await self._repository.get(session_id)
        if not session:
            return {'success': False, 'error': '会话不存在', 'messages': []}

        messages = session.get('messages', [])
        return {'success': True, 'messages': messages}

    def _get_timestamp(self) -> str:
        """
        获取当前时间戳

        Returns:
            str: 格式化为 HH:MM:SS 的时间字符串
        """
        from datetime import datetime
        return datetime.now().strftime('%H:%M:%S')

    async def cleanup_expired_sessions(self, max_age_seconds: int = 86400) -> int:
        """
        清理过期会话

        Args:
            max_age_seconds: int 会话最大存活时间，默认24小时

        Returns:
            int: 清理的会话数量
        """
        return await self._repository.cleanup_expired(max_age_seconds)

    async def generate_chat_stream(
        self,
        session_id: str,
        message: str,
        agent
    ) -> AsyncGenerator[str, None]:
        """
        生成聊天流式响应

        核心方法，生成SSE格式的流式响应。
        工作流程:
            1. 确保会话存在
            2. 保存用户消息
            3. 发送思考开始事件
            4. 调用Agent处理消息
            5. 发送思考内容
            6. 流式发送答案
            7. 保存助手消息
            8. 发送完成事件

        Args:
            session_id: str 会话ID
            message: str 用户消息
            agent: Agent Agent实例

        Yields:
            str: SSE格式的数据行
        """
        import json

        # 确保会话存在
        if not session_id:
            result = await self.create_session_for_chat()
            session_id = result['session_id']
            yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"

        # 保存用户消息
        await self.save_message(session_id, 'user', message)

        # 发送思考开始事件
        yield f"data: {json.dumps({'type': 'reasoning_start'})}\n\n"

        # 调用Agent处理消息
        result = await agent.process(message)

        # 发送思考内容
        if result.get('reasoning'):
            reasoning_text = result.get('reasoning', {}).get('text', '')
            yield f"data: {json.dumps({'type': 'reasoning_chunk', 'content': reasoning_text})}\n\n"

        # 发送思考结束事件
        yield f"data: {json.dumps({'type': 'reasoning_end'})}\n\n"

        # 发送答案开始事件
        yield f"data: {json.dumps({'type': 'answer_start'})}\n\n"

        # 获取答案
        answer = result.get('answer', '')

        # 流式发送答案（逐字符）
        for char in answer:
            yield f"data: {json.dumps({'type': 'chunk', 'content': char})}\n\n"

        # 保存助手消息
        await self.save_message(session_id, 'assistant', answer, result.get('reasoning', {}).get('text', ''))

        # 发送完成事件
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    async def create_session_for_chat(self) -> Dict[str, Any]:
        """
        为聊天创建新会话

        Returns:
            Dict: {'success': bool, 'session_id': str}
        """
        from datetime import datetime
        now = datetime.now().isoformat()
        session_id = str(uuid.uuid4())

        session = {
            'session_id': session_id,
            'created_at': now,
            'last_active': now,
            'message_count': 0,
            'name': f"会话 {now[:10]}",
            'model_id': 'gpt-4o-mini',
            'messages': [],
            'user_preferences': {},
        }

        await self._repository.create(session)
        return {'success': True, 'session_id': session_id}
