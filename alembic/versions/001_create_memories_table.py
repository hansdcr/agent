"""create memories table

Revision ID: 001
Revises:
Create Date: 2026-03-14 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建memories表
    op.create_table(
        'memories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', sa.String(255), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=True),
        sa.Column('memory_type', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('importance', sa.String(50), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('accessed_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('access_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
    )

    # 添加CHECK约束
    op.create_check_constraint(
        'memories_memory_type_check',
        'memories',
        "memory_type IN ('short_term', 'long_term')"
    )
    op.create_check_constraint(
        'memories_importance_check',
        'memories',
        "importance IN ('low', 'medium', 'high')"
    )

    # 创建索引
    op.create_index('idx_memories_session_id', 'memories', ['session_id'])
    op.create_index('idx_memories_user_id', 'memories', ['user_id'])
    op.create_index('idx_memories_memory_type', 'memories', ['memory_type'])
    op.create_index('idx_memories_importance', 'memories', ['importance'])
    op.create_index('idx_memories_created_at', 'memories', ['created_at'])
    op.create_index('idx_memories_accessed_at', 'memories', ['accessed_at'])

    # 创建JSONB索引（用于元数据查询）
    op.execute('CREATE INDEX idx_memories_metadata ON memories USING GIN(metadata)')

    # 创建全文搜索索引（用于内容搜索）
    op.execute("CREATE INDEX idx_memories_content_fts ON memories USING GIN(to_tsvector('english', content))")


def downgrade() -> None:
    # 删除索引
    op.drop_index('idx_memories_content_fts')
    op.drop_index('idx_memories_metadata')
    op.drop_index('idx_memories_accessed_at')
    op.drop_index('idx_memories_created_at')
    op.drop_index('idx_memories_importance')
    op.drop_index('idx_memories_memory_type')
    op.drop_index('idx_memories_user_id')
    op.drop_index('idx_memories_session_id')

    # 删除表
    op.drop_table('memories')

