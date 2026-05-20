# Plano Completo de Desenvolvimento, Testes, Deploy e Documentacao

Gerado em: 2026-05-20

## Objetivo

Construir o backend da One Fianca Locaticia como plataforma operacional segura para cadastro de parceiros, clientes, imoveis, propostas, documentos, calculo de fianca, comissoes e integracao com Hermes/WhatsApp via MCP.

## Premissas

- Banco canonico: PostgreSQL no container `postgresql-1ua2`, database `one`.
- Runtime backend: Python 3.12, FastAPI, SQLAlchemy 2.x, Pydantic v2, Alembic.
- MCP: FastMCP ou SDK MCP Python, com ferramentas semanticas e sem SQL bruto.
- Documentos: filesystem local seguro em `/srv/one-fianca/documents` no MVP.
- Front-end operacional: React + TypeScript + Vite, responsivo/mobile-first.
- Worker: fase 2 para processamento assincrono.
- Aprovacao/reprovacao: operador humano no MVP.
- Dados sensiveis: hash para busca/deduplicacao e criptografia para valores recuperaveis.
- Segredos reais nao devem ser versionados.
- A formula de calculo encontrada no app React esta aprovada como regra inicial.
- O output inicial sera JSON/tela no painel; geracao de PDF/imagem nao bloqueia o MVP.
- Ainda nao ha dominio final; o primeiro deploy pode usar acesso direto pela VPS para validacao.
- O painel interno pode iniciar publico com login, mas deve migrar para HTTPS e dominio antes de uso real com dados sensiveis.
- O Postgres atual pode ser recriado se isso simplificar padronizacao em PostgreSQL 18.

## Estrutura inicial do repositorio

```text
one-fianca-backend/
  AGENTS.md
  README.md
  pyproject.toml
  .env.example
  .gitignore
  docker-compose.yml
  docker-compose.prod.yml
  Dockerfile.api
  Dockerfile.mcp

  app/
    main.py
    core/
    db/
      models/
      repositories/
    schemas/
    services/
    api/v1/endpoints/
    mcp/
    storage/
    workers/
    integrations/one_calculator/

  web-admin/
  alembic/
  scripts/
  tests/
    unit/
    integration/
    security/
  docs/
```

## Fase 0 - Fundacao e seguranca operacional

Entregas:

- Inicializar repositorio Git.
- Criar `AGENTS.md`, `README.md`, `.gitignore`, `.env.example` e `ops.env.example`.
- Remover qualquer credencial real do escopo versionavel.
- Criar scaffold FastAPI.
- Criar configuracao central com Pydantic Settings.
- Criar conexao SQLAlchemy assync/sync conforme decisao tecnica.
- Configurar Alembic.
- Criar healthchecks `/v1/health` e `/v1/health/db`.
- Criar Dockerfiles e Compose local/prod.
- Criar scripts de bootstrap de roles.
- Confirmar versao real do PostgreSQL na VPS.

Critérios de aceite:

- `pytest` roda com pelo menos healthcheck unitario.
- `ruff check .` e `ruff format --check .` passam.
- `alembic upgrade head` executa em banco local.
- `.env.example` nao contem segredo real.
- Postgres nao e exposto publicamente no compose de producao.

## Fase 1 - Core operacional

Entregas:

- Migrations e modelos para:
  - `audit_events`;
  - `consents`;
  - `intake_sessions`;
  - `intake_messages`;
  - `leads`;
  - `agencies`;
  - `agency_contacts`;
  - `brokers`;
  - `broker_agency_links`;
  - `customers`;
  - `customer_pf_details`;
  - `customer_pj_details`;
  - `properties`;
  - `proposals`;
  - `proposal_status_history`;
  - `proposal_checklist_items`.
- Services de intake, parceiros, clientes, imoveis, propostas, checklist e auditoria.
- Validadores de CPF, CNPJ, telefone, UF, CEP e moeda.
- Endpoints REST para criar/listar/consultar/editar parceiros, clientes, imoveis e propostas.
- Regra de CEP obrigatorio para imovel.
- Criacao automatica de checklist PF/PJ ao criar proposta.
- Transicoes de status auditadas.
- Painel interno minimo com login, dashboard e detalhe de proposta.

