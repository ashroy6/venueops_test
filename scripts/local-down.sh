#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Stopping VenueOps local demo..."
docker compose down --remove-orphans
echo "Stopped."
