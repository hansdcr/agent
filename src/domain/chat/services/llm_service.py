"""聊天领域 - LLM服务接口"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Dict


class LLMService(ABC):
    """LLM服务接口（领域服务）"""

    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """生成回复"""
        pass

    @abstractmethod
    async def generate_response_stream(
        self, messages: List[Dict[str, str]]
    ) -> AsyncIterator[str]:
        """流式生成回复"""
        pass
