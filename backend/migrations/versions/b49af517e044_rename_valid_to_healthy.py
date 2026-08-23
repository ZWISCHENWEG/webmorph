"""rename_valid_to_healthy

Revision ID: b49af517e044
Revises: f11d6dd45df1
Create Date: 2026-08-22 16:07:09.768342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b49af517e044'
down_revision: Union[str, Sequence[str], None] = 'f11d6dd45df1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        # On PostgreSQL, we must create a new type and cast the data to handle ENUM changes
        op.execute("ALTER TYPE validationstate RENAME TO validationstate_old")
        op.execute("CREATE TYPE validationstate AS ENUM('PENDING', 'HEALTHY', 'INVALID', 'DEGRADED', 'DRIFT_DETECTED')")
        op.execute(
            "ALTER TABLE snapshots ALTER COLUMN validation_state TYPE validationstate USING ("
            "CASE "
            "WHEN validation_state::text = 'VALID' THEN 'HEALTHY'::validationstate "
            "ELSE validation_state::text::validationstate "
            "END)"
        )
        op.execute("DROP TYPE validationstate_old")
    else:
        # SQLite
        op.execute("UPDATE snapshots SET validation_state = 'HEALTHY' WHERE validation_state = 'VALID'")
        with op.batch_alter_table('snapshots', schema=None) as batch_op:
            batch_op.alter_column('validation_state',
                   existing_type=sa.Enum('PENDING', 'VALID', 'INVALID', 'DEGRADED', 'DRIFT_DETECTED', name='validationstate'),
                   type_=sa.Enum('PENDING', 'HEALTHY', 'INVALID', 'DEGRADED', 'DRIFT_DETECTED', name='validationstate'),
                   existing_nullable=False)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute("ALTER TYPE validationstate RENAME TO validationstate_old")
        op.execute("CREATE TYPE validationstate AS ENUM('PENDING', 'VALID', 'INVALID', 'DEGRADED', 'DRIFT_DETECTED')")
        op.execute(
            "ALTER TABLE snapshots ALTER COLUMN validation_state TYPE validationstate USING ("
            "CASE "
            "WHEN validation_state::text = 'HEALTHY' THEN 'VALID'::validationstate "
            "ELSE validation_state::text::validationstate "
            "END)"
        )
        op.execute("DROP TYPE validationstate_old")
    else:
        op.execute("UPDATE snapshots SET validation_state = 'VALID' WHERE validation_state = 'HEALTHY'")
        with op.batch_alter_table('snapshots', schema=None) as batch_op:
            batch_op.alter_column('validation_state',
                   existing_type=sa.Enum('PENDING', 'HEALTHY', 'INVALID', 'DEGRADED', 'DRIFT_DETECTED', name='validationstate'),
                   type_=sa.Enum('PENDING', 'VALID', 'INVALID', 'DEGRADED', 'DRIFT_DETECTED', name='validationstate'),
                   existing_nullable=False)
