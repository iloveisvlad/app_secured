#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports/baseline

docker compose build api worker
trivy image --format json --output reports/baseline/trivy-image-api.json taskops-board-api:vulnerable
trivy image --format json --output reports/baseline/trivy-image-worker.json taskops-board-worker:vulnerable
trivy image --format table --output reports/baseline/trivy-image-api.txt taskops-board-api:vulnerable
trivy image --format table --output reports/baseline/trivy-image-worker.txt taskops-board-worker:vulnerable

echo "image scan reports saved to reports/baseline"