Critérios de aceite:

- Criar imobiliaria, corretor, cliente PF/PJ, imovel e proposta via API.
- Checklist PF/PJ e recalculado corretamente.
- Mudanca de status cria `proposal_status_history` e `audit_event`.
- Rotas nao logam CPF/CNPJ em claro.
- Painel permite ver propostas e alterar dados basicos.

## Fase 2 - Calculo, documentos e dados bancarios

Entregas:

- Reimplementar calculo do app `pballeste/one` em Python:
  - seguro = aluguel * 1.20;
  - a vista = seguro;
  - total 5x = seguro * 1.10;
  - parcela 5x = total 5x / 5;
  - total 12x = seguro * 1.15;
  - parcela 12x = total 12x / 12.
- Criar `pricing_rules` e `proposal_calculations`.
- Persistir input/output de calculo.
- Criar `documents`, `secure_upload_links`, `partner_bank_accounts`, `commissions`, `payment_events`.
- Implementar storage local com nomes fisicos gerados.
- Implementar link seguro de upload com TTL.
- Validar extensao, MIME, magic bytes, tamanho, path traversal e dupla extensao.
- Implementar hash SHA-256 de documentos.
- Implementar criptografia e hash de CPF/CNPJ/PIX/conta bancaria.
- Implementar comissao default de 10% sobre `total_calculated_amount`, configuravel.
- Expandir painel para checklist documental, upload, calculo, dados bancarios e comissoes.

Critérios de aceite:

- Calculo retorna valores equivalentes ao app React para casos conhecidos.
- Upload aceita PDF/JPG/PNG validos e rejeita arquivos proibidos.
- Documento e salvo fora do banco e metadados ficam no Postgres.
- Download exige autorizacao.
- Dados bancarios recuperaveis ficam criptografados; buscas usam hash.
- Criacao/alteracao de conta bancaria gera auditoria.

## Fase 3 - Hermes MCP e fluxo conversacional

Entregas:

- Criar `one-mcp` com autenticacao Bearer.
- Expor apenas tools semanticas:
  - `search_by_whatsapp`;
  - `get_or_create_intake_session`;
  - `append_intake_message`;
  - `create_or_update_agency`;
  - `create_or_update_broker`;
  - `create_or_update_customer`;
  - `create_or_update_property`;
  - `create_or_update_proposal`;
  - `get_proposal_checklist`;
  - `list_missing_fields`;
  - `generate_secure_upload_link`;
  - `register_bank_account`;
  - `calculate_proposal`;
  - `advance_proposal_status`;
  - `append_internal_note`.
- Bloquear ferramentas genericas como `execute_sql`, `query_database`, `raw_update` e listagens sensiveis amplas.
- Criar prompt operacional do Hermes com limites de conduta.
- Configurar Hermes para usar URL interna `http://one-mcp:8100/mcp`.
- Testar fluxos WhatsApp:
  - corretor -> cliente -> imovel -> proposta;
  - imobiliaria -> corretor -> cliente -> proposta;
  - proposta com documento pendente;
  - dados bancarios de parceiro;
  - transferencia para humano.

Critérios de aceite:

- Hermes cria/continua intake sem duplicar cadastros obvios.
- Hermes pergunta campos faltantes um a um.
- Backend, nao Hermes, decide checklist e status.
- Aprovacao/reprovacao nao e feita pelo Hermes.
- Todas as chamadas MCP relevantes sao auditadas.

## Fase 4 - Operacao interna avancada

Entregas:

- Filtros avancados por status, parceiro, cidade, data, prioridade e pendencias.
- Timeline completa de proposta.
- Validacao/rejeicao de documentos no painel.
- Controle de pagamento recebido.
- Controle de comissao pendente/paga.
- Perfis internos: admin, operador, financeiro, leitura.
- Exportacoes operacionais simples em CSV.
- Indicadores: propostas por status, documentos pendentes, tempo medio de analise, comissoes pendentes.

Critérios de aceite:

