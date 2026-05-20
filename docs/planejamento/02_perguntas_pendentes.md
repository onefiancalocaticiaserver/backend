# Perguntas Pendentes

Gerado em: 2026-05-20

Algumas perguntas originais ja foram respondidas em 2026-05-20. Este arquivo agora separa decisoes confirmadas de pontos ainda pendentes.

## Decisoes ja respondidas

1. Formula atual do app React: aprovada como regra oficial inicial.
2. Output do MVP: pode comecar como JSON/tela no painel.
3. Dominio/subdominio final: ainda indefinido; iniciar por acesso direto da VPS.
4. Painel interno: inicialmente publico com login.
5. Postgres atual: pode ser recriado.
6. SSH/secrets: aprovado usar chave SSH e separar credenciais reais.
7. Todo o sistema deve usar nomes em portugues, inclusive APIs, schemas, modulos e ferramentas MCP.
8. Fase 1 tera CRUD completo para imobiliarias e corretores via API.
9. Hermes podera usar CRUD completo de imobiliarias e corretores via MCP.
10. Havera um unico usuario admin inicial.
11. Admin inicial: `admin@onefiancalocaticia.com.br`.
12. Para CRUD do frontend publico, usar a opcao mais simples: token seguro por cadastro, sem login de parceiro na Fase 1.
13. `origem` representa a fonte do cadastro e pode ser automatica: `site`, `chatbot`, `one`, `app_interno`, `api`, `importacao` ou `outro`.

## Pontos ainda pendentes

### Para iniciar Fase 1

1. Quais campos serao obrigatorios no cadastro publico de imobiliaria?
   - Recomendacao atual: razao social, nome fantasia, CNPJ, WhatsApp, e-mail, endereco, cidades/UFs de atuacao, responsavel principal e cargo do responsavel.
   - Opcionais confirmados: site, Instagram, media de locacoes por mes.
   - Default solicitado: aceite LGPD = sim; opt-in marketing = sim.
   - Pendencia juridica: validar se opt-in marketing pode vir pre-marcado como sim no formulario publico.

2. Quais campos serao obrigatorios no cadastro publico de corretor?
   - Recomendacao atual: nome completo, CPF, CRECI, WhatsApp, e-mail, cidade/UF e tipo de corretor.
   - Opcionais confirmados: perfil profissional, imobiliaria vinculada e volume de indicacoes.
   - Se tipo de corretor for `autonomo`, imobiliaria vinculada fica vazia/nula.
   - Default solicitado: aceite LGPD = sim; opt-in marketing = sim.
   - Pendencia juridica: validar se opt-in marketing pode vir pre-marcado como sim no formulario publico.

3. O cadastro publico cria diretamente imobiliaria/corretor com status `pendente`, ou deve criar uma solicitacao separada?
   - Recomendacao inicial: criar diretamente o parceiro com status `pendente`, sem modulo de leads na Fase 1.

4. Confirmar se `DELETE` via Hermes deve existir na Fase 1.
   - Decisao ja dada: Hermes tera CRUD completo.
   - Recomendacao tecnica: implementar delete como soft delete/cancelamento, nunca exclusao fisica.

5. Definir a senha inicial real do admin no `.env` da VPS.
   - E-mail confirmado: `admin@onefiancalocaticia.com.br`.
   - A senha nao deve ser registrada em documento versionado.

### Bloqueiam deploy publico final

7. Quais serao os dominios/subdominios finais para producao?
   - API: `api.onefiancalocaticia.com.br`?
   - Admin: `admin.onefiancalocaticia.com.br`?
   - Site publico: `onefiancalocaticia.com.br`?

8. O acesso por IP/porta da VPS sera usado apenas para homologacao ou tambem no inicio da operacao real?

9. Quem serao os usuarios internos iniciais?
   - admin;
   - operador;
   - financeiro;
   - somente leitura.

10. Depois da criacao da chave SSH, podemos desabilitar login root por senha?

### Bloqueiam regra de negocio final

11. A comissao de 10% deve incidir sempre sobre `total_calculated_amount`, inclusive quando o cliente pagar parcelado?

12. Ha estados ou regras especificas por UF/cidade que mudem calculo, documentos ou comissao?

### Bloqueiam LGPD/compliance final

13. Qual politica juridica final de retencao?
   - lead sem conversao;
   - proposta reprovada;
   - proposta aprovada/contratada;
   - documentos;
   - dados bancarios de parceiros.

14. Ja existe politica de privacidade e termos de uso aprovados juridicamente?

15. Qual e-mail oficial de privacidade deve ser usado em producao?

16. O aceite LGPD sera coletado em formulario, WhatsApp, painel interno ou todos?

### Bloqueiam integracao Hermes final

17. O Hermes ja esta rodando na mesma VPS ou em outro ambiente?

18. O Hermes consegue acessar containers por rede Docker interna, ou precisara chamar endpoint HTTP publicado?

19. Qual sera a regra de handoff para humano?
   - documento invalido;
   - duvida juridica;
   - pagamento;
   - reprovacao;
   - excecao operacional.

### Bloqueiam operacao de documentos

20. No MVP, quais documentos exatos serao aceitos para PF e PJ?

21. O upload por link seguro pode ser feito sem login, apenas por token com TTL?

22. Qual limite real por arquivo e por proposta deve ser usado em producao?

23. Devemos ativar antivirus/ClamAV ja no MVP ou deixar para Fase 2?

### Bloqueiam deploy definitivo do banco

24. O container `postgresql-1ua2` atual ja esta em PostgreSQL 18?

25. Confirmar operacionalmente que nao ha dados importantes no volume atual antes de remover/recriar.

26. Podemos criar roles separadas `one_migrator`, `one_app` e `one_readonly` e parar de usar o usuario administrativo em runtime?

## Minha recomendacao de resposta minima para iniciar

Para iniciar sem travar:

```text
1. Usar IP/porta da VPS durante desenvolvimento e homologacao.
2. Painel admin restrito por login e, se possivel, IP allowlist.
3. Usar formula atual como default_2026_v1.
4. Output MVP em JSON/tela; PDF/imagem na fase seguinte.
5. Upload por link tokenizado com TTL de 72h.
6. Criar roles separadas e nao usar Admin na aplicacao.
7. Executar Fase 0/Fase 1 antes de conectar Hermes em producao.
```
