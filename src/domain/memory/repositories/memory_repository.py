"""记忆领域 - 记忆仓储接口"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities import Memory, MemoryType


class MemoryRepository(ABC):
    """记忆仓储接口"""

    @abstractmethod
    async def save(self, memory: Memory) -> Memory:
        """保存记忆"""
        pass

    @abstractmethod
    async def find_by_id(self, memory_id: UUID) -> Optional[Memory]:
        """根据ID查找记忆"""
        pass

    @abstractmethod
    async def find_by_session(
        self,
        session_id: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10,
    ) -> List[Memory]:
        """根据会话ID查找记忆"""
        pass

    @abstractmethod
    async def delete(self, memory_id: UUID) -> bool:
        """删除记忆"""
        pass
