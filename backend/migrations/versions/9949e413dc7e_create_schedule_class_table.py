"""create schedule class table

Revision ID: 9949e413dc7e
Revises: 153c7712ff1d
Create Date: 2023-04-22 22:49:05.638265

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9949e413dc7e'
down_revision = '153c7712ff1d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('classes',
    sa.Column('class_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('week', sa.Integer(), nullable=True),
    sa.Column('day', sa.Integer(), nullable=True),
    sa.Column('time', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('class_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('classes')
    # ### end Alembic commands ###
