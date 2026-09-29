import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import FastAPI

from backend.app.core.config import settings
from backend.app.db.session import SessionLocal
from backend.app.repositories.operation_repo import OperationRepository
from backend.app.repositories.notification_repo import NotificationRepository
from backend.app.repositories.configuration_repo import ConfigurationRepository
from backend.app.services.notification_service import NotificationService
from backend.app.services.device_client import DeviceClient

async def operations_worker(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        try:
            async with SessionLocal() as db:
                repo = OperationRepository(db)
                # claim next queued
                op = await repo.claim_next_queued()
                if not op:
                    await asyncio.sleep(settings.OPERATIONS_POLL_INTERVAL_SEC)
                    continue

                # mark running
                await repo.mark_running(op)
                await db.commit()

                # Capture the id up front: a DB failure inside _execute() below can
                # poison the session, and after the rollback that clears it the ORM
                # object is expired.
                op_id = op.id

                # Execute based on operation_type
                client = DeviceClient(op.device_id)
                output = ""
                success = True
                error = None

                async def _execute() -> str:
                    if op.operation_type == "command":
                        return await client.run_command(op.command)
                    elif op.operation_type == "backup":
                        return await client.backup_config()
                    elif op.operation_type == "restore":
                        if not op.command:
                            raise ValueError("Missing config_text in command")
                        res = await client.restore_config(op.command)
                        # optionally add a configuration version
                        cfg_repo = ConfigurationRepository(db)
                        cfg = await cfg_repo.ensure_config_for_device(op.device_id)  # type: ignore[arg-type]
                        await cfg_repo.add_version(cfg, op.command, created_by=op.user_id)  # type: ignore[arg-type]
                        return res
                    else:
                        raise ValueError(f"Unknown operation_type '{op.operation_type}'")

                try:
                    output = await asyncio.wait_for(_execute(), timeout=settings.OPERATION_TIMEOUT_SEC)
                except asyncio.TimeoutError:
                    success = False
                    error = f"Operation timed out after {settings.OPERATION_TIMEOUT_SEC}s"
                except Exception as ex:
                    success = False
                    error = str(ex)

                # Decide on retry or finalize
                if success:
                    await repo.set_result(op, success=True, output=output, error=None)
                else:
                    # _execute() may have failed on a DB error (e.g. the restore
                    # branch), which poisons the session so that any further query
                    # raises PendingRollbackError. Roll back to clear it and re-load
                    # the operation before recording the failure, otherwise the
                    # bookkeeping below fails and the op is stuck in "running" forever.
                    await db.rollback()
                    op = await repo.get(op_id)
                    if op is None:
                        continue
                    failed = await repo.count_failed_attempts(op_id)
                    attempt_number = failed + 1
                    if attempt_number >= settings.MAX_OPERATION_RETRIES:
                        # Final failure -> dead-letter
                        await repo.set_result(op, success=False, output=output or "", error=error)
                    else:
                        # Record attempt and re-queue with backoff
                        await repo.add_attempt_result(op, success=False, output=output or "", error=error)
                        await repo.mark_queued(op)
                        backoff = settings.OPERATION_RETRY_BACKOFF_BASE_SEC * (2 ** (attempt_number - 1))
                        await db.commit()
                        await asyncio.sleep(backoff)
                        continue  # next loop will pick up again

                await db.commit()
        except Exception:
            # Swallow worker exceptions; brief backoff
            await asyncio.sleep(1)

        await asyncio.sleep(0)  # yield

async def notifications_worker(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        try:
            async with SessionLocal() as db:
                nrepo = NotificationRepository(db)
                ns = NotificationService(nrepo)
                pending = await nrepo.list_pending(limit=50)
                if not pending:
                    await asyncio.sleep(settings.NOTIFICATIONS_POLL_INTERVAL_SEC)
                    continue
                for n in pending:
                    try:
                        await ns.send(n)
                    except Exception as ex:
                        await nrepo.mark_error(n, str(ex))
                await db.commit()
        except Exception:
            await asyncio.sleep(1)

        await asyncio.sleep(0)

async def start_workers(app: FastAPI) -> None:
    app.state.stop_event = asyncio.Event()
    app.state.worker_tasks: List[asyncio.Task] = []
    app.state.worker_tasks.append(asyncio.create_task(operations_worker(app.state.stop_event)))
    app.state.worker_tasks.append(asyncio.create_task(notifications_worker(app.state.stop_event)))

async def stop_workers(app: FastAPI) -> None:
    stop_event = getattr(app.state, "stop_event", None)
    tasks: List[asyncio.Task] = getattr(app.state, "worker_tasks", [])
    if stop_event:
        stop_event.set()
    for t in tasks:
        t.cancel()
    if tasks:
        # gather(return_exceptions=True) collects the CancelledError raised by each
        # cancelled task instead of letting it propagate out of the shutdown handler.
        # Note: asyncio.CancelledError is a BaseException (not Exception) on 3.8+,
        # so a plain `except Exception` would NOT swallow it.
        await asyncio.gather(*tasks, return_exceptions=True)
