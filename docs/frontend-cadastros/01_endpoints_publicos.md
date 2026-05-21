# Endpoints Publicos

Base path:

```text
/v1/publico
```

## Criar Imobiliaria

```http
POST /v1/publico/imobiliarias
Content-Type: application/json
```

Autenticacao: nenhuma.

Resposta de sucesso:

```http
201 Created
```

```json
{
  "id": "1c01f85d-1ac4-4e90-8b3c-cd9c7e4a5ef1",
  "token_cadastro": "token-seguro-retornado-uma-unica-vez"
}
```

## Consultar Imobiliaria

```http
GET /v1/publico/imobiliarias/{imobiliaria_id}
X-Cadastro-Token: <token_cadastro>
```

Resposta de sucesso:

```http
200 OK
```

Retorna o schema completo de resposta de imobiliaria.

## Atualizar Imobiliaria

```http
PATCH /v1/publico/imobiliarias/{imobiliaria_id}
Content-Type: application/json
X-Cadastro-Token: <token_cadastro>
```

Enviar somente os campos que mudaram. Campos omitidos permanecem iguais.

Resposta de sucesso:

```http
200 OK
```

Retorna o schema completo de resposta de imobiliaria.

## Criar Corretor

```http
POST /v1/publico/corretores
Content-Type: application/json
```

Autenticacao: nenhuma.

Resposta de sucesso:

```http
201 Created
```

```json
{
  "id": "2d5c8b43-2738-4dd8-8e44-652d9efc1c00",
  "token_cadastro": "token-seguro-retornado-uma-unica-vez"
}
```

## Consultar Corretor

```http
GET /v1/publico/corretores/{corretor_id}
X-Cadastro-Token: <token_cadastro>
```

Resposta de sucesso:

```http
200 OK
```

Retorna o schema completo de resposta de corretor.

## Atualizar Corretor

```http
PATCH /v1/publico/corretores/{corretor_id}
Content-Type: application/json
X-Cadastro-Token: <token_cadastro>
```

Enviar somente os campos que mudaram. Campos omitidos permanecem iguais.

Resposta de sucesso:

```http
200 OK
```

Retorna o schema completo de resposta de corretor.

## Status Codes Esperados

```text
200 OK                  consulta/atualizacao concluida
201 Created             cadastro criado
403 Forbidden           X-Cadastro-Token invalido
404 Not Found           cadastro nao encontrado ou removido
409 Conflict            CNPJ/CPF ou token duplicado
422 Unprocessable Entity payload invalido ou regra de negocio invalida
```

Sem o header `X-Cadastro-Token`, FastAPI retorna `422` por header obrigatorio ausente.

## Fluxo Recomendado No Frontend

Para primeiro cadastro:

1. Validar campos obrigatorios no formulario.
2. Enviar `POST`.
3. Persistir localmente ou no fluxo do usuario:
   - `id`;
   - `token_cadastro`;
   - tipo de cadastro: `imobiliaria` ou `corretor`.
4. Exibir mensagem de sucesso.

Para edicao posterior:

1. Recuperar `id` e `token_cadastro`.
2. Enviar `GET` para carregar o cadastro.
3. Enviar `PATCH` apenas com campos alterados.

## Headers

Criacao:

```http
Content-Type: application/json
```

Consulta/edicao:

```http
Content-Type: application/json
X-Cadastro-Token: <token_cadastro>
```

