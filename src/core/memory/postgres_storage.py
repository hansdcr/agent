"""PostgreSQL记忆存储实现"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from .models import Memory, MemoryImportance, MemoryType, Base
from .storage import MemoryStorage

logger = logging.getLogger(__name__)


class PostgresMemoryStorage(MemoryStorage):
    """PostgreSQL记忆存储实现"""

    def __init__(self, database_url: str, pool_size: int = 10):
        """
        初始化PostgreSQL存储

        Args:
            database_url: 数据库连接URL
            pool_size: 连接池大小
        """
        # 将 postgresql:// 转换为 postgresql+asyncpg://
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        self.database_url = database_url
        self.pool_size = pool_size
        self.engine = None
        self.async_session_maker = None

    async def initialize(self) -> None:
        """初始化数据库连接池"""
        try:
            self.engine = create_async_engine(
                self.database_url,
                pool_size=self.pool_size,
                max_overflow=10,
                echo=False,
            )
            self.async_session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            # 创建表
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            logger.info("PostgreSQL连接池初始化成功")
        except Exception as e:
            logger.error(f"PostgreSQL连接池初始化失败: {e}")
            raise

    async def save(self, memory: Memory) -> Memory:
        """保存记忆"""
        if not self.async_session_maker:
            raise RuntimeError("数据库连接池未初始化")

        try:
            async with self.async_session_maker() as session:
                session.add(memory)
                await session.commit()
                await session.refresh(memory)
                logger.info(f"保存记忆成功: {memory.id}")
                return memory
        except Exception as e:
            logger.error(f"保存记忆失败: {e}")
            raise

    async def get_by_id(self, memory_id: UUID) -> Optional[Memory]:
        """根据ID获取记忆"""
        if not self.async_session_maker:
            raise RuntimeError("数据库连接池未初始化")

        try:
            async with self.async_session_maker() as session:
                stmt = select(Memory).where(Memory.id == memory_id)
                result = await session.execute(stmt)
                memory = result.scalar_one_or_none()

                if memory:
                    # 更新访问时间和访问次数
                    memory.accessed_at = datetime.now()
                    memory.access_count += 1
                    await session.commit()
                    await session.refresh(memory)

                return memory
        except Exception as e:
            logger.error(f"获取记忆失败: {e}")
            raise

    async def get_by_session(
        self,
        session_id: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10,
    ) -> List[Memory]:
        """获取会话的记忆"""
        if not self.async_session_maker:
            raise RuntimeError("数据库连接池未初始化")

        try:
            async with self.async_session_maker() as session:
                stmt = select(Memory).where(Memory.session_id == session_id)

                if memory_type:
                    stmt = stmt.where(Memory.memory_type == memory_type)

                stmt = stmt.order_by(Memory.created_at.desc()).limit(limit)

                result = await session.execute(stmt)
                memories = result.scalars().all()
                return list(memories)
        except Exception as e:
            logger.error(f"获取会话记忆失败: {e}")
            raise

    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[Memory]:
        """搜索记忆（使用PostgreSQL全文搜索）"""
        if not self.async_session_maker:
            raise RuntimeError("数据库连接池未初始化")

        try:
            async with self.async_session_maker() as session:
                # 使用 PostgreSQL 全文搜索
                stmt = select(Memory).where(
                    func.to_tsvector('english', Memory.content).op('@@')(
                        func.plainto_tsquery('english', query)
                    )
                )

                # 应用过滤器
                if filters:
                    if "session_id" in filters:
                        stmt = stmt.where(Memory.session_id == filters["session_id"])
                    if "memory_type" in filters:
                        stmt = stmt.where(Memory.memory_type == filters["memory_type"])
                    if "importance" in filters:
                        stmt = stmt.where(Memory.importance == filters["importance"])

                stmt = stmt.order_by(Memory.created_at.desc()).limit(limit)

                result = await session.execute(stmt)
                memories = result.scalars().all()
                return list(memories)
        except Exception as e:
            logger.error(f"搜索记忆失败: {e}")
            raise

    async def update(self, memory: Memory) -> Memory:
        """更新记忆"""
        if not self.async_session_maker:
            raise RuntimeError("数据库连接池未初始化")

        try:
            async with self.async_session_maker() as session:
                # 获取现有记忆
                stmt = select(Memory).where(Memory.id == memory.id)
                result = await session.execute(stmt)
                existing_memory = result.scalar_one_or_none()

                if not existing_memory:
                    raise ValueError(f"记忆不存在: {memory.id}")

                # 更新字段
                existing_memory.content = memory.content
                existing_memory.importance = memory.importance
                existing_memory.extra_data = memory.extra_data
                existing_memory.updated_at = datetime.now()

                await session.commit()
                await session.refresh(existing_memory)
                logger.info(f"更新记忆成功: {memory.id}")
                return existing_memory
        except Exception as e:
            logger.error(f"更新记忆失败: {e}")
            raise

    async def delete(self, memory_id: UUID) -> bool:
        """删除记忆"""
        if not self.async_session_maker:
            raise RuntimeError("数据库连接池未初始化")

        try:
            async with self.async_session_maker() as session:
                stmt = delete(Memory).where(Memory.id == memory_id)
                result = await session.execute(stmt)
                await session.commit()

                deleted = result.rowcount > 0
                if deleted:
                    logger.info(f"删除记忆成功: {memory_id}")
                return deleted
        except Exception as e:
            logger.error(f"删除记忆失败: {e}")
            raise

    async def cleanup_old_memories(
        self,
        days: int,
        memory_type: Optional[MemoryType] = None,
    ) -> int:
        """清理过期记忆"""
        if not self.async_session_maker:
            raise RuntimeError("数据库连接池未初始化")

        cutoff_date = datetime.now() - timedelta(days=days)

        try:
            async with self.async_session_maker() as session:
                stmt = delete(Memory).where(Memory.created_at < cutoff_date)

                if memory_type:
                    stmt = stmt.where(Memory.memory_type == memory_type)

                result = await session.execute(stmt)
                await session.commit()

                count = result.rowcount
                logger.info(f"清理了 {count} 条过期记忆")
                return count
        except Exception as e:
            logger.error(f"清理记忆失败: {e}")
            raise

    async def close(self) -> None:
        """关闭数据库连接池"""
        if self.engine:
            await self.engine.dispose()
            logger.info("PostgreSQL连接池已关闭")
