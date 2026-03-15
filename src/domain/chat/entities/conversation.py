"""聊天领域 - 对话聚合根"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from ..value_objects import SessionId
from .message import Message


@dataclass
class Conversation:
    """对话聚合根

    管理一个会话的所有消息和状态
    """
    session_id: SessionId
    messages: List[Message] = field(default_factory=list)
    system_prompt: Optional[str] = None
    user_id: Optional[str] = None
    agent_id: Optional[str] = None

    def __post_init__(self):
        """初始化后处理"""
        if self.system_prompt and not self.messages:
            self.add_system_message(self.system_prompt)

    def add_system_message(self, content: str) -> None:
        """添加系统消息"""
        message = Message.create_system(content)
        self.messages.append(message)

    def add_user_message(self, content: str) -> None:
        """添加用户消息"""
        message = Message.create_user(content)
        self.messages.append(message)

    def add_assistant_message(self, content: str) -> None:
        """添加助手消息"""
        message = Message.create_assistant(content)
        self.messages.append(message)

    def get_messages_as_dicts(self) -> List[Dict[str, str]]:
        """获取消息列表（字典格式）"""
        return [msg.to_dict() for msg in self.messages]

    def clear_messages(self, keep_system: bool = True) -> None:
        """清空消息历史"""
        if keep_system and self.system_prompt:
            system_messages = [
                msg for msg in self.messages
                if msg.role.value == "system"
            ]
            self.messages = system_messages
        else:
            self.messages = []

    def message_count(self) -> int:
        """获取消息数量"""
        return len(self.messages)
