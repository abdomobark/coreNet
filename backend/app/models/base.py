from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func

class Base(AsyncAttrs, DeclarativeBase):
    # AsyncAttrs enables `await instance.awaitable_attrs.<relationship>` so that
    # relationship attributes can be loaded safely inside an async session
    # (e.g. on freshly-inserted objects, where lazy="selectin" does not fire and
    # a plain attribute access would raise sqlalchemy.exc.MissingGreenlet).
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
