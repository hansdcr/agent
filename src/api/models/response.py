"""统一响应模型.

定义RESTful风格的统一响应格式。
"""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

# 泛型类型变量
T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应模型.

    Attributes:
        code: HTTP状态码
        status: 响应状态码（与code相同）
        data: 响应数据
        message: 可选的消息说明
    """

    code: int = Field(..., description="HTTP状态码")
    status: int = Field(..., description="响应状态码")
    data: Optional[T] = Field(default=None, description="响应数据")
    message: Optional[str] = Field(default=None, description="消息说明")

    @classmethod
    def success(
        cls, data: T, code: int = 200, message: str = "success"
    ) -> "ApiResponse[T]":
        """创建成功响应.

        Args:
            data: 响应数据
            code: HTTP状态码，默认200
            message: 消息说明

        Returns:
            成功响应对象
        """
        return cls(code=code, status=code, data=data, message=message)

    @classmethod
    def error(
        cls, error: str, code: int = 500, message: str = "error"
    ) -> "ApiResponse[dict]":
        """创建错误响应.

        Args:
            error: 错误信息
            code: HTTP状态码，默认500
            message: 消息说明

        Returns:
            错误响应对象
        """
        return cls(code=code, status=code, data={"error": error}, message=message)
