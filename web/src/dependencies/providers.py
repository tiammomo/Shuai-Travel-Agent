"""依赖提供者模块 (Dependency Providers)

提供依赖注入容器所需的服务提供者函数。
每个提供者函数负责创建并返回对应的服务实例。

主要组件:
- provide_session_repository(): 提供会话仓储实例
- provide_session_service(): 提供会话服务实例
- provide_chat_service(): 提供聊天服务实例
- provide_travel_agent(): 提供旅游Agent实例

功能特点:
- 延迟初始化：服务实例在使用时才创建
- 依赖链管理：自动处理服务之间的依赖关系
- 配置路径处理：动态计算配置文件路径

使用示例:
    from dependencies.providers import (
        provide_session_repository,
        provide_session_service,
        provide_travel_agent
    )

    # 获取会话仓储
    repository = provide_session_repository()

    # 获取会话服务（自动注入仓储）
    service = provide_session_service()

    # 获取旅游Agent
    agent = provide_travel_agent()

设计说明:
    提供者模式遵循以下原则：
    1. 每个提供者是一个无参数的工厂函数
    2. 返回值类型标注用于类型检查
    3. 内部处理所有依赖创建逻辑
    4. 支持延迟导入避免循环依赖
"""

import sys
import os

# 将 agent 模块的 src 目录添加到 Python 路径
# 这样可以正确导入 agent 模块中的类
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        '..', '..', 'agent', 'src'
    )
)

from ..repositories.session_repository_impl import SessionRepositoryImpl
from ..services.session_service import SessionService
from ..services.chat_service import ChatService
from ..storage.session_storage import MemorySessionStorage


def provide_session_repository() -> SessionRepositoryImpl:
    """
    提供会话仓储实例

    创建基于内存存储的会话仓储实现。
    每次调用创建新的仓储实例。

    Returns:
        SessionRepositoryImpl: 会话仓储实例
    """
    storage = MemorySessionStorage()
    return SessionRepositoryImpl(storage)


def provide_session_service() -> SessionService:
    """
    提供会话服务实例

    自动创建并注入会话仓储依赖。
    每次调用创建新的服务实例。

    Returns:
        SessionService: 会话服务实例
    """
    repository = provide_session_repository()
    return SessionService(repository)


def provide_chat_service() -> ChatService:
    """
    提供聊天服务实例

    自动创建并注入会话仓储依赖。
    每次调用创建新的服务实例。

    Returns:
        ChatService: 聊天服务实例
    """
    repository = provide_session_repository()
    return ChatService(repository)


def provide_travel_agent():
    """
    提供旅游Agent实例

    连接后端gRPC服务的旅游规划Agent。
    使用配置文件的路径动态计算。

    Returns:
        ReActTravelAgent: 旅游Agent实例

    路径说明:
        从 web/src/dependencies 目录向上查找：
        - ../../agent/config/llm_config.yaml
    """
    from core.travel_agent import ReActTravelAgent

    # 动态计算配置文件路径
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        '..', '..', 'agent', 'config', 'llm_config.yaml'
    )
    return ReActTravelAgent(config_path=config_path)
