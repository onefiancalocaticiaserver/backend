# AGENTS.md - One Fianca Backend

## Project Context

This repository implements the backend for One Fianca Locaticia, a Brazilian rental
guarantee operation. The system handles personal, financial, banking, document,
contract and commission-related data. Treat all code as security-sensitive and
LGPD-relevant.

## Architecture

- Python 3.12
- FastAPI for REST APIs
- PostgreSQL 18 as canonical database
- SQLAlchemy 2.x and Alembic for persistence and migrations
- Pydantic v2 for schemas and settings
- Local filesystem storage for documents in the MVP
- Custom MCP service for Hermes integration in a later phase

## Rules

- Do not hardcode secrets.
- Do not commit `.env`, `*.env`, `vps.env`, dumps, logs, keys or real credentials.
- Never expose a generic SQL execution endpoint or MCP tool.
- Keep business rules in services, not route handlers.
- All sensitive writes must be auditable once the domain layer is implemented.
- Store document metadata in Postgres, not binary blobs.
- Use migrations for schema changes.

## Commands

- Install/sync: `uv sync`
- Run API locally: `uv run uvicorn app.main:app --reload`
- Run tests: `uv run pytest`
- Lint: `uv run ruff check .`
- Format check: `uv run ruff format --check .`
- Type check: `uv run mypy app`
- Migrate: `uv run alembic upgrade head`

