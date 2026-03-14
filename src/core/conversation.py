"""对话管理模块.

管理对话历史和上下文，支持多轮对话。
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Literal, Optional

from src.core.logger import get_logger

if TYPE_CHECKING:
    from src.core.memory import MemoryManager

logger = get_logger("conversation")


@dataclass
class Message:
    """消息数据类.

    Attributes:
        role: 消息角色（system/user/assistant）
        content: 消息内容
    """

    role: Literal["system", "user", "assistant"]
    content: str

    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式.

        Returns:
            包含role和content的字典
        """
        return {"role": self.role, "content": self.content}


@dataclass
class Conversation:
    """对话管理器.

    管理单个会话的消息历史，支持添加消息和获取消息列表。

    Attributes:
        system_prompt: 系统提示词
        messages: 消息列表
        memory_manager: 记忆管理器（可选）
    """

    system_prompt: str = "你是一个有帮助的AI助手。"
    messages: List[Message] = field(default_factory=list)
    memory_manager: Optional["MemoryManager"] = None

    def __post_init__(self):
        """初始化后处理，添加系统消息."""
        if self.system_prompt:
            self.messages.append(Message(role="system", content=self.system_prompt))

    def add_user_message(self, content: str) -> None:
        """添加用户消息.

        Args:
            content: 用户消息内容
        """
        self.messages.append(Message(role="user", content=content))

    def add_assistant_message(self, content: str) -> None:
        """添加助手消息.

        Args:
            content: 助手消息内容
        """
        self.messages.append(Message(role="assistant", content=content))

    def get_messages(self) -> List[Dict[str, str]]:
        """获取消息列表（API格式）.

        Returns:
            消息字典列表，格式为[{"role": "user", "content": "..."}]
        """
        return [msg.to_dict() for msg in self.messages]

    def clear(self) -> None:
        """清空对话历史，保留系统消息."""
        message_count = len(self.messages) - 1  # 减去系统消息
        self.messages = []
        if self.system_prompt:
            self.messages.append(Message(role="system", content=self.system_prompt))
        logger.info(f"清空对话历史 | 清除消息数: {message_count}")

    async def add_memory_context(self, session_id: str) -> None:
        """添加记忆上下文到对话.

        Args:
            session_id: 会话ID
        """
        if not self.memory_manager:
            return

        # 获取相关记忆
        memories = await self.memory_manager.get_relevant_memories(
            session_id=session_id,
            limit=5,
        )

        if memories:
            # 格式化并插入记忆上下文
            memory_context = self.memory_manager.format_memories_for_context(memories)
            memory_message = Message(role="system", content=memory_context)
            # 插入到系统消息之后
            self.messages.insert(1, memory_message)
            logger.info(f"添加记忆上下文 | 记忆数量: {len(memories)}")

