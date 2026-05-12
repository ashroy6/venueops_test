#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p docs/evidence

timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

echo "Generating final evidence at $timestamp..."

{
  echo "# Final Validation Evidence"
  echo ""
  echo "Generated at: $timestamp"
  echo ""
  bash scripts/final-validate.sh
} > docs/evidence/final-validation.txt

{
  echo "# Final Project Tree"
  echo ""
  echo "Generated at: $timestamp"
  echo ""
  tree -L 4 || find . -maxdepth 4 -type f | sort
} > docs/evidence/final-project-tree.txt

{
  echo "# Docker Compose Status"
  echo ""
  echo "Generated at: $timestamp"
  echo ""
  docker compose ps
} > docs/evidence/final-docker-compose-status.txt

{
  echo "# Prometheus Targets"
  echo ""
  echo "Generated at: $timestamp"
  echo ""
  curl -sS http://localhost:9090/api/v1/targets | head -c 5000
  echo ""
} > docs/evidence/final-prometheus-targets.txt

{
  echo "# GitHub Actions Workflows"
  echo ""
  echo "Generated at: $timestamp"
  echo ""
  find .github/workflows -type f | sort
} > docs/evidence/final-github-actions.txt

{
  echo "# Terraform Files"
  echo ""
  echo "Generated at: $timestamp"
  echo ""
  find infra/terraform -type f | sort
} > docs/evidence/final-terraform-files.txt

{
  echo "# Helm Files"
  echo ""
  echo "Generated at: $timestamp"
  echo ""
  find infra/helm/venueops -type f | sort
} > docs/evidence/final-helm-files.txt

{
  echo "# Documentation Files"
  echo ""
  echo "Generated at: $timestamp"
  echo ""
  find docs -maxdepth 2 -type f | sort
} > docs/evidence/final-docs-files.txt

echo "Final evidence generated under docs/evidence/"
