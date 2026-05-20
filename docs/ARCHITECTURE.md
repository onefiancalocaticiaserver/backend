# Architecture

The target architecture separates conversational collection, business rules and
storage:

- Hermes collects data through WhatsApp.
- `one-mcp` exposes controlled semantic tools to Hermes.
- `one-api` owns validation, REST APIs, business rules and auditing.
- PostgreSQL 18 is the canonical database.
- Documents are stored outside the database, with metadata in Postgres.

Marco 1 implements only the backend foundation: API, DB healthcheck, migrations,
Docker and quality tooling.

