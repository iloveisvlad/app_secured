#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-reports/runtime_monitoring}"
IMAGE="${FALCO_IMAGE:-falcosecurity/falco:0.44.1}"

mkdir -p "$OUT_DIR"

echo "[*] Falco container smoke test"
echo "[*] Image: $IMAGE"
echo "[*] Output directory: $OUT_DIR"

echo "[*] Pulling Falco image"
if ! docker pull "$IMAGE" > "$OUT_DIR/falco-container-pull.log" 2>&1; then
  echo "[!] Failed to pull $IMAGE"
  echo "Falco container image pull failed. See falco-container-pull.log" > "$OUT_DIR/falco-container-failed.txt"
  exit 0
fi

echo "[*] Starting Falco for 60 seconds"
set +e
timeout 60s docker run --rm \
  --name falco-smoke \
  --privileged \
  -v /var/run/docker.sock:/host/var/run/docker.sock \
  -v /run/containerd/containerd.sock:/host/run/containerd/containerd.sock \
  -v /dev:/host/dev \
  -v /proc:/host/proc:ro \
  -v /boot:/host/boot:ro \
  -v /lib/modules:/host/lib/modules:ro \
  -v /usr:/host/usr:ro \
  --entrypoint /usr/bin/falco \
  "$IMAGE" \
  -o json_output=true \
  > "$OUT_DIR/falco-container-events.jsonl" \
  2> "$OUT_DIR/falco-container-stderr.log" &

FALCO_PID=$!
sleep 10

echo "[*] Triggering benign runtime activity"
docker exec taskops_api_secured sh -lc 'id; touch /tmp/falco-container-test; rm /tmp/falco-container-test' >/dev/null 2>&1 || true
docker exec taskops_nginx_secured sh -lc 'id; nginx -t' >/dev/null 2>&1 || true

wait "$FALCO_PID"
FALCO_EXIT=$?
set -e

echo "[*] Falco container exit code: $FALCO_EXIT" | tee "$OUT_DIR/falco-container-result.txt"

if [ -s "$OUT_DIR/falco-container-events.jsonl" ]; then
  echo "[*] Falco events captured"
else
  echo "[!] No Falco events captured or Falco failed to initialize"
fi

echo "[*] Done"