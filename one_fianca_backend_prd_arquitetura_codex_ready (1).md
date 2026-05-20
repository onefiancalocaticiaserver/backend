# One Fiança Locatícia — PRD, Arquitetura Backend e Especificação Codex-Ready

**Versão:** 1.0 — especificação consolidada para desenvolvimento  
**Data:** 12/05/2026  
**Projeto:** One Fiança Locatícia  
**Stack-alvo:** Docker + PostgreSQL 18 + Python FastAPI + FastMCP + Hermes WhatsApp + front-end operacional responsivo  
**Infra atual:** VPS Ubuntu Hostinger KVM 4, container Postgres já criado `postgresql-1ua2`, banco `one`, usuário administrativo inicial `Admin`  
**Uso esperado:** documento mestre para Codex, Cursor, Windsurf, Claude Code, GitHub Copilot ou outro Agentic AI IDE  

---

## 0. Objetivo deste documento

Este documento consolida a PRD, arquitetura técnica, arquitetura de dados, modelo lógico, integrações, segurança, LGPD, containers, serviços, APIs, MCP/Hermes, upload de documentos, front-end operacional e roadmap de implementação do backend da One Fiança Locatícia.

Ele deve ser usado como **fonte de verdade inicial** para desenvolvimento assistido por Codex/OpenAI, Cursor, Windsurf, Claude Code ou GitHub Copilot.

O objetivo é construir um backend seguro, extensível e operacional para:

1. cadastro de imobiliárias;
2. cadastro de corretores vinculados ou autônomos;
3. coleta de dados bancários/PIX para comissões;
4. criação e acompanhamento de leads;
5. criação de clientes PF/PJ;
6. cadastro estruturado de imóveis;
7. geração de cálculo/output de fiança a partir da lógica existente no GitHub `pballeste/one`;
8. controle de propostas/análises de fiança;
9. upload seguro de documentos via link web;
10. gestão de status até aprovação/reprovação, contrato, pagamento e comissão;
11. integração conversacional com Hermes/WhatsApp;
12. interface operacional responsiva para operador humano interno.

---

## 1. Decisões arquiteturais finais

### 1.1 Decisões aprovadas

1. O **PostgreSQL local** será o banco canônico do projeto.
2. O container atual `postgresql-1ua2` será aproveitado, desde que esteja em **PostgreSQL 18** ou seja recriado/migrado para essa versão.
3. O banco canônico se chamará `one`.
4. O usuário administrativo inicial será `Admin`, com senha carregada por `.env`/secret.
5. O Hermes será mantido como **interface conversacional via WhatsApp**, não como banco, não como CRM e não como executor direto de SQL.
6. O backend será composto por:
   - `one-api`: serviço REST em Python/FastAPI;
   - `one-mcp`: servidor MCP em Python/FastMCP para integração controlada com Hermes;
   - `one-web-admin`: front-end operacional responsivo para uso interno;
   - `one-worker`: fase 2, para tarefas assíncronas, validações de arquivo, notificações e automações;
   - `postgresql-1ua2`: PostgreSQL 18;
   - storage local seguro para documentos.
7. Arquivos PDF/JPG/PNG serão armazenados fora das tabelas principais, em filesystem local seguro da VPS, com metadados no Postgres.
8. Dados sensíveis serão tratados com:
   - normalização;
   - hash para busca/deduplicação;
   - criptografia no backend para valores que precisam ser recuperáveis;
   - logs de auditoria;
   - acesso restrito;
   - política de retenção.
9. Skills comunitárias não auditadas do Hermes/OpenClaw/ClawHub não serão usadas para CRUD, banco, documentos, dados bancários ou cadastro.
10. A integração recomendada do Hermes é via **FastMCP/custom MCP server**, criando o `one-mcp` próprio e permitindo ao Hermes chamar apenas ferramentas de negócio bem definidas.
11. O MVP terá **operador humano interno** responsável por aprovação/reprovação de propostas.
12. O front-end operacional deve ser **responsivo/mobile-first**, pois boa parte dos usuários internos/parceiros poderá operar pelo celular.
13. Documentos serão enviados inicialmente por **link seguro/upload web**, não diretamente por WhatsApp. Upload via WhatsApp fica para fase posterior.
14. A geração de contrato PDF ficará para fase 2. No MVP, será gerado/armazenado apenas o output de cálculo/proposta.
15. A integração bancária/PIX para pagamento automático de comissão fica para fase 3. No MVP, o pagamento de comissão será apenas registrado manualmente.

### 1.2 Decisão sobre versão do Postgres

**Recomendação:** instalar ou recriar o container com **PostgreSQL 18**.

Motivos:

- PostgreSQL 18 possui `uuidv7()` nativo.
- UUIDv7 é ordenável por tempo, melhora localidade de índice e facilita auditoria temporal.
- É uma versão nova, adequada para um sistema novo sem legado.
- O projeto ainda está em fase inicial; portanto, não há custo relevante de migração.

Fallback: se por qualquer motivo o container ficar em PostgreSQL 16/17, usar `gen_random_uuid()` com `pgcrypto` e manter compatibilidade.

### 1.3 Decisão sobre storage de documentos

**MVP recomendado:** filesystem local em volume/bind mount seguro na VPS Hostinger.

Caminho sugerido no host:

```bash
/srv/one-fianca/documents
/srv/one-fianca/backups
/srv/one-fianca/logs
```

Caminho montado nos containers:

```bash
/app/storage/documents
/app/storage/backups
/app/logs
```

Não usar AWS S3 no MVP se a prioridade é menor custo, menor complexidade, menor superfície de compliance e controle local LGPD. S3, Cloudflare R2, Backblaze B2 ou MinIO podem entrar depois.

**Fase 2 recomendada:** avaliar MinIO local se houver necessidade de API S3, versionamento de objetos, melhor separação lógica e URLs temporárias internas.

**Fase 3 possível:** backup criptografado externo em S3 Glacier, Cloudflare R2, Backblaze B2 ou outro storage, desde que os arquivos estejam criptografados antes de sair da VPS.

### 1.4 Decisão sobre privacidade

E-mail de privacidade configurável:

```env
PRIVACY_EMAIL=privacidade@onefiancalocaticia.com.br
```

Enquanto o e-mail oficial não existir, usar valor de teste no `.env`. O texto de política e aceites deve referenciar esse valor via configuração, não hardcoded.

---

## 2. Visão do produto

A One Fiança Locatícia precisa de um backend que suporte:

1. cadastro de imobiliárias parceiras;
2. cadastro de corretores vinculados a imobiliárias;
3. cadastro de corretores autônomos;
4. dados bancários/PIX para pagamento de comissões;
5. leads e propostas de fiança locatícia;
6. cadastro de clientes PF/PJ;
7. cadastro completo de imóvel, com CEP obrigatório;
8. checklist documental por tipo de cliente;
9. upload, versionamento e validação operacional de documentos;
10. cálculo/output de fiança com base no projeto existente do GitHub `pballeste/one`;
11. status operacional da proposta até contrato, pagamento e comissão;
12. integração com Hermes via WhatsApp para coleta conversacional;
13. integração com website/front-end via REST;
14. interface operacional interna responsiva/mobile-first.

O backend não será apenas um formulário. Ele será a base operacional de um **mini-CRM + workflow de proposta + checklist documental + gestão de comissão**.

---

## 3. Escopo funcional do MVP

### 3.1 Cadastros de parceiros

#### Imobiliária

Campos principais:

- razão social;
- nome fantasia;
- CNPJ;
- telefone/WhatsApp;
- e-mail;
- site;
- Instagram;
- endereço;
- cidades/UFs de atuação;
- responsável principal;
- cargo do responsável;
- média de locações por mês;
- status da parceria;
- observações internas;
- aceite LGPD;
- opt-in marketing;
- origem/UTM.

#### Corretor

Campos principais:

- nome completo;
- CPF;
- CRECI, se houver;
- WhatsApp;
- e-mail;
- cidade/UF;
- perfil profissional;
- tipo: `autonomo`, `vinculado_imobiliaria`, `consultor`, `outro`;
- imobiliária vinculada, se houver;
- status da parceria;
- volume de indicações;
- observações;
- aceite LGPD;
- opt-in marketing;
- origem/UTM.

#### Relacionamento imobiliária-corretor

Um corretor pode:

- estar vinculado a uma imobiliária;
- atuar de forma autônoma;
- futuramente ter múltiplos vínculos, se necessário.

No MVP, permitir múltiplos vínculos, mas marcar apenas um como principal.

### 3.2 Dados bancários de parceiros

Dados necessários:

- tipo de parceiro: imobiliária/corretor;
- ID do parceiro;
- nome do titular;
- CPF/CNPJ do titular;
- banco;
- código do banco;
- agência;
- dígito da agência;
- conta;
- dígito da conta;
- tipo de conta: corrente/poupança/pagamento;
- chave PIX;
- tipo de chave PIX: CPF/CNPJ/e-mail/telefone/aleatória;
- status de verificação;
- conta principal;
- histórico de alteração.

