"""依赖注入容器模块 (Dependency Injection Container)

本模块提供简单的依赖注入容器实现，用于管理应用程序中的服务实例。
采用单例模式和提供者模式，实现服务的注册、解析和生命周期管理。

主要组件:
- Container: 依赖注入容器核心类

功能特点:
- 支持单例和非单例模式的依赖注册
- 自动管理实例生命周期
- 支持延迟初始化
- 提供全局容器访问点

使用示例:
    from dependencies.container import get_container

    container = get_container()

    # 获取服务实例
    session_service = container.resolve('SessionService')
    chat_service = container.resolve('ChatService')

    # 注册新服务
    container.register('CustomService', custom_provider, singleton=True)

设计模式:
- 单例模式 (Singleton): 全局容器实例
- 工厂模式 (Factory): 依赖提供者
- 依赖注入 (Dependency Injection): 通过构造函数注入依赖
"""

from typing import Dict, Any, Callable


class Container:
    """
    依赖注入容器核心类

    管理应用程序中所有服务的注册和解析，支持单例和非单例两种模式。

    容器工作流程:
    1. 启动时注册所有服务提供者
    2. 解析时根据提供者创建实例
    3. 单例模式缓存实例，复用已创建的实例
    4. 非每次创建新实例

    属性:
        _providers: Dict[str, Callable] 服务提供者字典，key为服务名，value为(提供者函数, 是否单例)
        _instances: Dict[str, Any] 已创建的实例字典，用于单例模式缓存
    """

    def __init__(self):
        """
        初始化依赖注入容器
        """
        # 服务提供者字典：{(provider_fn, singleton_bool)}
        self._providers: Dict[str, tuple[Callable, bool]] = {}
        # 已创建的实例字典：{service_name: instance}
        self._instances: Dict[str, Any] = {}

    def register(self, name: str, provider: Callable, singleton: bool = True) -> None:
        """
        注册依赖服务提供者

        Args:
            name: str 服务名称，用于后续解析的标识符
            provider: Callable 服务提供者函数，无参数调用返回服务实例
            singleton: bool 是否单例模式，True则缓存实例复用，False则每次创建新实例
        """
        self._providers[name] = (provider, singleton)

    def resolve(self, name: str) -> Any:
        """
        解析并获取服务实例

        根据服务名称从容器中获取对应的服务实例。
        如果是单例模式且已存在缓存实例，直接返回缓存。
        否则调用提供者函数创建新实例。

        Args:
            name: str 要解析的服务名称

        Returns:
            Any: 服务实例对象

        Raises:
            ValueError: 服务未注册时抛出
        """
        if name not in self._providers:
            raise ValueError(f"Dependency not found: {name}")

        provider, singleton = self._providers[name]

        # 单例模式：返回缓存的实例
        if singleton and name in self._instances:
            return self._instances[name]

        # 创建新实例
        instance = provider()

        # 单例模式：缓存实例
        if singleton:
            self._instances[name] = instance

        return instance


# 全局容器实例
_container: Container = None


def get_container() -> Container:
    """
    获取全局依赖注入容器实例

    提供全局访问点，确保整个应用程序共享同一个容器实例。
    首次调用时自动创建容器并注册默认服务提供者。

    Returns:
        Container: 全局容器实例

    初始化流程:
    1. 检查是否已存在容器实例
    2. 不存在则创建新Container实例
    3. 调用_setup_default_providers()注册默认服务
    4. 返回容器实例
    """
    global _container
    if _container is None:
        _container = Container()
        _setup_default_providers()
    return _container


def _setup_default_providers() -> None:
    """
    设置默认服务提供者

    预注册应用程序核心服务到容器中：
    - SessionRepository: 会话数据仓储
    - SessionService: 会话管理服务
    - ChatService: 聊天服务
    - TravelAgent: 旅游规划Agent

    使用延迟导入避免循环依赖问题。
    """
    from .providers import (
        provide_session_repository,
        provide_session_service,
        provide_chat_service,
        provide_travel_agent
    )

    container = get_container()

    # 注册核心服务
    container.register('SessionRepository', provide_session_repository)
    container.register('SessionService', provide_session_service)
    container.register('ChatService', provide_chat_service)
    container.register('TravelAgent', provide_travel_agent)
