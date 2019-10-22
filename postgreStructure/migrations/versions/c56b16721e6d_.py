"""empty message

Revision ID: c56b16721e6d
Revises: 
Create Date: 2019-03-28 22:49:48.850872

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c56b16721e6d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('Vendor', sa.String(length=80), nullable=False),
    sa.Column('Menu', sa.LargeBinary(), nullable=True),
    sa.Column('Queue_Image', sa.LargeBinary(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('Vendor')
    )
    op.create_table('timelog',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('Time', sa.DateTime(), nullable=True),
    sa.Column('Queue_Length', sa.Integer(), nullable=False),
    sa.Column('Audience', sa.String(length=200), nullable=False),
    sa.Column('Activities_Of_Interest', sa.String(length=500), nullable=False),
    sa.Column('info_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['info_id'], ['info.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('info_id', 'Time', name='composite_unique')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('timelog')
    op.drop_table('info')
    # ### end Alembic commands ###