Regra:

- dados bancários podem ser coletados pelo Hermes ou pelo operador interno;
- o operador interno também terá interface responsiva para cadastro/edição;
- dados bancários devem ser criptografados quando recuperáveis;
- hashes devem ser usados para deduplicação/busca exata;
- todo acesso/alteração deve gerar evento em `audit_events`.

### 3.3 Leads e propostas

O sistema deve aceitar entrada por:

- formulário web;
- Hermes WhatsApp;
- operador interno;
- futuramente API externa.

A proposta/análise será a entidade central que conecta:

- cliente PF/PJ;
- imóvel;
- parceiro responsável, que pode ser imobiliária ou corretor;
- documentos;
- cálculo/output da fiança;
- status;
- comissão.

### 3.4 Cliente PF/PJ

#### Cliente PF

Campos:

- nome completo;
- CPF;
- RG/CNH/outro documento;
- WhatsApp;
- e-mail;
- endereço de contato;
- profissão;
- renda declarada;
- tipo de comprovante de renda;
- observações.

#### Cliente PJ

Campos:

- razão social;
- nome fantasia;
- CNPJ;
- responsável;
- cargo do responsável;
- WhatsApp;
- e-mail;
- endereço da sede;
- faturamento/renda declarada;
- tipo de comprovante;
- observações.

### 3.5 Imóvel

Qualquer proposta/contrato precisa ter dados completos do imóvel.

Campos mínimos obrigatórios no MVP:

- CEP obrigatório;
- logradouro;
- número;
- bairro;
- cidade;
- UF;
- tipo de imóvel;
- finalidade da locação;
- valor do aluguel.

Campos adicionais recomendados:

- complemento;
- endereço completo textual;
- valor do condomínio;
- valor do IPTU;
- taxa de lixo;
- outras taxas financeiras cobertas, se houver;
- valor mensal total de referência;
- observações.

### 3.6 Documentos

Documentos mínimos por proposta:

#### PF

- documento de identidade: RG, CNH ou equivalente;
- comprovante de renda: holerite, carta do contador, extrato/declaração equivalente;
- dados completos do imóvel.

#### PJ

- contrato social;
- comprovante de renda/faturamento: carta do contador, declaração equivalente ou documento fiscal/contábil aceito;
- dados completos do imóvel.

Tipos de arquivo aceitos no MVP:

- PDF preferencial;
- JPG opcional;
- PNG opcional.

Tipos rejeitados:

- DOC/DOCX;
- XLS/XLSX;
- ZIP/RAR;
- EXE;
- HTML;
- qualquer arquivo executável;
- qualquer arquivo fora da allowlist.

Limites sugeridos:

- PDF: até 10 MB;
- JPG/PNG: até 8 MB;
- total por proposta: até 50 MB no MVP.

### 3.7 Fluxo de status da proposta

Status recomendados:

1. `lead_aberto`
2. `cadastro_iniciado`
3. `dados_imovel_pendentes`
4. `documentacao_pendente`
5. `documentacao_parcial`
6. `documentacao_concluida`
7. `em_analise`
8. `analise_concluida`
9. `aprovada`
10. `reprovada`
11. `output_calculo_emitido`
12. `contrato_emitido`
13. `contrato_assinado`
14. `pagamento_pendente`
15. `pagamento_recebido`
16. `comissao_pendente`
17. `comissao_paga`
18. `cancelada`
19. `arquivada`

Regras:

- Status só deve avançar se os requisitos mínimos forem atendidos.
- Hermes pode sugerir avanço, mas backend valida.
- Apenas operador interno humano aprova/reprova no MVP.
- Todo avanço de status gera evento em `proposal_status_history` e `audit_events`.

---

## 4. Motor de cálculo/output de fiança

### 4.1 Fonte atual

Já existe um projeto no GitHub:

```text
https://github.com/pballeste/one
```

Esse projeto contém ou explica a lógica de cálculo e geração de output.

### 4.2 Decisão de arquitetura

O backend deve tratar o cálculo como um módulo/serviço separado, para facilitar manutenção e evolução.

Opção recomendada no MVP:

```text
one-api
  services/
    calculation_service.py
  integrations/
    one_calculator/
      adapter.py
      schemas.py
      README.md
```

O Codex deve primeiro inspecionar o repositório `pballeste/one` e identificar:

1. linguagem/framework usado;
2. fórmula de cálculo;
3. inputs obrigatórios;
4. output gerado;
5. se o código pode ser importado como biblioteca;
6. se deve ser reimplementado em Python no backend;
7. se deve ser executado como serviço externo/container separado.

### 4.3 Decisão prática para MVP

Preferência:

1. Reimplementar a lógica de cálculo no backend Python se ela for simples e determinística.
2. Criar testes de equivalência comparando output do backend com o output atual do projeto GitHub.
3. Persistir cada cálculo em tabela própria.
4. Permitir regras configuráveis por tabela, não hardcoded.

### 4.4 Tabelas de cálculo

Criar:

- `pricing_rules`
- `proposal_calculations`

### 4.5 Comissão de 10%

A comissão incide inicialmente sobre o **valor total calculado**, conforme a lógica do app GitHub.

Mas deve ser configurável externamente.

Criar configuração:

```text
commission_base = total_calculated_amount
commission_rate = 10.00
```

Valores possíveis futuros:

```text
total_calculated_amount
gross_paid_amount
net_paid_amount
base_annual_fee
manual_amount
```

---

## 5. Arquitetura de containers

### 5.1 Topologia recomendada

```text
Internet / WhatsApp
        │
        ▼
Hermes WhatsApp Gateway  [container existente ou stack atual]
        │
        │ MCP interno HTTP com token
        ▼
one-mcp
        │
        ▼
one-api / service layer
        │
        ├── PostgreSQL 18: postgresql-1ua2 / db one
        └── Storage local: /srv/one-fianca/documents

Website / Front-end público
        │
        ▼
one-api REST

Operador interno / celular / desktop
        │
        ▼
one-web-admin responsivo
        │
        ▼
one-api REST
```

### 5.2 Containers

#### `postgresql-1ua2`

- Imagem: `postgres:18`
- Banco: `one`
- Usuário admin inicial: `Admin`
- Não expor porta publicamente.
- Rede: `one_backend`
- Volume: `one_postgres_data`

#### `one-api`

- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic v2
- Uvicorn/Gunicorn
- Responsável por REST, validações, regras de negócio, upload/download, autenticação interna, cálculos e auditoria.

#### `one-mcp`

- Python 3.12
- FastMCP / MCP SDK
- Expõe apenas ferramentas de domínio para Hermes.
- Não expõe SQL bruto.
- Rede interna apenas.
- Autenticação via bearer token interno.

#### `one-web-admin`

- React + TypeScript + Vite
- shadcn/ui ou Tailwind + componentes simples
- Mobile-first/responsivo
- Uso interno por operador humano
- Funcionalidades MVP:
  - dashboard de propostas;
  - cadastro de imobiliárias;
  - cadastro de corretores;
  - vínculo corretor-imobiliária;
  - cadastro/edição de dados bancários;
  - cadastro de cliente PF/PJ;
  - cadastro de imóvel;
  - checklist documental;
  - upload web;
  - atualização de status;
  - registro de pagamento/comissão.

#### `one-worker` — fase 2

- Python 3.12
- RQ/Celery/Arq, a decidir.
- Redis se necessário.
- Validação assíncrona de documentos, antivírus, notificações, relatórios.

#### `redis` — fase 2

- Broker/cache para filas e rate limit distribuído.

#### `adminer` ou `pgadmin` — uso restrito

- Apenas via SSH tunnel ou IP allowlist.
- Nunca público sem autenticação forte.

### 5.3 Redes Docker

```yaml
networks:
  one_public:
    driver: bridge
  one_backend:
    driver: bridge
    internal: true
```

- `one-api` pode estar em `one_public` e `one_backend`.
- `one-web-admin` pode estar em `one_public` via reverse proxy.
- `one-mcp` e `postgresql-1ua2` ficam em `one_backend`.
- Postgres nunca deve estar em `one_public`.

---

## 6. Estrutura de repositório Codex-ready

