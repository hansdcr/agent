"""基础设施层 - 内存对话仓储实现"""

from typing import Dict, Optional

from src.domain.chat.entities import Conversation
from src.domain.chat.repositories import ConversationRepository
from src.domain.chat.value_objects import SessionId


class InMemoryConversationRepository(ConversationRepository):
    """内存对话仓储实现"""

    def __init__(self):
        self._storage: Dict[str, Conversation] = {}

    async def save(self, conversation: Conversation) -> None:
        """保存对话"""
        self._storage[conversation.session_id.value] = conversation

    async def find_by_id(self, session_id: SessionId) -> Optional[Conversation]:
        """根据会话ID查找对话"""
        return self._storage.get(session_id.value)

    async def delete(self, session_id: SessionId) -> None:
        """删除对话"""
        if session_id.value in self._storage:
            del self._storage[session_id.value]
