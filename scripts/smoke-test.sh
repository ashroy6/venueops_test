#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

API_BASE="${API_BASE:-http://localhost:8000}"
INGESTION_BASE="${INGESTION_BASE:-http://localhost:8001}"
WEB_BASE="${WEB_BASE:-http://localhost:3000}"

echo "Running VenueOps smoke tests..."
echo ""

check_http() {
  local name="$1"
  local url="$2"

  echo "Checking $name: $url"

  local code
  code="$(curl -sS -o /tmp/venueops_smoke_response.txt -w "%{http_code}" "$url")"

  if [[ "$code" != "200" ]]; then
    echo "FAILED: $name returned HTTP $code"
    cat /tmp/venueops_smoke_response.txt || true
    exit 1
  fi

  echo "PASSED: $name"
}

post_json() {
  local name="$1"
  local url="$2"
  local payload="$3"

  echo "Posting $name: $url"

  local code
  code="$(curl -sS -o /tmp/venueops_smoke_response.txt -w "%{http_code}" \
    -X POST "$url" \
    -H "Content-Type: application/json" \
    -d "$payload")"

  if [[ "$code" != "200" ]]; then
    echo "FAILED: $name returned HTTP $code"
    cat /tmp/venueops_smoke_response.txt || true
    exit 1
  fi

  echo "PASSED: $name"
  cat /tmp/venueops_smoke_response.txt
  echo ""
}

check_http "web dashboard" "$WEB_BASE/health.html"
check_http "backend API health" "$API_BASE/health"
check_http "ingestion API health" "$INGESTION_BASE/health"
check_http "venues endpoint" "$API_BASE/venues"
check_http "devices endpoint" "$API_BASE/devices"

post_json "device log ingestion" "$INGESTION_BASE/ingest/logs" '{
  "venue_id": "venue-london-001",
  "device_id": "camera-01",
  "level": "INFO",
  "event_type": "smoke_test_log",
  "message": "smoke test device log",
  "metadata": {
    "test": "smoke"
  }
}'

post_json "SMS job queue" "$API_BASE/notifications/sms" '{
  "guest_id": "guest-smoke-001",
  "phone_number": "+440000000000",
  "message": "Smoke test SMS"
}'

post_json "email job queue" "$API_BASE/notifications/email" '{
  "guest_id": "guest-smoke-001",
  "email": "guest@example.com",
  "subject": "Smoke test email",
  "body": "Smoke test body"
}'

post_json "video job queue" "$API_BASE/videos/process" '{
  "venue_id": "venue-london-001",
  "source_blob": "landing/smoke-test-video.mp4",
  "requested_by": "smoke-test"
}'

echo "Waiting for workers to process queued messages..."
sleep 8

docker compose logs --tail=100 log-processor > /tmp/venueops_log_processor.txt
docker compose logs --tail=100 notification-worker > /tmp/venueops_notification_worker.txt
docker compose logs --tail=100 video-processor > /tmp/venueops_video_processor.txt

if ! grep -q "device_log_processed" /tmp/venueops_log_processor.txt; then
  echo "FAILED: log processor did not process a device log"
  exit 1
fi

if ! grep -q "notification_job_processed" /tmp/venueops_notification_worker.txt; then
  echo "FAILED: notification worker did not process a notification job"
  exit 1
fi

if ! grep -q "video_job_processed" /tmp/venueops_video_processor.txt; then
  echo "FAILED: video worker did not process a video job"
  exit 1
fi

echo ""
echo "SMOKE TEST PASSED"
echo ""
echo "Proven flows:"
echo "  web dashboard reachable"
echo "  backend API healthy"
echo "  ingestion API healthy"
echo "  device log accepted"
echo "  log worker processed device log"
echo "  SMS/email jobs queued"
echo "  notification worker processed jobs"
echo "  video job queued"
echo "  video worker processed job"
