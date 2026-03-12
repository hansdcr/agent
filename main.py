"""AI Agent FastAPI应用入口.

提供DeepSeek聊天API接口。
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.models.response import ApiResponse
from src.api.routes import chat
from src.config.settings import Settings
from src.core.exceptions import AppException
from src.core.logger import setup_logger, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用生命周期管理.

    Args:
        app: FastAPI应用实例

    Yields:
        None
    """
    # 启动时初始化
    settings = Settings()
    app.state.settings = settings

    # 初始化日志系统
    logger = setup_logger(
        name="ai_agent",
        level=settings.log_level,
        log_file=settings.log_file,
        max_bytes=settings.log_max_bytes,
        backup_count=settings.log_backup_count,
        enable_color=settings.log_enable_color,
    )

    logger.info("🚀 AI Agent启动中...")
    logger.info("✓ 配置加载成功")
    logger.info(f"✓ 模型: {settings.deepseek_model}")
    logger.info(f"✓ 日志级别: {settings.log_level}")
    if settings.log_file:
        logger.info(f"✓ 日志文件: {settings.log_file}")

    yield

    # 关闭时清理
    logger.info("👋 AI Agent关闭")


app = FastAPI(
    title="AI Agent API",
    description="基于DeepSeek的AI智能体API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """全局AppException异常处理器.

    Args:
        request: FastAPI请求对象
        exc: AppException异常实例

    Returns:
        统一格式的JSON错误响应
    """
    logger = get_logger()
    logger.error(
        f"AppException: {exc.data.get('error')} | "
        f"Code: {exc.code} | "
        f"Path: {request.url.path}"
    )

    return JSONResponse(
        status_code=exc.code,
        content={
            "code": exc.code,
            "status": exc.status,
            "data": exc.data,
            "message": exc.message,
        },
    )


# 注册路由
app.include_router(chat.router)


@app.get("/health")
async def health_check() -> ApiResponse[Dict[str, str]]:
    """健康检查接口.

    Returns:
        统一格式的健康状态响应
    """
    health_data = {"status": "healthy", "version": "0.1.0"}
    return ApiResponse.success(data=health_data)
