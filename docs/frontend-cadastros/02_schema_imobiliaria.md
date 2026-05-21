# Schema Publico - Imobiliaria

## Campos Obrigatorios No POST

| Campo | Tipo | Regra |
| --- | --- | --- |
| `razao_social` | string | 2 a 220 caracteres |
| `nome_fantasia` | string | 2 a 220 caracteres |
| `cnpj` | string | CNPJ valido, com ou sem mascara |
| `whatsapp` | string | 10 a 13 digitos apos normalizacao |
| `email` | string | e-mail valido, max. 255 caracteres |
| `endereco` | string | minimo 5 caracteres |
| `cidades_ufs_atuacao` | array | minimo 1 item |
| `responsavel_principal` | string | 2 a 200 caracteres |
| `cargo_responsavel` | string | 2 a 120 caracteres |

## Campos Opcionais No POST

| Campo | Tipo | Regra/Default |
| --- | --- | --- |
| `site` | string/null | max. 300 caracteres |
| `instagram` | string/null | max. 120 caracteres |
| `media_locacoes_mes` | integer/null | >= 0 |
| `aceite_lgpd` | boolean | default `true` |
| `opt_in_marketing` | boolean | default `true` |
| `origem` | string | default `site`; ver dominios |
| `origem_nome` | string/null | max. 120 caracteres |
| `utm_source` | string/null | max. 120 caracteres |
| `utm_medium` | string/null | max. 120 caracteres |
| `utm_campaign` | string/null | max. 120 caracteres |
| `utm_content` | string/null | max. 200 caracteres |
| `utm_term` | string/null | max. 200 caracteres |

## Campos Nao Editaveis Pelo Publico

Estes campos podem aparecer na resposta, mas nao devem ser enviados pelo frontend publico:

| Campo | Observacao |
| --- | --- |
| `id` | gerado pela API |
| `status` | controlado pelo admin; inicia como `pendente` |
| `observacoes_internas` | uso interno/admin |

## Objeto `cidades_ufs_atuacao`

Cada item:

| Campo | Tipo | Regra |
| --- | --- | --- |
| `cidade` | string | 2 a 120 caracteres |
| `uf` | string | UF brasileira valida, 2 letras |

Exemplo:

```json
[
  {"cidade": "Sao Paulo", "uf": "SP"},
  {"cidade": "Campinas", "uf": "SP"}
]
```

## Exemplo De POST

```json
{
  "razao_social": "Imobiliaria Exemplo Ltda",
  "nome_fantasia": "Imobiliaria Exemplo",
  "cnpj": "11.222.333/0001-81",
  "whatsapp": "+55 11 99999-9999",
  "email": "contato@imobiliariaexemplo.com.br",
  "endereco": "Rua Exemplo, 100 - Sao Paulo/SP",
  "cidades_ufs_atuacao": [
    {"cidade": "Sao Paulo", "uf": "SP"}
  ],
  "responsavel_principal": "Maria Silva",
  "cargo_responsavel": "Diretora",
  "site": "https://imobiliariaexemplo.com.br",
  "instagram": "@imobiliariaexemplo",
  "media_locacoes_mes": 12,
  "aceite_lgpd": true,
  "opt_in_marketing": true,
  "origem": "site",
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "cadastro-parceiros"
}
```

Resposta:

```json
{
  "id": "1c01f85d-1ac4-4e90-8b3c-cd9c7e4a5ef1",
  "token_cadastro": "token-seguro-retornado-uma-unica-vez"
}
```

## Exemplo De PATCH

```json
{
  "site": "https://novo-site.example.com.br",
  "media_locacoes_mes": 18
}
```

## Exemplo De Resposta Completa

```json
{
  "id": "1c01f85d-1ac4-4e90-8b3c-cd9c7e4a5ef1",
  "razao_social": "Imobiliaria Exemplo Ltda",
  "nome_fantasia": "Imobiliaria Exemplo",
  "cnpj": "11222333000181",
  "whatsapp": "5511999999999",
  "email": "contato@imobiliariaexemplo.com.br",
  "endereco": "Rua Exemplo, 100 - Sao Paulo/SP",
  "cidades_ufs_atuacao": [
    {"cidade": "Sao Paulo", "uf": "SP"}
  ],
  "responsavel_principal": "Maria Silva",
  "cargo_responsavel": "Diretora",
  "site": "https://imobiliariaexemplo.com.br",
  "instagram": "@imobiliariaexemplo",
  "media_locacoes_mes": 12,
  "aceite_lgpd": true,
  "opt_in_marketing": true,
  "origem": "site",
  "origem_nome": null,
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "cadastro-parceiros",
  "utm_content": null,
  "utm_term": null,
  "status": "pendente",
  "observacoes_internas": null
}
```

