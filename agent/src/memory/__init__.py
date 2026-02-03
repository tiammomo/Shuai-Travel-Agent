# Memory Module - 记忆管理模块
#
# 提供完整的记忆管理解决方案，包括：
# - 短期记忆（对话历史）
# - 长期记忆（会话存档）
# - 重要性评分
# - 智能淘汰
# - 对话摘要
# - 用户画像
# - 分层存储
# - 记忆整合

# 核心管理器
from .manager import MemoryManager, Message, UserPreference

# 短期记忆优化
from .importance_scorer import ImportanceScorer, ImportanceScore, PriorityCalculator
from .eviction_manager import EvictionManager, EvictionStrategy, EvictionConfig, MemoryItem

# 对话摘要
from .summarizer import ConversationSummarizer, ConversationSummary, CompressionLevel

# 长期记忆优化
from .user_profile import UserProfileStore, UserProfile, UserPreference as EnhancedUserPreference, TravelHistory
from .hierarchical_store import HierarchicalMemoryStore, MemoryTier, SessionData, RetrievedMemory

# 记忆整合
from .consolidation import MemoryConsolidator, MemoryCluster, MemoryType, ConsolidationResult

__all__ = [
    # 核心
    'MemoryManager',
    'Message',
    'UserPreference',

    # 短期记忆
    'ImportanceScorer',
    'ImportanceScore',
    'PriorityCalculator',
    'EvictionManager',
    'EvictionStrategy',
    'EvictionConfig',
    'MemoryItem',

    # 摘要
    'ConversationSummarizer',
    'ConversationSummary',
    'CompressionLevel',

    # 长期记忆
    'UserProfileStore',
    'UserProfile',
    'TravelHistory',
    'HierarchicalMemoryStore',
    'MemoryTier',
    'SessionData',
    'RetrievedMemory',

    # 整合
    'MemoryConsolidator',
    'MemoryCluster',
    'MemoryType',
    'ConsolidationResult'
]
