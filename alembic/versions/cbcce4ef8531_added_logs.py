"""added logs

Revision ID: cbcce4ef8531
Revises: a90c22f7a6ae
Create Date: 2025-04-23 15:47:14.992250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cbcce4ef8531'
down_revision: Union[str, None] = 'a90c22f7a6ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('logs',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_ip', sa.String(length=15), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(), nullable=False),
    sa.Column('information', sa.Text(), nullable=True),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('logs')
    # ### end Alembic commands ###
