from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.site import Site

class SiteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self, skip: int = 0, limit: int = 100) -> List[Site]:
        res = await self.db.execute(select(Site).offset(skip).limit(limit))
        return list(res.scalars().all())

    async def get(self, site_id: int) -> Optional[Site]:
        return await self.db.get(Site, site_id)

    async def create(self, data: dict) -> Site:
        site = Site(**data)
        self.db.add(site)
        await self.db.flush()
        return site

    async def update(self, site: Site, data: dict) -> Site:
        for k, v in data.items():
            if v is not None:
                setattr(site, k, v)
        await self.db.flush()
        return site

    async def delete(self, site: Site) -> None:
        await self.db.delete(site)
