"""AI Agent FastAPI应用入口.

提供DeepSeek聊天API接口。
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routes import chat
from src.config.settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理.

    Args:
        app: FastAPI应用实例

    Yields:
        None
    """
    # 启动时初始化
    print("🚀 AI Agent启动中...")
    settings = Settings()
    app.state.settings = settings
    print("✓ 配置加载成功")
    print(f"✓ 模型: {settings.deepseek_model}")
    yield
    # 关闭时清理
    print("👋 AI Agent关闭")


app = FastAPI(
    title="AI Agent API",
    description="基于DeepSeek的AI智能体API",
    version="0.1.0",
    lifespan=lifespan,
)

# 注册路由
app.include_router(chat.router)


@app.get("/health")
async def health_check():
    """健康检查接口.

    Returns:
        包含状态信息的字典
    """
    return {"status": "healthy", "version": "0.1.0"}
