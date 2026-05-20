#!/usr/bin/env bash
set -euo pipefail

OPS_ENV="${OPS_ENV:-./ops.env}"

if [ ! -f "${OPS_ENV}" ]; then
  echo "Arquivo ${OPS_ENV} nao encontrado. Copie ops.env.example para fora do Git e preencha."
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "${OPS_ENV}"
set +a

: "${VPS_HOST:?defina VPS_HOST em ${OPS_ENV}}"
: "${VPS_SSH_PORT:=22}"
: "${VPS_SSH_USER:=root}"
: "${VPS_PROJECT_DIR:=/opt/one-fianca-backend}"
: "${VPS_DATA_DIR:=/srv/one-fianca}"
: "${VPS_SSH_KEY_PATH:?defina VPS_SSH_KEY_PATH em ${OPS_ENV}}"
: "${DEPLOY_BRANCH:=main}"
: "${DOCKER_COMPOSE_FILE:=docker-compose.prod.yml}"
: "${VPS_REPO_URL:=https://github.com/onefiancalocaticiaserver/backend.git}"

VPS_SSH_KEY_PATH="${VPS_SSH_KEY_PATH/#\~/${HOME}}"
SSH_TARGET="${VPS_SSH_USER}@${VPS_HOST}"
SSH_ARGS=(-i "${VPS_SSH_KEY_PATH}" -p "${VPS_SSH_PORT}" -o IdentitiesOnly=yes)

ssh "${SSH_ARGS[@]}" "${SSH_TARGET}" "mkdir -p '${VPS_PROJECT_DIR}' '${VPS_DATA_DIR}/documents' '${VPS_DATA_DIR}/backups' '${VPS_DATA_DIR}/logs'"

ssh "${SSH_ARGS[@]}" "${SSH_TARGET}" bash -s -- \
  "${VPS_PROJECT_DIR}" "${VPS_REPO_URL}" "${DEPLOY_BRANCH}" <<'REMOTE_BOOTSTRAP'
set -euo pipefail
PROJECT_DIR="$1"
REPO_URL="$2"
DEPLOY_BRANCH="$3"

if [ -d "${PROJECT_DIR}/.git" ]; then
  git -C "${PROJECT_DIR}" fetch origin "${DEPLOY_BRANCH}"
  git -C "${PROJECT_DIR}" checkout "${DEPLOY_BRANCH}"
  git -C "${PROJECT_DIR}" pull --ff-only origin "${DEPLOY_BRANCH}"
elif [ -z "$(find "${PROJECT_DIR}" -mindepth 1 -maxdepth 1 -print -quit)" ]; then
  git clone --branch "${DEPLOY_BRANCH}" "${REPO_URL}" "${PROJECT_DIR}"
else
  echo "${PROJECT_DIR} existe, mas nao e um repositorio Git vazio."
  exit 1
fi

if [ ! -f "${PROJECT_DIR}/.env" ]; then
  cp "${PROJECT_DIR}/.env.example" "${PROJECT_DIR}/.env"
  echo "Criei ${PROJECT_DIR}/.env a partir de .env.example. Preencha os segredos reais na VPS e rode novamente."
  exit 2
fi
REMOTE_BOOTSTRAP

ssh "${SSH_ARGS[@]}" "${SSH_TARGET}" bash -s -- \
  "${VPS_PROJECT_DIR}" "${DOCKER_COMPOSE_FILE}" <<'REMOTE_DEPLOY'
set -euo pipefail
PROJECT_DIR="$1"
COMPOSE_FILE="$2"

cd "${PROJECT_DIR}"
if docker compose version >/dev/null 2>&1; then
  COMPOSE=(docker compose -f "${COMPOSE_FILE}")
else
  COMPOSE=(docker-compose -f "${COMPOSE_FILE}")
fi

"${COMPOSE[@]}" up -d --build
"${COMPOSE[@]}" exec -T one-api /app/.venv/bin/alembic upgrade head
"${COMPOSE[@]}" exec -T one-api /app/.venv/bin/python scripts/bootstrap_admin.py
curl -fsS http://127.0.0.1:8000/v1/health
curl -fsS http://127.0.0.1:8000/v1/health/db
REMOTE_DEPLOY

echo "Deploy concluido."
