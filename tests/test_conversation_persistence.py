"""测试对话持久化功能"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.domain.chat.entities import Conversation
from src.domain.chat.value_objects import SessionId
from src.infrastructure.persistence.repositories.conversation_repository import (
    PostgresConversationRepository,
)
from src.infrastructure.persistence.models import Base


async def test_conversation_persistence():
    """测试对话持久化"""
    print("=" * 60)
    print("测试对话持久化功能")
    print("=" * 60)

    # 连接数据库
    database_url = "postgresql+asyncpg://agent:agent123@localhost:5432/agent_db"
    engine = create_async_engine(database_url, echo=False)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    repo = PostgresConversationRepository(session_factory)

    # 1. 创建新对话
    print("\n1. 创建新对话")
    session_id = SessionId.generate()
    conversation = Conversation(
        session_id=session_id,
        system_prompt="你是一个有帮助的AI助手。",
    )
    conversation.add_user_message("你好")
    conversation.add_assistant_message("你好！我是AI助手。")
    conversation.add_user_message("你能做什么？")
    conversation.add_assistant_message("我可以回答问题、提供建议等。")

    await repo.save(conversation)
    print(f"   ✓ 保存对话，session_id: {session_id.value}")
    print(f"   ✓ 消息数量: {conversation.message_count()}")

    # 2. 从数据库加载对话
    print("\n2. 从数据库加载对话")
    loaded_conversation = await repo.find_by_id(session_id)
    assert loaded_conversation is not None
    print(f"   ✓ 加载成功，session_id: {loaded_conversation.session_id.value}")
    print(f"   ✓ 消息数量: {loaded_conversation.message_count()}")

    # 验证消息内容
    messages = loaded_conversation.get_messages_as_dicts()
    print(f"   ✓ 消息列表:")
    for i, msg in enumerate(messages, 1):
        print(f"      {i}. [{msg['role']}] {msg['content'][:30]}...")

    # 3. 更新对话
    print("\n3. 更新对话")
    loaded_conversation.add_user_message("再见")
    loaded_conversation.add_assistant_message("再见！")
    await repo.save(loaded_conversation)
    print(f"   ✓ 更新成功，新消息数量: {loaded_conversation.message_count()}")

    # 4. 再次加载验证
    print("\n4. 再次加载验证")
    reloaded_conversation = await repo.find_by_id(session_id)
    assert reloaded_conversation is not None
    assert reloaded_conversation.message_count() == loaded_conversation.message_count()
    print(f"   ✓ 验证成功，消息数量: {reloaded_conversation.message_count()}")

    # 5. 删除对话
    print("\n5. 删除对话")
    await repo.delete(session_id)
    deleted_conversation = await repo.find_by_id(session_id)
    assert deleted_conversation is None
    print("   ✓ 删除成功")

    print("\n" + "=" * 60)
    print("✓ 所有测试通过！对话持久化功能正常")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_conversation_persistence())
