"""DDD架构对比测试

对比原架构和DDD架构的实现
"""

import asyncio
from src.domain.chat.entities import Conversation, Message
from src.domain.chat.value_objects import SessionId, MessageRole, MessageContent


async def test_ddd_architecture():
    """测试DDD架构"""
    print("=" * 60)
    print("DDD架构测试")
    print("=" * 60)

    # 1. 测试值对象
    print("\n1. 测试值对象")
    session_id = SessionId.generate()
    print(f"   ✓ 生成会话ID: {session_id.value}")

    role = MessageRole.user()
    print(f"   ✓ 创建消息角色: {role.value}")

    content = MessageContent("你好，AI助手！")
    print(f"   ✓ 创建消息内容: {content.value}")

    # 2. 测试实体
    print("\n2. 测试实体")
    message = Message.create_user("你好，AI助手！")
    print(f"   ✓ 创建用户消息: {message.to_dict()}")

    # 3. 测试聚合根
    print("\n3. 测试聚合根")
    conversation = Conversation(
        session_id=session_id,
        system_prompt="你是一个有帮助的AI助手。",
    )
    print(f"   ✓ 创建对话: session_id={conversation.session_id.value}")

    conversation.add_user_message("你好")
    conversation.add_assistant_message("你好！我是AI助手。")
    print(f"   ✓ 添加消息: 消息数量={conversation.message_count()}")

    messages = conversation.get_messages_as_dicts()
    print(f"   ✓ 获取消息列表: {len(messages)} 条消息")

    # 4. 测试领域规则
    print("\n4. 测试领域规则")
    try:
        invalid_content = MessageContent("")
    except Exception as e:
        print(f"   ✓ 验证失败（预期）: {e}")

    print("\n" + "=" * 60)
    print("DDD架构测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_ddd_architecture())
