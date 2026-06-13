#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-reports/runtime_monitoring}"
mkdir -p "$OUT_DIR"

echo "[*] Collecting Docker runtime state"
docker compose ps -a > "$OUT_DIR/compose-ps.txt"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}" > "$OUT_DIR/docker-ps.txt"
docker images > "$OUT_DIR/docker-images.txt"
docker stats --no-stream > "$OUT_DIR/docker-stats.txt"

echo "[*] Collecting service logs"
for svc in nginx api worker postgres redis; do
  docker compose logs --tail=300 "$svc" > "$OUT_DIR/${svc}.log" 2>&1 || true
done

echo "[*] Collecting security settings"
{
  for c in taskops_nginx_secured taskops_api_secured taskops_worker_secured taskops_postgres_secured taskops_redis_secured; do
    echo "=== $c ==="
    docker inspect "$c" --format 'Image={{.Config.Image}}'
    docker inspect "$c" --format 'User={{.Config.User}}'
    docker inspect "$c" --format 'AppArmor={{.AppArmorProfile}}'
    docker inspect "$c" --format 'ReadonlyRootfs={{.HostConfig.ReadonlyRootfs}}'
    docker inspect "$c" --format 'CapDrop={{.HostConfig.CapDrop}} CapAdd={{.HostConfig.CapAdd}}'
    docker inspect "$c" --format 'SecurityOpt={{.HostConfig.SecurityOpt}}'
    docker inspect "$c" --format 'PidsLimit={{.HostConfig.PidsLimit}} Memory={{.HostConfig.Memory}} NanoCpus={{.HostConfig.NanoCpus}}'
    docker inspect "$c" --format 'NetworkMode={{.HostConfig.NetworkMode}}'
    echo
  done
} > "$OUT_DIR/container-security-settings.txt"

echo "[*] Collecting Docker daemon info"
docker info > "$OUT_DIR/docker-info.txt" 2>&1 || true
docker network ls > "$OUT_DIR/docker-networks.txt"
docker network inspect app_secured_frontend > "$OUT_DIR/network-frontend.json" 2>&1 || true
docker network inspect app_secured_backend > "$OUT_DIR/network-backend.json" 2>&1 || true

echo "[*] Collecting auditd Docker records"
sudo auditctl -l > "$OUT_DIR/audit-rules.txt" 2>&1 || true
sudo ausearch -k docker --start recent > "$OUT_DIR/audit-docker-recent.log" 2>&1 || true

echo "[*] Collecting host firewall and AppArmor state"
sudo ufw status verbose > "$OUT_DIR/ufw-status.txt" 2>&1 || true
sudo aa-status > "$OUT_DIR/apparmor-status.txt" 2>&1 || true

echo "[*] Done: $OUT_DIR"