"""initial schema

Revision ID: 000000000001
Revises:
Create Date: 2026-02-03 20:32:03.725703

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "000000000001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.create_index("ix_users_is_deleted", "users", ["is_deleted"], unique=False)

    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("code", name="uq_courses_code"),
    )
    op.create_index("ix_courses_code", "courses", ["code"], unique=False)
    op.create_index("ix_courses_is_deleted", "courses", ["is_deleted"], unique=False)

    op.create_table(
        "enrollments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_enrollments_user_id", "enrollments", ["user_id"], unique=False)
    op.create_index("ix_enrollments_course_id", "enrollments", ["course_id"], unique=False)
    op.create_index(
        "ix_enrollments_is_deleted",
        "enrollments",
        ["is_deleted"],
        unique=False,
    )

    op.create_table(
        "enrollment_audits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "actor_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id"), nullable=True),
        sa.Column(
            "enrollment_id",
            sa.Integer(),
            sa.ForeignKey("enrollments.id"),
            nullable=True,
        ),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_enrollment_audits_actor_user_id",
        "enrollment_audits",
        ["actor_user_id"],
        unique=False,
    )
    op.create_index("ix_enrollment_audits_user_id", "enrollment_audits", ["user_id"], unique=False)
    op.create_index(
        "ix_enrollment_audits_course_id",
        "enrollment_audits",
        ["course_id"],
        unique=False,
    )
    op.create_index(
        "ix_enrollment_audits_enrollment_id",
        "enrollment_audits",
        ["enrollment_id"],
        unique=False,
    )

    # Remove server defaults where the application provides defaults.
    op.alter_column("users", "is_active", server_default=None)
    op.alter_column("users", "is_deleted", server_default=None)
    op.alter_column("courses", "is_active", server_default=None)
    op.alter_column("courses", "is_deleted", server_default=None)
    op.alter_column("enrollments", "created_at", server_default=None)
    op.alter_column("enrollments", "is_deleted", server_default=None)
    op.alter_column("enrollment_audits", "created_at", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_enrollment_audits_enrollment_id", table_name="enrollment_audits")
    op.drop_index("ix_enrollment_audits_course_id", table_name="enrollment_audits")
    op.drop_index("ix_enrollment_audits_user_id", table_name="enrollment_audits")
    op.drop_index("ix_enrollment_audits_actor_user_id", table_name="enrollment_audits")
    op.drop_table("enrollment_audits")

    op.drop_index("ix_enrollments_is_deleted", table_name="enrollments")
    op.drop_index("ix_enrollments_course_id", table_name="enrollments")
    op.drop_index("ix_enrollments_user_id", table_name="enrollments")
    op.drop_table("enrollments")

    op.drop_index("ix_courses_is_deleted", table_name="courses")
    op.drop_index("ix_courses_code", table_name="courses")
    op.drop_table("courses")

    op.drop_index("ix_users_is_deleted", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
