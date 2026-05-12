#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p dist

timestamp="$(date -u +"%Y%m%dT%H%M%SZ")"
pack_name="venueops-evidence-pack-${timestamp}.zip"

echo "Building evidence pack: dist/${pack_name}"

if command -v zip >/dev/null 2>&1; then
  zip -r "dist/${pack_name}" \
    README.md \
    docs \
    infra/helm/venueops \
    infra/terraform \
    .github/workflows \
    scripts \
    observability \
    -x "*/.terraform/*" \
    -x "*.tfstate" \
    -x "*.tfstate.*"
else
  tar -czf "dist/${pack_name%.zip}.tar.gz" \
    README.md \
    docs \
    infra/helm/venueops \
    infra/terraform \
    .github/workflows \
    scripts \
    observability
fi

echo "Evidence pack created under dist/"
