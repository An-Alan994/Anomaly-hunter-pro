#!/bin/bash
set -e

APP_DIR="$HOME/anomaly_hunter_pro"
COMPOSE_FILE="$APP_DIR/docker-compose.prod.yml"
SERVICE_NAME="anomaly"

TELEGRAM_BOT_TOKEN="ISI_TOKEN_BOTMU"
TELEGRAM_CHAT_ID="ISI_CHAT_IDMU"

send_telegram() {
    local MESSAGE=$1
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d chat_id="${TELEGRAM_CHAT_ID}" \
        -d parse_mode="Markdown" \
        -d text="$MESSAGE" > /dev/null
}

send_telegram "🚀 Deployment started on $(hostname)..."

cd "$APP_DIR"
git fetch --all
git reset --hard origin/main
docker compose -f "$COMPOSE_FILE" pull
sudo systemctl restart $SERVICE_NAME
docker image prune -af

if systemctl is-active --quiet $SERVICE_NAME; then
    send_telegram "✅ Deployment succeeded on $(hostname). Service $SERVICE_NAME is running."
else
    send_telegram "❌ Deployment failed on $(hostname)."
fi
