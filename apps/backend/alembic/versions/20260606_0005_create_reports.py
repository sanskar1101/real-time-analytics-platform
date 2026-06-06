"""create reports

Revision ID: 20260606_0005
Revises: fee6d9fcfa62
Create Date: 2026-06-06
"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260606_0005"
down_revision: Union[str, None] = "fee6d9fcfa62"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

reportfrequency_enum = postgresql.ENUM(
    "DAILY",
    "WEEKLY",
    "MONTHLY",
    name="reportfrequency",
    create_type=False,
)


def upgrade() -> None:
    reportfrequency_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "reports",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dashboard_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("frequency", reportfrequency_enum, nullable=False),
        sa.Column("file_path", sa.String(length=1024), nullable=True),
        sa.Column("last_generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_reports_organization_id_organizations",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["dashboard_id"],
            ["dashboards.id"],
            name="fk_reports_dashboard_id_dashboards",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reports_organization_id", "reports", ["organization_id"])
    op.create_index("ix_reports_dashboard_id", "reports", ["dashboard_id"])


def downgrade() -> None:
    op.drop_index("ix_reports_dashboard_id", table_name="reports")
    op.drop_index("ix_reports_organization_id", table_name="reports")
    op.drop_table("reports")
    reportfrequency_enum.drop(op.get_bind(), checkfirst=True)
