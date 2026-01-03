"""会话应用服务模块 (Session Application Service)

提供会话管理功能的应用服务层实现，负责会话的创建、查询、更新和删除操作。
采用依赖注入模式，通过SessionRepository进行数据持久化。

主要组件:
- SessionService: 会话服务类

功能特点:
- 会话的创建、列表查询
- 会话名称和模型配置更新
- 聊天记录清空
- 会话信息获取

使用示例:
    from services.session_service import SessionService
    from dependencies.container import get_container

    service = get_container().resolve('SessionService')

    # 创建新会话
    result = await service.create_session('我的旅行计划')

    # 列出所有会话
    sessions = await service.list_sessions()

    # 删除会话
    await service.delete_session('session-id')
"""

from typing import Dict, Any, List
from ..repositories.session_repository import SessionRepository


class SessionService:
    """
    会话应用服务类

    提供会话管理操作的业务逻辑层接口，负责协调会话数据的增删改查。
    采用依赖注入模式，通过SessionRepository访问底层数据存储。

    服务职责:
        - 创建新会话
        - 列出和查询会话
        - 更新会话配置（名称、模型）
        - 清空聊天记录
        - 获取会话详细信息

    错误处理:
        - 会话不存在时返回 {'success': False, 'error': '会话不存在'}
        - 操作成功时返回 {'success': True, ...}
    """

    def __init__(self, repository: SessionRepository):
        """
        初始化会话服务

        Args:
            repository: SessionRepository 会话仓储实例
        """
        self._repository = repository

    async def create_session(self, name: str = None) -> Dict[str, Any]:
        """
        创建新会话

        Args:
            name: str 可选的会话名称，默认值为"新会话"

        Returns:
            Dict: 操作结果
            {
                'success': bool,
                'session_id': str,  // 新创建的会话ID
                'name': str         // 会话名称
            }
        """
        session_id = await self._repository.create({
            'name': name or "新会话",
        })
        return {
            'success': True,
            'session_id': session_id,
            'name': name or "新会话"
        }

    async def list_sessions(self, include_empty: bool = False) -> Dict[str, Any]:
        """
        列出所有会话

        Args:
            include_empty: bool 是否包含空会话（无消息的会话），默认False

        Returns:
            Dict: 会话列表结果
            {
                'success': bool,
                'sessions': [...],  // 会话摘要列表
                'total': int        // 会话总数
            }
        """
        sessions = await self._repository.list_all(include_empty=include_empty)
        return {
            'success': True,
            'sessions': sessions,
            'total': len(sessions)
        }

    async def delete_session(self, session_id: str) -> Dict[str, Any]:
        """
        删除会话

        Args:
            session_id: str 要删除的会话ID

        Returns:
            Dict: 操作结果
            {'success': bool}
        """
        result = await self._repository.delete(session_id)
        if result:
            return {'success': True}
        return {'success': False, 'error': '会话不存在'}

    async def update_session_name(self, session_id: str, name: str) -> Dict[str, Any]:
        """
        更新会话名称

        Args:
            session_id: str 要更新的会话ID
            name: str 新的会话名称

        Returns:
            Dict: 操作结果
            {'success': bool, 'name': str}
        """
        session = await self._repository.get(session_id)
        if not session:
            return {'success': False, 'error': '会话不存在'}

        await self._repository.update(session_id, {'name': name})
        return {'success': True, 'name': name}

    async def update_session_model(self, session_id: str, model_id: str) -> Dict[str, Any]:
        """
        更新会话使用的模型

        Args:
            session_id: str 要更新的会话ID
            model_id: str 新的模型ID（如 'gpt-4o-mini'）

        Returns:
            Dict: 操作结果
            {'success': bool, 'model_id': str}
        """
        session = await self._repository.get(session_id)
        if not session:
            return {'success': False, 'error': '会话不存在'}

        await self._repository.update(session_id, {'model_id': model_id})
        return {'success': True, 'model_id': model_id}

    async def get_session_model(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话当前使用的模型

        Args:
            session_id: str 会话ID

        Returns:
            Dict: 模型信息
            {
                'success': bool,
                'model_id': str  // 当前使用的模型ID
            }
        """
        session = await self._repository.get(session_id)
        if not session:
            return {'success': False, 'error': '会话不存在'}

        return {
            'success': True,
            'model_id': session.get('model_id', 'gpt-4o-mini')
        }

    async def clear_chat(self, session_id: str) -> Dict[str, Any]:
        """
        清空会话的聊天记录

        将指定会话的消息列表清空，消息计数归零。

        Args:
            session_id: str 要清空的会话ID

        Returns:
            Dict: 操作结果
            {'success': bool}
        """
        session = await self._repository.get(session_id)
        if not session:
            return {'success': False, 'error': '会话不存在'}

        await self._repository.update(session_id, {
            'messages': [],
            'message_count': 0
        })
        return {'success': True}

    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话的完整信息

        Args:
            session_id: str 会话ID

        Returns:
            Dict: 会话详细信息
            {
                'success': bool,
                'session': {...}  // 完整的会话数据
            }
        """
        session = await self._repository.get(session_id)
        if not session:
            return {'success': False, 'error': '会话不存在'}

        return {
            'success': True,
            'session': session
        }
