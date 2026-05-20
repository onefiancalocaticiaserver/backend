# One Fianca Backend

Backend scaffold for One Fianca Locaticia.

## Current Milestone

Marco 1 creates the secure project foundation:

- FastAPI app with `/v1/health` and `/v1/health/db`;
- SQLAlchemy/PostgreSQL connection;
- Alembic migrations;
- Docker and Docker Compose base;
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
```

## Security Notes

- Never commit real `.env` files or `vps.env`.
- Keep the GitHub repository private.
- Use SSH keys for VPS access.
- Use a dedicated app DB role for runtime; do not run the app as the Postgres admin user.

