"""接口层 - API Schemas"""

from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., min_length=1, description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    message: str = Field(..., description="AI回复")
    session_id: str = Field(..., description="会话ID")


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应格式"""
    code: int = Field(200, description="状态码")
    status: int = Field(200, description="HTTP状态码")
    data: Optional[T] = Field(None, description="响应数据")
    message: str = Field("success", description="响应消息")

    @classmethod
    def success(cls, data: T, message: str = "success") -> "ApiResponse[T]":
        """成功响应"""
        return cls(code=200, status=200, data=data, message=message)

    @classmethod
    def error(cls, code: int, message: str) -> "ApiResponse":
        """错误响应"""
        return cls(code=code, status=code, data=None, message=message)
