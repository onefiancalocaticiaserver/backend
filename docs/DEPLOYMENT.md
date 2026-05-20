# Deployment

## Current State

The first milestone is local/backend scaffold only. Production deployment should
wait until:

- the GitHub repository is private;
- VPS credentials are rotated;
- SSH key access is validated;
- Postgres 18 is confirmed or recreated;
- runtime DB roles are created.

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

