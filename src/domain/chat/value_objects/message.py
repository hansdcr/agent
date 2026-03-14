"""聊天领域 - 值对象"""

from dataclasses import dataclass
from typing import Literal
from src.domain.shared.exceptions import InvalidMessageException


@dataclass(frozen=True)
class MessageRole:
    """消息角色值对象"""
    value: Literal["system", "user", "assistant"]

    @staticmethod
    def system() -> "MessageRole":
        return MessageRole("system")

    @staticmethod
    def user() -> "MessageRole":
        return MessageRole("user")

    @staticmethod
    def assistant() -> "MessageRole":
        return MessageRole("assistant")


@dataclass(frozen=True)
class MessageContent:
    """消息内容值对象"""
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise InvalidMessageException("消息内容不能为空")