```text
one-fianca-backend/
  AGENTS.md
  README.md
  pyproject.toml
  uv.lock / requirements.txt
  .env.example
  .gitignore
  docker-compose.yml
  docker-compose.prod.yml

  app/
    main.py
    core/
      config.py
      security.py
      crypto.py
      logging.py
      errors.py
      constants.py
    db/
      session.py
      base.py
      models/
        __init__.py
        mixins.py
        users.py
        intake.py
        partners.py
        customers.py
        properties.py
        proposals.py
        calculations.py
        documents.py
        payments.py
        audit.py
      repositories/
    schemas/
      common.py
      intake.py
      partners.py
      customers.py
      properties.py
      proposals.py
      calculations.py
      documents.py
      payments.py
    services/
      intake_service.py
      partner_service.py
      customer_service.py
      proposal_service.py
      calculation_service.py
      document_service.py
      payment_service.py
      checklist_service.py
      audit_service.py
      crypto_service.py
    integrations/
      one_calculator/
        adapter.py
        schemas.py
        README.md
    api/
      v1/
        router.py
        endpoints/
          health.py
          intake.py
          partners.py
          customers.py
          proposals.py
          calculations.py
          documents.py
          payments.py
          admin.py
    mcp/
      server.py
      tools/
        intake_tools.py
        partner_tools.py
        proposal_tools.py
        calculation_tools.py
        document_tools.py
        payment_tools.py
      prompts/
        hermes_system_instructions.md
    storage/
      local_storage.py
      validators.py
    workers/
      jobs.py

  web-admin/
    package.json
    src/
      app/
      components/
      pages/
      lib/
      hooks/

  alembic/
    env.py
    script.py.mako
    versions/

  scripts/
    bootstrap_db.sql
    create_roles.sql
    backup_db.sh
    backup_documents.sh
    restore_db.sh
    check_health.sh

  tests/
    conftest.py
    unit/
    integration/
    e2e/

  docs/
    PRD.md
    ARCHITECTURE.md
    DATA_MODEL.md
    API_CONTRACTS.md
    MCP_TOOLS.md
    SECURITY_LGPD.md
    DEPLOYMENT.md
    BACKUP_RESTORE.md
    RETENTION_POLICY.md
```

---

## 7. AGENTS.md para Codex/Cursor/Windsurf/Claude Code

Criar `AGENTS.md` na raiz:

```markdown
# AGENTS.md — One Fiança Backend

## Project context
This repository implements the backend for One Fiança Locatícia, a Brazilian financial guarantor for rental contracts. The system handles personal, financial, banking, document, contract and commission-related data. Treat all code as security-sensitive and LGPD-relevant.

## Architecture
- Python 3.12
- FastAPI for REST APIs
- FastMCP/Python MCP SDK for Hermes integration
- PostgreSQL 18 as canonical database
- Alembic for migrations
- SQLAlchemy 2.x ORM
- Pydantic v2 for schemas/validation
- Local filesystem storage for documents in MVP
- Responsive internal web admin for operators
- No direct SQL exposure to Hermes
- No community skills for sensitive business logic

## Coding rules
- Do not hardcode secrets.
- Do not expose raw database credentials.
- Never implement a generic execute_sql tool.
- All writes must go through service-layer methods.
- All sensitive field updates must create audit_events.
- Use typed Pydantic schemas for all inputs and outputs.
- Use repository/service separation.
- Keep business rules out of route handlers.
- Validate CPF/CNPJ server-side.
- Validate upload extension, MIME type, signature and size.
- Store uploaded files outside the webroot.
- Store document metadata in Postgres, not binary blobs.
- Implement pricing/calculation rules as configurable data, not hardcoded constants.
- Preserve compatibility with mobile-first operator UX.

## Required commands
- Run tests: `pytest`
- Run formatting: `ruff format .`
- Run linting: `ruff check .`
- Run type checks: `mypy app`
- Run migrations: `alembic upgrade head`

## Database
- Use PostgreSQL 18.
- Prefer `uuidv7()` for primary IDs if available.
- Use timestamptz for all timestamps.
- Use `numeric(12,2)` for monetary values.
- Use check constraints and enum-like varchar fields for controlled status values.
- Do not use floats for currency.

## Security
- Use least privilege roles.
- Use separate roles for migrations and app runtime.
- Use encrypted fields for CPF/CNPJ, PIX, bank account and sensitive recoverable data.
- Use hashes for lookup/deduplication of sensitive identifiers.
- Log metadata, not raw sensitive values.

## PR discipline
- Include migrations for schema changes.
- Include tests for service-layer business rules.
- Update docs when API contracts change.
```

---

## 8. Modelo de dados — visão conceitual

### 8.1 Entidades principais

```text
User / Internal Operator
Consent
Intake Session
Intake Message
Lead
Agency
Broker
Agency-Broker Link
Partner Bank Account
Customer
Customer PF Detail
Customer PJ Detail
Property
Proposal
Pricing Rule
Proposal Calculation
Proposal Participant
Proposal Checklist Item
Document
Document Version
Proposal Status History
Commission
Payment Event
Audit Event
```

### 8.2 Relações principais

```text
Agency 1 → N Brokers, via broker_agency_links
Agency 1 → N Proposals, quando originadora/responsável
Broker 1 → N Proposals, quando originador/responsável
Customer 1 → N Proposals
Property 1 → N Proposals
Proposal 1 → N Documents
Proposal 1 → N Checklist Items
Proposal 1 → N Calculations
Proposal 1 → N Status History
Partner 1 → N Bank Accounts
Proposal 0/1 → 1 Commission
```

### 8.3 Proposta como entidade central

A `proposal` conecta:

- quem quer alugar;
- qual imóvel;
- quem indicou ou conduz;
- quais documentos faltam;
- qual valor será analisado;
- qual cálculo/output foi gerado;
- qual status operacional;
- se contrato foi emitido;
- se pagamento foi recebido;
- se comissão foi paga.

---

## 9. Modelo lógico de banco — tabelas

### 9.1 Extensões

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

Se PostgreSQL 18:

```sql
-- Usar uuidv7() nativo como default.
```

### 9.2 Função padrão de ID

Para PostgreSQL 18:

```sql
id UUID PRIMARY KEY DEFAULT uuidv7()
```

Fallback compatível:

```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
```

### 9.3 Convenções

Todas as tabelas principais devem ter:

```sql
created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
deleted_at TIMESTAMPTZ NULL
```

Preferir soft delete para dados operacionais e jurídicos.

---

## 10. DDL inicial recomendado — versão compacta

