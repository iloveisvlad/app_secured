#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports/baseline

trivy fs --scanners vuln,secret,misconfig --format json --output reports/baseline/trivy-fs.json .
trivy fs --scanners vuln,secret,misconfig --format table --output reports/baseline/trivy-fs.txt .

echo "filesystem scan reports saved to reports/baseline"
