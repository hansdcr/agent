"""基础设施层 - 对话仓储实现"""

from typing import Dict, Optional, List
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.domain.chat.entities import Conversation
from src.domain.chat.repositories import ConversationRepository
from src.domain.chat.value_objects import SessionId
from src.infrastructure.persistence.models import ConversationModel


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


class PostgresConversationRepository(ConversationRepository):
    """PostgreSQL对话仓储实现"""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def save(self, conversation: Conversation) -> None:
        """保存对话"""
        async with self._session_factory() as session:
            # 查找是否已存在
            stmt = select(ConversationModel).where(
                ConversationModel.session_id == conversation.session_id.value
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # 更新现有记录
                existing.user_id = getattr(conversation, 'user_id', existing.user_id)
                existing.agent_id = getattr(conversation, 'agent_id', existing.agent_id)
                existing.system_prompt = conversation.system_prompt
                existing.messages = conversation.get_messages_as_dicts()
                existing.message_count = conversation.message_count()
            else:
                # 创建新记录
                model = ConversationModel.from_entity(conversation)
                session.add(model)

            await session.commit()

    async def find_by_id(self, session_id: SessionId) -> Optional[Conversation]:
        """根据会话ID查找对话"""
        async with self._session_factory() as session:
            stmt = select(ConversationModel).where(
                ConversationModel.session_id == session_id.value
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                return model.to_entity()
            return None

    async def find_by_user_and_agent(
        self, user_id: str, agent_id: str
    ) -> Optional[Conversation]:
        """根据用户ID和Agent ID查找今天的对话"""
        async with self._session_factory() as session:
            # 获取今天的开始时间（UTC）
            now = datetime.now(timezone.utc)
            today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

            stmt = (
                select(ConversationModel)
                .where(ConversationModel.user_id == user_id)
                .where(ConversationModel.agent_id == agent_id)
                .where(ConversationModel.created_at >= today_start)
                .order_by(ConversationModel.updated_at.desc())
                .limit(1)
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                return model.to_entity()
            return None

    async def find_all_by_user_and_agent(
        self, user_id: str, agent_id: str, limit: int = 50
    ) -> List[Conversation]:
        """根据用户ID和Agent ID查找所有对话（按时间倒序）"""
        async with self._session_factory() as session:
            stmt = (
                select(ConversationModel)
                .where(ConversationModel.user_id == user_id)
                .where(ConversationModel.agent_id == agent_id)
                .order_by(ConversationModel.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            models = result.scalars().all()

            return [model.to_entity() for model in models]

    async def delete(self, session_id: SessionId) -> None:
        """删除对话"""
        async with self._session_factory() as session:
            stmt = select(ConversationModel).where(
                ConversationModel.session_id == session_id.value
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                await session.delete(model)
                await session.commit()

