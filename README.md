# One Fianca Backend

Backend for One Fianca Locaticia.

## Current Milestone

Fase 1 implements the partner registration foundation:

- FastAPI app with `/v1/health` and `/v1/health/db`;
- SQLAlchemy/PostgreSQL connection;
- Alembic migrations;
- Docker and Docker Compose base;
- public CRUD for `imobiliarias` and `corretores` protected by `X-Cadastro-Token`;
- admin login with JWT and internal CRUD;
- MCP tools for Hermes with bearer token;
- audit events for admin/public/MCP writes;
- sanitized environment examples;
- tests, lint and type-checking setup.

## Local Setup

```bash
uv sync
cp .env.example .env
uv run uvicorn app.main:app --reload
```

With Docker:

```bash
cp .env.example .env
docker compose up --build
```

## Quality Gates

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy app
uv run alembic upgrade head
uv run python scripts/bootstrap_admin.py
```

## Security Notes

- Never commit real `.env` files or `vps.env`.
- Keep the GitHub repository private.
- Use SSH keys for VPS access.
- Use a dedicated app DB role for runtime; do not run the app as the Postgres admin user.
