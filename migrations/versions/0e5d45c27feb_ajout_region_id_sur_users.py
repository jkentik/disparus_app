"""ajout region_id sur users

Revision ID: 0e5d45c27feb
Revises: 3f8d733bd891
Create Date: 2026-09-14 20:45:25.246286

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e5d45c27feb'
down_revision = '3f8d733bd891'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('region_id', sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('region_id')
