# Arquitetura recomendada do backend One Fiança com Hermes

## Síntese executiva

A melhor arquitetura para o seu cenário é esta: manter o banco canônico no container de urlPostgreSQLturn4search22 já existente, criar um backend Python separado para regras de negócio e APIs, e conectar o Hermes a esse backend por uma superfície controlada de MCP, em vez de deixar o agente falar SQL diretamente. Em outras palavras: **Hermes vira a interface conversacional**, **o backend vira a camada de domínio e validação**, e **o Postgres vira a fonte única da verdade**. Essa separação é exatamente a que melhor combina com o suporte nativo do urlHermes Agentturn24search10 a MCP, com filtros finos por servidor/ferramenta e com o modelo de segurança recomendado pelo próprio urlModel Context Protocolturn19view4 para dados específicos de usuário e operações auditáveis. citeturn17view0turn18view1turn20view3turn19view2

Também é a arquitetura que mais respeita o que aparece nos seus rascunhos: o relacionamento central gira em torno de **imobiliária**, **corretor**, **cliente**, **imóvel** e **proposta/análise**, com ordem de coleta variável na conversa; por isso, a modelagem não pode assumir que os dados chegam sempre completos e na mesma sequência. O desenho correto é ter uma **camada de intake flexível** para capturar fragmentos vindos do WhatsApp e dos formulários, e uma **camada canônica normalizada** para o CRM, propostas, documentos e pagamentos. Isso está alinhado com os dois arquivos enviados, que já apontam tanto para formulários de lead quanto para uma estrutura operacional em que a proposta conecta cliente, imóvel e parceiro responsável. fileciteturn0file0 fileciteturn0file1

Minha recomendação final, portanto, é:

- **Usar o container Postgres atual como banco principal**, mas com papéis dedicados de aplicação, migração e leitura; não usar `Admin` no runtime.
- **Criar um serviço `one-api` em Python** para REST interno/externo.
- **Criar um serviço `one-mcp` em Python** com poucas ferramentas MCP, estritamente whitelistadas, para o Hermes.
- **Guardar metadados no Postgres e arquivos fora das tabelas principais**, em volume local do VPS ou em storage de objetos auto-hospedado no mesmo VPS.
- **Não depender de skills comunitárias de terceiros** para esse domínio sensível; faça um MCP próprio e, no máximo, use o skill oficial `fastmcp` apenas como apoio de desenvolvimento. citeturn15view3turn17view1turn27view2turn15view1turn13news36turn13search13

## Arquitetura-alvo

O papel do urlHermes Agentturn24search10 no seu projeto deve ser o de **canal conversacional e orquestrador**. A própria documentação mostra que o Hermes já tem bridge nativa para WhatsApp via Baileys, mas que essa integração é **não oficial**, com risco operacional e necessidade de atualização/repareamento quando o protocolo do WhatsApp Web muda; por isso, a sua arquitetura tem de assumir que o canal pode oscilar e que o estado relevante do negócio deve ficar fora do Hermes. citeturn15view4

Outro ponto importante: o Hermes já persiste **seu próprio estado interno** em um SQLite `~/.hermes/state.db`, com histórico de mensagens, FTS e metadados de sessão. Isso é útil para memória do agente, mas **não substitui** o banco de negócio. O banco do negócio, no seu caso, precisa ser o Postgres `one`, porque ele vai armazenar entidades transacionais, documentos, trilhas de auditoria, pagamentos e integrações operacionais. citeturn15view5

A arquitetura recomendada fica assim:

```text
WhatsApp
   │
   ▼
Hermes (já existente)
   │
   │  MCP HTTP interno (ou stdio se estiver no mesmo namespace)
   ▼
one-mcp  ───────► camada de serviços Python ◄─────── one-api
   │                                               │
   │                                               ├── formulários web
   │                                               ├── painel operacional
   │                                               └── webhooks futuros
   ▼
PostgreSQL "one" (container existente)
   │
   ├── dados estruturados
   ├── auditoria
   └── metadados de arquivos

Armazenamento de documentos no mesmo VPS
   ├── volume local fora do webroot
   └── opcionalmente storage de objetos compatível com S3
```

