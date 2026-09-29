from backend.app.models.logging import Notification
from backend.app.repositories.notification_repo import NotificationRepository

class NotificationService:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    async def send(self, n: Notification) -> Notification:
        # Simulate sending via channel; actual integrations can be added later
        # For now, just mark as sent
        return await self.repo.mark_sent(n)
