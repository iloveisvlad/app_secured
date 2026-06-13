#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-reports/runtime_monitoring}"
mkdir -p "$OUT_DIR"

echo "[*] Capturing Docker events for 30 seconds"
timeout 30s docker events \
  --filter container=taskops_api_secured \
  --filter container=taskops_nginx_secured \
  --filter container=taskops_postgres_secured \
  --filter container=taskops_redis_secured \
  --filter container=taskops_worker_secured \
  > "$OUT_DIR/docker-events.log" &

EVENT_PID=$!
sleep 5

curl -s http://localhost/health >/dev/null
docker exec taskops_api_secured sh -lc 'id >/tmp/docker-events-test && rm /tmp/docker-events-test' || true

wait "$EVENT_PID" || true

echo "[*] Docker events saved to $OUT_DIR/docker-events.log"