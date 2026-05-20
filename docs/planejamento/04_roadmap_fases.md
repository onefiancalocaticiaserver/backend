# Roadmap por Fases

Gerado em: 2026-05-20

## Fase 0 - Fundacao tecnica

Status: iniciada.

Entregas:

- scaffold FastAPI;
- SQLAlchemy e Alembic;
- Docker local/prod;
- healthchecks;
- `.env.example` e `ops.env.example`;
- documentacao inicial;
- testes, lint, format e type check;
- Git local e remoto configurado.

Aceite:

- API sobe localmente e por Docker;
- Postgres 18 local sobe sem conflito;
- migration inicial executa;
- `/v1/health` e `/v1/health/db` respondem OK;
- `vps.env` permanece fora do Git.

## Fase 1 - Cadastro de imobiliarias e corretores

Objetivo: permitir que o site/frontend e o Hermes cadastrem imobiliarias e corretores, e que um unico admin interno consulte e gerencie esses cadastros.

Escopo funcional:

- um unico usuario admin inicial;
- login admin com JWT;
- cadastro de imobiliarias;
- cadastro de corretores;
- vinculo corretor-imobiliaria;
- status operacional de parceiro: `pending`, `active`, `inactive`, `rejected`;
- aceite LGPD obrigatorio nos cadastros publicos;
- opt-in marketing separado e opcional;
- auditoria basica de criacao/edicao;
- APIs publicas de envio para o frontend do site;
- APIs autenticadas para admin;
- tools MCP iniciais para Hermes criar/atualizar cadastro de parceiro e consultar campos faltantes.

Dados de imobiliaria disponiveis para implementacao:

- razao social;
- nome fantasia;
- CNPJ;
- telefone/WhatsApp;
- e-mail;
- site;
- Instagram;
- endereco;
- cidades/UFs de atuacao;
- responsavel principal;
- cargo do responsavel;
- media de locacoes por mes;
- status da parceria;
- observacoes internas;
- aceite LGPD;
- opt-in marketing;
- origem/UTM.

Dados de corretor disponiveis para implementacao:

- nome completo;
- CPF;
- CRECI, se houver;
- WhatsApp;
- e-mail;
- cidade/UF;
- perfil profissional;
- tipo: `autonomo`, `vinculado_imobiliaria`, `consultor`, `outro`;
- imobiliaria vinculada, se houver;
- status da parceria;
- volume de indicacoes;
- observacoes;
- aceite LGPD;
- opt-in marketing;
- origem/UTM.

APIs publicas sugeridas para o site:

```text
POST /v1/public/agencies
POST /v1/public/brokers
```

APIs admin sugeridas:

```text
POST   /v1/admin/auth/login
GET    /v1/admin/me
GET    /v1/admin/agencies
GET    /v1/admin/agencies/{agency_id}
PATCH  /v1/admin/agencies/{agency_id}
GET    /v1/admin/brokers
GET    /v1/admin/brokers/{broker_id}
PATCH  /v1/admin/brokers/{broker_id}
POST   /v1/admin/agencies/{agency_id}/brokers/{broker_id}
DELETE /v1/admin/agencies/{agency_id}/brokers/{broker_id}
```

Tools MCP sugeridas para Hermes na Fase 1:

```text
get_or_create_partner_intake_session
create_or_update_agency
create_or_update_broker
link_broker_to_agency
list_partner_missing_fields
append_partner_note
```

Fora do escopo da Fase 1:

- leads de cotacao;
- clientes PF/PJ;
- imoveis;
- propostas;
- documentos;
- dados bancarios;
- calculo de fianca;
- comissoes;
- painel operacional avancado.

## Fase 2 - Leads, clientes, imoveis, propostas e documentos

Objetivo: transformar o backend em fluxo operacional de proposta de fianca.

Escopo:

- leads de cotacao;
- clientes PF/PJ;
- imoveis com CEP obrigatorio;
- propostas;
- checklist documental;
- links seguros de upload;
- storage local de documentos;
- metadados de documentos;
- status de proposta;
- calculo/output JSON/tela;
- dados bancarios de parceiros;
- comissao configuravel;
- MCP ampliado para intake conversacional de propostas.

## Fase 3 - Operacao, pagamentos e painel avancado

Escopo:

- painel interno mais completo;
- filtros operacionais;
- timeline/auditoria detalhada;
- financeiro de pagamentos e comissoes;
- notificacoes;
- worker para tarefas assincronas;
- antivirus/ClamAV;
- metricas operacionais;
- backups e restore automatizados.

## Fase 4 - Automacoes e expansao

Escopo:

- OCR;
- antifraude documental;
- validacao externa CPF/CNPJ;
- geracao de contrato PDF;
- assinatura eletronica;
- portal de parceiros;
- RLS ou isolamento tenant;
- conciliacao automatica de pagamento.