Para Docker, eu recomendo duas redes lógicas: uma `frontend` para o que deve receber tráfego HTTP externo, e uma `backend` privada para `one-api`, `one-mcp` e o Postgres. A documentação do urlDocker Composeturn5search20 mostra exatamente esse padrão: serviços isolados por redes diferentes, em que apenas a aplicação fala com o banco. Também vale usar `depends_on` e healthchecks para ordenação de subida, volumes nomeados para persistência e secrets do Compose para credenciais em vez de espalhar senhas em variáveis de ambiente. citeturn30view1turn30view2turn30view3turn30view0turn30view7

Há ainda uma correção importante sobre o seu container atual `postgresql-1ua2`: se ele já foi inicializado com volume persistente, **mudar `POSTGRES_PASSWORD` depois no `.env` não reconfigura automaticamente o banco**. A imagem oficial do urlPostgres no Docker Hubturn11search0 deixa claro que essas variáveis só fazem efeito quando o diretório de dados está vazio. Então, se você vai “colocar a senha depois”, isso significa ou **alterar a role por SQL**, ou **recriar o banco a partir de um volume vazio**. citeturn30view6

## PRD do produto

O produto que emerge dos seus rascunhos não é apenas um “capturador de leads”. Ele é, na prática, um **motor de intake e gestão operacional de fiança locatícia** com quatro capacidades centrais:

1. captar dados por formulário e por conversa no WhatsApp;
2. montar e enriquecer cadastros de imobiliárias, corretores, clientes e imóveis;
3. criar, acompanhar e completar propostas/análises de fiança;
4. receber, organizar e validar documentos e dados bancários para pagamento. fileciteturn0file0 fileciteturn0file1

O objetivo do MVP não deve ser “ter um banco”, mas sim **ter um backend que controle o fluxo de coleta, completude, validação e status**. O Hermes deve perguntar o próximo campo faltante, mas **quem decide o que está faltando, o que é válido e em que status a proposta está** deve ser o backend. Essa distinção é crucial para evitar que regras críticas fiquem apenas no prompt do agente.

As personas naturais do sistema são:

- a imobiliária cadastrada, com responsáveis e corretores vinculados;
- o corretor autônomo, com seus próprios clientes e imóveis;
- o cliente final PF ou PJ;
- o operador interno que revisa, qualifica, complementa e converte. fileciteturn0file0 fileciteturn0file1

O fluxo principal recomendado é este:

- o contato entra por formulário ou WhatsApp;
- o backend cria um **registro de intake** e uma **sessão de coleta**;
- o Hermes consulta o backend para saber o próximo campo faltante;
- o backend vai materializando ou atualizando a **proposta rascunho**;
- quando houver dados mínimos, o backend cria ou vincula **parceiro**, **cliente**, **imóvel** e **proposta**;
- documentos e dados bancários passam a ser itens controlados da proposta;
- o operador interno ou regras automáticas movem a proposta pelos estados.  

Esse desenho conversa bem com o que o rascunho técnico dos formulários já sugere para os leads e com o que o rascunho relacional exige para o domínio operacional. fileciteturn0file0 fileciteturn0file1

## Modelo de dados e armazenamento

A recomendação mais importante aqui é separar o banco em **duas camadas de dados**.

A primeira camada é **intake**: ela recebe dados incompletos, parciais e fora de ordem. Isso é especialmente importante porque seus fluxos por WhatsApp podem começar com o cliente, com o imóvel, com o corretor ou com a proposta; o seu próprio rascunho relacional diz que a ordem pode variar. Para essa camada, faz sentido usar tabelas de intake e colunas `jsonb` para guardar fragmentos e payloads originais, já que o urlPostgreSQLturn4search22 trata `jsonb` de forma mais eficiente que `json` para processamento e consulta. citeturn31view2 fileciteturn0file0

A segunda camada é a **camada canônica**: nela ficam as entidades do negócio já normalizadas. É aqui que vivem parceiros, clientes, imóveis, propostas, documentos, contas bancárias e auditoria. Essa separação evita dois erros comuns: forçar a conversa do WhatsApp a caber diretamente na tabela final e transformar as tabelas de lead do front na modelagem definitiva do produto.

Eu estruturaria o domínio assim:

**Camada de intake**
- `intake_sessions`
- `intake_messages`
- `intake_entities_snapshot`
- `intake_web_leads`
- `intake_raw_payloads`
- `intake_links`

