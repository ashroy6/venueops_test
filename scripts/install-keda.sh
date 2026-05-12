#!/usr/bin/env bash
set -euo pipefail

echo "Installing KEDA with Helm..."

if ! command -v helm >/dev/null 2>&1; then
  echo "ERROR: helm is not installed."
  exit 1
fi

if ! command -v kubectl >/dev/null 2>&1; then
  echo "ERROR: kubectl is not installed."
  exit 1
fi

helm repo add kedacore https://kedacore.github.io/charts
helm repo update

helm upgrade --install keda kedacore/keda \
  --namespace keda \
  --create-namespace \
  --wait \
  --timeout 5m

kubectl get pods -n keda
