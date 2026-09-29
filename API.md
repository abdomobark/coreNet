# API Specification (v1)

Base: `/api/v1`

## Auth
- POST /auth/login
  - Body: { username_or_email, password }
  - 200: { access_token, refresh_token, user: {...} }
  - 401: invalid credentials; increments failed count; audit
- POST /auth/logout
  - Auth: Bearer
  - 204
- POST /auth/refresh
  - Body: { refresh_token }
  - 200: { access_token }

## Users
- GET /users (Admin) – list, filter, paginate
- POST /users (Admin) – create
- GET /users/{id} (Admin/self)
- PUT /users/{id} (Admin/self partial)
- DELETE /users/{id} (Admin)
- GET /roles (Admin)
- POST /roles (Admin)
- GET /permissions (Admin)

## Devices
- GET /devices – filters: site, type, vendor, status
- POST /devices (Admin/Engineer)
- GET /devices/{id}
- PUT /devices/{id} (Admin/Engineer as permitted)
- DELETE /devices/{id} (Admin)
- POST /devices/{id}/test (Admin/Engineer) – connectivity check (async op)
- POST /devices/{id}/operations (Admin/Engineer) – command/backup/etc (async op)

## Configurations
- GET /configurations?device_id=
- POST /configurations (Admin/Engineer) – upload/save
- GET /configuration-versions/{id}
- POST /configurations/{id}/restore (Admin/Engineer)

## Monitoring
- GET /monitoring/metrics?device_id=&type=&from=&to=
- GET /alerts?status=&severity=
- POST /alerts/{id}/resolve (Admin/Engineer)

## Logs & Audit
- GET /logs?level=&from=&to=
- GET /audit?user=&action=&from=&to=
- GET /operations?status=&device_id=
- GET /operations/{id}

## Consistency
- Auth: Bearer JWT
- Errors: { error: { code, message } }
- Pagination: { items: [...], total, page, size }
