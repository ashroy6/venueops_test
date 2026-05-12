#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Running final VenueOps validation..."
echo ""

echo "1. Docker Compose config"
docker compose config >/tmp/venueops-compose-final.yaml
echo "PASSED: docker compose config"
echo ""

echo "2. Local smoke test"
make smoke
echo ""

echo "3. Terraform validate"
terraform -chdir=infra/terraform validate
echo ""

echo "4. Helm lint"
helm lint infra/helm/venueops
echo ""

echo "5. Helm template dev"
helm template venueops infra/helm/venueops \
  --values infra/helm/venueops/values-dev.yaml \
  >/tmp/venueops-final-dev.yaml
echo "PASSED: helm template dev"
echo ""

echo "6. Required workflow files"
required_workflows=(
  ".github/workflows/ci.yml"
  ".github/workflows/terraform-validate.yml"
  ".github/workflows/helm-validate.yml"
  ".github/workflows/security-scan.yml"
  ".github/workflows/deploy-dev.yml"
  ".github/workflows/deploy-prod.yml"
  ".github/workflows/keda-aks-hardening.yml"
)

for workflow in "${required_workflows[@]}"; do
  if [[ ! -f "$workflow" ]]; then
    echo "FAILED: missing workflow $workflow"
    exit 1
  fi
done

echo "PASSED: workflow files exist"
echo ""

echo "7. Required documentation files"
required_docs=(
  "README.md"
  "docs/architecture.md"
  "docs/security.md"
  "docs/scalability.md"
  "docs/reliability.md"
  "docs/resiliency.md"
  "docs/observability.md"
  "docs/automation.md"
  "docs/tradeoffs.md"
  "docs/database.md"
  "docs/cloudflare-app-gateway.md"
  "docs/aks-hardening.md"
  "docs/interview-walkthrough.md"
)

for doc in "${required_docs[@]}"; do
  if [[ ! -f "$doc" ]]; then
    echo "FAILED: missing doc $doc"
    exit 1
  fi
done

echo "PASSED: documentation files exist"
echo ""

echo "8. Observability endpoints"
curl -sS http://localhost:8000/metrics >/tmp/venueops-api-metrics.txt
curl -sS http://localhost:8001/metrics >/tmp/venueops-ingestion-metrics.txt
curl -sS http://localhost:9090/api/v1/query?query=up >/tmp/venueops-prometheus-up.json

grep -q "venueops_api_http_requests_total" /tmp/venueops-api-metrics.txt
grep -q "venueops_ingestion_http_requests_total" /tmp/venueops-ingestion-metrics.txt
grep -q "venueops-api" /tmp/venueops-prometheus-up.json

echo "PASSED: metrics endpoints and Prometheus query"
echo ""

echo "FINAL VALIDATION PASSED"