- Operador consegue operar uma proposta do lead ate pagamento/comissao sem acessar banco manualmente.
- Financeiro consegue ver e marcar comissoes sem editar dados tecnicos.
- Auditoria permite reconstituir alteracoes sensiveis.

## Fase 5 - Automacao e expansao

Entregas futuras:

- Worker com fila robusta.
- ClamAV ou servico equivalente para antivirus.
- OCR e extracao assistida de documentos.
- Antifraude documental.
- Validacao externa CPF/CNPJ.
- Geracao de contrato PDF.
- Assinatura eletronica.
- Portal de parceiros.
- Isolamento por tenant/RLS.
- Conciliacao de pagamento.
- Backup externo criptografado.

## Plano de testes

### Unitarios

- CPF/CNPJ validos e invalidos.
- Normalizacao de telefone, CEP e moeda.
- Hash e criptografia de dados sensiveis.
- Checklist PF/PJ.
- Transicoes de status permitidas e proibidas.
- Calculo de fianca e arredondamento.
- Comissao configuravel.
- Validacao de extensao/MIME/magic bytes.
- Sanitizacao de filename e path traversal.

### Integracao

- Criacao completa de imobiliaria.
- Criacao completa de corretor autonomo.
- Vinculo corretor-imobiliaria.
- Criacao de cliente PF/PJ.
- Criacao de imovel com CEP obrigatorio.
- Criacao de proposta e checklist automatico.
- Calculo de proposta e persistencia do output.
- Upload por link seguro.
- Download autenticado.
- Avanco de status com historico.
- Registro de pagamento e criacao de comissao.

### Segurança

- Arquivo grande demais.
- Arquivo com dupla extensao.
- Arquivo com MIME falso.
- Tentativa de path traversal.
- Download sem autorizacao.
- Token de upload expirado.
- MCP sem Bearer token.
- Tentativa de tool proibida.
- Logs sem CPF/CNPJ/PIX/conta em claro.
- Acesso do usuario runtime sem privilegio de DDL.

### E2E

- Formulario web de cotacao -> proposta -> checklist -> upload -> analise.
- Hermes/WhatsApp -> intake -> proposta -> link de upload.
- Operador interno -> aprovar/reprovar -> pagamento -> comissao.
- Restore em ambiente temporario usando backup de banco e documentos.

## Plano de deploy

### Preparacao da VPS

- Conectar por SSH apenas quando for executar deploy.
- Preferir chave SSH em vez de senha root.
- Criar diretorio do projeto em `/opt/one-fianca-backend`.
- Criar diretorios persistentes:

```bash
/srv/one-fianca/documents
/srv/one-fianca/backups
/srv/one-fianca/logs
```

- Definir permissao restrita nesses diretorios.
- Confirmar versao do Postgres:

```bash
docker exec -it postgresql-1ua2 psql -U Admin -d one -c "SELECT version();"
```

### Banco

- Se Postgres 18 estiver disponivel, usar `uuidv7()`.
- Se nao estiver, usar `gen_random_uuid()` e registrar a decisao.
- Criar roles:
  - `one_admin`;
  - `one_migrator`;
  - `one_app`;
  - `one_readonly`.
- Rodar migrations com `one_migrator`.
- Rodar app com `one_app`.

### Containers

- `one-api` em rede publica e backend.
- `one-mcp` somente em rede backend.
- `one-web-admin` em rede publica via reverse proxy.
- `postgresql-1ua2` somente em rede backend.
- `one-worker` e `redis` a partir da Fase 2.

### Publicacao de APIs

- Primeiro ambiente: expor temporariamente por IP/porta da VPS para validacao controlada, por exemplo `http://<VPS_IP>:8000` para API e `http://<VPS_IP>:3000` para admin.
- Para uso com dados reais: publicar `one-api` via subdominio HTTPS, preferencialmente `api.onefiancalocaticia.com.br`.
- Para uso com dados reais: publicar `one-web-admin` via HTTPS, preferencialmente `admin.onefiancalocaticia.com.br`, com login forte e restricao progressiva de acesso.
- Nao expor `one-mcp` publicamente.
- Nao expor Postgres publicamente.
- Usar reverse proxy com TLS, CORS restrito e trusted hosts.

