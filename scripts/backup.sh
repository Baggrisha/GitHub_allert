#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME=githubbot
DB_PATH=/app/data/bot.db
BACKUP_DIR=./backups
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE=${BACKUP_DIR}/bot_${TIMESTAMP}.db

mkdir -p "${BACKUP_DIR}"

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  if docker exec ${CONTAINER_NAME} test -f ${DB_PATH}; then
    docker cp ${CONTAINER_NAME}:${DB_PATH} "${BACKUP_FILE}"
    echo "Backup saved to ${BACKUP_FILE}"
  else
    echo "No DB file in container, skipping copy"
  fi
else
  echo "Container ${CONTAINER_NAME} is not running, skipping copy"
fi
