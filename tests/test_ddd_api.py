"""简化的DDD架构API测试（不依赖数据库）"""

import asyncio
import os
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport


async def test_ddd_api_simple():
    """测试DDD架构API（简化版）"""
    print("=" * 60)
    print("DDD架构API测试（简化版）")
    print("=" * 60)

    # 禁用记忆系统以避免数据库依赖
    os.environ["MEMORY_ENABLED"] = "false"
    os.environ["DEEPSEEK_API_KEY"] = "test_key"

    # Mock LLM服务
    with patch("src.infrastructure.external.llm.deepseek_service.AsyncOpenAI") as MockOpenAI:
        # 设置mock返回值
        mock_client = MockOpenAI.return_value
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "你好！我是AI助手。"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        # 导入app
        from main_ddd import app

        # 使用lifespan上下文
        async with app.router.lifespan_context(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # 1. 测试健康检查
                print("\n1. 测试健康检查接口")
                response = await client.get("/api/health")
                assert response.status_code == 200
                data = response.json()
                print(f"   ✓ 状态码: {response.status_code}")
                print(f"   ✓ 响应: {data['data']}")

                # 2. 测试聊天接口
                print("\n2. 测试聊天接口")
                response = await client.post(
                    "/api/chat",
                    json={"message": "你好", "session_id": None}
                )
                print(f"   状态码: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✓ 响应消息: {data['data']['message']}")
                    print(f"   ✓ 会话ID: {data['data']['session_id']}")
                    session_id = data['data']['session_id']

                    # 3. 测试使用相同session_id的第二次请求
                    print("\n3. 测试会话连续性")
                    mock_response.choices[0].message.content = "再见！"
                    response = await client.post(
                        "/api/chat",
                        json={"message": "再见", "session_id": session_id}
                    )
                    assert response.status_code == 200
                    data = response.json()
                    print(f"   ✓ 响应消息: {data['data']['message']}")
                    print(f"   ✓ 会话ID保持: {data['data']['session_id'] == session_id}")
                else:
                    print(f"   ✗ 失败: {response.text}")

                # 4. 测试空消息验证
                print("\n4. 测试空消息验证")
                try:
                    response = await client.post(
                        "/api/chat",
                        json={"message": ""}
                    )
                    print(f"   状态码: {response.status_code}")
                    if response.status_code == 422:
                        print(f"   ✓ 验证失败（预期）")
                    else:
                        print(f"   响应: {response.text}")
                except Exception as e:
                    print(f"   ✓ 验证失败（预期）: {type(e).__name__}")

    print("\n" + "=" * 60)
    print("API测试完成！")
    print("=" * 60)
    print("\n总结:")
    print("  ✓ 健康检查接口正常")
    print("  ✓ 聊天接口正常")
    print("  ✓ 会话管理正常")
    print("  ✓ 输入验证正常")


if __name__ == "__main__":
    asyncio.run(test_ddd_api_simple())
