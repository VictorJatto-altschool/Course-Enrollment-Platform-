"""add soft delete columns

Revision ID: 6b3a0b8f9c1d
Revises: ed2172ff9f92
Create Date: 2026-02-03

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "6b3a0b8f9c1d"
down_revision: str | None = "ed2172ff9f92"
branch_labels: str | None = None
depends_on: str | None = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def _has_index(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    indexes = [idx["name"] for idx in inspector.get_indexes(table_name)]
    return index_name in indexes


def upgrade() -> None:
    # courses
    if not _has_column("courses", "is_deleted"):
        op.add_column(
            "courses",
            sa.Column(
                "is_deleted",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )
        # Remove default after backfill
        op.alter_column("courses", "is_deleted", server_default=None)

    if not _has_column("courses", "deleted_at"):
        op.add_column(
            "courses",
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        )

    if not _has_index("courses", "ix_courses_is_deleted"):
        op.create_index("ix_courses_is_deleted", "courses", ["is_deleted"], unique=False)

    # enrollments
    if not _has_column("enrollments", "is_deleted"):
        op.add_column(
            "enrollments",
            sa.Column(
                "is_deleted",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )
        op.alter_column("enrollments", "is_deleted", server_default=None)

    if not _has_column("enrollments", "deleted_at"):
        op.add_column(
            "enrollments",
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        )

    if not _has_index("enrollments", "ix_enrollments_is_deleted"):
        op.create_index(
            "ix_enrollments_is_deleted",
            "enrollments",
            ["is_deleted"],
            unique=False,
        )


def downgrade() -> None:
    # enrollments
    if _has_index("enrollments", "ix_enrollments_is_deleted"):
        op.drop_index("ix_enrollments_is_deleted", table_name="enrollments")

    if _has_column("enrollments", "deleted_at"):
        op.drop_column("enrollments", "deleted_at")

    if _has_column("enrollments", "is_deleted"):
        op.drop_column("enrollments", "is_deleted")

    # courses
    if _has_index("courses", "ix_courses_is_deleted"):
        op.drop_index("ix_courses_is_deleted", table_name="courses")

    if _has_column("courses", "deleted_at"):
        op.drop_column("courses", "deleted_at")

    if _has_column("courses", "is_deleted"):
        op.drop_column("courses", "is_deleted")
