from typing import List, Optional
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin

class Site(Base, TimestampMixin):
    __tablename__ = "sites"
    __table_args__ = (UniqueConstraint("code", name="uq_sites_code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(255))

    devices: Mapped[List["Device"]] = relationship("Device", back_populates="site")
