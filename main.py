"""AI Agent FastAPI应用入口 - DDD架构版本"""

from contextlib import asynccontextmanager
from typing import AsyncIterator
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.application.chat.commands import ChatCommandHandler
from src.infrastructure.persistence.repositories.conversation_repository import (
    PostgresConversationRepository,
)
from src.infrastructure.persistence.repositories.memory_repository import (
    PostgresMemoryRepository,
)
from src.infrastructure.persistence.models import Base
from src.infrastructure.external.llm.deepseek_service import DeepSeekLLMService
from src.interfaces.api.rest import chat
from src.interfaces.api.schemas import ApiResponse
from src.config.settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用生命周期管理"""
    # 加载配置
    settings = Settings()
    app.state.settings = settings

    # 转换数据库URL
    database_url = settings.database_url
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+asyncpg://", 1
        )

    # 创建数据库引擎
    engine = create_async_engine(database_url, echo=False)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 初始化对话仓储（使用数据库持久化）
    conversation_repo = PostgresConversationRepository(session_factory)

    # 初始化记忆仓储（如果启用）
    memory_repo = None
    if settings.memory_enabled:
        memory_repo = PostgresMemoryRepository(session_factory)

    # 初始化LLM服务
    llm_service = DeepSeekLLMService(
        api_key=settings.deepseek_api_key,
        model=settings.deepseek_model,
        base_url=settings.deepseek_base_url,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
    )

    # 初始化应用服务
    chat_handler = ChatCommandHandler(
        conversation_repo=conversation_repo,
        llm_service=llm_service,
        memory_repo=memory_repo,
        system_prompt=settings.system_prompt,
    )

    app.state.chat_handler = chat_handler

    print("🚀 AI Agent启动成功 (DDD架构)")
    print(f"✓ 模型: {settings.deepseek_model}")
    print(f"✓ 记忆系统: {'启用' if settings.memory_enabled else '禁用'}")
    print(f"✓ 对话持久化: 数据库存储")

    yield

    print("👋 AI Agent关闭")


app = FastAPI(
    title="AI Agent API (DDD)",
    description="基于DDD架构的AI智能体API",
    version="0.2.0",
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 注册路由
app.include_router(chat.router)

# 挂载静态文件（简单的 HTML 聊天界面）
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 挂载前端 React 应用
web_app_dist = os.path.join(os.path.dirname(__file__), "../web-app/dist")
if os.path.exists(web_app_dist):
    app.mount("/", StaticFiles(directory=web_app_dist, html=True), name="webapp")


@app.get("/api/health")
async def health_check() -> ApiResponse:
    """健康检查接口"""
    return ApiResponse.success(data={"status": "healthy", "version": "0.2.0"})
