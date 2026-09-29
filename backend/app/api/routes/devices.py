from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db
from backend.app.security.rbac import require_permissions
from backend.app.schemas.device import DeviceCreate, DeviceUpdate, DeviceRead
from backend.app.repositories.device_repo import DeviceRepository

router = APIRouter(prefix="/devices", tags=["devices"])

@router.get("", response_model=List[DeviceRead], dependencies=[Depends(require_permissions("devices:view"))])
async def list_devices(db: AsyncSession = Depends(get_db), skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500)):
    return await DeviceRepository(db).list(skip=skip, limit=limit)

@router.post("", response_model=DeviceRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions("devices:manage"))])
async def create_device(payload: DeviceCreate, db: AsyncSession = Depends(get_db)):
    repo = DeviceRepository(db)
    device = await repo.create(payload.model_dump())
    await db.commit()
    return device

@router.get("/{device_id}", response_model=DeviceRead, dependencies=[Depends(require_permissions("devices:view"))])
async def get_device(device_id: int, db: AsyncSession = Depends(get_db)):
    device = await DeviceRepository(db).get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.put("/{device_id}", response_model=DeviceRead, dependencies=[Depends(require_permissions("devices:manage"))])
async def update_device(device_id: int, payload: DeviceUpdate, db: AsyncSession = Depends(get_db)):
    repo = DeviceRepository(db)
    device = await repo.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device = await repo.update(device, payload.model_dump(exclude_unset=True))
    await db.commit()
    return device

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permissions("devices:manage"))])
async def delete_device(device_id: int, db: AsyncSession = Depends(get_db)):
    repo = DeviceRepository(db)
    device = await repo.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    await repo.delete(device)
    await db.commit()
    return None
