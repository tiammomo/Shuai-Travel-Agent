"""LLM Factory Module - LLM工厂模块

本模块重新导出LLM客户端相关类，提供统一的导入接口。

使用此模块可以方便地导入所需的LLM客户端组件：

    from llm.factory import LLMClient, LLMClientFactory, ProtocolType, ModelManager

主要组件:
- LLMClient: 统一的LLM客户端封装
- LLMClientFactory: LLM客户端工厂类，用于创建适配器
- ProtocolType: 协议类型枚举
- ModelManager: 模型管理器

详细文档请参阅 llm/client.py 和 llm/manager.py
"""

from .client import LLMClient, LLMClientFactory, ProtocolType
from .manager import ModelManager, ModelInfo, ModelStatus

__all__ = ['LLMClient', 'LLMClientFactory', 'ProtocolType', 'ModelManager', 'ModelInfo', 'ModelStatus']
