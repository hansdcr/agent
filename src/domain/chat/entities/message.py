"""聊天领域 - 消息实体"""

from dataclasses import dataclass
from typing import Dict

from ..value_objects import MessageRole, MessageContent


@dataclass
class Message:
    """消息实体"""
    role: MessageRole
    content: MessageContent

    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式"""
        return {
            "role": self.role.value,
            "content": self.content.value,
        }

    @staticmethod
    def create_system(content: str) -> "Message":
        """创建系统消息"""
        return Message(
            role=MessageRole.system(),
            content=MessageContent(content),
        )

    @staticmethod
    def create_user(content: str) -> "Message":
        """创建用户消息"""
        return Message(
            role=MessageRole.user(),
            content=MessageContent(content),
        )

    @staticmethod
    def create_assistant(content: str) -> "Message":
        """创建助手消息"""
        return Message(
            role=MessageRole.assistant(),
            content=MessageContent(content),
        )
