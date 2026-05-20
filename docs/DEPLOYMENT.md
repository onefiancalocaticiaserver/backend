# Deployment

## Current State

Fase 1 tem deploy scriptado por SSH e Docker Compose. Antes de producao real,
ainda e necessario preencher `.env` na VPS com segredos reais, validar chave SSH,
CORS do frontend e TLS/reverse proxy.

## Temporary Access

During homologation, API access may use direct VPS IP and port:

```text
http://<VPS_IP>:8000
```

For real operation with personal data and documents, use HTTPS with a dedicated
domain/subdomain before opening regular access.

## Production Services

- `postgresql-1ua2`
- `one-api`
- `one-mcp`

`one-mcp` and Postgres must stay internal. Do not expose either publicly.

## Local Deploy Command

Crie um `ops.env` fora do Git a partir de `ops.env.example` e rode:

```bash
OPS_ENV=/caminho/seguro/ops.env scripts/deploy_vps.sh
```

Antes do deploy, valide SSH e Docker:

```bash
OPS_ENV=/caminho/seguro/ops.env scripts/check_vps_access.sh
```

Se a chave ainda nao estiver instalada na VPS, use uma senha temporaria em
runtime:

```bash
VPS_SSH_PASSWORD='senha-temporaria' OPS_ENV=/caminho/seguro/ops.env scripts/install_vps_ssh_key.sh
```

O script:

- cria diretorios em `/opt/one-fianca-backend` e `/srv/one-fianca`;
- clona ou atualiza o repo;
- exige `.env` real na VPS;
- sobe `docker-compose.prod.yml`;
- executa `alembic upgrade head`;
- executa `scripts/bootstrap_admin.py`;
- valida `/v1/health` e `/v1/health/db`.

## Bootstrap Admin

O admin inicial e criado/atualizado por:

```bash
python scripts/bootstrap_admin.py
```

Variaveis usadas:

- `BOOTSTRAP_ADMIN_EMAIL`;
- `BOOTSTRAP_ADMIN_PASSWORD`;
- `BOOTSTRAP_ADMIN_FULL_NAME`.
