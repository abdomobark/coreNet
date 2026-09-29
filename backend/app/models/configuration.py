from __future__ import annotations
from typing import List, Optional

from sqlalchemy import String, Text, Integer, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin

class Configuration(Base, TimestampMixin):
    __tablename__ = "configurations"
    __table_args__ = (
        Index("ix_configurations_device", "device_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    current_version_id: Mapped[Optional[int]] = mapped_column(ForeignKey("configuration_versions.id", ondelete="SET NULL"))

    device: Mapped["Device"] = relationship("Device", back_populates="configurations", lazy="selectin")
    versions: Mapped[List["ConfigurationVersion"]] = relationship(
        "ConfigurationVersion",
        back_populates="configuration",
        cascade="all, delete-orphan",
        foreign_keys="ConfigurationVersion.configuration_id",
        lazy="selectin",
    )
    current_version: Mapped[Optional["ConfigurationVersion"]] = relationship(
        "ConfigurationVersion", foreign_keys=[current_version_id], uselist=False, post_update=True, lazy="selectin"
    )

class ConfigurationVersion(Base, TimestampMixin):
    __tablename__ = "configuration_versions"
    __table_args__ = (
        UniqueConstraint("configuration_id", "version", name="uq_conf_ver"),
        Index("ix_configuration_versions_config", "configuration_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    configuration_id: Mapped[int] = mapped_column(ForeignKey("configurations.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    config_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    configuration: Mapped["Configuration"] = relationship(
        "Configuration",
        back_populates="versions",
        foreign_keys=[configuration_id],
        lazy="selectin",
    )
