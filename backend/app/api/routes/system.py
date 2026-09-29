from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from backend.app.services.metrics import scrape

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    return PlainTextResponse(scrape(), media_type="text/plain; version=0.0.4")
