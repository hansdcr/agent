"""聊天API请求和响应模型.

定义聊天接口的数据结构。
"""

from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """聊天请求模型.

    Attributes:
        message: 用户消息内容
        session_id: 会话ID，用于多轮对话（可选）
    """

    message: str = Field(..., description="用户消息内容", min_length=1)
    session_id: Optional[str] = Field(default=None, description="会话ID，用于多轮对话")


class ChatResponse(BaseModel):
    """聊天响应模型.

    Attributes:
        message: AI助手的回复内容
        session_id: 会话ID
    """

    message: str = Field(..., description="AI助手的回复内容")
    session_id: str = Field(..., description="会话ID")
