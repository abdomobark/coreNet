# Network Management System (NMS)
# CoreNet Manager

## Setup

Install dependencies:

    pip install -r requirements.txt

If you previously saw `sqlalchemy.exc.MissingGreenlet`, ensure `greenlet` is installed (it is included in requirements.txt). Recreate/upgrade your virtualenv if needed so the compiled wheel matches your Python version and platform.

Run the app:

    uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
A modular, production-oriented web application for managing and monitoring network devices (Routers, Switches, Wireless APs).

Status:
- Phase 1: Project foundation (DONE)
- Phase 2: PostgreSQL + SQLAlchemy + Alembic (DONE: models and initial migration)
- Phase 3+: Authentication/RBAC, Users, Devices, Communication, Monitoring, Alerts, Logging/Audit, Frontend (planned)

## Tech Stack

- Backend: FastAPI, Pydantic, SQLAlchemy 2.x (async), Alembic
- DB: PostgreSQL (asyncpg)
- Auth: JWT (planned), RBAC with roles/permissions (planned)
- Workers: In-process background scheduler (initial), extensible to external queue if needed (future)

## Quickstart

1) Create environment file
- Copy `.env.example` to `.env` and set values (especially DATABASE_URL and SECRET_KEY).

2) Create and activate Python environment
