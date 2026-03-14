"""记忆领域异常"""

from .base import DomainException


class MemoryException(DomainException):
    """记忆领域异常"""

    def __init__(self, message: str):
        super().__init__(message, "MEMORY_ERROR")


class MemoryNotFoundException(MemoryException):
    """记忆未找到异常"""

    def __init__(self, memory_id: str):
        super().__init__(f"记忆未找到: {memory_id}")
