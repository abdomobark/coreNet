from typing import Callable, Awaitable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse

from backend.app.core.config import settings

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if request.method not in SAFE_METHODS:
            cl = request.headers.get("content-length")
            if cl and cl.isdigit():
                if int(cl) > settings.MAX_REQUEST_BODY_BYTES:
                    return PlainTextResponse("Request Entity Too Large", status_code=413)
        return await call_next(request)
