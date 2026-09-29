from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.device import Device

class DeviceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self, skip: int = 0, limit: int = 100) -> List[Device]:
        res = await self.db.execute(select(Device).offset(skip).limit(limit))
        return list(res.scalars().all())

    async def get(self, device_id: int) -> Optional[Device]:
        return await self.db.get(Device, device_id)

    async def create(self, data: dict) -> Device:
        device = Device(**data)
        self.db.add(device)
        await self.db.flush()
        return device

    async def update(self, device: Device, data: dict) -> Device:
        for k, v in data.items():
            if v is not None:
                setattr(device, k, v)
        await self.db.flush()
        return device

    async def delete(self, device: Device) -> None:
        await self.db.delete(device)
