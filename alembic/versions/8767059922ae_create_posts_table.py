"""create posts table

Revision ID: 8767059922ae
Revises: 22d21d3b4c12
Create Date: 2022-10-09 15:55:13.416445

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8767059922ae'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('posts', sa.Column('id', sa.Integer(), nullable=False, primary_key=True), sa.Column('title', sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_table('users')
    pass
