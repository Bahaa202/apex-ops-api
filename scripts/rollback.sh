#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PREV=$(cat .previous_tag 2>/dev/null || true)
[ -n "$PREV" ] || { echo "no previous tag recorded"; exit 1; }
CUR=$(grep '^APP_IMAGE_TAG=' .env | cut -d= -f2)
sed -i "s/^APP_IMAGE_TAG=.*/APP_IMAGE_TAG=${PREV}/" .env
docker compose up -d
for i in $(seq 1 30); do
  if curl -sf localhost:8000/ready >/dev/null; then
    echo "rolled back ${CUR} -> ${PREV} OK"; echo "$CUR" > .previous_tag; exit 0
  fi
  sleep 2
done
echo "rollback health check failed"; exit 1
