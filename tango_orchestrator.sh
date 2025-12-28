#!/bin/bash
set -e

echo "🛑 Stopping all running containers..."
docker ps -q | xargs -r docker stop

echo "🧹 Removing all containers..."
docker ps -aq | xargs -r docker rm -f

echo "🗑️ Removing all images..."
docker images -aq | xargs -r docker rmi -f

echo "📦 Removing all volumes..."
docker volume ls -q | xargs -r docker volume rm

echo "🌐 Removing unused networks..."
docker network prune -f

echo "🧽 Clearing build cache..."
docker builder prune -af

echo "🔥 Full system prune..."
docker system prune -af --volumes

echo "🚀 Building fresh image..."
docker build --no-cache -t tango-reseller-bot .

echo "▶️ Running container..."
docker run -it \
  --env-file .env \
  tango-reseller-bot
