#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports/baseline

trivy config --format json --output reports/baseline/trivy-config.json .
trivy config --format table --output reports/baseline/trivy-config.txt .

echo "config scan reports saved to reports/baseline"
