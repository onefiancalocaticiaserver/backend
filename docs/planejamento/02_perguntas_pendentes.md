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
7. `agency` significa imobiliaria.
8. `broker` significa corretor.
9. Fase 1 tera CRUD completo para imobiliarias e corretores via API.
10. Hermes podera usar CRUD completo de imobiliarias e corretores via MCP.
11. Havera um unico usuario admin inicial.

## Pontos ainda pendentes

### Para iniciar Fase 1

1. Quais campos serao obrigatorios no cadastro publico de imobiliaria?
   - Campos disponiveis: razao social, nome fantasia, CNPJ, WhatsApp, e-mail, site, Instagram, endereco, cidades/UFs de atuacao, responsavel principal, cargo do responsavel, media de locacoes por mes, aceite LGPD, opt-in marketing.
   - Campos de sistema/admin: status da parceria, observacoes internas, origem/UTM.
   - Recomendacao inicial obrigatoria: nome fantasia, razao social, CNPJ, WhatsApp, e-mail, cidade/UF, responsavel principal, aceite LGPD.

2. Quais campos serao obrigatorios no cadastro publico de corretor?
   - Campos disponiveis: nome completo, CPF, CRECI, WhatsApp, e-mail, cidade/UF, perfil profissional, tipo de corretor, imobiliaria vinculada, volume de indicacoes, aceite LGPD, opt-in marketing.
   - Campos de sistema/admin: status da parceria, observacoes internas, origem/UTM.
   - Recomendacao inicial obrigatoria: nome completo, CPF, WhatsApp, e-mail, cidade/UF, tipo de corretor, aceite LGPD.

3. O cadastro publico cria diretamente imobiliaria/corretor com status `pending`, ou deve criar uma solicitacao separada?
   - Recomendacao inicial: criar diretamente o parceiro com status `pending`, sem modulo de leads na Fase 1.

4. Como o frontend publico vai autenticar consulta, alteracao e exclusao de cadastros?
   - Decisao ja dada: a API deve permitir CRUD.
   - Recomendacao tecnica: CRUD publico deve exigir token seguro por cadastro ou login de parceiro. Sem autenticacao, permitir apenas `POST`.
   - Opcao segura para Fase 1: admin tem CRUD completo por JWT; frontend publico tem `POST` aberto e `GET/PATCH` por token retornado ou enviado por e-mail/WhatsApp; `DELETE` fica restrito ao admin.

5. Qual sera o e-mail e senha inicial do unico usuario admin?
   - Decisao ja dada: criar somente um admin e uma senha.
   - Recomendacao: usar variaveis `BOOTSTRAP_ADMIN_EMAIL` e `BOOTSTRAP_ADMIN_PASSWORD` no `.env` real, sem hardcode.

6. Confirmar se `DELETE` via Hermes deve existir na Fase 1.
   - Decisao ja dada: Hermes tera CRUD completo.
   - Recomendacao tecnica: implementar delete como soft delete/cancelamento, nunca exclusao fisica.

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
