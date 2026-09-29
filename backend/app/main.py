from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.logging import setup_logging
from backend.app.middleware.request_id import RequestIDMiddleware
from backend.app.middleware.ip_allowlist import IPAllowlistMiddleware
from backend.app.middleware.rate_limit import RateLimitMiddleware
from backend.app.middleware.request_size_limit import RequestSizeLimitMiddleware

from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.users import router as users_router
from backend.app.api.routes.users_admin import router as users_admin_router
from backend.app.api.routes.sites import router as sites_router
from backend.app.api.routes.devices import router as devices_router
from backend.app.api.routes.configurations import router as configs_router
from backend.app.api.routes.operations import router as operations_router
from backend.app.api.routes.monitoring import router as monitoring_router
from backend.app.api.routes.alerts import router as alerts_router
from backend.app.api.routes.logs import router as logs_router
from backend.app.api.routes.notifications import router as notifications_router
from backend.app.api.routes.rbac import router as rbac_router
from backend.app.api.routes.system import router as system_router

from backend.app.db.session import engine, SessionLocal
from backend.app.db.base import target_metadata
from backend.app.services.bootstrap import bootstrap
from backend.app.services.workers import start_workers, stop_workers
from backend.app.security.authz import get_current_user

# Configure logging early
setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# CORS
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
# Never combine a wildcard origin with allow_credentials=True: Starlette then
# reflects the caller's Origin and returns Access-Control-Allow-Credentials: true
# for ANY site. If no origins are configured, fall back to a safe localhost dev
# default in development and to "no cross-origin access" otherwise.
if not origins and settings.APP_ENV == "development":
    origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cross-cutting middlewares
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)
if settings.ENABLE_IP_ALLOWLIST:
    app.add_middleware(IPAllowlistMiddleware)
if settings.ENABLE_RATE_LIMIT:
    app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)

# Auto-create schema and bootstrap on startup (PostgreSQL)
@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: target_metadata.create_all(bind=sync_conn))
    # Bootstrap roles/permissions and optional admin
    async with SessionLocal() as db:
        await bootstrap(db)
    # Background workers
    if settings.BACKGROUND_JOBS_ENABLED:
        await start_workers(app)

@app.on_event("shutdown")
async def on_shutdown() -> None:
    if settings.BACKGROUND_JOBS_ENABLED:
        await stop_workers(app)

# Routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(users_admin_router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(sites_router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(devices_router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(configs_router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(operations_router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(monitoring_router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(alerts_router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(logs_router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(notifications_router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(rbac_router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(system_router, prefix="/api/v1", dependencies=[Depends(get_current_user)])

@app.get("/api")
async def root():
    return {"name": settings.APP_NAME, "status": "ok"}
