# Integracao Frontend - Cadastros

Este pacote documenta a integracao do frontend publico com os cadastros da Fase 1:

- imobiliarias;
- corretores;
- consulta/edicao publica por `token_cadastro`.

Arquivos:

- [01_endpoints_publicos.md](./01_endpoints_publicos.md): URLs, headers, status codes e fluxo esperado.
- [02_schema_imobiliaria.md](./02_schema_imobiliaria.md): campos, obrigatoriedade, regras e exemplos de imobiliaria.
- [03_schema_corretor.md](./03_schema_corretor.md): campos, obrigatoriedade, regras e exemplos de corretor.
- [04_regras_dominios_validacoes.md](./04_regras_dominios_validacoes.md): dominios, normalizacoes, erros e observacoes de UX.

Base URL atual de homologacao:

```text
http://<VPS_IP>:8000
```

Quando o dominio HTTPS estiver configurado, trocar para algo como:

```text
https://api.onefiancalocaticia.com.br
```

## Resumo Do Fluxo Publico

1. Frontend envia `POST /v1/publico/imobiliarias` ou `POST /v1/publico/corretores`.
2. API responde `201` com:

   ```json
   {
     "id": "uuid",
     "token_cadastro": "token-retornado-uma-unica-vez"
   }
   ```

3. Frontend deve guardar `id` e `token_cadastro` se quiser permitir consulta/edicao posterior.
4. Para consultar ou editar, enviar header:

   ```http
   X-Cadastro-Token: <token_cadastro>
   ```

5. Nao existe `DELETE` publico na Fase 1.

## Observacoes Importantes

- Todos os nomes de campos sao em portugues e devem ser enviados exatamente como documentado.
- `POST` publico nao exige login.
- `GET/PATCH` publico exigem `X-Cadastro-Token`.
- O `token_cadastro` so aparece na resposta do `POST`; a API nao permite recuperar esse token depois.
- `aceite_lgpd` e `opt_in_marketing` tem default `true` no backend.
- `opt_in_marketing=true` ainda deve ser revisado juridicamente antes de producao final.

