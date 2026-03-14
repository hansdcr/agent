"""聊天API路由.

提供聊天接口，支持普通对话和流式对话。
"""

import uuid
from typing import AsyncIterator, Dict, Tuple

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from src.api.models.chat import ChatRequest, ChatResponse
from src.api.models.response import ApiResponse
from src.core.conversation import Conversation
from src.core.exceptions import InternalServerException
from src.core.llm import DeepSeekClient
from src.core.logger import get_logger

logger = get_logger("chat")

router = APIRouter(prefix="/api/chat", tags=["chat"])

# 会话存储（内存）
sessions: Dict[str, Conversation] = {}


def get_or_create_session(
    session_id: str | None, system_prompt: str
) -> Tuple[str, Conversation]:
    """获取或创建会话.

    Args:
        session_id: 会话ID，如果为None则创建新会话
        system_prompt: 系统提示词

    Returns:
        (会话ID, 会话对象)的元组
    """
    if session_id and session_id in sessions:
        logger.debug(f"使用现有会话 | session_id: {session_id}")
        return session_id, sessions[session_id]

    # 创建新会话
    new_session_id = str(uuid.uuid4())
    sessions[new_session_id] = Conversation(system_prompt=system_prompt)
    logger.info(f"创建新会话 | session_id: {new_session_id}")
    return new_session_id, sessions[new_session_id]


@router.post("/", response_model=ApiResponse[ChatResponse])
async def chat(
    request_data: ChatRequest, request: Request
) -> ApiResponse[ChatResponse]:
    """普通对话接口.

    Args:
        request_data: 聊天请求数据
        request: FastAPI请求对象

    Returns:
        统一格式的聊天响应
    """
    logger.info(f"收到聊天请求 | 消息长度: {len(request_data.message)} 字符")
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
        logger.info(f"聊天请求成功 | session_id: {session_id} | 响应长度: {len(response)} 字符")
        chat_response = ChatResponse(message=response, session_id=session_id)
        return ApiResponse.success(data=chat_response)
    except Exception as e:
        logger.error(f"聊天请求失败 | session_id: {session_id} | 错误: {str(e)}")
        raise InternalServerException(error=str(e))


@router.post("/stream")
async def chat_stream(
    request_data: ChatRequest, request: Request
) -> StreamingResponse:
    """流式对话接口.

    Args:
        request_data: 聊天请求数据
        request: FastAPI请求对象

    Returns:
        Server-Sent Events流式响应

    Raises:
        HTTPException: API调用失败时抛出500错误
    """
    logger.info(f"收到流式聊天请求 | 消息长度: {len(request_data.message)} 字符")
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

    async def generate() -> AsyncIterator[str]:
        """生成流式响应."""
        try:
            full_response = ""
            # 发送会话ID
            yield f"data: {{'session_id': '{session_id}'}}\n\n"

            # 流式获取回复
            async for chunk in client.chat_stream(conversation.get_messages()):
                full_response += chunk
                # 发送文本片段
                yield f"data: {{'content': '{chunk}'}}\n\n"

            # 添加完整的助手消息到会话
            conversation.add_assistant_message(full_response)
            logger.info(f"流式聊天完成 | session_id: {session_id} | 响应长度: {len(full_response)} 字符")
            # 发送结束标记
            yield "data: {'done': true}\n\n"
        except Exception as e:
            logger.error(f"流式聊天失败 | session_id: {session_id} | 错误: {str(e)}")
            yield f"data: {{'error': '{str(e)}'}}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
