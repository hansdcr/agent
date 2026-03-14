"""接口层 - REST API路由"""

from typing import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.application.chat.commands import ChatCommandHandler
from src.application.chat.dtos import ChatRequestDTO, ChatResponseDTO
from ..schemas import ChatRequest, ChatResponse, ApiResponse
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
