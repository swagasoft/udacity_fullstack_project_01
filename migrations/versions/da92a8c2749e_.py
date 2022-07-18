"""empty message

Revision ID: da92a8c2749e
Revises: 55281b50590a
Create Date: 2022-06-07 22:25:34.987978

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da92a8c2749e'
down_revision = '55281b50590a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website_link', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'website_link')
    # ### end Alembic commands ###
