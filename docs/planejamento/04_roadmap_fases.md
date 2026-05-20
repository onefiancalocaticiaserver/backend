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

- todo o sistema usara nomes em portugues;
- usar `imobiliaria` e `corretor` em rotas, schemas, modulos, tabelas e tools MCP;
- evitar nomes tecnicos em ingles como `agency` e `broker`.

Escopo funcional:

- um unico usuario admin inicial;
- login admin com JWT;
- cadastro de imobiliarias;
- cadastro de corretores;
- CRUD completo de imobiliarias e corretores para admin;
- CRUD de imobiliarias e corretores para o frontend do site, protegido por token seguro por cadastro;
- CRUD completo de imobiliarias e corretores via MCP/Hermes, com soft delete para remocao;
- vinculo corretor-imobiliaria;
- status operacional de parceiro: `pendente`, `ativo`, `inativo`, `rejeitado`;
- aceite LGPD com default `sim`;
- opt-in marketing com default `sim`, sujeito a validacao juridica antes de producao;
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

Obrigatorios atuais para formulario publico de imobiliaria:

- razao social;
- nome fantasia;
- CNPJ;
- WhatsApp;
- e-mail;
- endereco;
- cidades/UFs de atuacao;
- responsavel principal;
- cargo do responsavel.

Campos opcionais confirmados para formulario publico de imobiliaria:

- site;
- Instagram;
- media de locacoes por mes.

Campos controlados pelo sistema/admin:

- status da parceria;
- observacoes internas;
- aceite LGPD, default `sim`;
- opt-in marketing, default `sim`, sujeito a validacao juridica;
- origem;
- origem_nome;
- origem_usuario_id;
- UTM.

Origem:

- `origem` identifica de onde veio o cadastro;
- valores controlados: `site`, `chatbot`, `one`, `app_interno`, `api`, `importacao`, `outro`;
- `origem_nome` permite informar um nome livre pelo app interno;
- `origem_usuario_id` guarda o usuario/admin logado quando aplicavel;
- UTM segue como metadados de campanha: `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`.

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

Obrigatorios atuais para formulario publico de corretor:

- nome completo;
- CPF;
- CRECI;
- WhatsApp;
- e-mail;
- cidade/UF;
- tipo de corretor.

Campos opcionais confirmados para formulario publico de corretor:

- perfil profissional;
- imobiliaria vinculada;
- volume de indicacoes.

Observacoes sobre corretor:

- `perfil_profissional` e um campo livre opcional para descrever a atuacao do corretor; se nao houver uso claro no frontend, pode ficar nulo na Fase 1;
- se o tipo for `autonomo`, `imobiliaria_vinculada_id` fica nulo;
- se o tipo for `vinculado_imobiliaria`, `imobiliaria_vinculada_id` deve apontar para uma imobiliaria existente ou para uma imobiliaria criada no mesmo fluxo.

Campos controlados pelo sistema/admin:

- status da parceria;
- observacoes internas;
- aceite LGPD, default `sim`;
- opt-in marketing, default `sim`, sujeito a validacao juridica;
- origem;
- origem_nome;
- origem_usuario_id;
- UTM.

APIs sugeridas para o site:

```text
POST   /v1/publico/imobiliarias
GET    /v1/publico/imobiliarias/{imobiliaria_id}
PATCH  /v1/publico/imobiliarias/{imobiliaria_id}
POST   /v1/publico/corretores
GET    /v1/publico/corretores/{corretor_id}
PATCH  /v1/publico/corretores/{corretor_id}
```

Observacao: `POST` publico retorna `id` e `token_cadastro` uma unica vez. `GET/PATCH` publicos exigem header `X-Cadastro-Token`. `DELETE` publico nao e recomendado na Fase 1; deve ficar no admin ou virar solicitacao de cancelamento.

APIs admin sugeridas:

```text
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

Tools MCP sugeridas para Hermes na Fase 1:

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

Observacao: `remover_*` via MCP deve ser soft delete/cancelamento, com auditoria.

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
