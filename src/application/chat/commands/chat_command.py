"""聊天应用层 - 聊天命令处理器"""

from typing import Optional

from src.domain.chat.entities import Conversation
from src.domain.chat.repositories import ConversationRepository
from src.domain.chat.services import LLMService
from src.domain.chat.value_objects import SessionId
from src.domain.memory.repositories import MemoryRepository
from src.domain.memory.entities import Memory, MemoryType, MemoryImportance
from ..dtos import ChatRequestDTO, ChatResponseDTO


class ChatCommandHandler:
    """聊天命令处理器（应用服务）"""

    def __init__(
        self,
        conversation_repo: ConversationRepository,
        llm_service: LLMService,
        memory_repo: Optional[MemoryRepository] = None,
        system_prompt: str = "你是一个有帮助的AI助手。",
    ):
        self.conversation_repo = conversation_repo
        self.llm_service = llm_service
        self.memory_repo = memory_repo
        self.system_prompt = system_prompt

    async def handle(self, request: ChatRequestDTO) -> ChatResponseDTO:
        """处理聊天请求"""
        # 获取或创建对话
        if request.session_id:
            session_id = SessionId.from_string(request.session_id)
            conversation = await self.conversation_repo.find_by_id(session_id)
            if not conversation:
                conversation = Conversation(
                    session_id=session_id,
                    system_prompt=self.system_prompt,
                )
        else:
            session_id = SessionId.generate()
            conversation = Conversation(
                session_id=session_id,
                system_prompt=self.system_prompt,
            )

        # 添加记忆上下文（如果启用）
        if self.memory_repo:
            await self._add_memory_context(conversation)

        # 添加用户消息
        conversation.add_user_message(request.message)

        # 调用LLM生成回复
        messages = conversation.get_messages_as_dicts()
        response = await self.llm_service.generate_response(messages)

        # 添加助手消息
        conversation.add_assistant_message(response)

        # 保存对话
        await self.conversation_repo.save(conversation)

        # 提取并保存记忆（如果启用）
        if self.memory_repo:
            await self._extract_and_save_memory(
                conversation, session_id.value
            )

        return ChatResponseDTO(
            message=response,
            session_id=session_id.value,
        )

    async def _add_memory_context(self, conversation: Conversation) -> None:
        """添加记忆上下文"""
        if not self.memory_repo:
            return

        memories = await self.memory_repo.find_by_session(
            session_id=conversation.session_id.value,
            limit=5,
        )

        if memories:
            context = self._format_memories(memories)
            conversation.add_system_message(context)

    async def _extract_and_save_memory(
        self, conversation: Conversation, session_id: str
    ) -> None:
        """提取并保存记忆"""
        # 简单规则：检测包含"记住"等关键词的消息
        import re

        memory_keywords = [
            r"记住[：:](.*)",
            r"我叫(.+)",
            r"我是(.+)",
            r"请记住(.+)",
        ]

        messages = conversation.get_messages_as_dicts()
        for message in messages:
            if message.get("role") != "user":
                continue

            content = message.get("content", "")
            for pattern in memory_keywords:
                match = re.search(pattern, content)
                if match:
                    memory_content = match.group(0)
                    is_long_term = any(
                        kw in content for kw in ["记住", "请记住", "永远"]
                    )

                    memory = Memory.create(
                        session_id=session_id,
                        content=memory_content,
                        memory_type=(
                            MemoryType.LONG_TERM
                            if is_long_term
                            else MemoryType.SHORT_TERM
                        ),
                        importance=MemoryImportance.HIGH,
                    )
                    await self.memory_repo.save(memory)
                    break

    def _format_memories(self, memories: list[Memory]) -> str:
        """格式化记忆为上下文"""
        if not memories:
            return ""

        parts = ["# 相关记忆\n"]
        for memory in memories:
            label = "长期记忆" if memory.memory_type == MemoryType.LONG_TERM else "短期记忆"
            parts.append(f"- [{label}] {memory.content}")

        return "\n".join(parts)