**Camada canônica**
- `agencies`
- `agency_contacts`
- `brokers`
- `broker_agency_links`
- `customers`
- `customer_contacts`
- `properties`
- `proposals`
- `proposal_participants`
- `proposal_requirements`
- `documents`
- `document_versions`
- `partner_bank_accounts`
- `payment_recipients`
- `audit_events`

O centro do modelo deve ser a tabela `proposals`. Ela precisa apontar, no mínimo, para:
- um **applicant/customer**;
- um **property**;
- um **origin/responsible partner**, que pode ser imobiliária ou corretor;
- uma **origem de intake**;
- um **estado operacional**. fileciteturn0file0

Eu **não** recomendaria uma abstração excessivamente genérica do tipo “party para tudo” no MVP, porque isso aumenta muito o custo de implementação. O desenho mais pragmático é usar tabelas explícitas para `agencies`, `brokers`, `customers` e `properties`, com ligações claras e históricas.

Sobre identificadores, a melhor escolha é UUID. Se o seu container já estiver em Postgres 18, você pode usar `uuidv7()` nativo; se não estiver, `gen_random_uuid()` continua sendo uma base sólida e compatível. citeturn31view3turn31view4

### Dados bancários

Para imobiliárias e corretores, eu criaria uma tabela `partner_bank_accounts` separada, porque:
- um mesmo parceiro pode trocar de conta;
- você pode precisar manter histórico;
- a conta de pagamento não deve poluir a tabela principal do parceiro;
- você provavelmente vai querer um conceito de “conta ativa”.  

Estrutura recomendada:

```text
partner_bank_accounts
- id
- partner_type            -- agency | broker
- partner_id
- holder_name
- holder_document
- bank_code
- bank_name
- branch_number
- branch_digit
- account_number
- account_digit
- account_type            -- corrente | poupanca | pagamento | pj
- pix_key_type            -- cpf | cnpj | email | phone | random
- pix_key
- is_primary
- verified_at
- active
- created_at
- updated_at
```

Como esses campos são muito sensíveis do ponto de vista operacional e de fraude, eu recomendo **criptografia de campo** com chave fora do banco para valores como `pix_key`, `account_number` e `branch_number`, mantendo hashes separados quando for necessário busca exata. O urlPostgreSQLturn4search22 oferece `pgcrypto`, mas a prática mais limpa é deixar a chave mestra fora do banco e fazer envelope encryption na aplicação; se você quiser manter parte da lógica no banco, o `pgcrypto` existe e suporta funções criptográficas e PGP. citeturn31view0

### Documentos, PDFs e imagens

Tecnicamente, o Postgres consegue armazenar binários em `bytea` e também suporta Large Objects. Então a resposta curta é: **sim, você pode guardar PDFs, JPG e PNG no Postgres**. Mas a resposta arquitetural correta, para o seu cenário, é: **não é a melhor estratégia padrão**. O banco deve guardar os **metadados**; os arquivos devem ficar em um storage local fora das tabelas principais. citeturn32search0turn32search1turn32search12turn32search20

O motivo é que você terá documentos de identidade, comprovantes de renda, contrato social e possivelmente muitos anexos por proposta. O guia da urlOWASPturn36view0 recomenda validar extensão, MIME e assinatura, renomear arquivos, impor limites de tamanho, armazenar fora do webroot e, quando possível, passar por antivírus. A própria comunidade técnica costuma apontar que jogar binários dentro do banco simplifica transação, mas aumenta o tamanho do banco e piora backup/restore; em especial, threads de comunidade sobre PostgreSQL destacam esse trade-off de forma consistente. citeturn36view0turn36view1turn33view0turn33view1turn33view2

Minha recomendação é a seguinte:

- **MVP simples:** volume local no mesmo VPS, por exemplo `/srv/one/documents`, montado no container do backend.
- **Produção mais robusta:** storage de objetos compatível com S3 no mesmo VPS, em container próprio, para facilitar versionamento, multipart upload e URLs temporárias; isso continua local ao seu ambiente e não te empurra para um terceiro. citeturn34search4turn34search5

A tabela `documents` deveria registrar apenas:

