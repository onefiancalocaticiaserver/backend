# DBeaver - Acesso Ao PostgreSQL Da VPS

Este documento explica como conectar no PostgreSQL do backend pelo DBeaver usando
SSH Tunnel.

O arquivo local `setup_dbeaver.env` contem os valores reais, incluindo senhas, e
fica fora do Git. Ele e ignorado por `.gitignore`.

## Estado Do Banco

Servico Docker na VPS:

```text
postgresql-1ua2
```

Banco:

```text
one
```

Usuario PostgreSQL:

```text
Admin
```

O PostgreSQL nao fica exposto publicamente. Ele esta publicado apenas no loopback
da VPS:

```text
127.0.0.1:15432 -> postgresql-1ua2:5432
```

Por isso o acesso externo deve usar SSH Tunnel.

## DBeaver - Aba Main

Preencha:

```text
Host: 127.0.0.1
Port: 15432
Database: one
Authentication: Username/password
Username: Admin
Password: valor de DBEAVER_MAIN_PASSWORD em setup_dbeaver.env
```

Nao use o IP da VPS na aba Main.

## DBeaver - Aba SSH

Ative SSH Tunnel e preencha:

```text
Host/IP: valor de DBEAVER_SSH_HOST em setup_dbeaver.env
Port: valor de DBEAVER_SSH_PORT em setup_dbeaver.env
User Name: valor de DBEAVER_SSH_USERNAME em setup_dbeaver.env
Authentication Method: Password
Password: valor de DBEAVER_SSH_PASSWORD em setup_dbeaver.env
```

Observacao: `Admin` e usuario do PostgreSQL, nao usuario SSH.

## Senhas

Ha duas senhas diferentes:

- senha SSH: usada na aba SSH para abrir o tunel;
- senha PostgreSQL: usada na aba Main para autenticar no banco.

## Testes De Infra

Na VPS, a porta do banco deve aparecer apenas em loopback:

```text
127.0.0.1:15432->5432/tcp
```

De fora da VPS, a porta `15432` deve permanecer fechada. O acesso externo deve
passar pelo tunel SSH do DBeaver.

## Arquivo Local Com Segredos

O arquivo `setup_dbeaver.env` foi criado localmente com permissao restrita e nao
deve ser enviado ao Git.

Campos esperados:

```text
DBEAVER_MAIN_HOST
DBEAVER_MAIN_PORT
DBEAVER_MAIN_DATABASE
DBEAVER_MAIN_USERNAME
DBEAVER_MAIN_PASSWORD
DBEAVER_SSH_HOST
DBEAVER_SSH_PORT
DBEAVER_SSH_USERNAME
DBEAVER_SSH_AUTHENTICATION_METHOD
DBEAVER_SSH_PASSWORD
POSTGRES_INTERNAL_DOCKER_HOST
POSTGRES_INTERNAL_DOCKER_PORT
POSTGRES_LOCAL_TUNNEL_PORT
```
