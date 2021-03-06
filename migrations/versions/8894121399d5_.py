"""empty message

Revision ID: 8894121399d5
Revises: 1fe840add506
Create Date: 2022-06-09 09:06:15.091729

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8894121399d5'
down_revision = '1fe840add506'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('looking_for_talent', sa.String(), nullable=True))
    op.drop_column('Venue', 'seeking_talent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_talent', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('Venue', 'looking_for_talent')
    # ### end Alembic commands ###
