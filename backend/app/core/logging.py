import logging
from backend.app.core.config import settings
import json
import logging
import sys
import contextvars
from datetime import datetime, timezone

from backend.app.core.config import settings

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")

class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            record.request_id = request_id_var.get()
        except Exception:
            record.request_id = "-"
        return True

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.now(timezone.utc).isoformat()
        data = {
            "ts": ts,
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        if record.exc_info:
            data["exc"] = self.formatException(record.exc_info)
        return json.dumps(data, ensure_ascii=False)

def setup_logging() -> None:
    root = logging.getLogger()
    # Clear existing handlers if any (idempotent setup)
    for h in list(root.handlers):
        root.removeHandler(h)
    root.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())
    if settings.LOG_JSON:
        handler.setFormatter(JsonFormatter())
    else:
        fmt = "%(asctime)s %(levelname)s [%(name)s] [rid=%(request_id)s] %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
    root.addHandler(handler)
