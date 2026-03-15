"""聊天应用层 - DTO"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ChatRequestDTO:
    """聊天请求DTO"""
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    agent_id: Optional[str] = None


@dataclass
class ChatResponseDTO:
    """聊天响应DTO"""
    message: str
    session_id: str