```text
documents
- id
- proposal_id
- owner_type              -- customer | agency | broker
- owner_id
- document_type           -- rg, cnh, comprovante_renda, contrato_social, etc
- storage_driver          -- local_fs | s3_local
- object_key
- original_filename
- mime_type
- size_bytes
- sha256
- status                  -- pending | uploaded | validated | rejected | expired
- uploaded_by             -- hermes | web | operator
- uploaded_at
- validated_at
- rejection_reason
```

Para os seus requisitos atuais, o checklist mínimo por tipo de proposta deve nascer no backend:

- **PF:** documento de identidade, comprovante de renda e dados completos do imóvel.
- **PJ:** contrato social, comprovantes de renda/faturamento e dados completos do imóvel.
- **Qualquer contrato/proposta:** endereço e características do imóvel, valor do aluguel e metadados da negociação.  

Isso é coerente com as suas mensagens e com o rascunho do formulário de cotação, que já traz endereço, cidade, estado e `valor_aluguel`. fileciteturn0file1

## Integração do Hermes e superfície MCP

A documentação do urlHermes Agentturn24search10 é bastante clara: ele suporta servidores MCP tanto por `stdio` quanto por HTTP, faz descoberta automática de ferramentas, permite `include`/`exclude` por servidor e ainda registra recursos e prompts quando o servidor expõe essas capacidades. O próprio guia de uso recomenda usar MCP justamente quando você quer ligar o Hermes a APIs, bancos ou sistemas internos sem modificar o core do agente — mas enfatiza que o bom uso é conectar **o menor conjunto útil de ferramentas**. citeturn17view0turn17view1turn18view1

No seu caso, eu recomendo o seguinte:

- **Em desenvolvimento local ou se MCP e Hermes estiverem no mesmo processo/namespace:** `stdio` é levemente mais seguro.
- **No seu deploy em Docker com separação clara de serviços:** **HTTP MCP interno** é o melhor compromisso operacional.

O próprio MCP diz que os dois transportes padrão são `stdio` e Streamable HTTP, e recomenda `stdio` quando possível. Mas também diz que, quando o servidor acessa dados específicos do usuário, auditoria e rate limiting, autorização passa a ser fortemente recomendada — exatamente o seu caso. citeturn19view2turn20view3

Por isso, para containers separados, a minha recomendação é:

```yaml
mcp_servers:
  one_backend:
    url: "http://one-mcp:8001/mcp"
    headers:
      Authorization: "Bearer ${ONE_MCP_TOKEN}"
    tools:
      include:
        - get_or_create_intake_session
        - upsert_partner
        - upsert_customer
        - upsert_property
        - create_or_update_proposal
        - list_missing_fields
        - register_document_metadata
        - register_bank_account
        - search_by_whatsapp
        - get_checklist_for_proposal
      prompts: false
      resources: true
```

O ponto importante não é a sintaxe em si, e sim o princípio: **não exponha uma ferramenta “executar SQL”**. Exponha ferramentas estreitas e semânticas. O backend deve ser o dono das validações, deduplicação, merges e status.

As ferramentas MCP que eu realmente criaria são poucas:

- `search_by_whatsapp`
- `get_or_create_intake_session`
- `upsert_partner`
- `upsert_customer`
- `upsert_property`
- `create_or_update_proposal`
- `list_missing_fields`
- `register_document_metadata`
- `register_bank_account`
- `get_checklist_for_proposal`
- `append_conversation_note`

Esse desenho usa o MCP como ele deveria ser usado: **camada RPC de domínio**, e não acesso bruto ao banco. citeturn19view3turn17view1turn18view1

### Skills confiáveis

Para esse projeto, o que vale aproveitar é muito pouco:

- o skill oficial `fastmcp` do Hermes é útil **para desenvolver e testar o seu MCP server**;
- o runtime do Hermes já tem suporte MCP nativo, então você não precisa depender de skill comunitária para fazer o backend conversar com o agente. citeturn15view3turn17view0

Eu **não recomendo** usar skills da comunidade do urlOpenClawturn14view9 ou do urlClawHubturn25view1 para cadastro, documentos, pagamentos ou qualquer operação de negócio sensível. A própria documentação diz que o ClawHub é aberto por padrão, que qualquer pessoa pode publicar skills, e que a moderação existe, mas é essencialmente reativa; além disso, o modelo de segurança do OpenClaw assume um boundary de confiança por gateway, não um ambiente multiusuário adversarial. Reportagens e auditorias comunitárias recentes reforçaram o risco de skills maliciosas. Para o seu domínio, o correto é **skill própria**, **código auditado** e **allowlist explícita**. citeturn27view2turn15view1turn26view0turn13news36turn13search5turn13search13

