from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db
from backend.app.security.rbac import get_current_user, require_permissions
from backend.app.schemas.configuration import ConfigurationRead, ConfigurationVersionRead, CreateVersionRequest, SetCurrentRequest
from backend.app.repositories.configuration_repo import ConfigurationRepository
from backend.app.repositories.device_repo import DeviceRepository

router = APIRouter(prefix="/configs", tags=["configurations"])


async def _require_device(db: AsyncSession, device_id: int) -> None:
    # ensure_config_for_device() inserts Configuration(device_id=...) directly; a
    # non-existent device would raise a raw ForeignKey violation (HTTP 500) instead
    # of a clean 404, so validate the device up front.
    device = await DeviceRepository(db).get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")


@router.get("/devices/{device_id}", response_model=ConfigurationRead, dependencies=[Depends(require_permissions("configs:view"))])
async def get_or_create_config_for_device(device_id: int, db: AsyncSession = Depends(get_db)):
    repo = ConfigurationRepository(db)
    await _require_device(db, device_id)
    cfg = await repo.ensure_config_for_device(device_id)
    await db.commit()
    return ConfigurationRead.model_validate(cfg)

@router.get("/{config_id}/versions", response_model=List[ConfigurationVersionRead], dependencies=[Depends(require_permissions("configs:view"))])
async def list_versions(config_id: int, db: AsyncSession = Depends(get_db)):
    repo = ConfigurationRepository(db)
    cfg = await repo.get(config_id)
    if not cfg:
        raise HTTPException(status_code=404, detail="Configuration not found")
    versions = await repo.list_versions(cfg.id)
    return [ConfigurationVersionRead.model_validate(v) for v in versions]

@router.post("/devices/{device_id}/versions", response_model=ConfigurationVersionRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions("configs:manage"))])
async def create_version_for_device(device_id: int, payload: CreateVersionRequest, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    repo = ConfigurationRepository(db)
    await _require_device(db, device_id)
    cfg = await repo.ensure_config_for_device(device_id)
    cv = await repo.add_version(cfg, payload.config_text, created_by=payload.created_by or user.id)
    # default to set current on first version
    if cfg.current_version_id is None:
        await repo.set_current(cfg, cv.id)
    await db.commit()
    return ConfigurationVersionRead.model_validate(cv)

@router.post("/{config_id}/current", response_model=ConfigurationRead, dependencies=[Depends(require_permissions("configs:manage"))])
async def set_current_version(config_id: int, payload: SetCurrentRequest, db: AsyncSession = Depends(get_db)):
    repo = ConfigurationRepository(db)
    cfg = await repo.get(config_id)
    if not cfg:
        raise HTTPException(status_code=404, detail="Configuration not found")
    # ensure version belongs to config
    versions = await repo.list_versions(cfg.id)
    if payload.version_id not in {v.id for v in versions}:
        raise HTTPException(status_code=400, detail="Version does not belong to configuration")
    await repo.set_current(cfg, payload.version_id)
    await db.commit()
    return ConfigurationRead.model_validate(cfg)
