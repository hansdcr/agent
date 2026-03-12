"""LLM客户端模块.

提供与大语言模型交互的异步接口，支持DeepSeek等模型。
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, List

from openai import AsyncOpenAI

from src.core.logger import get_logger

logger = get_logger("llm")


class LLMClient(ABC):
    """LLM客户端抽象基类.

    定义与大语言模型交互的标准接口，支持异步调用。
    """

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """发送消息并获取回复.

        Args:
            messages: 消息列表，每个消息包含role和content字段
                     例如: [{"role": "user", "content": "你好"}]

        Returns:
            AI助手的回复内容

        Raises:
            Exception: API调用失败时抛出异常
        """
        pass

    @abstractmethod
    async def chat_stream(self, messages: List[Dict[str, str]]) -> AsyncIterator[str]:
        """流式对话接口.

        Args:
            messages: 消息列表

        Yields:
            AI助手回复的文本片段

        Raises:
            Exception: API调用失败时抛出异常
        """
        pass


class DeepSeekClient(LLMClient):
    """DeepSeek客户端实现.

    使用AsyncOpenAI客户端与DeepSeek API交互。

    Attributes:
        client: AsyncOpenAI客户端实例
        model: 使用的模型名称
        kwargs: 额外的模型参数（temperature、max_tokens等）
    """

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com",
        **kwargs,
    ):
        """初始化DeepSeek客户端.

        Args:
            api_key: DeepSeek API密钥
            model: 模型名称，默认为deepseek-chat
            base_url: API基础URL
            **kwargs: 额外的模型参数
        """
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.kwargs = kwargs
        logger.info(f"DeepSeek客户端初始化成功 | 模型: {model} | URL: {base_url}")

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """异步调用DeepSeek API获取回复.

        Args:
            messages: 消息列表

        Returns:
            AI助手的回复内容

        Raises:
            Exception: API调用失败时抛出异常
        """
        try:
            logger.debug(f"发送聊天请求 | 消息数: {len(messages)}")
            response = await self.client.chat.completions.create(
                model=self.model, messages=messages, **self.kwargs
            )
            content = response.choices[0].message.content
            logger.debug(f"收到聊天响应 | 长度: {len(content)} 字符")
            return content
        except Exception as e:
            logger.error(f"聊天请求失败 | 错误: {str(e)}")
            raise

    async def chat_stream(self, messages: List[Dict[str, str]]) -> AsyncIterator[str]:
        """流式对话接口.

        Args:
            messages: 消息列表

        Yields:
            AI助手回复的文本片段

        Raises:
            Exception: API调用失败时抛出异常
        """
        try:
            logger.debug(f"发送流式聊天请求 | 消息数: {len(messages)}")
            stream = await self.client.chat.completions.create(
                model=self.model, messages=messages, stream=True, **self.kwargs
            )
            chunk_count = 0
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    chunk_count += 1
                    yield chunk.choices[0].delta.content
            logger.debug(f"流式聊天完成 | 片段数: {chunk_count}")
        except Exception as e:
            logger.error(f"流式聊天请求失败 | 错误: {str(e)}")
            raise
