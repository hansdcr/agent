"""接口层 - REST API路由"""

from typing import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from src.application.chat.commands import ChatCommandHandler
from src.application.chat.dtos import ChatRequestDTO, ChatResponseDTO
from ..schemas import ChatRequest, ChatResponse, ApiResponse, HistoryResponse, MessageItem
from ..dependencies import get_chat_handler


router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ApiResponse[ChatResponse])
async def chat(
    request: ChatRequest,
    handler: ChatCommandHandler = Depends(get_chat_handler),
) -> ApiResponse[ChatResponse]:
    """普通聊天接口"""
    dto = ChatRequestDTO(
        message=request.message,
        session_id=request.session_id,
    )

    result = await handler.handle(dto)

    response = ChatResponse(
        message=result.message,
        session_id=result.session_id,
    )

    return ApiResponse.success(data=response)


@router.get("/chat/history/{session_id}", response_model=ApiResponse[HistoryResponse])
async def get_chat_history(
    session_id: str,
    handler: ChatCommandHandler = Depends(get_chat_handler),
) -> ApiResponse[HistoryResponse]:
    """获取聊天历史"""
    from src.domain.chat.value_objects import SessionId

    try:
        # 查找对话
        sid = SessionId.from_string(session_id)
        conversation = await handler.conversation_repo.find_by_id(sid)

        if not conversation:
            # 如果没有找到对话，返回空历史
            return ApiResponse.success(
                data=HistoryResponse(
                    session_id=session_id,
                    messages=[]
                )
            )

        # 获取消息列表（排除 system 消息）
        messages = conversation.get_messages_as_dicts()
        message_items = [
            MessageItem(role=msg["role"], content=msg["content"])
            for msg in messages
            if msg["role"] != "system"  # 不返回系统消息给前端
        ]

        return ApiResponse.success(
            data=HistoryResponse(
                session_id=session_id,
                messages=message_items
            )
        )
    except ValueError:
        # 无效的 session_id 格式，返回空历史
        return ApiResponse.success(
            data=HistoryResponse(
                session_id=session_id,
                messages=[]
            )
        )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    handler: ChatCommandHandler = Depends(get_chat_handler),
) -> StreamingResponse:
    """流式聊天接口"""

    async def generate() -> AsyncIterator[str]:
        """生成流式响应"""
        from src.domain.chat.value_objects import SessionId
        from src.domain.chat.entities import Conversation

        # 获取或创建对话
        if request.session_id:
            session_id = SessionId.from_string(request.session_id)
            conversation = await handler.conversation_repo.find_by_id(session_id)
            if not conversation:
                conversation = Conversation(
                    session_id=session_id,
                    system_prompt=handler.system_prompt,
                )
        else:
            session_id = SessionId.generate()
            conversation = Conversation(
                session_id=session_id,
                system_prompt=handler.system_prompt,
            )

        # 发送会话ID
        yield f"data: {{'session_id': '{session_id.value}'}}\n\n"

        # 添加用户消息
        conversation.add_user_message(request.message)

        # 流式生成回复
        full_response = ""
        messages = conversation.get_messages_as_dicts()
        async for chunk in handler.llm_service.generate_response_stream(messages):
            full_response += chunk
            yield f"data: {{'content': '{chunk}'}}\n\n"

        # 添加助手消息并保存
        conversation.add_assistant_message(full_response)
        await handler.conversation_repo.save(conversation)

        yield "data: {'done': true}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
