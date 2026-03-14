"""聊天领域异常"""

from .base import DomainException


class ChatException(DomainException):
    """聊天领域异常"""

    def __init__(self, message: str):
        super().__init__(message, "CHAT_ERROR")


class InvalidMessageException(ChatException):
    """无效消息异常"""

    def __init__(self, message: str = "消息内容无效"):
        super().__init__(message)
