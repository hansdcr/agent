"""rename metadata to extra_data

Revision ID: 002
Revises: 001
Create Date: 2026-03-14 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 重命名 metadata 列为 extra_data
    op.alter_column('memories', 'metadata', new_column_name='extra_data')


def downgrade() -> None:
    # 回滚：重命名 extra_data 列为 metadata
    op.alter_column('memories', 'extra_data', new_column_name='metadata')
