#!/usr/bin/env bash
set -euo pipefail
NEW="${1:?usage: deploy.sh <version>}"
cd "$(dirname "$0")/.."
PREV=$(grep '^APP_IMAGE_TAG=' .env | cut -d= -f2)
docker image inspect "apex-ops-api:${NEW}" >/dev/null
echo "$PREV" > .previous_tag
sed -i "s/^APP_IMAGE_TAG=.*/APP_IMAGE_TAG=${NEW}/" .env
docker compose up -d
for i in $(seq 1 30); do
  if curl -sf localhost:8000/ready >/dev/null; then
    echo "deployed ${NEW} OK"; exit 0
  fi
  sleep 2
done
echo "health check failed for ${NEW}, rolling back to ${PREV}"
./scripts/rollback.sh
exit 1
