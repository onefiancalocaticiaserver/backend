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
: "${VPS_PROJECT_DIR:=/opt/one-fianca-backend}"
: "${VPS_DATA_DIR:=/srv/one-fianca}"

VPS_SSH_KEY_PATH="${VPS_SSH_KEY_PATH/#\~/${HOME}}"
SSH_TARGET="${VPS_SSH_USER}@${VPS_HOST}"
SSH_ARGS=(-i "${VPS_SSH_KEY_PATH}" -p "${VPS_SSH_PORT}" -o BatchMode=yes -o IdentitiesOnly=yes -o ConnectTimeout=10)

ssh "${SSH_ARGS[@]}" "${SSH_TARGET}" bash -s -- "${VPS_PROJECT_DIR}" "${VPS_DATA_DIR}" <<'REMOTE_CHECK'
set -euo pipefail
PROJECT_DIR="$1"
DATA_DIR="$2"

printf "ssh=ok\n"
command -v git >/dev/null && printf "git=ok\n"
command -v docker >/dev/null && printf "docker=ok\n"
docker info >/dev/null && printf "docker_daemon=ok\n"
if docker compose version >/dev/null 2>&1; then
  printf "docker_compose=ok\n"
elif command -v docker-compose >/dev/null 2>&1; then
  printf "docker_compose_legacy=ok\n"
else
  echo "docker_compose=missing"
  exit 1
fi
mkdir -p "${PROJECT_DIR}" "${DATA_DIR}/documents" "${DATA_DIR}/backups" "${DATA_DIR}/logs"
test -w "${PROJECT_DIR}" && printf "project_dir_writable=ok\n"
test -w "${DATA_DIR}" && printf "data_dir_writable=ok\n"
REMOTE_CHECK
