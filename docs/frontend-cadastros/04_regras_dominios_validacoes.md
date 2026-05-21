# Regras, Dominios E Validacoes

## Dominios

### `origem`

Valores aceitos:

```text
site
chatbot
one
app_interno
api
importacao
outro
```

Uso recomendado no frontend publico:

- enviar `site`;
- ou omitir o campo, pois o backend usa `site` como default nas rotas publicas.

`origem_nome` e texto livre opcional para detalhar a origem quando fizer sentido.

### `status`

Valores internos:

```text
pendente
ativo
inativo
rejeitado
```

O frontend publico nao deve enviar `status`. Novos cadastros entram como `pendente`.

### `tipo_corretor`

Valores aceitos:

```text
autonomo
vinculado_imobiliaria
consultor
outro
```

## Normalizacoes Feitas Pelo Backend

| Campo | Normalizacao |
| --- | --- |
| `cnpj` | remove mascara e salva somente digitos |
| `cpf` | remove mascara e salva somente digitos |
| `whatsapp` | remove mascara e salva somente digitos |
| `email` | trim e lowercase |
| `uf` | uppercase |
| `creci` | trim e uppercase |

Exemplo: `+55 11 99999-9999` vira `5511999999999`.

## Validacoes De Documento

- `cnpj` precisa passar no calculo de digitos verificadores.
- `cpf` precisa passar no calculo de digitos verificadores.
- sequencias repetidas como `111.111.111-11` sao rejeitadas.

## Validacoes De Contato

- `email` precisa ser formalmente valido.
- `whatsapp` deve ter entre 10 e 13 digitos depois de remover mascara.

## Validacoes De UF

UFs aceitas:

```text
AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO
```

## Regras De Token De Cadastro

- `token_cadastro` e retornado somente no `POST`.
- Guardar esse token junto com o `id` se o usuario puder voltar para editar/consultar.
- Enviar o token em `GET/PATCH` no header `X-Cadastro-Token`.
- Token errado retorna `403`.
- Header ausente retorna `422`.
- Nao armazenar esse token em local publico compartilhado; ele funciona como uma credencial simples daquele cadastro.

## UTM

Campos opcionais aceitos:

```text
utm_source
utm_medium
utm_campaign
utm_content
utm_term
```

Recomendacao:

- capturar da URL do site quando existirem;
- enviar no `POST`;
- manter `null`/omitido quando nao houver campanha.

## LGPD E Marketing

Campos:

```text
aceite_lgpd
opt_in_marketing
```

Defaults atuais:

```json
{
  "aceite_lgpd": true,
  "opt_in_marketing": true
}
```

Observacao: `opt_in_marketing=true` como default e uma decisao temporaria e deve ser revisada juridicamente antes de producao final.

## Erros E Formato De Resposta

Erros de validacao FastAPI/Pydantic geralmente retornam:

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "cnpj"],
      "msg": "Value error, CNPJ invalido",
      "input": "11.111.111/1111-11"
    }
  ]
}
```

Erros de regra de negocio podem retornar:

```json
{
  "detail": "origem_invalida"
}
```

Principais `detail` esperados:

```text
token_cadastro_invalido
imobiliaria_nao_encontrada
corretor_nao_encontrado
imobiliaria_ja_cadastrada
corretor_ja_cadastrado
origem_invalida
status_invalido
tipo_corretor_invalido
```

## Recomendacoes De UX

- Aplicar mascara de CPF/CNPJ/WhatsApp no frontend, mas enviar com ou sem mascara; o backend aceita ambos.
- Mostrar `aceite_lgpd` como checkbox explicito no formulario.
- Nao mostrar `status` no fluxo publico inicial, salvo em uma tela de acompanhamento.
- Salvar `id` e `token_cadastro` no estado do fluxo se houver tela de revisao/edicao.
- Em caso de `409`, orientar o usuario a verificar se o CPF/CNPJ ja foi cadastrado.

