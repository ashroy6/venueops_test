#!/usr/bin/env bash
set -euo pipefail

APP_URL="${APP_URL:-}"

if [[ -z "$APP_URL" ]]; then
  echo "APP_URL is not set. Skipping live post-deploy smoke test."
  echo "This is expected for local/render-only CI runs."
  exit 0
fi

echo "Running post-deploy smoke test against: $APP_URL"

check_url() {
  local name="$1"
  local url="$2"

  echo "Checking $name: $url"

  local code
  code="$(curl -sS -o /tmp/venueops_post_deploy_response.txt -w "%{http_code}" "$url")"

  if [[ "$code" != "200" ]]; then
    echo "FAILED: $name returned HTTP $code"
    cat /tmp/venueops_post_deploy_response.txt || true
    exit 1
  fi

  echo "PASSED: $name"
}

check_url "web health" "$APP_URL/health.html"
check_url "backend health" "$APP_URL/api/health"
check_url "ingestion health" "$APP_URL/ingestion/health"

echo "POST-DEPLOY SMOKE TEST PASSED"
