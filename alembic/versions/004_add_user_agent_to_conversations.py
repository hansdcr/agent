"""add user_id and agent_id to conversations

Revision ID: 004
Revises: 003
Create Date: 2026-03-14 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加 user_id 和 agent_id 字段
    op.add_column('conversations', sa.Column('user_id', sa.String(255), nullable=True))
    op.add_column('conversations', sa.Column('agent_id', sa.String(255), nullable=True))

    # 创建索引
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_agent_id', 'conversations', ['agent_id'])
    op.create_index('idx_conversations_user_agent', 'conversations', ['user_id', 'agent_id'])


def downgrade() -> None:
    # 删除索引
    op.drop_index('idx_conversations_user_agent')
    op.drop_index('idx_conversations_agent_id')
    op.drop_index('idx_conversations_user_id')

    # 删除字段
    op.drop_column('conversations', 'agent_id')
    op.drop_column('conversations', 'user_id')
