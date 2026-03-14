"""基础设施层 - 记忆ORM模型"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import declarative_base

from src.domain.memory.entities import Memory, MemoryType, MemoryImportance

Base = declarative_base()


class MemoryModel(Base):
    """记忆ORM模型"""
    __tablename__ = "memories"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    memory_type = Column(String(50), nullable=False, index=True)
    content = Column(Text, nullable=False)
    importance = Column(String(50), nullable=False)
    extra_data = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.now, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    accessed_at = Column(DateTime, nullable=False, default=datetime.now)
    access_count = Column(Integer, nullable=False, default=0)

    @staticmethod
    def from_entity(memory: Memory) -> "MemoryModel":
        """从领域实体创建ORM模型"""
        return MemoryModel(
            id=memory.id,
            session_id=memory.session_id,
            user_id=memory.user_id,
            memory_type=memory.memory_type.value,
            content=memory.content,
            importance=memory.importance.value,
            extra_data=memory.extra_data or {},
            created_at=memory.created_at or datetime.now(),
            updated_at=memory.updated_at or datetime.now(),
            accessed_at=memory.accessed_at or datetime.now(),
            access_count=memory.access_count,
        )

    def to_entity(self) -> Memory:
        """转换为领域实体"""
        return Memory(
            id=self.id,
            session_id=self.session_id,
            user_id=self.user_id,
            memory_type=MemoryType(self.memory_type),
            content=self.content,
            importance=MemoryImportance(self.importance),
            extra_data=self.extra_data,
            created_at=self.created_at,
            updated_at=self.updated_at,
            accessed_at=self.accessed_at,
            access_count=self.access_count,
        )

    def update_from_entity(self, memory: Memory) -> None:
        """从领域实体更新ORM模型"""
        self.content = memory.content
        self.importance = memory.importance.value
        self.extra_data = memory.extra_data
        self.updated_at = memory.updated_at
        self.accessed_at = memory.accessed_at
        self.access_count = memory.access_count
