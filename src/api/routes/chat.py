"""聊天API路由.

提供聊天接口，支持普通对话和流式对话。
"""

import uuid
from typing import Dict

from fastapi import APIRouter, HTTPException, Request

from src.api.models.chat import ChatRequest, ChatResponse
from src.core.conversation import Conversation
from src.core.llm import DeepSeekClient

router = APIRouter(prefix="/chat", tags=["chat"])

# 会话存储（内存）
sessions: Dict[str, Conversation] = {}


def get_or_create_session(session_id: str | None, system_prompt: str) -> tuple:
    """获取或创建会话.

    Args:
        session_id: 会话ID，如果为None则创建新会话
        system_prompt: 系统提示词

    Returns:
        (会话ID, 会话对象)的元组
    """
    if session_id and session_id in sessions:
        return session_id, sessions[session_id]

    # 创建新会话
    new_session_id = str(uuid.uuid4())
    sessions[new_session_id] = Conversation(system_prompt=system_prompt)
    return new_session_id, sessions[new_session_id]


@router.post("/", response_model=ChatResponse)
async def chat(request_data: ChatRequest, request: Request):
    """普通对话接口.

    Args:
        request_data: 聊天请求数据
        request: FastAPI请求对象

    Returns:
        聊天响应

    Raises:
        HTTPException: API调用失败时抛出500错误
    """
    settings = request.app.state.settings

    # 获取或创建会话
    session_id, conversation = get_or_create_session(
        request_data.session_id, settings.system_prompt
    )

    # 添加用户消息
    conversation.add_user_message(request_data.message)

    # 创建LLM客户端
    client = DeepSeekClient(
        api_key=settings.deepseek_api_key,
        model=settings.deepseek_model,
        base_url=settings.deepseek_base_url,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
    )

    try:
        # 调用LLM获取回复
        response = await client.chat(conversation.get_messages())
        # 添加助手消息
        conversation.add_assistant_message(response)
        return ChatResponse(message=response, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API调用失败: {str(e)}")
