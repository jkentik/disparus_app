"""ajout photo profil user

Revision ID: f15b576c0feb
Revises: 2e9c66c76686
Create Date: 2026-09-14 18:53:44.447264

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f15b576c0feb'
down_revision = '2e9c66c76686'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('photo', sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('photo')