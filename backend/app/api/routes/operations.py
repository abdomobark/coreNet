from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_db
from backend.app.security.rbac import get_current_user, require_permissions
from backend.app.schemas.operation import OperationCreate, OperationRead
from backend.app.repositories.operation_repo import OperationRepository

router = APIRouter(prefix="/operations", tags=["operations"])

@router.post("", response_model=OperationRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions("devices:operate"))])
async def queue_operation(payload: OperationCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    repo = OperationRepository(db)
    op = await repo.create(user_id=user.id, device_id=payload.device_id, operation_type=payload.operation_type, command=payload.command)
    await db.commit()
    return OperationRead.model_validate(op)

@router.get("", response_model=List[OperationRead], dependencies=[Depends(require_permissions("devices:view"))])
async def list_operations(db: AsyncSession = Depends(get_db), skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500)):
    ops = await OperationRepository(db).list(skip=skip, limit=limit)
    return [OperationRead.model_validate(o) for o in ops]

@router.get("/{operation_id}", response_model=OperationRead, dependencies=[Depends(require_permissions("devices:view"))])
async def get_operation(operation_id: int, db: AsyncSession = Depends(get_db)):
    op = await OperationRepository(db).get(operation_id)
    if not op:
        raise HTTPException(status_code=404, detail="Operation not found")
    return OperationRead.model_validate(op)
