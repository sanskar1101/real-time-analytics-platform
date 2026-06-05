"""create alerts notifications

Revision ID: 20260605_0004
Revises: 20260605_0003
Create Date: 2026-06-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260605_0004"
down_revision: Union[str, None] = "20260605_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

alertstatus_enum = postgresql.ENUM(
    "ACTIVE",
    "TRIGGERED",
    "RESOLVED",
    "MUTED",
    name="alertstatus",
    create_type=False,
)

alertmetrictype_enum = postgresql.ENUM(
    "EVENT_COUNT",
    "ERROR_COUNT",
    name="alertmetrictype",
    create_type=False,
)


def upgrade() -> None:
    alertstatus_enum.create(op.get_bind(), checkfirst=True)
    alertmetrictype_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "alerts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("metric_type", alertmetrictype_enum, nullable=False),
        sa.Column("threshold", sa.Float(), nullable=False),
        sa.Column("window_minutes", sa.Integer(), server_default=sa.text("5"), nullable=False),
        sa.Column("status", alertstatus_enum, server_default="ACTIVE", nullable=False),
        sa.Column("is_muted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_alerts_organization_id_organizations",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alerts_organization_id", "alerts", ["organization_id"], unique=False)

    op.create_table(
        "alert_histories",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("alert_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("status", alertstatus_enum, nullable=False),
        sa.Column(
            "triggered_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["alert_id"],
            ["alerts.id"],
            name="fk_alert_histories_alert_id_alerts",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alert_histories_alert_id", "alert_histories", ["alert_id"], unique=False)

    op.create_table(
        "notifications",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_notifications_organization_id_organizations",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_notifications_organization_id_created_at",
        "notifications",
        ["organization_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_notifications_organization_id_created_at", table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("ix_alert_histories_alert_id", table_name="alert_histories")
    op.drop_table("alert_histories")
    op.drop_index("ix_alerts_organization_id", table_name="alerts")
    op.drop_table("alerts")
    alertmetrictype_enum.drop(op.get_bind(), checkfirst=True)
    alertstatus_enum.drop(op.get_bind(), checkfirst=True)
