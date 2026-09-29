import time
from typing import Callable, Awaitable, Dict, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse

from backend.app.core.config import settings

# key -> (count, window_start)
_BUCKETS: Dict[str, Tuple[int, float]] = {}

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int):
        super().__init__(app)
        self.rpm = max(1, requests_per_minute)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if not settings.ENABLE_RATE_LIMIT:
            return await call_next(request)
        now = time.monotonic()
        window = 60.0
        key = self._key_for_request(request)
        count, start = _BUCKETS.get(key, (0, now))
        if now - start >= window:
            # new window
            count, start = 0, now
        count += 1
        _BUCKETS[key] = (count, start)
        if count > self.rpm:
            retry_after = int(max(1, window - (now - start)))
            return PlainTextResponse("Too Many Requests", status_code=429, headers={"Retry-After": str(retry_after)})
        return await call_next(request)

    def _key_for_request(self, request: Request) -> str:
        # Prefer authenticated user id if available in state, else client IP
        uid = getattr(request.state, "user_id", None)
        if uid:
            return f"user:{uid}"
        ip = (request.client.host if request.client else "unknown") or "unknown"
        return f"ip:{ip}"
