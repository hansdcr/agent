"""记忆存储抽象接口"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from uuid import UUID

from .models import Memory, MemoryType


class MemoryStorage(ABC):
    """记忆存储抽象基类"""

    @abstractmethod
    async def initialize(self) -> None:
        """初始化存储"""
        pass

    @abstractmethod
    async def save(self, memory: Memory) -> Memory:
        """保存记忆"""
        pass

    @abstractmethod
    async def get_by_id(self, memory_id: UUID) -> Optional[Memory]:
        """根据ID获取记忆"""
        pass

    @abstractmethod
    async def get_by_session(
        self,
        session_id: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10,
    ) -> List[Memory]:
        """获取会话的记忆"""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[Memory]:
        """搜索记忆"""
        pass

    @abstractmethod
    async def update(self, memory: Memory) -> Memory:
        """更新记忆"""
        pass

    @abstractmethod
    async def delete(self, memory_id: UUID) -> bool:
        """删除记忆"""
        pass

    @abstractmethod
    async def cleanup_old_memories(
        self,
        days: int,
        memory_type: Optional[MemoryType] = None,
    ) -> int:
        """清理过期记忆"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """关闭存储连接"""
        pass
