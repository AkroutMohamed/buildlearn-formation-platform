"""add_course_instructors

Revision ID: 86d5634dad9e
Revises: d075d494b9e6
Create Date: 2026-08-13 11:18:42.013376

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86d5634dad9e'
down_revision: Union[str, Sequence[str], None] = 'd075d494b9e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'course_instructors',
        sa.Column('course_id', sa.UUID(), nullable=False),
        sa.Column('instructor_id', sa.UUID(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['instructor_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('course_id', 'instructor_id')
    )

    op.execute("""
        INSERT INTO course_instructors (course_id, instructor_id, assigned_at)
        SELECT c.id, c.instructor_id, NOW()
        FROM courses c
        WHERE c.instructor_id IS NOT NULL
          AND EXISTS (
              SELECT 1 FROM users u
              WHERE u.id = c.instructor_id
                AND u.role = 'INSTRUCTOR'
          )
        ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('course_instructors')
