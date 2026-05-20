# Entendimento do Projeto

Gerado em: 2026-05-20

## Sintese

O projeto One Fianca Locaticia deve ser tratado como um backend operacional para cadastro, intake, analise e acompanhamento de propostas de fianca locaticia. Ele nao e apenas um coletor de formulario. O produto combina mini-CRM, workflow de proposta, checklist documental, dados bancarios de parceiros, calculo/output de fianca, controle de pagamento/comissao e integracao conversacional com Hermes/WhatsApp.

## Documentos analisados

- `Arquitetura_geral.md`: documento preliminar, com a recomendacao central de separar Hermes, backend e Postgres.
- `one_fianca_backend_prd_arquitetura_codex_ready (1).md`: PRD consolidada e codex-ready, com decisoes de stack, dominios, DDL inicial, endpoints, MCP, seguranca, LGPD, deploy e roadmap.
- `vps.env`: contem acesso operacional da VPS e credenciais do Postgres existente. Esses valores devem ser movidos para controle operacional seguro e nunca montados em containers da aplicacao.
- `https://github.com/pballeste/one`: app Vite/React existente usado como referencia do calculo/output de fianca.

## Arquitetura entendida

A arquitetura alvo e:

```text
Hermes/WhatsApp = conversa e coleta
one-mcp = ferramentas MCP semanticas e controladas
one-api = regras de negocio, REST, validacao, auditoria, calculo e storage
one-web-admin = operacao humana interna responsiva
one-worker = tarefas assincronas fase 2
PostgreSQL = fonte canonica dos dados
filesystem local = documentos protegidos fora das tabelas principais
```

O Hermes nao deve acessar SQL diretamente, nao deve aprovar/reprovar proposta e nao deve guardar estado canonico do negocio. O backend deve decidir campos faltantes, validade dos dados, checklist, transicoes de status e auditoria.

## Dominio funcional

Entidades centrais:

- imobiliarias;
- corretores autonomos ou vinculados;
- dados bancarios/PIX de parceiros;
- clientes PF/PJ;
- imoveis;
- leads/intake sessions;
- propostas/analises;
- documentos e versoes;
- calculos/output de fianca;
- comissoes e eventos de pagamento;
- auditoria e consentimentos.

A proposta e a entidade central. Ela conecta cliente, imovel, parceiro originador/responsavel, checklist documental, calculo, status, pagamento e comissao.

## Entrada de dados

O sistema deve aceitar dados por:

- formulario web;
- Hermes/WhatsApp via MCP;
- operador interno;
- API externa futura.

Como a conversa no WhatsApp pode chegar incompleta e fora de ordem, o modelo deve separar:

- camada de intake, flexivel e tolerante a dados parciais;
- camada canonica, normalizada e auditavel.

## Calculo existente

O repositorio `pballeste/one` e um app front-end Vite/React, nao uma biblioteca backend. A logica encontrada no commit analisado e:

```text
valor_seguro = aluguel * 1.20
valor_a_vista = valor_seguro
total_5x = valor_seguro * 1.10
parcela_5x = total_5x / 5
total_12x = valor_seguro * 1.15
parcela_12x = total_12x / 12
```

Todos os valores sao arredondados para 2 casas decimais. O app atual tambem gera uma arte/JPG e persiste JSON localmente no navegador. Para o backend, essa regra deve virar um `calculation_service` com testes de equivalencia contra exemplos do app atual e regras configuraveis em tabela.

## Infra atual entendida

O arquivo `vps.env` informa:

- acesso SSH root da VPS;
- container PostgreSQL existente chamado `postgresql-1ua2`;
- banco `one`;
- usuario administrativo inicial;
- porta Postgres.

Esses dados indicam o destino de deploy, mas ha uma separacao importante:

- credenciais SSH/root pertencem a operacao, nao ao `.env` runtime da aplicacao;
- credenciais reais nao devem ser versionadas;
- a aplicacao deve usar usuarios dedicados como `one_app` e `one_migrator`, nao o usuario administrativo inicial em runtime;
- o Postgres nao deve ter porta publica exposta.

## Decisoes confirmadas em 2026-05-20

- A formula atual do app React esta aprovada como regra oficial inicial.
- O output do MVP pode comecar como JSON/tela no painel; PDF/imagem fica para etapa posterior.
- Ainda nao ha dominio/subdominio final definido.
- Acesso inicial pode ser feito direto pela VPS, usando IP/porta para desenvolvimento e validacao.
- O painel interno sera inicialmente publico com login.
- O container/volume atual do Postgres pode ser recriado.
- Acesso SSH por chave e separacao de segredos estao aprovados.

## Riscos e pontos de atencao

- Confirmar se o container atual esta em PostgreSQL 18. Se nao estiver e ainda nao houver dados relevantes, recriar com `postgres:18`; caso contrario, usar fallback `gen_random_uuid()`.
- O arquivo `vps.env` contem segredos em claro. Deve ser retirado de qualquer futuro Git e substituido por `.env.example`, `ops.env.example` e secrets reais fora do repositorio.
- Dados bancarios, documentos, CPF/CNPJ e renda exigem hash, criptografia, controle de acesso, logs sem dados brutos e auditoria.
- Upload de documentos precisa validar extensao, MIME, magic bytes, tamanho, path traversal e dupla extensao.
- Backups do banco e dos documentos precisam ser coordenados para evitar metadados sem arquivo, ou arquivo sem metadado.
- A politica juridica de retencao precisa ser confirmada antes de automatizar expurgo.
- O painel interno com acesso multiusuario pode comecar com RBAC simples, mas portal de parceiros exigira isolamento por tenant ou RLS futuramente.

## Decisao tecnica recomendada

Manter a PRD consolidada como fonte de verdade inicial, com pequenos ajustes:

- tratar `vps.env` como arquivo operacional temporario, nao como configuracao de app;
- criar repositorio real com scaffold FastAPI/FastMCP/Alembic;
- implementar Fase 0 e Fase 1 sem bloquear por decisoes futuras de dominio, juridico e gateway;
- integrar calculo do app React por reimplementacao em Python, pois a logica e simples e deterministica;
- deixar geracao de contrato PDF, OCR, antifraude e pagamento automatico para fases posteriores.
