"""quizresult_cascade

Revision ID: a1b2c3d4e5f6
Revises: 86d5634dad9e
Create Date: 2026-08-13 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '86d5634dad9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(op.f('quiz_results_course_id_fkey'), 'quiz_results', type_='foreignkey')
    op.drop_constraint(op.f('quiz_results_quiz_id_fkey'), 'quiz_results', type_='foreignkey')
    op.create_foreign_key(None, 'quiz_results', 'courses', ['course_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'quiz_results', 'quizzes', ['quiz_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, 'quiz_results', type_='foreignkey')
    op.drop_constraint(None, 'quiz_results', type_='foreignkey')
    op.create_foreign_key(op.f('quiz_results_quiz_id_fkey'), 'quiz_results', 'quizzes', ['quiz_id'], ['id'])
    op.create_foreign_key(op.f('quiz_results_course_id_fkey'), 'quiz_results', 'courses', ['course_id'], ['id'])
