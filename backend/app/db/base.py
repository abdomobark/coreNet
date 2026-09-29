# Verify greenlet is available as early as possible.
try:
    import greenlet as _greenlet  # type: ignore
    _ = _greenlet.getcurrent
except Exception as exc:  # pragma: no cover
    raise RuntimeError(
        "Required dependency 'greenlet' is missing or not functional. "
        "Install it with: pip install --upgrade greenlet>=3.0.3"
    ) from exc

from backend.app.models.base import Base  # declarative base

# Import all models for Alembic's autogenerate to discover
# Keep imports local to avoid circulars on runtime import order
from backend.app.models import user as _user  # noqa
from backend.app.models import site as _site  # noqa
from backend.app.models import device as _device  # noqa
from backend.app.models import configuration as _config  # noqa
from backend.app.models import operation as _op  # noqa
from backend.app.models import monitoring as _mon  # noqa
from backend.app.models import logging as _log  # noqa

target_metadata = Base.metadata
