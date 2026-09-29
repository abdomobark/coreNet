from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin

class MonitoringMetric(Base, TimestampMixin):
    __tablename__ = "monitoring_metrics"
    __table_args__ = (
        Index("ix_metrics_device", "device_id"),
        Index("ix_metrics_type", "metric_type"),
        Index("ix_metrics_time", "timestamp"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"))
    metric_type: Mapped[str] = mapped_column(String(64), nullable=False)  # cpu, memory, iface_*, ping
    metric_value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    severity: Mapped[Optional[str]] = mapped_column(String(16))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    device: Mapped["Device"] = relationship("Device", lazy="selectin")

class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"
    __table_args__ = (
        Index("ix_alerts_status", "status"),
        Index("ix_alerts_severity", "severity"),
        Index("ix_alerts_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[Optional[int]] = mapped_column(ForeignKey("devices.id", ondelete="SET NULL"))
    alert_type: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)  # INFO/WARNING/CRITICAL
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="open")
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
