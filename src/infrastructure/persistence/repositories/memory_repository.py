"""基础设施层 - PostgreSQL记忆仓储实现"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.memory.entities import Memory, MemoryType
from src.domain.memory.repositories import MemoryRepository
from ..models.memory_model import MemoryModel


class PostgresMemoryRepository(MemoryRepository):
    """PostgreSQL记忆仓储实现"""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def save(self, memory: Memory) -> Memory:
        """保存记忆"""
        async with self.session_factory() as session:
            model = MemoryModel.from_entity(memory)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return model.to_entity()

    async def find_by_id(self, memory_id: UUID) -> Optional[Memory]:
        """根据ID查找记忆"""
        async with self.session_factory() as session:
            stmt = select(MemoryModel).where(MemoryModel.id == memory_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                # 更新访问信息
                entity = model.to_entity()
                entity.mark_accessed()
                model.update_from_entity(entity)
                await session.commit()
                return entity

            return None

    async def find_by_session(
        self,
        session_id: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10,
    ) -> List[Memory]:
        """根据会话ID查找记忆"""
        async with self.session_factory() as session:
            stmt = select(MemoryModel).where(MemoryModel.session_id == session_id)

            if memory_type:
                stmt = stmt.where(MemoryModel.memory_type == memory_type.value)

            stmt = stmt.order_by(MemoryModel.created_at.desc()).limit(limit)

            result = await session.execute(stmt)
            models = result.scalars().all()
            return [model.to_entity() for model in models]

    async def delete(self, memory_id: UUID) -> bool:
        """删除记忆"""
        async with self.session_factory() as session:
            stmt = delete(MemoryModel).where(MemoryModel.id == memory_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