> Este DDL é uma base inicial para Alembic. O Codex deve converter em migrations e modelos SQLAlchemy.

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE audit_events (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  actor_type VARCHAR(30) NOT NULL,
  actor_id UUID,
  action VARCHAR(80) NOT NULL,
  entity_type VARCHAR(80) NOT NULL,
  entity_id UUID,
  before_data JSONB,
  after_data JSONB,
  metadata JSONB,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_entity ON audit_events(entity_type, entity_id);
CREATE INDEX idx_audit_created_at ON audit_events(created_at DESC);

CREATE TABLE consents (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  subject_type VARCHAR(30) NOT NULL,
  subject_id UUID,
  channel VARCHAR(30) NOT NULL,
  consent_type VARCHAR(50) NOT NULL,
  consent_text_version VARCHAR(50) NOT NULL,
  accepted BOOLEAN NOT NULL,
  accepted_at TIMESTAMPTZ,
  source_ip INET,
  user_agent TEXT,
  raw_evidence JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE intake_sessions (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  channel VARCHAR(30) NOT NULL CHECK (channel IN ('web','whatsapp','operator','api')),
  external_session_id VARCHAR(200),
  whatsapp_sender_id VARCHAR(100),
  whatsapp_phone_e164 VARCHAR(30),
  whatsapp_display_name VARCHAR(200),
  current_intent VARCHAR(80),
  status VARCHAR(40) NOT NULL DEFAULT 'open',
  raw_context JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  closed_at TIMESTAMPTZ
);

CREATE INDEX idx_intake_whatsapp ON intake_sessions(whatsapp_phone_e164);
CREATE INDEX idx_intake_status ON intake_sessions(status);

CREATE TABLE intake_messages (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  intake_session_id UUID NOT NULL REFERENCES intake_sessions(id) ON DELETE CASCADE,
  direction VARCHAR(20) NOT NULL CHECK (direction IN ('inbound','outbound','internal')),
  sender_type VARCHAR(30),
  message_text TEXT,
  raw_payload JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE leads (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  intake_session_id UUID REFERENCES intake_sessions(id) ON DELETE SET NULL,
  lead_type VARCHAR(30) NOT NULL CHECK (lead_type IN ('agency','broker','quote_pf','quote_pj','unknown')),
  status VARCHAR(40) NOT NULL DEFAULT 'new',
  priority VARCHAR(20) NOT NULL DEFAULT 'medium',
  email VARCHAR(200),
  whatsapp VARCHAR(30),
  city VARCHAR(120),
  state CHAR(2),
  utm_source VARCHAR(100),
  utm_medium VARCHAR(100),
  utm_campaign VARCHAR(100),
  utm_content VARCHAR(200),
  utm_term VARCHAR(200),
  source_url TEXT,
  user_agent TEXT,
  ip_address INET,
  raw_payload JSONB,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_leads_type_status ON leads(lead_type, status);
CREATE INDEX idx_leads_whatsapp ON leads(whatsapp);
CREATE INDEX idx_leads_email ON leads(email);

CREATE TABLE agencies (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
  legal_name VARCHAR(220),
  trade_name VARCHAR(220) NOT NULL,
  cnpj_hash CHAR(64),
  cnpj_encrypted TEXT,
  email VARCHAR(200),
  whatsapp VARCHAR(30),
  phone VARCHAR(30),
  website VARCHAR(300),
  instagram VARCHAR(100),
  address_line TEXT,
  city VARCHAR(120),
  state CHAR(2),
  operating_cities JSONB,
  monthly_rentals_range VARCHAR(30),
  partnership_status VARCHAR(40) NOT NULL DEFAULT 'pending',
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_agencies_cnpj_hash ON agencies(cnpj_hash);
CREATE INDEX idx_agencies_status ON agencies(partnership_status);

CREATE TABLE agency_contacts (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  agency_id UUID NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
  full_name VARCHAR(200) NOT NULL,
  role_title VARCHAR(100),
  email VARCHAR(200),
  whatsapp VARCHAR(30),
  is_primary BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE brokers (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
  full_name VARCHAR(220) NOT NULL,
  cpf_hash CHAR(64),
  cpf_encrypted TEXT,
  creci VARCHAR(30),
  email VARCHAR(200),
  whatsapp VARCHAR(30),
  city VARCHAR(120),
  state CHAR(2),
  professional_profile VARCHAR(300),
  broker_type VARCHAR(40) NOT NULL DEFAULT 'autonomo',
  partnership_status VARCHAR(40) NOT NULL DEFAULT 'pending',
  referral_volume_range VARCHAR(30),
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_brokers_cpf_hash ON brokers(cpf_hash);
CREATE INDEX idx_brokers_status ON brokers(partnership_status);

CREATE TABLE broker_agency_links (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  broker_id UUID NOT NULL REFERENCES brokers(id) ON DELETE CASCADE,
  agency_id UUID NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
  link_status VARCHAR(30) NOT NULL DEFAULT 'active',
  is_primary BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  ended_at TIMESTAMPTZ,
  UNIQUE (broker_id, agency_id)
);

CREATE TABLE partner_bank_accounts (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  partner_type VARCHAR(20) NOT NULL CHECK (partner_type IN ('agency','broker')),
  partner_id UUID NOT NULL,
  holder_name VARCHAR(220) NOT NULL,
  holder_document_hash CHAR(64),
  holder_document_encrypted TEXT,
  bank_code VARCHAR(10),
  bank_name VARCHAR(120),
  branch_number_encrypted TEXT,
  branch_digit VARCHAR(5),
  account_number_hash CHAR(64),
  account_number_encrypted TEXT,
  account_digit VARCHAR(5),
  account_type VARCHAR(30) CHECK (account_type IN ('corrente','poupanca','pagamento')),
  pix_key_type VARCHAR(20) CHECK (pix_key_type IN ('cpf','cnpj','email','phone','random')),
  pix_key_hash CHAR(64),
  pix_key_encrypted TEXT,
  is_primary BOOLEAN NOT NULL DEFAULT true,
  status VARCHAR(30) NOT NULL DEFAULT 'pending_verification',
  verified_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_bank_partner ON partner_bank_accounts(partner_type, partner_id);
CREATE INDEX idx_bank_pix_hash ON partner_bank_accounts(pix_key_hash);

CREATE TABLE customers (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  customer_type VARCHAR(2) NOT NULL CHECK (customer_type IN ('pf','pj')),
  display_name VARCHAR(220) NOT NULL,
  email VARCHAR(200),
  whatsapp VARCHAR(30),
  city VARCHAR(120),
  state CHAR(2),
  status VARCHAR(30) NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE TABLE customer_pf_details (
  customer_id UUID PRIMARY KEY REFERENCES customers(id) ON DELETE CASCADE,
  full_name VARCHAR(220) NOT NULL,
  cpf_hash CHAR(64),
  cpf_encrypted TEXT,
  identity_document_type VARCHAR(30),
  identity_document_number_hash CHAR(64),
  identity_document_number_encrypted TEXT,
  profession VARCHAR(120),
  declared_monthly_income NUMERIC(12,2),
  income_proof_type VARCHAR(80)
);

CREATE TABLE customer_pj_details (
  customer_id UUID PRIMARY KEY REFERENCES customers(id) ON DELETE CASCADE,
  legal_name VARCHAR(220) NOT NULL,
  trade_name VARCHAR(220),
  cnpj_hash CHAR(64),
  cnpj_encrypted TEXT,
  responsible_name VARCHAR(220),
  responsible_role VARCHAR(120),
  declared_monthly_revenue NUMERIC(12,2),
  income_proof_type VARCHAR(80)
);

CREATE TABLE properties (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  property_type VARCHAR(40) NOT NULL CHECK (property_type IN ('residencial','comercial','industrial','logistico','outro')),
  rental_purpose VARCHAR(80),
  postal_code VARCHAR(12) NOT NULL,
  street VARCHAR(220) NOT NULL,
  number VARCHAR(30) NOT NULL,
  complement VARCHAR(120),
  district VARCHAR(120) NOT NULL,
  city VARCHAR(120) NOT NULL,
  state CHAR(2) NOT NULL,
  full_address TEXT,
  monthly_rent NUMERIC(12,2) NOT NULL,
  condominium_amount NUMERIC(12,2),
  iptu_amount NUMERIC(12,2),
  trash_fee_amount NUMERIC(12,2),
  other_fee_amount NUMERIC(12,2),
  total_monthly_financial_obligation NUMERIC(12,2),
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_properties_postal_code ON properties(postal_code);
CREATE INDEX idx_properties_city_state ON properties(city, state);

CREATE TABLE proposals (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
  intake_session_id UUID REFERENCES intake_sessions(id) ON DELETE SET NULL,
  customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
  property_id UUID REFERENCES properties(id) ON DELETE SET NULL,
  origin_partner_type VARCHAR(20) CHECK (origin_partner_type IN ('agency','broker','direct','unknown')),
  origin_partner_id UUID,
  responsible_partner_type VARCHAR(20) CHECK (responsible_partner_type IN ('agency','broker','one','unknown')),
  responsible_partner_id UUID,
  proposal_type VARCHAR(2) NOT NULL CHECK (proposal_type IN ('pf','pj')),
  status VARCHAR(50) NOT NULL DEFAULT 'lead_aberto',
  priority VARCHAR(20) NOT NULL DEFAULT 'medium',
  expected_start_date DATE,
  contract_months INTEGER DEFAULT 12,
  annual_fee_amount NUMERIC(12,2),
  payment_plan VARCHAR(40),
  total_calculated_amount NUMERIC(12,2),
  commission_base_type VARCHAR(60) DEFAULT 'total_calculated_amount',
  commission_rate NUMERIC(5,2) DEFAULT 10.00,
  commission_amount NUMERIC(12,2),
  analysis_result VARCHAR(30),
  rejection_reason TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  closed_at TIMESTAMPTZ,
  deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_proposals_status ON proposals(status);
CREATE INDEX idx_proposals_customer ON proposals(customer_id);
CREATE INDEX idx_proposals_property ON proposals(property_id);
CREATE INDEX idx_proposals_partner ON proposals(origin_partner_type, origin_partner_id);

CREATE TABLE pricing_rules (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  rule_key VARCHAR(100) NOT NULL UNIQUE,
  description TEXT,
  rule_config JSONB NOT NULL,
  active BOOLEAN NOT NULL DEFAULT true,
  valid_from TIMESTAMPTZ NOT NULL DEFAULT now(),
  valid_to TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE proposal_calculations (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  proposal_id UUID NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
  pricing_rule_id UUID REFERENCES pricing_rules(id) ON DELETE SET NULL,
  input_payload JSONB NOT NULL,
  output_payload JSONB NOT NULL,
  annual_fee_amount NUMERIC(12,2),
  total_calculated_amount NUMERIC(12,2),
  payment_plan VARCHAR(40),
  source VARCHAR(40) NOT NULL DEFAULT 'one_calculator',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_calculations_proposal ON proposal_calculations(proposal_id);

CREATE TABLE proposal_status_history (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  proposal_id UUID NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
  old_status VARCHAR(50),
  new_status VARCHAR(50) NOT NULL,
  changed_by_type VARCHAR(30) NOT NULL,
  changed_by_id UUID,
  reason TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE proposal_checklist_items (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  proposal_id UUID NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
  requirement_code VARCHAR(80) NOT NULL,
  requirement_label VARCHAR(200) NOT NULL,
  requirement_type VARCHAR(40) NOT NULL CHECK (requirement_type IN ('data','document','approval','payment')),
  status VARCHAR(30) NOT NULL DEFAULT 'pending',
  document_id UUID,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (proposal_id, requirement_code)
);

CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  owner_type VARCHAR(40) NOT NULL CHECK (owner_type IN ('lead','agency','broker','customer','property','proposal','contract','bank_account')),
  owner_id UUID NOT NULL,
  proposal_id UUID REFERENCES proposals(id) ON DELETE SET NULL,
  document_type VARCHAR(80) NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'uploaded',
  storage_driver VARCHAR(30) NOT NULL DEFAULT 'local_fs',
  storage_path TEXT NOT NULL,
  original_file_name VARCHAR(300) NOT NULL,
  stored_file_name VARCHAR(300) NOT NULL,
  mime_type VARCHAR(100) NOT NULL,
  extension VARCHAR(10) NOT NULL,
  size_bytes BIGINT NOT NULL,
  sha256_hash CHAR(64) NOT NULL,
  version INTEGER NOT NULL DEFAULT 1,
  uploaded_by_type VARCHAR(30),
  uploaded_by_id UUID,
  validated_by UUID,
  validated_at TIMESTAMPTZ,
  rejection_reason TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_documents_owner ON documents(owner_type, owner_id);
CREATE INDEX idx_documents_proposal ON documents(proposal_id);
CREATE INDEX idx_documents_hash ON documents(sha256_hash);

CREATE TABLE secure_upload_links (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  proposal_id UUID REFERENCES proposals(id) ON DELETE CASCADE,
  token_hash CHAR(64) NOT NULL UNIQUE,
  allowed_document_types JSONB,
  expires_at TIMESTAMPTZ NOT NULL,
  max_uploads INTEGER DEFAULT 5,
  uploads_count INTEGER DEFAULT 0,
  status VARCHAR(30) NOT NULL DEFAULT 'active',
  created_by_type VARCHAR(30),
  created_by_id UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  used_at TIMESTAMPTZ
);

CREATE TABLE commissions (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  proposal_id UUID NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
  partner_type VARCHAR(20) NOT NULL CHECK (partner_type IN ('agency','broker')),
  partner_id UUID NOT NULL,
  commission_base_type VARCHAR(60) NOT NULL DEFAULT 'total_calculated_amount',
  commission_base_amount NUMERIC(12,2) NOT NULL,
  commission_rate NUMERIC(5,2) NOT NULL DEFAULT 10.00,
  commission_amount NUMERIC(12,2) NOT NULL,
  status VARCHAR(40) NOT NULL DEFAULT 'pending',
  due_at TIMESTAMPTZ,
  paid_at TIMESTAMPTZ,
  bank_account_id UUID,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_commissions_partner ON commissions(partner_type, partner_id);
CREATE INDEX idx_commissions_status ON commissions(status);

CREATE TABLE payment_events (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  proposal_id UUID REFERENCES proposals(id) ON DELETE SET NULL,
  commission_id UUID REFERENCES commissions(id) ON DELETE SET NULL,
  event_type VARCHAR(60) NOT NULL,
  amount NUMERIC(12,2),
  payment_method VARCHAR(40),
  status VARCHAR(40),
  external_reference VARCHAR(200),
  raw_payload JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 11. Regras de checklist documental

### 11.1 PF

Ao criar proposal `proposal_type='pf'`, criar checklist:

```text
- property_complete: dados completos do imóvel, incluindo CEP obrigatório
- identity_document: RG/CNH/documento de identidade
- income_proof: holerite/carta do contador/comprovante equivalente
- privacy_consent: aceite LGPD
```

### 11.2 PJ

Ao criar proposal `proposal_type='pj'`, criar checklist:

```text
- property_complete: dados completos do imóvel, incluindo CEP obrigatório
- company_contract: contrato social
- income_or_revenue_proof: carta do contador/declaração equivalente
- privacy_consent: aceite LGPD
```

### 11.3 Avanço automático de status

```text
Se dados mínimos do imóvel faltam:
  status = dados_imovel_pendentes

Se todos os dados mínimos existem e documentos obrigatórios ausentes:
  status = documentacao_pendente

Se parte dos documentos existe:
  status = documentacao_parcial

Se todos os documentos obrigatórios existem:
  status = documentacao_concluida

Se operador inicia análise:
  status = em_analise

Se análise terminada:
  status = analise_concluida

Se aprovado:
  status = aprovada

Se reprovado:
  status = reprovada

Se cálculo/output gerado:
  status = output_calculo_emitido

Se contrato gerado:
  status = contrato_emitido

Se contrato assinado:
  status = contrato_assinado

Se pagamento recebido:
  status = pagamento_recebido
  criar comissão pendente, se houver parceiro comissionável

Se comissão paga:
  comissão.status = paid
  proposal.status pode avançar para comissao_paga
```

---

## 12. APIs REST

### 12.1 Health

```http
GET /v1/health
GET /v1/health/db
```

### 12.2 Intake web

```http
POST /v1/intake/web/agencies
POST /v1/intake/web/brokers
POST /v1/intake/web/quotes
```

### 12.3 Intake WhatsApp/Hermes interno

```http
POST /v1/intake/whatsapp/session
POST /v1/intake/whatsapp/message
GET  /v1/intake/whatsapp/search?phone=...
```

### 12.4 Parceiros

```http
POST   /v1/agencies
GET    /v1/agencies
GET    /v1/agencies/{agency_id}
PATCH  /v1/agencies/{agency_id}

POST   /v1/brokers
GET    /v1/brokers
GET    /v1/brokers/{broker_id}
PATCH  /v1/brokers/{broker_id}

POST   /v1/agencies/{agency_id}/brokers/{broker_id}
DELETE /v1/agencies/{agency_id}/brokers/{broker_id}
```

### 12.5 Dados bancários

```http
POST  /v1/partners/{partner_type}/{partner_id}/bank-accounts
GET   /v1/partners/{partner_type}/{partner_id}/bank-accounts
PATCH /v1/bank-accounts/{bank_account_id}
```

### 12.6 Clientes

```http
POST   /v1/customers
GET    /v1/customers
GET    /v1/customers/{customer_id}
PATCH  /v1/customers/{customer_id}
```

### 12.7 Imóveis

```http
POST   /v1/properties
GET    /v1/properties
GET    /v1/properties/{property_id}
PATCH  /v1/properties/{property_id}
```

### 12.8 Propostas

```http
POST  /v1/proposals
GET   /v1/proposals
GET   /v1/proposals/{proposal_id}
PATCH /v1/proposals/{proposal_id}
POST  /v1/proposals/{proposal_id}/status
GET   /v1/proposals/{proposal_id}/checklist
POST  /v1/proposals/{proposal_id}/checklist/recompute
POST  /v1/proposals/{proposal_id}/calculate
GET   /v1/proposals/{proposal_id}/calculations
```

### 12.9 Documentos

```http
POST /v1/upload-links
GET  /upload/{token}
POST /upload/{token}

POST /v1/documents/upload
GET  /v1/documents/{document_id}
GET  /v1/documents/{document_id}/download
POST /v1/documents/{document_id}/validate
POST /v1/documents/{document_id}/reject
DELETE /v1/documents/{document_id}
```

### 12.10 Comissões e pagamentos

```http
GET  /v1/commissions
GET  /v1/commissions/{commission_id}
POST /v1/commissions/{commission_id}/mark-paid
POST /v1/payment-events
```

### 12.11 Auditoria

```http
GET /v1/audit/{entity_type}/{entity_id}
```

---

## 13. Ferramentas MCP para Hermes

O Hermes deve usar ferramentas de domínio, não banco direto.

### 13.1 Tools obrigatórias MVP

```text
search_by_whatsapp(phone_or_sender_id)
get_or_create_intake_session(channel, whatsapp_sender_id, phone, display_name)
append_intake_message(session_id, direction, message_text, raw_payload)
create_or_update_agency(session_id, data)
create_or_update_broker(session_id, data)
create_or_update_customer(session_id, data)
create_or_update_property(session_id, data)
create_or_update_proposal(session_id, data)
get_proposal_checklist(proposal_id)
list_missing_fields(session_id or proposal_id)
generate_secure_upload_link(proposal_id, allowed_document_types)
register_document_request(proposal_id, document_type)
register_bank_account(partner_type, partner_id, data)
calculate_proposal(proposal_id)
get_latest_calculation(proposal_id)
advance_proposal_status(proposal_id, target_status, reason)
append_internal_note(entity_type, entity_id, note)
```

### 13.2 Tools proibidas

```text
execute_sql
query_database
raw_update
delete_record
download_document_without_auth
list_all_customers
list_all_bank_accounts
```

### 13.3 Comportamento esperado do Hermes

Hermes deve:

1. Identificar o canal e telefone/WhatsApp do usuário.
2. Criar/recuperar sessão de intake.
3. Entender intenção: imobiliária, corretor, cotação PF/PJ, documento, comissão, dúvida.
4. Chamar backend para descobrir campos faltantes.
5. Fazer perguntas uma a uma.
6. Salvar cada resposta via MCP.
7. Gerar link seguro de upload quando necessário.
8. Nunca inventar status ou aprovação.
9. Nunca aprovar/reprovar no MVP.
10. Nunca prometer aprovação garantida.
11. Usar linguagem institucional segura.
12. Transferir para humano quando houver dúvida jurídica, documento inválido, pagamento, reprovação ou exceção.

---

## 14. Storage de documentos

### 14.1 Layout local

```text
/srv/one-fianca/documents/
  proposals/
    <proposal_id>/
      identity_document/
      income_proof/
      company_contract/
      property_documents/
  partners/
    agencies/
      <agency_id>/
        bank/
    brokers/
      <broker_id>/
        bank/
  contracts/
    <proposal_id>/
```

### 14.2 Nome físico do arquivo

Nunca usar nome original como filename físico.

```text
<document_id>_v<version>.<extension>
```

Exemplo:

```text
019535d9-3df7-79fb-b466-fa907fa17f9e_v1.pdf
```

### 14.3 Segurança de upload

Obrigatório:

- allowlist de extensões;
- validação de MIME;
- validação de assinatura/magic bytes;
- limite de tamanho;
- renomear arquivo;
- armazenar fora do webroot;
- hash SHA-256;
- log de upload;
- download via endpoint autenticado;
- bloquear path traversal;
- bloquear dupla extensão;
- futura varredura ClamAV.

---

## 15. Segurança, LGPD e privacidade

### 15.1 Classificação dos dados

Dados pessoais:

- nome;
- CPF;
- RG/CNH;
- WhatsApp;
- e-mail;
- endereço;
- documentos;
- renda.

Dados empresariais sensíveis:

- CNPJ;
- contrato social;
- faturamento/renda PJ;
- responsáveis;
- dados bancários.

Dados financeiros de alto risco:

- banco;
- agência;
- conta;
- PIX;
- titular;
- comissão.

### 15.2 Tratamento

- CPF/CNPJ/PIX/conta: hash + criptografia.
- Documentos: storage protegido + metadados + hash.
- Logs: nunca registrar valores sensíveis completos.
- Banco: sem porta pública.
- Admin: uso interno apenas.

### 15.3 Consentimentos

Separar:

- aceite obrigatório de privacidade/tratamento para cadastro, contato, análise, proposta e atendimento;
- opt-in opcional de marketing.

### 15.4 Retenção sugerida MVP

Proposta convertida/contrato emitido:

- manter dados e documentos durante vigência + 5 anos, sujeito a revisão jurídica.

Lead sem conversão:

- manter por 180 dias;
- depois anonimizar documentos e dados sensíveis ou arquivar conforme decisão comercial.

Proposta reprovada:

- manter por 180 dias;
- depois anonimizar/excluir documentos, salvo necessidade jurídica.

Dados bancários de parceiro ativo:

- manter enquanto parceria ativa;
- manter histórico de conta anterior por 5 anos ou conforme orientação contábil/jurídica.

Fase 2:

- criar rotina de expurgo/anonimização;
- tela de solicitação LGPD;
- relatório de dados do titular.

---

## 16. Autenticação e autorização

### MVP interno

- API key interna para chamadas servidor-servidor.
- Token Bearer para `one-mcp`.
- Login simples/JWT para painel interno.
- Papéis internos iniciais:
  - admin;
  - operador;
  - financeiro;
  - somente leitura.
- IP allowlist ou VPN/SSH tunnel para admin DB.

### Fase 2

- RBAC mais completo:
  - admin;
  - operador;
  - analista;
  - financeiro;
  - jurídico;
  - somente leitura.

### Fase 3

- portal para parceiros;
- RLS ou service-layer tenant isolation por imobiliária/corretor.

---

## 17. Backups e restore

### 17.1 Banco

Script diário:

```bash
pg_dump -Fc -d one -f /srv/one-fianca/backups/db/one_$(date +%Y%m%d_%H%M%S).dump
```

Retenção sugerida:

- diário: 14 dias;
- semanal: 8 semanas;
- mensal: 12 meses.

### 17.2 Documentos

```bash
rsync -a --delete /srv/one-fianca/documents/ /srv/one-fianca/backups/documents/current/
```

Opcional:

- criptografar backup com age/gpg;
- copiar backup para storage externo criptografado.

### 17.3 Teste de restore

Mensal:

1. Subir Postgres temporário.
2. Restaurar dump.
3. Validar contagem de tabelas.
4. Validar documentos por hash.
5. Registrar teste em log.

---

## 18. Observabilidade

### MVP

- logs JSON no `one-api` e `one-mcp`;
- request ID por requisição;
- audit_events para ações de negócio;
- healthchecks Docker;
- endpoint `/v1/health`.

### Fase 2

- Prometheus/Grafana ou Uptime Kuma;
- alertas de erro;
- métricas de proposta por status;
- documentos pendentes;
- tempo médio até aprovação;
- comissão pendente.

---

## 19. Front-end operacional responsivo

### 19.1 Objetivo

Criar uma interface interna simples, responsiva e mobile-first para operador humano.

### 19.2 Funcionalidades MVP

1. Login interno.
2. Dashboard de propostas por status.
3. Busca por nome, CPF/CNPJ hash, telefone, e-mail, imobiliária, corretor e proposta.
4. Cadastro/edição de imobiliária.
5. Cadastro/edição de corretor.
6. Vínculo corretor-imobiliária.
7. Cadastro/edição de dados bancários.
8. Criação/edição de cliente PF/PJ.
9. Criação/edição de imóvel com CEP obrigatório.
10. Criação/edição de proposta.
11. Geração de cálculo/output.
12. Geração de link seguro para upload.
13. Checklist documental.
14. Aprovação/reprovação manual.
15. Registro de pagamento recebido.
16. Registro de comissão paga.
17. Timeline/auditoria da proposta.

### 19.3 Páginas sugeridas

```text
/login
/dashboard
/propostas
/propostas/:id
/imobiliarias
/imobiliarias/:id
/corretores
/corretores/:id
/clientes/:id
/imoveis/:id
/comissoes
/upload/:token
```

---

## 20. Testes

### Unit tests

- validação CPF/CNPJ;
- normalização telefone;
- cálculo de checklist;
- transição de status;
- cálculo de comissão;
- cálculo/output da fiança;
- criptografia/hash;
- validação de arquivo.

### Integration tests

- criação de imobiliária;
- criação de corretor autônomo;
- vínculo corretor-imobiliária;
- criação de cliente PF/PJ;
- criação de imóvel com CEP obrigatório;
- criação de proposta;
- cálculo de proposta;
- checklist PF/PJ;
- link seguro de upload;
- upload de documento;
- avanço de status.

### Security tests

- arquivo com extensão falsa;
- arquivo grande demais;
- path traversal;
- tentativa de download sem autorização;
- tentativa de MCP tool proibida.

---

## 21. Fases de implementação

### Fase 0 — Infra e base

- Confirmar/recriar Postgres 18.
- Criar roles.
- Criar repositório.
- Criar AGENTS.md.
- Criar docker-compose.
- Criar FastAPI skeleton.
- Criar Alembic.
- Criar healthchecks.

### Fase 1 — Core operacional

- Tabelas: intake, leads, agencies, brokers, customers, properties, proposals.
- CEP obrigatório em imóvel.
- Endpoints REST principais.
- Checklist PF/PJ.
- Status da proposta.
- Auditoria.
- Front-end interno responsivo básico.
- Testes.

### Fase 2 — Cálculo, documentos e dados bancários

- Integrar/reimplementar cálculo do projeto `pballeste/one`.
- Persistir outputs em `proposal_calculations`.
- Storage local.
- Link seguro de upload.
- Upload/download protegido.
- Document metadata.
- Dados bancários com hash/criptografia.
- Comissões configuráveis.
- Validações OWASP.
- Geração de contrato PDF, se aprovada.

### Fase 3 — Hermes MCP e pagamentos

- Criar `one-mcp`.
- Criar tools MVP.
- Configurar Hermes para chamar MCP interno.
- Testar fluxo WhatsApp: corretor → cliente → imóvel → proposta.
- Testar fluxo WhatsApp: imobiliária → corretor → cliente → proposta.
- Integração bancária/PIX futura para comissão.
- Upload via WhatsApp, se aprovado.

### Fase 4 — Painel interno avançado

- Listagem avançada de propostas.
- Filtros por status.
- Checklist visual.
- Validação de documentos.
- Status manual.
- Comissões pendentes.
- Métricas operacionais.

### Fase 5 — Automação avançada

- OCR.
- antifraude documental;
- validação externa CPF/CNPJ;
- geração automática de proposta/contrato PDF;
- assinatura eletrônica;
- conciliação de pagamento;
- portal parceiro.

---

## 22. Prompt inicial para Codex

```markdown
Você está trabalhando no projeto `one-fianca-backend`.

Objetivo: implementar o backend da One Fiança Locatícia seguindo a PRD e arquitetura neste repositório.

Comece criando o scaffold Python/FastAPI com SQLAlchemy 2.x, Alembic, Pydantic v2, estrutura modular, docker-compose, .env.example e AGENTS.md.

Banco alvo: PostgreSQL 18, database `one`, container existente `postgresql-1ua2`.

Implemente primeiro:
1. configuração do projeto;
2. conexão DB;
3. healthcheck;
4. migrations iniciais para audit_events, consents, intake_sessions, intake_messages, leads, agencies, agency_contacts, brokers, broker_agency_links, customers, customer_pf_details, customer_pj_details, properties, proposals, pricing_rules, proposal_calculations, proposal_status_history, proposal_checklist_items, documents, secure_upload_links, partner_bank_accounts, commissions e payment_events;
5. endpoints REST mínimos para criar imobiliária, corretor, cliente, imóvel e proposta;
6. service layer com validações;
7. front-end interno responsivo inicial;
8. testes unitários e de integração básicos.

Regras críticas:
- não expor SQL genérico;
- não armazenar arquivos binários no Postgres;
- não logar CPF/CNPJ/PIX/conta em claro;
- usar hash + criptografia para dados sensíveis recuperáveis;
- toda alteração sensível deve criar audit_event;
- usar migrations Alembic;
- manter compatibilidade com Docker;
- imóvel exige CEP obrigatório;
- aprovação/reprovação no MVP é humana;
- cálculo/output de fiança deve ser integrado a partir do projeto `https://github.com/pballeste/one` ou reimplementado com testes de equivalência;
- comissão padrão de 10% deve incidir sobre `total_calculated_amount`, mas com regra configurável em tabela.
```

---

## 23. Perguntas futuras — não bloqueiam Fase 0/Fase 1

1. Qual é a fórmula final e versionada de cálculo após inspeção do projeto `pballeste/one`?
2. O output de cálculo terá layout HTML/PDF ou apenas JSON no MVP?
3. Qual será o domínio/subdomínio do front-end interno?
4. Quais usuários internos terão acesso inicial?
5. Qual política final jurídica de retenção será aprovada?
6. Quais textos finais de política de privacidade e termos serão validados juridicamente?
7. Qual gateway ou meio será usado na fase 3 para pagamento/comissão?

---

## 24. Recomendação final

O desenho recomendado é:

```text
Hermes = conversa e coleta
one-mcp = ferramentas semânticas controladas
one-api = regras de negócio, REST, validação, auditoria, cálculo e storage
one-web-admin = operação humana responsiva/mobile-first
PostgreSQL 18 = fonte canônica de dados
filesystem local = documentos protegidos
```

Esse desenho é simples o suficiente para iniciar rápido na VPS atual, mas robusto o suficiente para crescer para portal interno, portal de parceiros, automação documental, geração de proposta, assinatura e conciliação de pagamentos.

---

## 25. Configuração de ambiente — `.env.example`

### 25.1 Regra principal

O projeto deve ter um `.env.example` versionado no Git, mas o arquivo real `.env` nunca deve ser commitado.

Dados sensíveis, como senhas, chaves de criptografia, tokens, SMTP, API keys, service tokens, credenciais de banco e tokens internos devem ficar apenas no `.env` real da VPS ou, idealmente, em Docker secrets.

Credenciais SSH da VPS/root **não devem** ficar no `.env` da aplicação. Elas pertencem ao plano operacional de acesso, não à configuração runtime do sistema.

### 25.2 `.env.example` recomendado

```dotenv
# ============================================================
# ONE FIANÇA LOCATÍCIA — BACKEND ENVIRONMENT
# File: .env.example
# Copy to .env and fill values on the VPS.
# NEVER commit the real .env.
# ============================================================

# ------------------------------------------------------------
# Application
# ------------------------------------------------------------
APP_NAME=one-fianca-backend
APP_ENV=production
APP_DEBUG=false
APP_TIMEZONE=America/Sao_Paulo
APP_BASE_URL=https://api.onefiancalocaticia.com.br
APP_PUBLIC_WEB_URL=https://onefiancalocaticia.com.br
APP_ADMIN_WEB_URL=https://admin.onefiancalocaticia.com.br
APP_VERSION=1.0.0

# Comma-separated list. Avoid '*' in production.
CORS_ALLOWED_ORIGINS=https://onefiancalocaticia.com.br,https://admin.onefiancalocaticia.com.br
TRUSTED_HOSTS=api.onefiancalocaticia.com.br,admin.onefiancalocaticia.com.br,onefiancalocaticia.com.br

# ------------------------------------------------------------
# PostgreSQL canonical database
# Existing container: postgresql-1ua2
# Recommended image/version: postgres:18
# ------------------------------------------------------------
POSTGRES_CONTAINER_NAME=postgresql-1ua2
POSTGRES_HOST=postgresql-1ua2
POSTGRES_PORT=5432
POSTGRES_DB=one
POSTGRES_USER=Admin
POSTGRES_PASSWORD=CHANGE_ME
POSTGRES_SSLMODE=disable

# Runtime app DB user — recommended after bootstrap.
# The app should not run forever as Admin/superuser.
APP_DB_USER=one_app
APP_DB_PASSWORD=CHANGE_ME
APP_DATABASE_URL=postgresql+psycopg://one_app:CHANGE_ME@postgresql-1ua2:5432/one

# Migration DB user — can have elevated privileges for Alembic.
MIGRATION_DB_USER=one_migrator
MIGRATION_DB_PASSWORD=CHANGE_ME
MIGRATION_DATABASE_URL=postgresql+psycopg://one_migrator:CHANGE_ME@postgresql-1ua2:5432/one

# ------------------------------------------------------------
# API server
# ------------------------------------------------------------
ONE_API_HOST=0.0.0.0
ONE_API_PORT=8000
ONE_API_WORKERS=2
ONE_API_LOG_LEVEL=info
ONE_API_INTERNAL_TOKEN=CHANGE_ME_LONG_RANDOM_TOKEN

# ------------------------------------------------------------
# MCP server for Hermes
# ------------------------------------------------------------
ONE_MCP_HOST=0.0.0.0
ONE_MCP_PORT=8100
ONE_MCP_BASE_URL=http://one-mcp:8100
ONE_MCP_TRANSPORT=http
ONE_MCP_AUTH_TOKEN=CHANGE_ME_LONG_RANDOM_TOKEN
ONE_MCP_ALLOWED_CLIENTS=hermes

# If Hermes calls MCP through an internal Docker network, prefer internal URL.
HERMES_MCP_SERVER_URL=http://one-mcp:8100/mcp
HERMES_MCP_SERVER_NAME=one-fianca-mcp

# ------------------------------------------------------------
# Hermes / WhatsApp bridge metadata
# These values are for integration config/reference, not for storing WhatsApp secrets.
# ------------------------------------------------------------
HERMES_PROFILE=one-fianca
HERMES_CHANNEL=whatsapp
HERMES_DEFAULT_LANGUAGE=pt-BR
HERMES_HANDOFF_PHONE=+5511970309686
HERMES_HANDOFF_EMAIL=proposta@onefiancalocaticia.com.br

# ------------------------------------------------------------
# Front-end admin
# ------------------------------------------------------------
ADMIN_WEB_PORT=3000
ADMIN_WEB_API_BASE_URL=https://api.onefiancalocaticia.com.br/v1
ADMIN_SESSION_SECRET=CHANGE_ME_LONG_RANDOM_SECRET
ADMIN_JWT_SECRET=CHANGE_ME_LONG_RANDOM_SECRET
ADMIN_JWT_EXPIRES_MINUTES=720

# Initial bootstrap admin user. Disable after first setup.
BOOTSTRAP_ADMIN_EMAIL=admin@example.com
BOOTSTRAP_ADMIN_PASSWORD=CHANGE_ME
BOOTSTRAP_ADMIN_FULL_NAME=One Admin

# ------------------------------------------------------------
# Security / cryptography
# ------------------------------------------------------------
# Generate with: openssl rand -base64 32
APP_SECRET_KEY=CHANGE_ME_BASE64_32_BYTES

# Used for hashes of CPF/CNPJ/PIX/bank fields. Do not rotate casually.
PII_HASH_PEPPER=CHANGE_ME_LONG_RANDOM_PEPPER

# Used for field-level encryption. Prefer Fernet/base64 32-byte key or app-defined key management.
FIELD_ENCRYPTION_KEY=CHANGE_ME_BASE64_32_BYTES

# Optional key identifier for future rotation.
FIELD_ENCRYPTION_KEY_ID=v1

# ------------------------------------------------------------
# LGPD / privacy
# ------------------------------------------------------------
PRIVACY_EMAIL=privacidade@onefiancalocaticia.com.br
PRIVACY_POLICY_URL=https://onefiancalocaticia.com.br/politica-de-privacidade
TERMS_OF_USE_URL=https://onefiancalocaticia.com.br/termos-de-uso
CONSENT_TEXT_VERSION=2026-05-v1
MARKETING_OPT_IN_TEXT_VERSION=2026-05-v1

# ------------------------------------------------------------
# Documents / upload storage
# ------------------------------------------------------------
STORAGE_DRIVER=local_fs
DOCUMENTS_STORAGE_ROOT=/app/storage/documents
DOCUMENTS_PUBLIC_ACCESS=false
DOCUMENTS_MAX_FILE_SIZE_MB=10
DOCUMENTS_MAX_TOTAL_PER_PROPOSAL_MB=50
DOCUMENTS_ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png
DOCUMENTS_ALLOWED_MIME_TYPES=application/pdf,image/jpeg,image/png
DOCUMENTS_REQUIRE_MAGIC_BYTES_VALIDATION=true
DOCUMENTS_HASH_ALGORITHM=sha256

# Secure upload links
UPLOAD_LINK_BASE_URL=https://api.onefiancalocaticia.com.br/upload
UPLOAD_LINK_TTL_HOURS=72
UPLOAD_LINK_MAX_UPLOADS=5
UPLOAD_LINK_TOKEN_BYTES=32

# Optional future malware scan
ENABLE_FILE_ANTIVIRUS_SCAN=false
CLAMAV_HOST=clamav
CLAMAV_PORT=3310

# ------------------------------------------------------------
# Pricing / calculation
# Existing calculator repo: https://github.com/pballeste/one
# ------------------------------------------------------------
CALCULATION_ENGINE=internal_python
CALCULATION_RULE_KEY=default_2026_v1
CALCULATION_SOURCE_REPO=https://github.com/pballeste/one
DEFAULT_CONTRACT_MONTHS=12
DEFAULT_COMMISSION_RATE=10.00
DEFAULT_COMMISSION_BASE_TYPE=total_calculated_amount

# ------------------------------------------------------------
# Notifications
# ------------------------------------------------------------
NOTIFICATIONS_ENABLED=false
NOTIFICATION_TO_EMAIL=proposta@onefiancalocaticia.com.br
NOTIFICATION_FROM_EMAIL=no-reply@onefiancalocaticia.com.br

# SMTP — fill only if email notifications are enabled.
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=true

# ------------------------------------------------------------
# Rate limiting / anti-spam
# ------------------------------------------------------------
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PUBLIC_FORMS_PER_HOUR=5
RATE_LIMIT_UPLOADS_PER_HOUR=20
HONEYPOT_FIELD_NAME=website_url
RECAPTCHA_ENABLED=false
RECAPTCHA_SECRET_KEY=

# ------------------------------------------------------------
# Logging / observability
# ------------------------------------------------------------
LOG_FORMAT=json
LOG_LEVEL=info
REQUEST_ID_HEADER=X-Request-ID
ENABLE_ACCESS_LOG=true
SENTRY_DSN=

# ------------------------------------------------------------
# Backup paths
# ------------------------------------------------------------
BACKUP_ROOT=/app/storage/backups
BACKUP_RETENTION_DAILY=14
BACKUP_RETENTION_WEEKLY=8
BACKUP_RETENTION_MONTHLY=12
BACKUP_ENCRYPTION_ENABLED=false
BACKUP_ENCRYPTION_PUBLIC_KEY=

# ------------------------------------------------------------
# Optional future external object storage — disabled in MVP
# ------------------------------------------------------------
S3_ENABLED=false
S3_ENDPOINT_URL=
S3_REGION=
S3_BUCKET=
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=
S3_FORCE_PATH_STYLE=true
```

### 25.3 Variáveis que não devem estar no `.env` da aplicação

Não colocar no `.env` do backend:

```dotenv
VPS_ROOT_PASSWORD=...
SSH_PRIVATE_KEY=...
HOSTINGER_PANEL_PASSWORD=...
GITHUB_PERSONAL_ACCESS_TOKEN=...
```

Esses dados devem ficar em:

- gerenciador de senhas;
- chave SSH local protegida;
- variável temporária do ambiente de CI/CD;
- Docker secret, se realmente precisar em runtime.

---

## 26. Configuração operacional opcional — `ops.env.example`

Este arquivo é apenas para o operador humano/automação local. Não deve ser montado nos containers e não deve ser commitado com valores reais.

```dotenv
# ============================================================
# OPS ENV — DO NOT MOUNT INTO APPLICATION CONTAINERS
# Used only by local deployment scripts from a secure machine.
# ============================================================

VPS_HOST=YOUR_SERVER_IP_OR_HOSTNAME
VPS_SSH_PORT=22
VPS_SSH_USER=root
VPS_PROJECT_DIR=/opt/one-fianca-backend
VPS_DATA_DIR=/srv/one-fianca

# Prefer SSH key auth. Do not store root password here.
VPS_SSH_KEY_PATH=~/.ssh/one_fianca_vps

# Existing Postgres container
POSTGRES_CONTAINER_NAME=postgresql-1ua2
POSTGRES_DB=one
POSTGRES_ADMIN_USER=Admin

# Optional deployment settings
DEPLOY_BRANCH=main
DOCKER_COMPOSE_FILE=docker-compose.prod.yml
```

---

## 27. Docker Compose target architecture

A PRD já endereça que teremos novos containers para backend e integração:

```text
one-api       = novo container FastAPI
one-mcp       = novo container MCP/FastMCP para Hermes
one-web-admin = novo container front-end responsivo interno
one-worker    = fase 2 para jobs assíncronos
postgresql-1ua2 = container Postgres existente/recriado em Postgres 18
```

### 27.1 `docker-compose.prod.yml` base

```yaml
services:
  one-api:
    build:
      context: .
      dockerfile: Dockerfile.api
    container_name: one-api
    env_file:
      - ./.env
    depends_on:
      - postgresql-1ua2
    volumes:
      - /srv/one-fianca/documents:/app/storage/documents
      - /srv/one-fianca/backups:/app/storage/backups
      - /srv/one-fianca/logs:/app/logs
    networks:
      - one_public
      - one_backend
    restart: unless-stopped
    ports:
      - "8000:8000"

  one-mcp:
    build:
      context: .
      dockerfile: Dockerfile.mcp
    container_name: one-mcp
    env_file:
      - ./.env
    depends_on:
      - one-api
    networks:
      - one_backend
    restart: unless-stopped
    expose:
      - "8100"

  one-web-admin:
    build:
      context: ./web-admin
      dockerfile: Dockerfile
    container_name: one-web-admin
    env_file:
      - ./.env
    depends_on:
      - one-api
    networks:
      - one_public
    restart: unless-stopped
    ports:
      - "3000:3000"

  postgresql-1ua2:
    image: postgres:18
    container_name: postgresql-1ua2
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      TZ: ${APP_TIMEZONE}
    volumes:
      - one_postgres_data:/var/lib/postgresql/data
    networks:
      - one_backend
    restart: unless-stopped
    expose:
      - "5432"

volumes:
  one_postgres_data:

networks:
  one_public:
    driver: bridge
  one_backend:
    driver: bridge
    internal: true
```

### 27.2 Observação sobre Postgres existente

Se o container `postgresql-1ua2` já existe com dados, as variáveis `POSTGRES_DB`, `POSTGRES_USER` e `POSTGRES_PASSWORD` da imagem oficial só inicializam banco/usuário na primeira criação do volume vazio. Se o volume já foi inicializado, mudanças nessas variáveis não recriam banco, usuário ou senha automaticamente.

Portanto, antes de conectar o backend, executar:

```bash
docker exec -it postgresql-1ua2 psql -U Admin -d one -c "SELECT version();"
```

Se não for PostgreSQL 18 e ainda não houver dados importantes, recriar o container/volume com `postgres:18`.

---

## 28. Checklist inicial antes do Codex começar

1. Confirmar versão do Postgres:

```bash
docker exec -it postgresql-1ua2 psql -U Admin -d one -c "SELECT version();"
```

2. Criar diretórios no host:

```bash
sudo mkdir -p /srv/one-fianca/documents /srv/one-fianca/backups /srv/one-fianca/logs
sudo chmod -R 750 /srv/one-fianca
```

3. Gerar chaves:

```bash
openssl rand -base64 32   # APP_SECRET_KEY
openssl rand -base64 32   # FIELD_ENCRYPTION_KEY
openssl rand -base64 48   # PII_HASH_PEPPER
openssl rand -hex 32      # ONE_API_INTERNAL_TOKEN
openssl rand -hex 32      # ONE_MCP_AUTH_TOKEN
openssl rand -base64 32   # ADMIN_JWT_SECRET
```

4. Criar `.env` a partir de `.env.example`.
5. Não colocar senha SSH/root no `.env`.
6. Subir primeiro `one-api` + Postgres.
7. Rodar migrations.
8. Só depois subir `one-mcp` e `one-web-admin`.

