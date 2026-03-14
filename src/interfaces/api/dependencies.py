"""接口层 - 依赖注入"""

from fastapi import Request

from src.application.chat.commands import ChatCommandHandler


def get_chat_handler(request: Request) -> ChatCommandHandler:
    """获取聊天命令处理器"""
    return request.app.state.chat_handler
