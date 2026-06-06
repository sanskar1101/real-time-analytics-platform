"""create dashboard widget engine

Revision ID: 20260605_0003
Revises: 20260604_0002
Create Date: 2026-06-05
"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260605_0003"
down_revision: Union[str, None] = "20260604_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

widgettype_enum = postgresql.ENUM(
    "KPI",
    "LINE",
    "BAR",
    "PIE",
    name="widgettype",
    create_type=False,
)

metrictype_enum = postgresql.ENUM(
    "EVENT_COUNT",
    "EVENTS_BY_DAY",
    "EVENTS_BY_TYPE",
    name="metrictype",
    create_type=False,
)


def upgrade() -> None:
    widgettype_enum.create(op.get_bind(), checkfirst=True)
    metrictype_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "dashboards",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_public", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_dashboards_organization_id_organizations",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_dashboards_organization_id", "dashboards", ["organization_id"], unique=False
    )

    op.create_table(
        "widgets",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("dashboard_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("widget_type", widgettype_enum, nullable=False),
        sa.Column("metric_type", metrictype_enum, nullable=False),
        sa.Column("time_range", sa.String(length=50), nullable=True),
        sa.Column("position_x", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("position_y", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("width", sa.Integer(), server_default=sa.text("4"), nullable=False),
        sa.Column("height", sa.Integer(), server_default=sa.text("3"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["dashboard_id"],
            ["dashboards.id"],
            name="fk_widgets_dashboard_id_dashboards",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_widgets_dashboard_id", "widgets", ["dashboard_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_widgets_dashboard_id", table_name="widgets")
    op.drop_table("widgets")
    op.drop_index("ix_dashboards_organization_id", table_name="dashboards")
    op.drop_table("dashboards")
    metrictype_enum.drop(op.get_bind(), checkfirst=True)
    widgettype_enum.drop(op.get_bind(), checkfirst=True)
