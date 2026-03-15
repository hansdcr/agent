"""接口层 - REST API路由"""

from typing import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from src.application.chat.commands import ChatCommandHandler
from src.application.chat.dtos import ChatRequestDTO, ChatResponseDTO
from ..schemas import ChatRequest, ChatResponse, ApiResponse, HistoryResponse, MessageItem, SessionListResponse, SessionItem
from ..dependencies import get_chat_handler

from src.domain.chat.value_objects import SessionId
from src.domain.chat.entities import Conversation

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ApiResponse[ChatResponse])
async def chat(
    request: ChatRequest,
    handler: ChatCommandHandler = Depends(get_chat_handler),
) -> ApiResponse[ChatResponse]:
    """普通聊天接口"""

    # 如果提供了 user_id 和 agent_id，尝试查找现有会话
    session_id_str = request.session_id
    if not session_id_str and request.user_id and request.agent_id:
        # 根据 user_id 和 agent_id 查找会话
        existing_conversation = await handler.conversation_repo.find_by_user_and_agent(
            request.user_id, request.agent_id
        )
        if existing_conversation:
            session_id_str = existing_conversation.session_id.value

    dto = ChatRequestDTO(
        message=request.message,
        session_id=session_id_str,
        user_id=request.user_id,
        agent_id=request.agent_id,
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


@router.get("/chat/sessions", response_model=ApiResponse[SessionListResponse])
async def get_sessions(
    user_id: str,
    agent_id: str,
    handler: ChatCommandHandler = Depends(get_chat_handler),
) -> ApiResponse[SessionListResponse]:
    """获取会话列表"""
    try:
        # 查找所有会话
        conversations = await handler.conversation_repo.find_all_by_user_and_agent(
            user_id, agent_id
        )

        # 转换为响应格式
        session_items = []
        for conv in conversations:
            # 获取会话的元数据
            from src.domain.chat.value_objects import SessionId
            sid = SessionId.from_string(conv.session_id.value)
            conversation = await handler.conversation_repo.find_by_id(sid)

            if conversation:
                # 从数据库获取创建时间和更新时间
                async with handler.conversation_repo._session_factory() as session:
                    from sqlalchemy import select
                    from src.infrastructure.persistence.models import ConversationModel

                    stmt = select(ConversationModel).where(
                        ConversationModel.session_id == conv.session_id.value
                    )
                    result = await session.execute(stmt)
                    model = result.scalar_one_or_none()

                    if model:
                        session_items.append(
                            SessionItem(
                                session_id=conv.session_id.value,
                                created_at=model.created_at.isoformat(),
                                updated_at=model.updated_at.isoformat(),
                                message_count=conversation.message_count(),
                            )
                        )

        return ApiResponse.success(
            data=SessionListResponse(sessions=session_items)
        )
    except Exception as e:
        return ApiResponse.error(code=500, message=f"获取会话列表失败: {str(e)}")


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
