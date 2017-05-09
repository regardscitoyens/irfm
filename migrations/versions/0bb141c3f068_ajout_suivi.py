"""Ajout suivi

Revision ID: 0bb141c3f068
Revises: 0550bb4083f7
Create Date: 2017-05-09 20:24:07.173655

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0bb141c3f068'
down_revision = '0550bb4083f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('actions', sa.Column('suivi', sa.Unicode(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('actions', 'suivi')
    # ### end Alembic commands ###
