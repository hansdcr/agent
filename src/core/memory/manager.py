"""记忆管理器"""

import logging
import re
from typing import List, Optional

from .models import Memory, MemoryImportance, MemoryType
from .storage import MemoryStorage

logger = logging.getLogger(__name__)


class MemoryManager:
    """记忆管理器 - 负责记忆的业务逻辑"""

    def __init__(self, storage: MemoryStorage):
        """
        初始化记忆管理器

        Args:
            storage: 记忆存储实现
        """
        self.storage = storage

    async def add_memory(
        self,
        content: str,
        session_id: str,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        user_id: Optional[str] = None,
    ) -> Memory:
        """
        添加新记忆

        Args:
            content: 记忆内容
            session_id: 会话ID
            memory_type: 记忆类型
            importance: 重要性级别
            user_id: 用户ID

        Returns:
            保存的记忆对象
        """
        memory = Memory(
            content=content,
            session_id=session_id,
            memory_type=memory_type,
            importance=importance,
            user_id=user_id,
        )

        saved_memory = await self.storage.save(memory)
        logger.info(f"添加记忆: {saved_memory.id} - {content[:50]}...")
        return saved_memory

    async def get_relevant_memories(
        self,
        session_id: str,
        limit: int = 5,
        include_long_term: bool = True,
    ) -> List[Memory]:
        """
        获取相关记忆

        Args:
            session_id: 会话ID
            limit: 最大记忆数量
            include_long_term: 是否包含长期记忆

        Returns:
            记忆列表
        """
        memories = []

        # 获取短期记忆（当前会话）
        short_term = await self.storage.get_by_session(
            session_id=session_id,
            memory_type=MemoryType.SHORT_TERM,
            limit=limit,
        )
        memories.extend(short_term)

        # 如果需要，获取长期记忆
        if include_long_term and len(memories) < limit:
            remaining = limit - len(memories)
            long_term = await self.storage.get_by_session(
                session_id=session_id,
                memory_type=MemoryType.LONG_TERM,
                limit=remaining,
            )
            memories.extend(long_term)

        logger.info(f"获取到 {len(memories)} 条相关记忆")
        return memories

    async def extract_and_save_memory(
        self,
        messages: List[dict],
        session_id: str,
    ) -> List[Memory]:
        """
        从对话中提取并保存记忆（简单规则版本）

        Args:
            messages: 对话消息列表
            session_id: 会话ID

        Returns:
            保存的记忆列表
        """
        saved_memories = []

        # 简单规则：检测包含"记住"、"我叫"、"我是"等关键词的消息
        memory_keywords = [
            r"记住[：:](.*)",
            r"我叫(.+)",
            r"我是(.+)",
            r"我的.*是(.+)",
            r"请记住(.+)",
        ]

        for message in messages:
            if message.get("role") != "user":
                continue

            content = message.get("content", "")

            # 检查是否包含记忆关键词
            for pattern in memory_keywords:
                match = re.search(pattern, content)
                if match:
                    memory_content = match.group(0)
                    importance = MemoryImportance.HIGH

                    # 判断是否为长期记忆
                    is_long_term = any(
                        keyword in content
                        for keyword in ["记住", "请记住", "永远", "一直"]
                    )
                    memory_type = (
                        MemoryType.LONG_TERM if is_long_term else MemoryType.SHORT_TERM
                    )

                    memory = await self.add_memory(
                        content=memory_content,
                        session_id=session_id,
                        memory_type=memory_type,
                        importance=importance,
                    )
                    saved_memories.append(memory)
                    break

        return saved_memories

    def format_memories_for_context(self, memories: List[Memory]) -> str:
        """
        格式化记忆为上下文字符串

        Args:
            memories: 记忆列表

        Returns:
            格式化的上下文字符串
        """
        if not memories:
            return ""

        context_parts = ["# 相关记忆\n"]

        for memory in memories:
            memory_type_label = (
                "长期记忆" if memory.memory_type == MemoryType.LONG_TERM else "短期记忆"
            )
            context_parts.append(
                f"- [{memory_type_label}] {memory.content}"
            )

        return "\n".join(context_parts)
