"""记忆系统数据模型"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Integer, String, Text, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MemoryType(str, Enum):
    """记忆类型"""
    SHORT_TERM = "short_term"  # 短期记忆（当前会话）
    LONG_TERM = "long_term"    # 长期记忆（跨会话）


class MemoryImportance(str, Enum):
    """记忆重要性级别"""
    LOW = "low"        # 低重要性
    MEDIUM = "medium"  # 中等重要性
    HIGH = "high"      # 高重要性


class Memory(Base):
    """记忆数据模型"""
    __tablename__ = "memories"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    memory_type = Column(SQLEnum(MemoryType), nullable=False, index=True)
    content = Column(Text, nullable=False)
    importance = Column(SQLEnum(MemoryImportance), nullable=False, default=MemoryImportance.MEDIUM)
    extra_data = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.now, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    accessed_at = Column(DateTime, nullable=False, default=datetime.now)
    access_count = Column(Integer, nullable=False, default=0)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": str(self.id),
            "session_id": self.session_id,
            "user_id": self.user_id,
            "memory_type": self.memory_type.value if self.memory_type else None,
            "content": self.content,
            "importance": self.importance.value if self.importance else None,
            "metadata": self.extra_data or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "accessed_at": self.accessed_at.isoformat() if self.accessed_at else None,
            "access_count": self.access_count,
        }
