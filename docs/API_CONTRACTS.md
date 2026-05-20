# API Contracts

## Health

```http
GET /v1/health
```

Response:

```json
{"status": "ok", "service": "one-api"}
```

```http
GET /v1/health/db
```

Success response:

```json
{"status": "ok", "database": "connected"}
```

Failure response:

```json
{"detail": "database_unavailable"}
```

## Fase 1 - Planejado

APIs publicas para o frontend do site:

```http
POST /v1/public/agencies
POST /v1/public/brokers
```

APIs autenticadas para o admin unico inicial:

```http
POST   /v1/admin/auth/login
GET    /v1/admin/me
GET    /v1/admin/agencies
GET    /v1/admin/agencies/{agency_id}
PATCH  /v1/admin/agencies/{agency_id}
GET    /v1/admin/brokers
GET    /v1/admin/brokers/{broker_id}
PATCH  /v1/admin/brokers/{broker_id}
POST   /v1/admin/agencies/{agency_id}/brokers/{broker_id}
DELETE /v1/admin/agencies/{agency_id}/brokers/{broker_id}
```

O contrato final dos payloads sera definido na implementacao da Fase 1 a partir do roadmap.
