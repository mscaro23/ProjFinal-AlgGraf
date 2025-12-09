"""remove_target_page_id_foreign_key

Revision ID: e09200e715e5
Revises: 112ea99078cd
Create Date: 2025-12-06 12:45:47.075059

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e09200e715e5"
down_revision: Union[str, Sequence[str], None] = "112ea99078cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remove foreign key constraint do target_page_id
    # Isso permite salvar links apontando para páginas que ainda não existem
    op.drop_constraint("links_target_page_id_fkey", "links", type_="foreignkey")
    op.drop_constraint("links_source_page_id_fkey", "links", type_="foreignkey")


def downgrade() -> None:
    """Downgrade schema."""
    # Restaura a foreign key constraint
    op.create_foreign_key(
        "links_target_page_id_fkey", "links", "pages", ["target_page_id"], ["page_id"]
    )
