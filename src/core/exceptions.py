"""统一异常处理模块.

定义应用级异常和常用错误类型。
异常会被全局异常处理器捕获，并转换为统一的ApiResponse格式。
"""

from typing import Optional


class AppException(RuntimeError):
    """应用异常基类.

    所有业务异常都应该继承此类。
    异常会被全局异常处理器捕获，并转换为统一的ApiResponse格式：
    {
        "code": HTTP状态码,
        "status": HTTP状态码（与code相同）,
        "data": {"error": 错误消息, ...额外详情},
        "message": "error"
    }

    Attributes:
        code: HTTP状态码
        status: 响应状态码（与code相同）
        data: 响应数据（包含error和details）
        message: 消息说明（固定为"error"）
    """

    def __init__(
        self, error: str, code: int = 500, details: Optional[dict] = None
    ) -> None:
        """初始化应用异常.

        Args:
            error: 错误消息
            code: HTTP状态码，默认500
            details: 额外的错误详情
        """
        super().__init__(error)
        self.code = code
        self.status = code  # status与code相同
        self.data = {"error": error}
        if details:
            self.data.update(details)
        self.message = "error"


class BadRequestException(AppException):
    """请求参数错误异常（400）."""

    def __init__(
        self, error: str = "请求参数错误", details: Optional[dict] = None
    ) -> None:
        """初始化请求参数错误异常.

        Args:
            error: 错误消息
            details: 额外的错误详情
        """
        super().__init__(error, code=400, details=details)


class UnauthorizedException(AppException):
    """未授权异常（401）."""

    def __init__(self, error: str = "未授权", details: Optional[dict] = None) -> None:
        """初始化未授权异常.

        Args:
            error: 错误消息
            details: 额外的错误详情
        """
        super().__init__(error, code=401, details=details)


class ForbiddenException(AppException):
    """禁止访问异常（403）."""

    def __init__(
        self, error: str = "禁止访问", details: Optional[dict] = None
    ) -> None:
        """初始化禁止访问异常.

        Args:
            error: 错误消息
            details: 额外的错误详情
        """
        super().__init__(error, code=403, details=details)


class NotFoundException(AppException):
    """资源未找到异常（404）."""

    def __init__(
        self, error: str = "资源未找到", details: Optional[dict] = None
    ) -> None:
        """初始化资源未找到异常.

        Args:
            error: 错误消息
            details: 额外的错误详情
        """
        super().__init__(error, code=404, details=details)


class ConflictException(AppException):
    """资源冲突异常（409）."""

    def __init__(
        self, error: str = "资源冲突", details: Optional[dict] = None
    ) -> None:
        """初始化资源冲突异常.

        Args:
            error: 错误消息
            details: 额外的错误详情
        """
        super().__init__(error, code=409, details=details)


class InternalServerException(AppException):
    """服务器内部错误异常（500）."""

    def __init__(
        self, error: str = "服务器内部错误", details: Optional[dict] = None
    ) -> None:
        """初始化服务器内部错误异常.

        Args:
            error: 错误消息
            details: 额外的错误详情
        """
        super().__init__(error, code=500, details=details)


class ServiceUnavailableException(AppException):
    """服务不可用异常（503）."""

    def __init__(
        self, error: str = "服务不可用", details: Optional[dict] = None
    ) -> None:
        """初始化服务不可用异常.

        Args:
            error: 错误消息
            details: 额外的错误详情
        """
        super().__init__(error, code=503, details=details)
