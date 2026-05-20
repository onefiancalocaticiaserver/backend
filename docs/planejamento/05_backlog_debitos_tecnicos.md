# Backlog e Debitos Tecnicos

Gerado em: 2026-05-20

## Backlog funcional

- Clientes PF/PJ.
- Imoveis.
- Leads de cotacao.
- Propostas.
- Checklist documental.
- Upload de documentos.
- Dados bancarios/PIX.
- Calculo de fianca.
- Comissoes.
- Pagamentos.
- Dashboard operacional.
- Notificacoes.
- Portal de parceiros.
- Contrato PDF.
- Assinatura eletronica.
- OCR e antifraude.

## Backlog de integracao

- Configuracao final Hermes/MCP.
- Definir se Hermes roda na mesma VPS e mesma rede Docker.
- Frontend publico do site consumindo APIs `public`.
- Admin web interno.
- Reverse proxy/TLS.
- Backup externo criptografado.

## Debitos tecnicos conhecidos

- Repositorio remoto ainda pode ficar publico por decisao temporaria; revisar antes de expor detalhes operacionais sensiveis.
- PAT colado em conversa deve ser revogado/rotacionado fora do projeto.
- Chave SSH da VPS foi criada localmente, mas ainda nao instalada porque a senha root informada foi recusada.
- Docker Compose de producao ainda expoe `one-api` diretamente em `8000`; antes de producao real, colocar reverse proxy HTTPS.
- Fase 0 ainda nao tem CI no GitHub Actions.
- `.env.example` ainda tem placeholders amplos; precisara ser alinhado com a Fase 1.
- MCP esta apenas como placeholder HTTP 501 no Marco 1.
- Ainda nao existe modelo de usuarios/admin.
- Ainda nao existe camada de auditoria real.
- Ainda nao existe politica automatizada de retencao/anonimizacao.

## Pendencias operacionais

- Decidir dominios/subdominios.
- Validar acesso SSH por chave na VPS.
- Recriar ou confirmar Postgres 18 na VPS.
- Criar roles `one_migrator`, `one_app`, `one_readonly` na VPS.
- Definir e-mail/senha bootstrap do admin no `.env` real.
- Definir se a API publica inicial usara IP/porta ou dominio temporario.
- Definir CORS do frontend do site Hostinger.
