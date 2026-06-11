#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports/baseline

# this check is intended for a linux docker host or linux vm
# docker desktop and wsl2 may return incomplete host-level results

docker run --rm --net host --pid host --userns host --cap-add audit_control \
  -e DOCKER_CONTENT_TRUST=${DOCKER_CONTENT_TRUST:-} \
  -v /etc:/etc:ro \
  -v /usr/bin/containerd:/usr/bin/containerd:ro \
  -v /usr/bin/runc:/usr/bin/runc:ro \
  -v /usr/lib/systemd:/usr/lib/systemd:ro \
  -v /var/lib:/var/lib:ro \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  --label docker_bench_security \
  docker/docker-bench-security | tee reports/baseline/docker-bench.txt
