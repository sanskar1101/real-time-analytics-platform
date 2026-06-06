from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base
from src.models.metric_type import MetricType
from src.models.widget_type import WidgetType

if TYPE_CHECKING:
    from src.models.dashboard import Dashboard


class Widget(Base):
    __tablename__ = "widgets"
    __table_args__ = (Index("ix_widgets_dashboard_id", "dashboard_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    dashboard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dashboards.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    widget_type: Mapped[WidgetType] = mapped_column(
        Enum(WidgetType, name="widgettype", values_callable=lambda e: [i.value for i in e]),
        nullable=False,
    )
    metric_type: Mapped[MetricType] = mapped_column(
        Enum(MetricType, name="metrictype", values_callable=lambda e: [i.value for i in e]),
        nullable=False,
    )
    time_range: Mapped[str | None] = mapped_column(String(50), nullable=True)
    position_x: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    position_y: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    width: Mapped[int] = mapped_column(Integer, nullable=False, server_default="4")
    height: Mapped[int] = mapped_column(Integer, nullable=False, server_default="3")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    dashboard: Mapped[Dashboard] = relationship("Dashboard", back_populates="widgets")
