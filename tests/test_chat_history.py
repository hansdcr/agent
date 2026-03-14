"""测试历史消息API"""
import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
import os


@pytest.mark.asyncio
async def test_chat_history_api():
    """测试聊天历史API"""
    print("=" * 60)
    print("测试聊天历史API")
    print("=" * 60)

    # 禁用记忆系统
    os.environ["MEMORY_ENABLED"] = "false"
    os.environ["DEEPSEEK_API_KEY"] = "test_key"

    # Mock LLM服务
    with patch("src.infrastructure.external.llm.deepseek_service.AsyncOpenAI") as MockOpenAI:
        mock_client = MockOpenAI.return_value
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "你好！我是AI助手。"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        from main import app

        async with app.router.lifespan_context(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # 1. 发送第一条消息
                print("\n1. 发送第一条消息")
                response = await client.post(
                    "/api/chat",
                    json={"message": "你好", "session_id": None}
                )
                assert response.status_code == 200
                data = response.json()
                session_id = data['data']['session_id']
                print(f"   ✓ 会话ID: {session_id}")

                # 2. 发送第二条消息
                print("\n2. 发送第二条消息")
                mock_response.choices[0].message.content = "有什么可以帮你的吗？"
                response = await client.post(
                    "/api/chat",
                    json={"message": "你能做什么？", "session_id": session_id}
                )
                assert response.status_code == 200
                print("   ✓ 第二条消息发送成功")

                # 3. 获取历史消息
                print("\n3. 获取历史消息")
                response = await client.get(f"/api/chat/history/{session_id}")
                assert response.status_code == 200
                data = response.json()
                messages = data['data']['messages']
                print(f"   ✓ 获取到 {len(messages)} 条消息")

                for i, msg in enumerate(messages, 1):
                    print(f"   {i}. [{msg['role']}] {msg['content'][:30]}...")

                # 验证消息数量（2条用户消息 + 2条助手消息 = 4条）
                assert len(messages) == 4
                assert messages[0]['role'] == 'user'
                assert messages[1]['role'] == 'assistant'
                assert messages[2]['role'] == 'user'
                assert messages[3]['role'] == 'assistant'

                # 4. 测试不存在的会话
                print("\n4. 测试不存在的会话")
                response = await client.get("/api/chat/history/non-existent-session")
                assert response.status_code == 200
                data = response.json()
                assert len(data['data']['messages']) == 0
                print("   ✓ 不存在的会话返回空列表")

    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_chat_history_api())
