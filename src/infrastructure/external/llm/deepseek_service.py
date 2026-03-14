"""基础设施层 - DeepSeek LLM服务实现"""

from typing import AsyncIterator, List, Dict

from openai import AsyncOpenAI

from src.domain.chat.services import LLMService


class DeepSeekLLMService(LLMService):
    """DeepSeek LLM服务实现"""

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com",
        **kwargs,
    ):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.kwargs = kwargs

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """生成回复"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **self.kwargs,
        )
        return response.choices[0].message.content

    async def generate_response_stream(
        self, messages: List[Dict[str, str]]
    ) -> AsyncIterator[str]:
        """流式生成回复"""
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            **self.kwargs,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
