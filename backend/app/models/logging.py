from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin

class SystemLog(Base, TimestampMixin):
    __tablename__ = "system_logs"
    __table_args__ = (
        Index("ix_system_logs_level", "level"),
        Index("ix_system_logs_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    level: Mapped[str] = mapped_column(String(16), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    logger: Mapped[Optional[str]] = mapped_column(String(128))
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    device_id: Mapped[Optional[int]] = mapped_column(ForeignKey("devices.id", ondelete="SET NULL"))
    context: Mapped[Optional[dict]] = mapped_column(JSONB)

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_created", "created_at"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_user", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(64))
    resource_id: Mapped[Optional[int]] = mapped_column()
    device_id: Mapped[Optional[int]] = mapped_column(ForeignKey("devices.id", ondelete="SET NULL"))
    source_ip: Mapped[Optional[str]] = mapped_column(String(64))
    status: Mapped[Optional[str]] = mapped_column(String(32))
    details: Mapped[Optional[str]] = mapped_column(Text)

class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_user", "user_id"),
        Index("ix_notifications_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    channel: Mapped[str] = mapped_column(String(32), nullable=False)  # email, slack, webhook
    subject: Mapped[Optional[str]] = mapped_column(String(255))
    body: Mapped[Optional[str]] = mapped_column(Text)
    meta: Mapped[Optional[dict]] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
