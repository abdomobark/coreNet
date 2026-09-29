from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db
from backend.app.security.rbac import require_permissions
from backend.app.schemas.site import SiteCreate, SiteUpdate, SiteRead
from backend.app.repositories.site_repo import SiteRepository

router = APIRouter(prefix="/sites", tags=["sites"])

@router.get("", response_model=List[SiteRead], dependencies=[Depends(require_permissions("sites:view"))])
async def list_sites(db: AsyncSession = Depends(get_db), skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500)):
    return await SiteRepository(db).list(skip=skip, limit=limit)

@router.post("", response_model=SiteRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions("sites:manage"))])
async def create_site(payload: SiteCreate, db: AsyncSession = Depends(get_db)):
    repo = SiteRepository(db)
    site = await repo.create(payload.model_dump())
    await db.commit()
    return site

@router.get("/{site_id}", response_model=SiteRead, dependencies=[Depends(require_permissions("sites:view"))])
async def get_site(site_id: int, db: AsyncSession = Depends(get_db)):
    site = await SiteRepository(db).get(site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site

@router.put("/{site_id}", response_model=SiteRead, dependencies=[Depends(require_permissions("sites:manage"))])
async def update_site(site_id: int, payload: SiteUpdate, db: AsyncSession = Depends(get_db)):
    repo = SiteRepository(db)
    site = await repo.get(site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    site = await repo.update(site, payload.model_dump(exclude_unset=True))
    await db.commit()
    return site

@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permissions("sites:manage"))])
async def delete_site(site_id: int, db: AsyncSession = Depends(get_db)):
    repo = SiteRepository(db)
    site = await repo.get(site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    await repo.delete(site)
    await db.commit()
    return None
