"""LTI 1.3: einmalige Launch-States

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-31 20:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('lti_launch_states',
    sa.Column('state', sa.String(length=64), nullable=False),
    sa.Column('nonce', sa.String(length=64), nullable=False),
    sa.Column('issuer', sa.String(length=255), nullable=False),
    sa.Column('client_id', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('state')
    )
    op.create_index(op.f('ix_lti_launch_states_created_at'), 'lti_launch_states', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_lti_launch_states_created_at'), table_name='lti_launch_states')
    op.drop_table('lti_launch_states')
