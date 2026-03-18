"""接口层 - 依赖注入"""

from typing import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.chat.commands import ChatCommandHandler


def get_chat_handler(request: Request) -> ChatCommandHandler:
    """获取聊天命令处理器"""
    return request.app.state.chat_handler


def get_settings(request: Request):
    """获取应用配置"""
    return request.app.state.settings


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    """获取数据库会话"""
    async with request.app.state.session_factory() as session:
        yield session
