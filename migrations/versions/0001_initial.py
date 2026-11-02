"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-11-01
"""

from __future__ import annotations

from alembic import op

from app.db.base import Base
from app.db.schema import ensure_schema_sync

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    ensure_schema_sync(op.get_bind())


def downgrade() -> None:
    conn = op.get_bind()
    for name in ("jobs_au", "jobs_ad", "jobs_ai"):
        conn.exec_driver_sql(f"DROP TRIGGER IF EXISTS {name}")
    conn.exec_driver_sql("DROP TABLE IF EXISTS jobs_fts")
    Base.metadata.drop_all(bind=conn)
