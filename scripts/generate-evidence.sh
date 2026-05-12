#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p docs/evidence

timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

echo "Generating evidence at $timestamp..."

{
  echo "# Docker Compose Service Status"
  echo "Generated at: $timestamp"
  echo ""
  docker compose ps
} > docs/evidence/docker-compose-status.txt

{
  echo "# Backend API Health"
  echo "Generated at: $timestamp"
  echo ""
  curl -sS http://localhost:8000/health || true
  echo ""
} > docs/evidence/backend-api-health.txt

{
  echo "# Ingestion API Health"
  echo "Generated at: $timestamp"
  echo ""
  curl -sS http://localhost:8001/health || true
  echo ""
} > docs/evidence/ingestion-api-health.txt

{
  echo "# Local Smoke Test Evidence"
  echo "Generated at: $timestamp"
  echo ""
  bash scripts/smoke-test.sh
} > docs/evidence/local-smoke-test.txt

{
  echo "# Log Processor Evidence"
  echo "Generated at: $timestamp"
  echo ""
  docker compose logs --tail=100 log-processor
} > docs/evidence/log-processor-evidence.txt

{
  echo "# Notification Worker Evidence"
  echo "Generated at: $timestamp"
  echo ""
  docker compose logs --tail=100 notification-worker
} > docs/evidence/notification-worker-evidence.txt

{
  echo "# Video Worker Evidence"
  echo "Generated at: $timestamp"
  echo ""
  docker compose logs --tail=100 video-processor
} > docs/evidence/video-worker-evidence.txt

cat > docs/evidence/README.md <<'EVIDENCE_README_EOF'
# Evidence

This folder stores command output proving the local platform works.

Local mode uses Docker Compose and mock queues:

- Mock Event Hub = local file-backed device log queue
- Mock Service Bus = local file-backed job queue
- SMS/email/video processing = simulated workers

In production:

- Mock Event Hub is replaced by Azure Event Hubs
- Mock Service Bus is replaced by Azure Service Bus
- Local containers are deployed to AKS using Helm
- Images are stored in Azure Container Registry
- Logs, metrics, and traces are sent to Azure Monitor, Log Analytics, Application Insights, Prometheus, and Grafana
EVIDENCE_README_EOF

echo "Evidence generated under docs/evidence/"
