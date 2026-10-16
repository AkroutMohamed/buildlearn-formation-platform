"""add_instructor_status

Revision ID: d075d494b9e6
Revises: 86414196097d
Create Date: 2026-08-13 10:48:29.610864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd075d494b9e6'
down_revision: Union[str, Sequence[str], None] = '86414196097d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    instructor_status = sa.Enum('PENDING', 'ACTIVE', 'REJECTED', name='instructorstatus')
    instructor_status.create(op.get_bind(), checkfirst=True)
    op.add_column('users', sa.Column('instructor_status', instructor_status, nullable=False, server_default='ACTIVE'))
    op.alter_column('users', 'instructor_status', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'instructor_status')
    sa.Enum(name='instructorstatus').drop(op.get_bind(), checkfirst=True)
