"""create states table

Revision ID: 692bdea5106b
Revises: 9949e413dc7e
Create Date: 2023-04-23 17:24:55.977331

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '692bdea5106b'
down_revision = '9949e413dc7e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('states',
    sa.Column('classroom_id', sa.Integer(), nullable=False),
    sa.Column('class_id', sa.Integer(), nullable=False),
    sa.Column('state', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['class_id'], ['classes.class_id'], ),
    sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.classroom_id'], ),
    sa.PrimaryKeyConstraint('classroom_id', 'class_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('states')
    # ### end Alembic commands ###
