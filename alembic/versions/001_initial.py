"""initial migration

Revision ID: 001
Revises:
Create Date: 2024-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create collections table
    op.create_table(
        'collections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_collections_id'), 'collections', ['id'], unique=False)

    # Create bookmarks table
    op.create_table(
        'bookmarks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('url', sa.String(length=2048), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('collection_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['collection_id'], ['collections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bookmarks_id'), 'bookmarks', ['id'], unique=False)
    op.create_index(op.f('ix_bookmarks_collection_id'), 'bookmarks', ['collection_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_bookmarks_collection_id'), table_name='bookmarks')
    op.drop_index(op.f('ix_bookmarks_id'), table_name='bookmarks')
    op.drop_table('bookmarks')
    op.drop_index(op.f('ix_collections_id'), table_name='collections')
    op.drop_table('collections')