### Ordem de deploy

1. Preparar `.env` real na VPS a partir de `.env.example`.
2. Criar diretorios persistentes.
3. Recriar Postgres em `postgres:18`, se a versao atual nao for 18 ou se for mais limpo para iniciar.
4. Subir Postgres em rede privada.
5. Rodar bootstrap de roles.
6. Rodar migrations.
7. Subir `one-api`.
8. Validar `/v1/health` e `/v1/health/db`.
9. Subir `one-web-admin`.
10. Subir `one-mcp`.
11. Configurar Hermes para MCP interno.
12. Executar smoke tests.
13. Ativar backup diario.

### Smoke tests de deploy

- Health API retorna OK.
- Health DB retorna OK.
- Criacao de lead teste funciona.
- Criacao de proposta teste funciona.
- Upload teste salva arquivo e metadado.
- Download autenticado funciona.
- MCP responde com autenticacao correta.
- Tool proibida nao existe.
- Logs aparecem em `/srv/one-fianca/logs`.

## Plano de backup e restore

- Backup diario do Postgres em formato custom (`pg_dump -Fc`).
- Backup sincronizado dos documentos.
- Retencao inicial:
  - diarios: 14 dias;
  - semanais: 8 semanas;
  - mensais: 12 meses.
- Teste mensal de restore em container temporario.
- Validar hashes de documentos apos restore.
- Registrar resultado do restore em log operacional.

## Plano de documentacao

Arquivos a manter no repositorio:

- `README.md`: como rodar local, arquitetura resumida e comandos principais.
- `AGENTS.md`: regras para Codex/Cursor/Windsurf/Claude Code.
- `docs/PRD.md`: PRD consolidada e versionada.
- `docs/ARCHITECTURE.md`: topologia, servicos, redes e decisoes.
- `docs/DATA_MODEL.md`: entidades, relacoes, indices e politicas.
- `docs/API_CONTRACTS.md`: endpoints REST e exemplos.
- `docs/MCP_TOOLS.md`: tools MCP, inputs, outputs e proibicoes.
- `docs/SECURITY_LGPD.md`: classificacao de dados, controles e retencao.
- `docs/DEPLOYMENT.md`: VPS, Docker, TLS, env e smoke tests.
- `docs/BACKUP_RESTORE.md`: backup, restore e teste periodico.
- `docs/OPERATIONS_RUNBOOK.md`: comandos de rotina, incidentes e rollback.
- `docs/CHANGELOG.md`: mudancas por versao.

Regra de manutencao:

- Qualquer mudanca de API atualiza `API_CONTRACTS.md`.
- Qualquer mudanca de schema atualiza migrations e `DATA_MODEL.md`.
- Qualquer mudanca de MCP atualiza `MCP_TOOLS.md`.
- Qualquer mudanca de dado sensivel atualiza `SECURITY_LGPD.md`.
- Qualquer mudanca operacional atualiza `DEPLOYMENT.md` ou `OPERATIONS_RUNBOOK.md`.

## Marcos sugeridos

- Marco 1: scaffold, banco, healthcheck e migrations base.
- Marco 2: cadastros centrais e propostas.
- Marco 3: checklist, status e auditoria.
- Marco 4: calculo, documentos e dados bancarios.
- Marco 5: painel interno MVP.
- Marco 6: MCP/Hermes.
- Marco 7: deploy completo na VPS com backup e smoke tests.

## Definicao de pronto do MVP

O MVP esta pronto quando:

- API esta publicada em HTTPS na VPS.
- Banco canonico esta com migrations versionadas.
- Operador consegue cadastrar parceiro, cliente, imovel e proposta.
- Sistema gera checklist PF/PJ.
- Sistema calcula output de fianca conforme regra inicial.
- Sistema gera link seguro e recebe documentos.
- Dados bancarios sao protegidos por hash/criptografia.
- Status e eventos sensiveis sao auditados.
- Painel interno permite operacao basica.
- Hermes consegue coletar dados via MCP sem SQL direto.
- Backup e restore foram testados.
- Documentacao operacional minima esta atualizada.
