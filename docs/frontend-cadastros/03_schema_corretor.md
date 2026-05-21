# Schema Publico - Corretor

## Campos Obrigatorios No POST

| Campo | Tipo | Regra |
| --- | --- | --- |
| `nome_completo` | string | 2 a 220 caracteres |
| `cpf` | string | CPF valido, com ou sem mascara |
| `creci` | string | 3 a 40 caracteres |
| `whatsapp` | string | 10 a 13 digitos apos normalizacao |
| `email` | string | e-mail valido, max. 255 caracteres |
| `cidade` | string | 2 a 120 caracteres |
| `uf` | string | UF brasileira valida, 2 letras |
| `tipo_corretor` | string | ver dominios |

## Campos Opcionais No POST

| Campo | Tipo | Regra/Default |
| --- | --- | --- |
| `perfil_profissional` | string/null | texto livre |
| `imobiliaria_vinculada_id` | uuid/null | permitido quando nao for autonomo |
| `volume_indicacoes` | integer/null | >= 0 |
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

## Regras Do Tipo De Corretor

Valores aceitos:

```text
autonomo
vinculado_imobiliaria
consultor
outro
```

Regra principal:

- se `tipo_corretor = "autonomo"`, o backend sempre força `imobiliaria_vinculada_id = null`, mesmo que o frontend envie um valor;
- se `tipo_corretor` for diferente de `autonomo` e `imobiliaria_vinculada_id` for enviada, ela precisa apontar para uma imobiliaria existente e nao removida;
- se o frontend ainda nao tiver a imobiliaria para vincular, enviar `tipo_corretor = "autonomo"` ou omitir `imobiliaria_vinculada_id`.

## Exemplo De POST - Autonomo

```json
{
  "nome_completo": "Joao Corretor",
  "cpf": "529.982.247-25",
  "creci": "CRECI-SP 12345",
  "whatsapp": "+55 11 98888-7777",
  "email": "joao.corretor@example.com",
  "cidade": "Sao Paulo",
  "uf": "SP",
  "tipo_corretor": "autonomo",
  "perfil_profissional": "Atua com locacoes residenciais",
  "volume_indicacoes": 8,
  "aceite_lgpd": true,
  "opt_in_marketing": true,
  "origem": "site"
}
```

Resposta:

```json
{
  "id": "2d5c8b43-2738-4dd8-8e44-652d9efc1c00",
  "token_cadastro": "token-seguro-retornado-uma-unica-vez"
}
```

## Exemplo De POST - Vinculado A Imobiliaria

```json
{
  "nome_completo": "Ana Corretora",
  "cpf": "111.444.777-35",
  "creci": "CRECI-SP 98765",
  "whatsapp": "+55 11 97777-6666",
  "email": "ana.corretora@example.com",
  "cidade": "Sao Paulo",
  "uf": "SP",
  "tipo_corretor": "vinculado_imobiliaria",
  "imobiliaria_vinculada_id": "1c01f85d-1ac4-4e90-8b3c-cd9c7e4a5ef1",
  "aceite_lgpd": true,
  "opt_in_marketing": true,
  "origem": "site"
}
```

## Exemplo De PATCH

```json
{
  "whatsapp": "+55 11 96666-5555",
  "volume_indicacoes": 15
}
```

## Exemplo De Resposta Completa

```json
{
  "id": "2d5c8b43-2738-4dd8-8e44-652d9efc1c00",
  "nome_completo": "Joao Corretor",
  "cpf": "52998224725",
  "creci": "CRECI-SP 12345",
  "whatsapp": "5511988887777",
  "email": "joao.corretor@example.com",
  "cidade": "Sao Paulo",
  "uf": "SP",
  "tipo_corretor": "autonomo",
  "perfil_profissional": "Atua com locacoes residenciais",
  "imobiliaria_vinculada_id": null,
  "volume_indicacoes": 8,
  "aceite_lgpd": true,
  "opt_in_marketing": true,
  "origem": "site",
  "origem_nome": null,
  "utm_source": null,
  "utm_medium": null,
  "utm_campaign": null,
  "utm_content": null,
  "utm_term": null,
  "status": "pendente",
  "observacoes_internas": null
}
```

