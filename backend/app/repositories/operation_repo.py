from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.operation import Operation, OperationResult

class OperationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, *, user_id: Optional[int], device_id: Optional[int], operation_type: str, command: Optional[str]) -> Operation:
        op = Operation(user_id=user_id, device_id=device_id, operation_type=operation_type, command=command, status="queued")
        self.db.add(op)
        await self.db.flush()
        return op

    async def list(self, skip: int = 0, limit: int = 100) -> List[Operation]:
        res = await self.db.execute(select(Operation).order_by(Operation.id.desc()).offset(skip).limit(limit))
        return list(res.scalars().all())

    async def get(self, operation_id: int) -> Optional[Operation]:
        return await self.db.get(Operation, operation_id)

    async def claim_next_queued(self) -> Optional[Operation]:
        stmt = (
            select(Operation)
            .where(Operation.status == "queued")
            .order_by(Operation.id.asc())
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        res = await self.db.execute(stmt)
        op = res.scalars().first()
        return op

    async def mark_running(self, operation: Operation) -> Operation:
        operation.status = "running"
        operation.started_at = datetime.now(timezone.utc)
        await self.db.flush()
        return operation

    async def mark_queued(self, operation: Operation) -> Operation:
        operation.status = "queued"
        await self.db.flush()
        return operation

    async def add_attempt_result(self, operation: Operation, success: bool, output: Optional[str], error: Optional[str]) -> OperationResult:
        res = OperationResult(operation_id=operation.id, success=success, output=output, error=error)
        self.db.add(res)
        await self.db.flush()
        return res

    async def count_failed_attempts(self, operation_id: int) -> int:
        stmt = select(func.count()).select_from(OperationResult).where(
            OperationResult.operation_id == operation_id, OperationResult.success == False  # noqa: E712
        )
        res = await self.db.execute(stmt)
        return int(res.scalar_one() or 0)

    async def set_result(self, operation: Operation, success: bool, output: Optional[str], error: Optional[str]) -> OperationResult:
        res = OperationResult(operation_id=operation.id, success=success, output=output, error=error)
        self.db.add(res)
        operation.status = "finished" if success else "failed"
        operation.finished_at = datetime.now(timezone.utc)
        await self.db.flush()
        return res
