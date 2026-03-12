"""API接口测试.

测试聊天接口和流式接口的基本功能。
使用mock避免真实API调用。
"""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch

from main import app


@pytest.fixture
def test_settings(monkeypatch):
    """设置测试环境变量并初始化app.state.

    Args:
        monkeypatch: pytest的monkeypatch fixture
    """
    from src.config.settings import Settings

    monkeypatch.setenv("DEEPSEEK_API_KEY", "test_key_for_testing")
    # 手动初始化app.state.settings
    app.state.settings = Settings()


@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查接口."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        # 验证统一响应格式
        assert data["code"] == 200
        assert data["status"] == 200
        assert "data" in data
        assert data["data"]["status"] == "healthy"
        assert "version" in data["data"]


@pytest.mark.asyncio
async def test_chat_endpoint(test_settings):
    """测试普通聊天接口.

    Args:
        test_settings: 测试环境变量fixture
    """
    # Mock LLM客户端的chat方法
    with patch("src.api.routes.chat.DeepSeekClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.chat = AsyncMock(return_value="你好！我是AI助手。")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 发送第一条消息
            response = await client.post(
                "/chat/", json={"message": "你好", "session_id": None}
            )
            assert response.status_code == 200
            data = response.json()
            # 验证统一响应格式
            assert data["code"] == 200
            assert data["status"] == 200
            assert "data" in data
            assert "message" in data["data"]
            assert "session_id" in data["data"]
            assert data["data"]["message"] == "你好！我是AI助手。"

            # 使用相同session_id发送第二条消息
            session_id = data["data"]["session_id"]
            mock_instance.chat = AsyncMock(return_value="再见！")
            response = await client.post(
                "/chat/", json={"message": "再见", "session_id": session_id}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert data["status"] == 200
            assert data["data"]["session_id"] == session_id
            assert data["data"]["message"] == "再见！"


@pytest.mark.asyncio
async def test_chat_stream_endpoint(test_settings):
    """测试流式聊天接口.

    Args:
        test_settings: 测试环境变量fixture
    """

    async def mock_stream():
        """Mock流式生成器."""
        for chunk in ["你", "好", "！"]:
            yield chunk

    # Mock LLM客户端的chat_stream方法
    with patch("src.api.routes.chat.DeepSeekClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.chat_stream = AsyncMock(return_value=mock_stream())

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 发送流式请求
            async with client.stream(
                "POST",
                "/chat/stream",
                json={"message": "你好", "session_id": None},
            ) as response:
                assert response.status_code == 200
                assert "text/event-stream" in response.headers["content-type"]

                # 读取流式响应
                chunks = []
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        chunks.append(line)

                # 验证至少收到了一些数据
                assert len(chunks) > 0
                # 第一个chunk应该包含session_id
                assert "session_id" in chunks[0]


@pytest.mark.asyncio
async def test_chat_empty_message():
    """测试空消息验证."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/chat/", json={"message": ""})
        assert response.status_code == 422  # Validation error
