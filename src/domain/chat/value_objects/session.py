"""会话ID值对象"""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class SessionId:
    """会话ID值对象"""
    value: str

    @staticmethod
    def generate() -> "SessionId":
        """生成新的会话ID"""
        return SessionId(str(uuid4()))

    @staticmethod
    def from_string(value: str) -> "SessionId":
        """从字符串创建会话ID"""
        # 验证是否为有效的UUID格式
        try:
            UUID(value)
            return SessionId(value)
        except ValueError:
            raise ValueError(f"无效的会话ID格式: {value}")
