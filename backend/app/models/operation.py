from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin

class Operation(Base, TimestampMixin):
    __tablename__ = "operations"
    __table_args__ = (
        Index("ix_operations_status", "status"),
        Index("ix_operations_started", "started_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    device_id: Mapped[Optional[int]] = mapped_column(ForeignKey("devices.id", ondelete="SET NULL"))
    operation_type: Mapped[str] = mapped_column(String(64), nullable=False)  # command, backup, restore, test
    command: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error: Mapped[Optional[str]] = mapped_column(Text)

    result: Mapped[Optional["OperationResult"]] = relationship(
        "OperationResult", back_populates="operation", uselist=False, cascade="all, delete-orphan", lazy="selectin"
    )

class OperationResult(Base, TimestampMixin):
    __tablename__ = "operation_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey("operations.id", ondelete="CASCADE"))
    success: Mapped[bool] = mapped_column()
    output: Mapped[Optional[str]] = mapped_column(Text)
    error: Mapped[Optional[str]] = mapped_column(Text)

    operation: Mapped["Operation"] = relationship("Operation", back_populates="result", lazy="selectin")