## Segurança, LGPD e operação

A urlANPDturn8search1 publica material específico de segurança da informação para agentes de tratamento de pequeno porte e também regulamenta transferência internacional de dados pela Resolução 19/2024. A sua preferência por manter tudo dentro do VPS reduz complexidade operacional e de soberania de dados; isso **não garante** conformidade por si só, mas ajuda muito no controle de acesso, inventário de dados e fluxo internacional. citeturn9search0turn8search2turn8search10

Pela LGPD, dado pessoal é informação relacionada a pessoa natural identificada ou identificável; dado pessoal sensível tem definição legal mais restrita. Então, estritamente falando, dados bancários não entram automaticamente na categoria legal de “dado pessoal sensível” só por serem bancários. Ainda assim, no seu contexto eles devem ser tratados como **dados de alto risco operacional**, porque viabilizam fraude, desvio e engenharia social. Documentos como RG, CNH e comprovantes também exigem camada forte de proteção, e alguns podem carregar elementos biométricos ou fotografia que ampliam o risco. citeturn38search1turn8search0

Os controles que eu considero obrigatórios no seu desenho são estes:

- autenticação de banco com `scram-sha-256`, nunca MD5; o próprio urlPostgreSQLturn4search22 considera SCRAM o método mais seguro entre os baseados em senha e já sinaliza a depreciação do MD5; citeturn31view5turn31view6
- `Docker secrets` para segredos de banco e tokens internos, não `.env` espalhado por todos os serviços; citeturn30view0
- redes Docker isoladas, com o banco sem porta pública;
- contas de banco separadas: `one_admin`, `one_migrator`, `one_app`, `one_readonly`;
- trilha de auditoria obrigatória para qualquer criação/edição/exclusão de parceiro, proposta, documento e conta bancária;
- storage de documentos fora do webroot, com validação OWASP, hash SHA-256, limite de tamanho, nome gerado pela aplicação e antivírus; citeturn36view0turn36view1
- retenção mínima necessária e política de exclusão/arquivamento;
- autorização por serviço e, se você vier a ter portal multiusuário com escopo por imobiliária/corretor, considerar RLS no Postgres; o comportamento default-deny do RLS quando habilitado sem policy é útil para cenários de segregação forte. citeturn31view1

No lado operacional do banco, mantenha autovacuum ligado. A documentação do urlPostgreSQLturn4search22 é explícita em dizer que a estratégia saudável é deixar o autovacuum manter o banco em steady state, em vez de depender de `VACUUM FULL` esporádico. citeturn31view7

Para backup, a política correta é dupla:
- backup lógico ou físico do Postgres;
- backup do volume ou object storage de documentos.  

Se você optar por filesystem local para documentos, os backups do banco e dos arquivos precisam acontecer muito próximos no tempo, porque senão você pode restaurar o banco para um ponto em que metadados e arquivos já não batem. Essa é uma preocupação clássica citada pela comunidade técnica quando se separa binário do banco. citeturn30view5turn33view0

## Plano de implementação para o Codex

O pacote de desenvolvimento que eu mandaria para o Codex é este.

### Estrutura de repositório

```text
one-backend/
  app/
    core/
      config.py
      security.py
      logging.py
    db/
      base.py
      session.py
      models/
    modules/
      intake/
      crm/
      proposals/
      documents/
      payments/
      audit/
      hermes/
    api/
      v1/
    mcp/
      server.py
      tools/
      resources/
    workers/
      tasks.py
    storage/
      local_fs.py
      s3_local.py
  alembic/
  tests/
  docker/
    api.Dockerfile
    mcp.Dockerfile
    worker.Dockerfile
  compose/
    docker-compose.yml
  scripts/
    bootstrap_roles.sql
    init_extensions.sql
```

### Containers

**MVP mínimo**
- `postgresql-1ua2` — banco `one`
- `one-api` — REST
- `one-mcp` — MCP para Hermes

**Produção recomendada**
- `postgresql-1ua2`
- `one-api`
- `one-mcp`
- `one-worker`
- `redis` ou broker equivalente, caso você queira fila robusta para processamento pesado
- storage de documentos no mesmo VPS, por volume local ou serviço de objetos auto-hospedado

