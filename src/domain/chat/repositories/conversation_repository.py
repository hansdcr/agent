"""聊天领域 - 对话仓储接口"""

from abc import ABC, abstractmethod
from typing import Optional

from ..entities import Conversation
from ..value_objects import SessionId


class ConversationRepository(ABC):
    """对话仓储接口"""

    @abstractmethod
    async def save(self, conversation: Conversation) -> None:
        """保存对话"""
        pass

    @abstractmethod
    async def find_by_id(self, session_id: SessionId) -> Optional[Conversation]:
        """根据会话ID查找对话"""
        pass

    @abstractmethod
    async def delete(self, session_id: SessionId) -> None:
        """删除对话"""
        pass
