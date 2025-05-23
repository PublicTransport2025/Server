"""added login indexes

Revision ID: 7dceba6eab0d
Revises: cbcce4ef8531
Create Date: 2025-05-18 18:30:44.981390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7dceba6eab0d'
down_revision: Union[str, None] = 'cbcce4ef8531'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_users_login'), 'users', ['login'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_login'), table_name='users')
    # ### end Alembic commands ###
