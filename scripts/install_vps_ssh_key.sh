#!/usr/bin/env bash
set -euo pipefail

OPS_ENV="${OPS_ENV:-./ops.env}"

if [ ! -f "${OPS_ENV}" ]; then
  echo "Arquivo ${OPS_ENV} nao encontrado. Crie a partir de ops.env.example fora do Git."
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "${OPS_ENV}"
set +a

: "${VPS_HOST:?defina VPS_HOST em ${OPS_ENV}}"
: "${VPS_SSH_PORT:=22}"
: "${VPS_SSH_USER:=root}"
: "${VPS_SSH_KEY_PATH:?defina VPS_SSH_KEY_PATH em ${OPS_ENV}}"

VPS_SSH_KEY_PATH="${VPS_SSH_KEY_PATH/#\~/${HOME}}"
PUBLIC_KEY_PATH="${VPS_SSH_KEY_PATH}.pub"
SSH_TARGET="${VPS_SSH_USER}@${VPS_HOST}"

if [ ! -f "${PUBLIC_KEY_PATH}" ]; then
  echo "Chave publica ${PUBLIC_KEY_PATH} nao encontrada."
  echo "Gere com: ssh-keygen -t ed25519 -f ${VPS_SSH_KEY_PATH} -C one-fianca-vps"
  exit 1
fi

if ! command -v sshpass >/dev/null 2>&1; then
  echo "sshpass nao encontrado. Instale ou copie a chave manualmente com ssh-copy-id."
  exit 1
fi

if [ -z "${VPS_SSH_PASSWORD:-}" ]; then
  read -r -s -p "Senha SSH temporaria para ${SSH_TARGET}: " VPS_SSH_PASSWORD
  echo
fi

printf '%s\n' "$(cat "${PUBLIC_KEY_PATH}")" | SSHPASS="${VPS_SSH_PASSWORD}" sshpass -e ssh \
  -p "${VPS_SSH_PORT}" \
  -o PubkeyAuthentication=no \
  -o PreferredAuthentications=password \
  -o StrictHostKeyChecking=accept-new \
  -o ConnectTimeout=10 \
  "${SSH_TARGET}" \
  'umask 077; mkdir -p ~/.ssh; touch ~/.ssh/authorized_keys; read key; grep -qxF "$key" ~/.ssh/authorized_keys || printf "%s\n" "$key" >> ~/.ssh/authorized_keys; chmod 700 ~/.ssh; chmod 600 ~/.ssh/authorized_keys'

ssh -i "${VPS_SSH_KEY_PATH}" \
  -p "${VPS_SSH_PORT}" \
  -o BatchMode=yes \
  -o IdentitiesOnly=yes \
  -o StrictHostKeyChecking=accept-new \
  -o ConnectTimeout=10 \
  "${SSH_TARGET}" \
  'printf "Acesso SSH por chave validado.\n"'
