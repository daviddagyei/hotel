"""add unique constraint to room number per property

Revision ID: 17a137a5564c
Revises: 5f43e83ed0b0
Create Date: 2025-05-20 12:03:57.644767

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17a137a5564c'
down_revision: Union[str, None] = '5f43e83ed0b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Use batch_alter_table for SQLite compatibility
    with op.batch_alter_table('rooms', schema=None) as batch_op:
        batch_op.create_unique_constraint('uix_property_room_number', ['property_id', 'number'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('rooms', schema=None) as batch_op:
        batch_op.drop_constraint('uix_property_room_number', type_='unique')
    # ### end Alembic commands ###