A justificativa para o worker é simples: o urlFastAPIturn35view0 tem `BackgroundTasks`, o que atende muito bem tarefas simples pós-resposta, inclusive processamento lento de arquivo; mas, quando você começar a lidar com retries, reprocessamento, concorrência, validações demoradas e jobs independentes do request, um task queue como urlCeleryturn23search2 passa a fazer sentido. citeturn35view2turn35view4turn35view5

### Componentes de software

O `one-api` deve expor:
- endpoints dos formulários web;
- endpoints de painel operacional;
- upload/download controlado de documentos;
- consultas de proposta, checklist, pendências, histórico e auditoria.

O `one-mcp` deve expor:
- apenas as ferramentas semânticas usadas pelo Hermes;
- recursos para checklists e prompts operacionais;
- autenticação interna por token;
- logs de tool call em `audit_events`.

O `one-worker` deve cuidar de:
- validação de upload;
- antivírus;
- geração de miniaturas/PDF derivados se necessário;
- notificações;
- conciliações futuras.

### Endpoints REST prioritários

Eu faria só o que o negócio realmente precisa no MVP:

```text
POST   /v1/intake/web/imobiliarias
POST   /v1/intake/web/corretores
POST   /v1/intake/web/cotacoes
POST   /v1/documents/upload
GET    /v1/proposals/{id}
PATCH  /v1/proposals/{id}
GET    /v1/proposals/{id}/checklist
POST   /v1/partners/{type}/{id}/bank-accounts
GET    /v1/search?whatsapp=...
GET    /v1/audit/{entity}/{id}
```

### Banco e migrações

Use urlAlembicturn35view3 desde o início, no mesmo ambiente Python da aplicação, com extensões criadas por migration (`pgcrypto`, e eventualmente outras). A documentação do Alembic é clara ao tratar o ambiente de migrations como parte fixa do projeto, e isso é exatamente o que você quer para o Codex gerar scaffold corretamente. citeturn35view3

### Ordem de implementação

A ordem que faz mais sentido é:

1. bootstrap do Postgres e criação de roles;
2. migrations da camada de intake;
3. migrations da camada canônica;
4. `one-api` com intake web;
5. `one-mcp` com 5 ou 6 ferramentas essenciais;
6. Hermes apontando para o MCP interno;
7. documentos;
8. contas bancárias;
9. worker e assíncronos;
10. painel operacional.

## Questões em aberto e limitações

Ainda há algumas decisões que precisam ser fechadas antes de congelar o schema definitivo.

A primeira é **a versão exata do Postgres** do container atual. Se ele já estiver em 18, você pode usar `uuidv7()` nativo; se não estiver, melhor ficar em `gen_random_uuid()` por compatibilidade. citeturn31view3turn31view4

A segunda é **a escolha do storage de documentos**. A recomendação principal continua sendo “fora das tabelas principais”, mas você ainda precisa decidir se quer começar com bind mount simples ou já entrar em storage de objetos local.

A terceira é **o escopo do painel operacional**. Se haverá apenas uso interno, service-layer auth provavelmente basta. Se você pretende ter escopo por imobiliária, corretor ou equipe, vale desenhar autorização mais forte e talvez RLS.

A quarta é **o nível de automação sobre documentos**. O que está muito claro hoje é a necessidade de armazenar, checklistar e versionar; OCR, extração automática, antifraude documental e validação cadastral podem entrar depois.

A quinta é **a política de retenção e descarte**. Como você vai guardar identidade, renda, contrato social e dados bancários, isso precisa ser decidido como regra de negócio e compliance, não só de engenharia. citeturn9search0turn8search2turn38search1

Minha recomendação final, sem ambiguidade, é esta: **parta do Postgres `one` como banco canônico, crie `one-api` + `one-mcp` em Python, mantenha o Hermes apenas como interface conversacional, use storage de arquivos no mesmo VPS mas fora das tabelas principais, e evite completamente skills comunitárias não auditadas para este domínio**. Isso é o que melhor equilibra segurança, flexibilidade conversacional, velocidade de implementação e capacidade de crescimento do projeto. citeturn17view1turn18view1turn15view5turn36view0turn27view2turn15view1