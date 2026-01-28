"""seed default roles

Revision ID: 1c4bd058a11d
Revises: b137341cacb9
Create Date: 2026-01-28 09:42:27.016016

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "1c4bd058a11d"
down_revision: Union[str, Sequence[str], None] = "b137341cacb9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
    op.execute("""
        INSERT INTO roles (id, name, created_at, updated_at) VALUES
            (gen_random_uuid(), 'sys_admin', now(), now()),
            (gen_random_uuid(), 'institution_admin', now(), now()),
            (gen_random_uuid(), 'candidate', now(), now())
        ON CONFLICT (name) DO NOTHING;
    """)


def downgrade():
    op.execute("""
        DELETE FROM roles
        WHERE name IN ('sys_admin', 'institution_admin', 'candidate');
    """)
