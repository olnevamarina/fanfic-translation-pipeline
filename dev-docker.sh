#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="fanfic-site"
PORT="10000"

# Находим и прибиваем старые контейнеры этого образа, если вдруг зависли
OLD_CONTAINERS=$(docker ps -aq --filter "ancestor=${IMAGE_NAME}")
if [ -n "$OLD_CONTAINERS" ]; then
  echo "Останавливаю старые контейнеры..."
  docker rm -f $OLD_CONTAINERS
fi

echo "Пересобираю образ ${IMAGE_NAME}..."
docker build -t "$IMAGE_NAME" .

echo "Запускаю контейнер на порту ${PORT}..."
exec docker run --rm --init -p "${PORT}:${PORT}" --env-file .env "$IMAGE_NAME"