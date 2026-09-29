# Security Model

## Authentication
- Password hashing: bcrypt via passlib.
- Tokens: JWT (access/refresh), short-lived access tokens.
- Failed login tracking and account lockout after thresholds (configurable).
- Login/audit logging for auth events.

## Authorization (RBAC)
- Roles ↔ Permissions: many-to-many
- Route dependencies check permissions centrally.
- Service-layer authorization guards enforce least privilege.

## Secrets
- All secrets via env (.env for dev); SECRET_KEY, DB URL, encryption keys.
- Device credentials encrypted-at-rest (salt + IV + strong cipher, implemented in security module).

## Transport
- HTTPS in production (reverse proxy/ingress).
- CORS restricted to configured origins.

## Data Protection
- Never return device credentials in APIs.
- Redact logs; avoid sensitive data in exceptions.
- Parameterized queries via ORM.

## App Hardening
- Rate limiting via reverse proxy (NGINX/Traefik).
- CSRF: not needed for token auth; add if cookies used.
- Input validation using Pydantic schemas.
- Secure headers; audit significant changes.
