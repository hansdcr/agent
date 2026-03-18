"""Agent 凭证 ORM 模型 - 存储向 cultrue 注册后获得的 agent_id 和 api_key"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .memory_model import Base


class AgentCredentialModel(Base):
    """存储 agent 在 cultrue 注册后的凭证"""
    __tablename__ = "agent_credentials"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    agent_id = Column(String(255), nullable=False, unique=True, index=True)
    api_key = Column(Text, nullable=False)
    name = Column(String(100), nullable=True)
    avatar = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    registered_at = Column(DateTime, nullable=False, default=datetime.now)
