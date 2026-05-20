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

Nomenclatura tecnica:

- `agency` = imobiliaria;
- `broker` = corretor.

Escopo funcional:

- um unico usuario admin inicial;
- login admin com JWT;
- cadastro de imobiliarias;
- cadastro de corretores;
- CRUD completo de imobiliarias e corretores para admin;
- CRUD de imobiliarias e corretores para o frontend do site, desde que protegido por token seguro ou login de parceiro;
- CRUD completo de imobiliarias e corretores via MCP/Hermes, com soft delete para remocao;
- vinculo corretor-imobiliaria;
- status operacional de parceiro: `pending`, `active`, `inactive`, `rejected`;
- aceite LGPD obrigatorio nos cadastros publicos;
- opt-in marketing separado e opcional;
- auditoria basica de criacao/edicao;
- APIs para o frontend do site;
- APIs autenticadas para admin;
- tools MCP iniciais para Hermes operar CRUD de parceiro.

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

Obrigatorios recomendados para formulario publico de imobiliaria:

- nome fantasia;
- razao social;
- CNPJ;
- WhatsApp;
- e-mail;
- cidade/UF;
- responsavel principal;
- aceite LGPD.

Campos opcionais recomendados para formulario publico de imobiliaria:

- site;
- Instagram;
- endereco completo;
- cidades/UFs de atuacao;
- cargo do responsavel;
- media de locacoes por mes;
- opt-in marketing.

Campos controlados pelo sistema/admin:

- status da parceria;
- observacoes internas;
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

Obrigatorios recomendados para formulario publico de corretor:

- nome completo;
- CPF;
- WhatsApp;
- e-mail;
- cidade/UF;
- tipo de corretor;
- aceite LGPD.

Campos opcionais recomendados para formulario publico de corretor:

- CRECI;
- perfil profissional;
- imobiliaria vinculada;
- volume de indicacoes;
- opt-in marketing.

Campos controlados pelo sistema/admin:

- status da parceria;
- observacoes internas;
- origem/UTM.

APIs sugeridas para o site:

```text
POST   /v1/public/agencies
GET    /v1/public/agencies/{agency_id}
PATCH  /v1/public/agencies/{agency_id}
POST   /v1/public/brokers
GET    /v1/public/brokers/{broker_id}
PATCH  /v1/public/brokers/{broker_id}
```

Observacao: `GET/PATCH` publicos precisam de token seguro por cadastro ou login de parceiro. `DELETE` publico nao e recomendado na Fase 1; deve ficar no admin ou virar solicitacao de cancelamento.

APIs admin sugeridas:

```text
POST   /v1/admin/auth/login
GET    /v1/admin/me
GET    /v1/admin/agencies
GET    /v1/admin/agencies/{agency_id}
PATCH  /v1/admin/agencies/{agency_id}
DELETE /v1/admin/agencies/{agency_id}
GET    /v1/admin/brokers
GET    /v1/admin/brokers/{broker_id}
PATCH  /v1/admin/brokers/{broker_id}
DELETE /v1/admin/brokers/{broker_id}
POST   /v1/admin/agencies/{agency_id}/brokers/{broker_id}
DELETE /v1/admin/agencies/{agency_id}/brokers/{broker_id}
```

Tools MCP sugeridas para Hermes na Fase 1:

```text
create_agency
get_agency
update_agency
delete_agency
create_broker
get_broker
update_broker
delete_broker
link_broker_to_agency
append_partner_note
```

Observacao: `delete_*` via MCP deve ser soft delete/cancelamento, com auditoria.

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
