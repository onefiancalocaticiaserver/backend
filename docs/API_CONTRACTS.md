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

## Fase 1 - Cadastros de parceiros

Documento detalhado para integracao do frontend:

```text
docs/frontend-cadastros/README.md
```

APIs publicas para o frontend do site:

```http
POST   /v1/publico/imobiliarias
GET    /v1/publico/imobiliarias/{imobiliaria_id}
PATCH  /v1/publico/imobiliarias/{imobiliaria_id}
POST   /v1/publico/corretores
GET    /v1/publico/corretores/{corretor_id}
PATCH  /v1/publico/corretores/{corretor_id}
```

APIs autenticadas para o admin unico inicial:

```http
POST   /v1/admin/autenticacao/login
GET    /v1/admin/eu
GET    /v1/admin/imobiliarias
GET    /v1/admin/imobiliarias/{imobiliaria_id}
PATCH  /v1/admin/imobiliarias/{imobiliaria_id}
DELETE /v1/admin/imobiliarias/{imobiliaria_id}
GET    /v1/admin/corretores
GET    /v1/admin/corretores/{corretor_id}
PATCH  /v1/admin/corretores/{corretor_id}
DELETE /v1/admin/corretores/{corretor_id}
POST   /v1/admin/imobiliarias/{imobiliaria_id}/corretores/{corretor_id}
DELETE /v1/admin/imobiliarias/{imobiliaria_id}/corretores/{corretor_id}
```

Observacoes:

- Todo contrato publico da Fase 1 usa nomes em portugues.
- `POST` publico retorna `id` e `token_cadastro` uma unica vez.
- `GET/PATCH` publicos exigem `X-Cadastro-Token`.
- `DELETE` publico nao entra na recomendacao inicial; remocao deve ser admin ou solicitacao autenticada.
- `DELETE` admin e MCP devem ser soft delete/cancelamento.
- `origem` representa a fonte do cadastro: `site`, `chatbot`, `one`, `app_interno`, `api`, `importacao` ou `outro`.

## MCP Hermes

Endpoint HTTP MCP:

```http
POST /mcp
Authorization: Bearer <ONE_MCP_AUTH_TOKEN>
```

Tools implementadas:

```text
criar_imobiliaria
obter_imobiliaria
atualizar_imobiliaria
remover_imobiliaria
criar_corretor
obter_corretor
atualizar_corretor
remover_corretor
vincular_corretor_imobiliaria
adicionar_observacao_parceiro
```

Regras:

- `remover_*` executa soft delete;
- chamadas MCP registram auditoria com `ator_tipo=hermes`;
- `criar_*` usa `origem=chatbot` quando a origem nao for informada.
