from typing import Callable, Awaitable, Set

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse

from backend.app.core.config import settings

def _allowed_set() -> Set[str]:
    return {x.strip() for x in settings.API_ALLOWED_IPS.split(",") if x.strip()}

class IPAllowlistMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if not settings.ENABLE_IP_ALLOWLIST:
            return await call_next(request)
        allowed = _allowed_set()
        if not allowed:
            return PlainTextResponse("Access forbidden", status_code=403)
        client_ip = (request.client.host if request.client else "") or ""
        if client_ip not in allowed:
            return PlainTextResponse("Access forbidden", status_code=403)
        return await call_next(request)
