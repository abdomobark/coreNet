# System Architecture

A modular monolith with clean separation of API, services, repositories, device communication layer, and background workers.

## Components

- Frontend: Modern SPA (to be implemented), role-aware navigation.
- API: FastAPI, organized as versioned routers with schemas, services, repositories.
- DB: PostgreSQL, SQLAlchemy 2.x (async); schema auto-created at startup from metadata.
- Security: JWT auth (access/refresh), robust RBAC (roles ↔ permissions).
- Device Communication: Isolated service layer handling SSH/SNMP/HTTPS/API with timeouts/retries.
- Background Tasks: In-process scheduler/executor (initial) for monitoring, backups, batch operations; resilient patterns for retry and idempotency.
- Logging/Audit: Centralized app logs + immutable audit trails.
- Alerts/Notifications: Threshold-based alerting with severity and delivery hooks.

## Communication Flow

- Frontend → FastAPI (REST, JWT)
- FastAPI:
  - Routes → Schemas → Services → Repositories (DB)
  - Services → Device Manager (SSH/SNMP/API) for device operations
  - Services → Background Worker for long operations or periodic monitoring
- DB: Persistent storage for configs, metrics, alerts, logs, audit.
- Notifications: Email/Slack/Webhook (pluggable, future phases)

## Mermaid Architecture Diagram
