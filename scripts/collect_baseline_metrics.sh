#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports/baseline

{
  echo "# taskops vulnerable baseline metrics"
  echo "generated_at=$(date -Iseconds)"
  echo
  echo "## images"
  docker images "taskops-board-*" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
  echo
  echo "## published ports"
  docker compose ps
  echo
  echo "## api container user"
  docker inspect taskops_api_vulnerable --format '{{.Config.User}}' || true
  echo
  echo "## worker container user"
  docker inspect taskops_worker_vulnerable --format '{{.Config.User}}' || true
  echo
  echo "## api security options"
  docker inspect taskops_api_vulnerable --format '{{json .HostConfig.SecurityOpt}}' || true
  echo
  echo "## api readonly rootfs"
  docker inspect taskops_api_vulnerable --format '{{.HostConfig.ReadonlyRootfs}}' || true
  echo
  echo "## api memory limit"
  docker inspect taskops_api_vulnerable --format '{{.HostConfig.Memory}}' || true
  echo
  echo "## api pids limit"
  docker inspect taskops_api_vulnerable --format '{{.HostConfig.PidsLimit}}' || true
} | tee reports/baseline/baseline-metrics.txt
