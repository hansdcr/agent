"""记忆领域 - 记忆实体"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any
from uuid import UUID, uuid4


class MemoryType(str, Enum):
    """记忆类型"""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"


class MemoryImportance(str, Enum):
    """记忆重要性"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Memory:
    """记忆聚合根"""
    id: UUID
    session_id: str
    content: str
    memory_type: MemoryType
    importance: MemoryImportance
    user_id: str | None = None
    extra_data: Dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    accessed_at: datetime | None = None
    access_count: int = 0

    @staticmethod
    def create(
        session_id: str,
        content: str,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        user_id: str | None = None,
    ) -> "Memory":
        """创建新记忆"""
        now = datetime.now()
        return Memory(
            id=uuid4(),
            session_id=session_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            user_id=user_id,
            extra_data={},
            created_at=now,
            updated_at=now,
            accessed_at=now,
            access_count=0,
        )

    def mark_accessed(self) -> None:
        """标记为已访问"""
        self.accessed_at = datetime.now()
        self.access_count += 1

    def update_content(self, content: str) -> None:
        """更新内容"""
        self.content = content
        self.updated_at = datetime.now()
