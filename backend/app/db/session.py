from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from backend.app.core.config import settings

# Ensure greenlet is available for SQLAlchemy async ORM bridge.
# Without greenlet, SQLAlchemy will raise MissingGreenlet during startup/ORM use.
try:
    import greenlet  # type: ignore
    _ = greenlet.getcurrent  # basic sanity check that greenlet is functional
except Exception as exc:  # pragma: no cover
    raise RuntimeError(
        "The 'greenlet' package is required for SQLAlchemy's async ORM. "
        "Please install it, e.g.: pip install --upgrade greenlet>=3.0.3"
    ) from exc

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

class Base(DeclarativeBase):
    pass
