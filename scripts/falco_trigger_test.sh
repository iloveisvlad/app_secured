#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-reports/runtime_monitoring}"
FALCO_IMAGE="${FALCO_IMAGE:-falcosecurity/falco:0.44.1}"
TEST_IMAGE="${TEST_IMAGE:-alpine:latest}"

mkdir -p "$OUT_DIR"

echo "[*] Falco trigger test"
echo "[*] Falco image: $FALCO_IMAGE"
echo "[*] Test image: $TEST_IMAGE"

echo "[*] Pulling test image"
docker pull "$TEST_IMAGE" > "$OUT_DIR/falco-trigger-test-image-pull.log" 2>&1 || true

echo "[*] Starting Falco for 90 seconds"
set +e
timeout 90s docker run --rm \
  --name falco-trigger-monitor \
  --privileged \
  -v /var/run/docker.sock:/host/var/run/docker.sock \
  -v /run/containerd/containerd.sock:/host/run/containerd/containerd.sock \
  -v /dev:/host/dev \
  -v /proc:/host/proc:ro \
  -v /boot:/host/boot:ro \
  -v /lib/modules:/host/lib/modules:ro \
  -v /usr:/host/usr:ro \
  --entrypoint /usr/bin/falco \
  "$FALCO_IMAGE" \
  -o json_output=true \
  > "$OUT_DIR/falco-trigger-events.jsonl" \
  2> "$OUT_DIR/falco-trigger-stderr.log" &

FALCO_PID=$!
sleep 15

echo "[*] Triggering suspicious activity in a temporary test container"
docker run --rm --name falco-trigger-container --privileged "$TEST_IMAGE" sh -lc '
  id
  cat /etc/shadow >/dev/null 2>&1 || true
  touch /usr/bin/falco-test 2>/dev/null || true
  rm -f /usr/bin/falco-test 2>/dev/null || true
' > "$OUT_DIR/falco-trigger-container.log" 2>&1 || true

wait "$FALCO_PID"
FALCO_EXIT=$?
set -e

echo "[*] Falco monitor exit code: $FALCO_EXIT" | tee "$OUT_DIR/falco-trigger-result.txt"

echo "[*] Removing temporary test image tag if possible"
docker image rm "$TEST_IMAGE" >/dev/null 2>&1 || true

echo "[*] Done"