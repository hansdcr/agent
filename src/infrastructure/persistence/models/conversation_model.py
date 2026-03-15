"""基础设施层 - 对话持久化模型"""

from datetime import datetime
from typing import List
from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from src.infrastructure.persistence.models.memory_model import Base
from src.domain.chat.entities import Conversation, Message
from src.domain.chat.value_objects import SessionId, MessageRole, MessageContent


class ConversationModel(Base):
    """对话ORM模型"""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)  # 用户ID（人类或agent）
    agent_id = Column(String(255), nullable=True, index=True)  # 对话的agent ID
    system_prompt = Column(Text, nullable=True)
    messages = Column(JSONB, nullable=False, default=list)
    message_count = Column(Integer, nullable=False, default=0)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    @staticmethod
    def from_entity(conversation: Conversation) -> "ConversationModel":
        """从领域实体转换为ORM模型"""
        messages_data = conversation.get_messages_as_dicts()

        return ConversationModel(
            session_id=conversation.session_id.value,
            user_id=getattr(conversation, 'user_id', None),
            agent_id=getattr(conversation, 'agent_id', None),
            system_prompt=conversation.system_prompt,
            messages=messages_data,
            message_count=conversation.message_count(),
        )

    def to_entity(self) -> Conversation:
        """从ORM模型转换为领域实体"""
        session_id = SessionId.from_string(self.session_id)
        conversation = Conversation(
            session_id=session_id,
            system_prompt=self.system_prompt or "",
        )

        # 重建消息列表（跳过第一条系统消息，因为已经在构造函数中添加）
        for msg_data in self.messages[1:]:  # 跳过系统消息
            role = msg_data.get("role")
            content = msg_data.get("content", "")
            timestamp_str = msg_data.get("timestamp")

            # 创建消息对象
            from datetime import datetime, timezone
            if role == "user":
                msg = Message.create_user(content)
            elif role == "assistant":
                msg = Message.create_assistant(content)
            elif role == "system":
                msg = Message.create_system(content)
            else:
                continue

            # 如果有timestamp，覆盖默认的timestamp
            if timestamp_str:
                try:
                    msg.timestamp = datetime.fromisoformat(timestamp_str)
                except (ValueError, TypeError):
                    pass  # 如果解析失败，使用默认的timestamp

            conversation.messages.append(msg)

        return conversation
