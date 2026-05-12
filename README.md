# VenueOps Cloud Platform

This is a production-shaped DevOps interview project for an Azure platform protected by Cloudflare at the edge.

The goal is not to build a full business product. The goal is to show how I would design, deploy, secure, scale, monitor, and automate a real cloud platform.

## What the platform supports

- Web admin dashboard for central configuration
- Backend APIs
- Log ingestion from in-venue devices
- Log processing workers
- Video processing workers
- SMS/email notification workers
- Async communication between backend and devices
- CI/CD pipelines
- Infrastructure as code
- Observability and operational evidence

## Local demo

The local demo runs with Docker Compose.

Start it:

    make up

Run the smoke test:

    make smoke

Generate evidence:

    make evidence

Open:

    Web dashboard:  http://localhost:3000
    Backend API:    http://localhost:8000/health
    Ingestion API:  http://localhost:8001/health

## What the local demo proves

The smoke test proves:

- web dashboard is reachable
- backend API is healthy
- ingestion API is healthy
- device logs can be accepted
- log processor handles device logs
- SMS/email jobs can be queued
- notification worker processes jobs
- video jobs can be queued
- video worker processes jobs

Local mode uses mock queues:

- mock Event Hub = local file-backed device log queue
- mock Service Bus = local file-backed job queue

In production, these are replaced by Azure Event Hubs and Azure Service Bus.

## Production design

Traffic flow:

    Users / in-venue devices
      -> Cloudflare
      -> Azure Application Gateway WAF
      -> AKS Ingress
      -> AKS services

AKS runs:

- web admin frontend
- backend API
- device ingestion API
- log processor worker
- video processor worker
- notification worker

Azure services:

- Event Hubs for high-volume device logs
- Service Bus for reliable async jobs
- Blob Storage for logs and videos
- PostgreSQL for venues, devices, guests, config, jobs, and audit logs
- Redis for hot config and device state
- Key Vault for secrets and certificates
- ACR for container images
- Azure Monitor, Log Analytics, Application Insights, Prometheus, Grafana, and OpenTelemetry for observability

## Infrastructure

Terraform files live under:

    infra/terraform/

Validate:

    terraform -chdir=infra/terraform validate

Terraform currently covers the production foundation:

- Resource Group
- VNet and subnets
- ACR
- Key Vault
- Storage Account
- Event Hubs
- Service Bus
- PostgreSQL
- Log Analytics
- Application Insights
- Azure Monitor Workspace
- AKS
- Cloudflare placeholder module

## AKS deployment

Helm chart lives under:

    infra/helm/venueops/

Validate:

    helm lint infra/helm/venueops

Render:

    helm template venueops infra/helm/venueops --values infra/helm/venueops/values-dev.yaml

The Helm chart includes:

- Deployments
- Services
- Ingress
- HPA
- KEDA ScaledObjects
- PodDisruptionBudgets
- NetworkPolicy
- ServiceAccount
- ConfigMap

## CI/CD

GitHub Actions workflows live under:

    .github/workflows/

Workflows included:

- ci.yml
- terraform-validate.yml
- helm-validate.yml
- security-scan.yml
- deploy-dev.yml
- deploy-prod.yml

The deploy workflows are production-shaped. They can render manifests without Azure, and become real deployments when Azure OIDC secrets and repository variables are configured.

## Documentation

Detailed docs:

- docs/architecture.md
- docs/aks-hardening.md
- docs/security.md
- docs/scalability.md
- docs/reliability.md
- docs/resiliency.md
- docs/observability.md
- docs/automation.md
- docs/cloudflare-app-gateway.md
- docs/database.md
- docs/tradeoffs.md
- docs/interview-walkthrough.md

## Evidence

Evidence files live under:

    docs/evidence/

They contain command output for local smoke tests, API health, worker logs, Terraform validation, Helm validation, and workflow inventory.

## Interview summary

I built a lightweight local version of the platform to prove the service boundaries and async flows.

I used Docker Compose for the local demo, Helm for AKS deployment packaging, Terraform for Azure infrastructure, and GitHub Actions for CI/CD.

The app is intentionally minimal because the interview task is focused on DevOps, infrastructure, security, observability, reliability, scalability, resiliency, and automation.


## Final Validation

Run:

    bash scripts/final-validate.sh

Generate final evidence:

    bash scripts/final-evidence.sh

Final evidence is stored in:

    docs/evidence/

## Key Review Files

- docs/submission-checklist.md
- docs/final-interview-script.md
- docs/interview-walkthrough.md
- docs/architecture.md
- docs/security.md
- docs/scalability.md
- docs/reliability.md
- docs/resiliency.md
- docs/observability.md
- docs/automation.md
- docs/tradeoffs.md
- docs/database.md
- docs/cloudflare-app-gateway.md
- docs/aks-hardening.md


## Production Readiness Additions

This repo also includes production-readiness workflows and docs:

- Image scan and SBOM workflow
- Terraform plan workflow
- Terraform apply workflow with environment approval
- Production rollback workflow
- Evidence pack workflow
- Branch protection guidance
- Production approval guidance

Review:

- docs/branch-protection.md
- docs/production-approval.md
