from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models.configuration import Configuration, ConfigurationVersion

class ConfigurationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_device(self, device_id: int) -> Optional[Configuration]:
        stmt = (
            select(Configuration)
            .options(
                selectinload(Configuration.current_version),
                selectinload(Configuration.versions),
            )
            .where(Configuration.device_id == device_id)
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get(self, config_id: int) -> Optional[Configuration]:
        stmt = (
            select(Configuration)
            .options(
                selectinload(Configuration.current_version),
                selectinload(Configuration.versions),
            )
            .where(Configuration.id == config_id)
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def ensure_config_for_device(self, device_id: int) -> Configuration:
        cfg = await self.get_by_device(device_id)
        if cfg:
            return cfg
        cfg = Configuration(device_id=device_id)
        self.db.add(cfg)
        await self.db.flush()
        await self.db.refresh(cfg)
        return cfg

    async def list_versions(self, configuration_id: int) -> List[ConfigurationVersion]:
        stmt = select(ConfigurationVersion).where(ConfigurationVersion.configuration_id == configuration_id).order_by(ConfigurationVersion.version.desc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def next_version_number(self, configuration_id: int) -> int:
        stmt = select(func.coalesce(func.max(ConfigurationVersion.version), 0)).where(ConfigurationVersion.configuration_id == configuration_id)
        res = await self.db.execute(stmt)
        return (res.scalar_one() or 0) + 1

    async def add_version(self, configuration: Configuration, config_text: str, created_by: Optional[int]) -> ConfigurationVersion:
        ver = await self.next_version_number(configuration.id)
        cv = ConfigurationVersion(configuration_id=configuration.id, version=ver, config_text=config_text, created_by=created_by)
        self.db.add(cv)
        await self.db.flush()
        await self.db.refresh(cv)
        return cv

    async def set_current(self, configuration: Configuration, version_id: int) -> Configuration:
        configuration.current_version_id = version_id
        await self.db.flush()
        await self.db.refresh(configuration)
        return configuration
