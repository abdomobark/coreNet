from typing import Optional, Set
from fastapi import Header, HTTPException, status

from backend.app.core.config import settings

def _normalized_keys() -> Set[str]:
    if not settings.API_KEYS:
        return set()
    return {k.strip() for k in settings.API_KEYS.split(",") if k.strip()}

async def require_agent_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> None:
    keys = _normalized_keys()
    if not keys:
        # Disabled: no keys configured
        return
    if not x_api_key or x_api_key not in keys:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
