from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint, Index, Text
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin

class Device(Base, TimestampMixin):
    __tablename__ = "devices"
    __table_args__ = (
        Index("ix_devices_hostname", "hostname"),
        Index("ix_devices_ip", "ip_address"),
        Index("ix_devices_site", "site_id"),
        Index("ix_devices_type", "device_type"),
        Index("ix_devices_vendor", "vendor"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    hostname: Mapped[str] = mapped_column(String(128), nullable=False)
    ip_address: Mapped[str] = mapped_column(INET, nullable=False)
    device_type: Mapped[str] = mapped_column(String(32), nullable=False)  # router/switch/ap
    vendor: Mapped[Optional[str]] = mapped_column(String(64))
    model: Mapped[Optional[str]] = mapped_column(String(64))
    serial_number: Mapped[Optional[str]] = mapped_column(String(128))
    site_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sites.id", ondelete="SET NULL"))
    management_protocol: Mapped[Optional[str]] = mapped_column(String(16))  # ssh/snmp/api
    management_port: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    site: Mapped[Optional["Site"]] = relationship("Site", back_populates="devices")
    credentials: Mapped[Optional["DeviceCredential"]] = relationship(
        "DeviceCredential", back_populates="device", uselist=False, cascade="all, delete-orphan"
    )
    interfaces: Mapped[List["Interface"]] = relationship("Interface", back_populates="device", cascade="all, delete-orphan")
    configurations: Mapped[List["Configuration"]] = relationship("Configuration", back_populates="device", cascade="all, delete-orphan")

class DeviceCredential(Base, TimestampMixin):
    __tablename__ = "device_credentials"
    __table_args__ = (UniqueConstraint("device_id", name="uq_device_credentials_device_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"))
    username_enc: Mapped[bytes] = mapped_column(nullable=False)  # encrypted username
    password_enc: Mapped[bytes] = mapped_column(nullable=False)  # encrypted password
    secret_enc: Mapped[Optional[bytes]] = mapped_column(nullable=True)  # e.g., enable/privilege secret
    enc_salt: Mapped[bytes] = mapped_column(nullable=False)
    enc_iv: Mapped[bytes] = mapped_column(nullable=False)

    device: Mapped["Device"] = relationship("Device", back_populates="credentials")

class Interface(Base, TimestampMixin):
    __tablename__ = "interfaces"
    __table_args__ = (
        Index("ix_interfaces_device", "device_id"),
        Index("ix_interfaces_name", "name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[Optional[str]] = mapped_column(String(32))
    speed: Mapped[Optional[int]] = mapped_column(Integer)
    mac_address: Mapped[Optional[str]] = mapped_column(String(32))
    ip_address: Mapped[Optional[str]] = mapped_column(INET)
    rx_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    tx_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    errors: Mapped[Optional[int]] = mapped_column(Integer)
    last_updated: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    device: Mapped["Device"] = relationship("Device", back_populates="interfaces")
