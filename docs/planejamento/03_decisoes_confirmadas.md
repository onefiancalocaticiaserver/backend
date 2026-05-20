# Decisoes Confirmadas

Gerado em: 2026-05-20

## Respostas do responsavel do projeto

1. Formula atual do calculo: aprovada.
2. Output do MVP: pode comecar como JSON/tela no painel.
3. Dominio/subdominio final: ainda nao definido.
4. Acesso inicial: pode usar algo direto da VPS.
5. Painel interno: inicialmente publico com login.
6. Postgres atual: pode ser recriado.
7. SSH/secrets: aprovado usar chave SSH e separar credenciais.
8. Fase 1 sera cadastro de imobiliarias e corretores.
9. `agency` = imobiliaria; `broker` = corretor.
10. A API deve permitir CRUD para imobiliarias e corretores.
11. Hermes podera fazer CRUD completo via MCP na Fase 1.
12. Havera um unico usuario admin inicial.

## Impacto no plano

Com essas respostas, Fase 0 e Fase 1 podem iniciar sem novas decisoes de negocio.

O deploy inicial pode usar acesso direto por IP/porta da VPS para desenvolvimento e homologacao controlada:

```text
API:   http://<VPS_IP>:8000
Admin: http://<VPS_IP>:3000
```

Para uso real com dados pessoais, financeiros e documentos, a recomendacao continua sendo colocar HTTPS com dominio/subdominio proprio antes de abrir operacao regular.

## Decisoes tecnicas derivadas

- Recriar o Postgres com `postgres:18` se a versao atual nao for 18.
- Usar `uuidv7()` como default de IDs quando PostgreSQL 18 estiver confirmado.
- Reimplementar o calculo em Python como `default_2026_v1`.
- Persistir input/output de calculo em `proposal_calculations`.
- Nao priorizar geracao de PDF/imagem no MVP.
- Criar admin login desde o inicio, pois o painel sera publicado inicialmente.
- Preparar reverse proxy/TLS como tarefa antes de operacao com dados reais.
- Substituir acesso root por senha por chave SSH no primeiro ciclo operacional.
- Implementar delete como soft delete/cancelamento.
- Proteger consulta/alteracao publica por token seguro ou login de parceiro.
