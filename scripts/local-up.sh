#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Starting VenueOps local demo..."

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker command not found."
  echo "Install Docker Desktop and enable WSL integration."
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "ERROR: docker compose not available."
  exit 1
fi

docker compose up -d --build

echo ""
echo "Waiting for services..."
sleep 5

docker compose ps

echo ""
echo "Local URLs:"
echo "  Web dashboard:  http://localhost:3000"
echo "  Backend API:    http://localhost:8000/health"
echo "  Ingestion API:  http://localhost:8001/health"
echo ""
echo "Run smoke tests:"
echo "  make smoke"
