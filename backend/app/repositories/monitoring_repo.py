from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.monitoring import MonitoringMetric, Alert

class MonitoringRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_metrics(self, *, device_id: Optional[int] = None, metric_type: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[MonitoringMetric]:
        stmt = select(MonitoringMetric).order_by(MonitoringMetric.timestamp.desc())
        if device_id is not None:
            stmt = stmt.where(MonitoringMetric.device_id == device_id)
        if metric_type is not None:
            stmt = stmt.where(MonitoringMetric.metric_type == metric_type)
        stmt = stmt.offset(skip).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def list_alerts(self, *, status: Optional[str] = None, device_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Alert]:
        stmt = select(Alert).order_by(Alert.id.desc())
        if status is not None:
            stmt = stmt.where(Alert.status == status)
        if device_id is not None:
            stmt = stmt.where(Alert.device_id == device_id)
        stmt = stmt.offset(skip).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_alert(self, alert_id: int) -> Optional[Alert]:
        stmt = select(Alert).where(Alert.id == alert_id)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def resolve_alert(self, alert: Alert) -> Alert:
        alert.status = "resolved"
        alert.resolved_at = datetime.now(timezone.utc)
        await self.db.flush()
        return alert

    async def ingest_metric(self, *, device_id: int, metric_type: str, metric_value: Dict[str, Any], severity: Optional[str], timestamp: Optional[datetime]) -> MonitoringMetric:
        mm = MonitoringMetric(
            device_id=device_id,
            metric_type=metric_type,
            metric_value=metric_value,
            severity=severity,
            timestamp=timestamp or datetime.now(timezone.utc),
        )
        self.db.add(mm)
        await self.db.flush()
        # Auto-generate simple alerts for some thresholds
        await self._maybe_create_alert_for_metric(mm)
        return mm

    async def _maybe_create_alert_for_metric(self, metric: MonitoringMetric) -> Optional[Alert]:
        mt = metric.metric_type.lower()
        val = metric.metric_value
        if mt == "cpu" and isinstance(val, dict):
            usage = val.get("usage") or val.get("percent")
            try:
                usage_val = float(usage)
            except Exception:
                usage_val = None
            if usage_val is not None and usage_val >= 90.0:
                al = Alert(
                    device_id=metric.device_id,
                    alert_type="cpu_high",
                    severity="CRITICAL" if usage_val >= 95 else "WARNING",
                    message=f"CPU usage high: {usage_val:.1f}%",
                    status="open",
                )
                self.db.add(al)
                await self.db.flush()
                return al
        return None
