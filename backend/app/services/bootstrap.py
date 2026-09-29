from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.repositories.rbac_repo import RBACRepository
from backend.app.repositories.user_repo import UserRepository

PERMISSIONS = {
    # Users
    "users:view": "View users",
    "users:manage": "Create/Edit/Delete users",
    # Sites
    "sites:view": "View sites",
    "sites:manage": "Create/Edit/Delete sites",
    # Devices
    "devices:view": "View devices",
    "devices:manage": "Add/Edit/Delete devices",
    "devices:operate": "Execute commands and operations",
    # Configurations
    "configs:view": "View configurations",
    "configs:manage": "Backup/Restore/Change configurations",
    # Monitoring & Alerts
    "monitoring:view": "View monitoring dashboards and metrics",
    "monitoring:ingest": "Submit metrics from agents",
    "alerts:view": "View alerts",
    "alerts:manage": "Resolve/manage alerts",
    # Notifications
    "notifications:view": "View notifications",
    "notifications:manage": "Create/Send notifications",
    # Logs & Audit
    "logs:view": "View logs",
    "audit:view": "View audit trail",
    # Settings
    "settings:manage": "Manage system settings",
}

ROLE_PERMISSIONS = {
    "Admin": list(PERMISSIONS.keys()),
    "Engineer": [
        "sites:view", "sites:manage",
        "devices:view", "devices:manage", "devices:operate",
        "configs:view", "configs:manage",
        "monitoring:view", "monitoring:ingest",
        "alerts:view", "alerts:manage",
        "notifications:view", "notifications:manage",
        "logs:view", "audit:view"
    ],
    "Viewer": [
        "sites:view",
        "devices:view", "configs:view", "monitoring:view", "alerts:view", "logs:view", "notifications:view"
    ],
    "Auditor": [
        "audit:view", "logs:view", "configs:view", "devices:view", "sites:view"
    ],
}

async def bootstrap(db: AsyncSession) -> None:
    rbac = RBACRepository(db)
    # Ensure permissions
    name_to_perm = {}
    for name, desc in PERMISSIONS.items():
        perm = await rbac.get_or_create_permission(name, desc)
        name_to_perm[name] = perm

    # Ensure roles and assign permissions
    role_objs = {}
    for role_name, perm_names in ROLE_PERMISSIONS.items():
        role = await rbac.get_or_create_role(role_name)
        role_objs[role_name] = role
        for pn in perm_names:
            await rbac.ensure_role_permission(role, name_to_perm[pn])

    # Seed admin user if provided
    if settings.ADMIN_USERNAME and settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
        users = UserRepository(db)
        existing = await users.get_by_username_or_email(settings.ADMIN_USERNAME) or await users.get_by_username_or_email(settings.ADMIN_EMAIL)
        if not existing:
            admin_user = await users.create(settings.ADMIN_USERNAME, settings.ADMIN_EMAIL, settings.ADMIN_PASSWORD, is_active=True)
            # assign Admin role
            await rbac.ensure_user_role(admin_user, role_objs["Admin"])
        else:
            # Ensure Admin role exists on the existing user
            await rbac.ensure_user_role(existing, role_objs["Admin"])
    await db.commit()
