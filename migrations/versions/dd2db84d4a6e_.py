"""empty message

Revision ID: dd2db84d4a6e
Revises: 8894121399d5
Create Date: 2022-06-09 09:20:12.782094

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd2db84d4a6e'
down_revision = '8894121399d5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_venues', sa.String(), nullable=True))
    op.drop_column('Artist', 'looking_for_venues')
    op.add_column('Venue', sa.Column('seeking_talent', sa.String(), nullable=True))
    op.drop_column('Venue', 'looking_for_talent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('looking_for_talent', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('Venue', 'seeking_talent')
    op.add_column('Artist', sa.Column('looking_for_venues', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('Artist', 'seeking_venues')
    # ### end Alembic commands ###
