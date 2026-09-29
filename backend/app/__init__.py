# Ensure 'greenlet' is imported before any SQLAlchemy import occurs.
# SQLAlchemy detects greenlet availability at import time; if it's missing,
# async ORM operations will later raise MissingGreenlet even if greenlet
# is imported afterwards.
try:
    import greenlet as _greenlet  # type: ignore
    _ = _greenlet.getcurrent  # basic sanity check
except Exception as exc:  # pragma: no cover
    raise RuntimeError(
        "Required dependency 'greenlet' is missing or not functional. "
        "Install it with: pip install --upgrade greenlet>=3.0.3"
    ) from exc
