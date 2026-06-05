from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Index, Integer, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base
from src.models.alert_metric_type import AlertMetricType
from src.models.alert_status import AlertStatus

if TYPE_CHECKING:
    from src.models.alert_history import AlertHistory
    from src.models.organization import Organization


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        Index("ix_alerts_organization_id", "organization_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    metric_type: Mapped[AlertMetricType] = mapped_column(
        Enum(AlertMetricType, name="alertmetrictype", values_callable=lambda e: [i.value for i in e]),
        nullable=False,
    )
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    window_minutes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="5")
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, name="alertstatus", values_callable=lambda e: [i.value for i in e]),
        nullable=False,
        default=AlertStatus.ACTIVE,
        server_default="ACTIVE",
    )
    is_muted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    organization: Mapped["Organization"] = relationship("Organization", back_populates="alerts")
    history: Mapped[list["AlertHistory"]] = relationship(
        "AlertHistory",
        back_populates="alert",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
