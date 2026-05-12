# Final Interview Script

## Opening Summary

I built a production-shaped Azure platform design for VenueOps.

The system is designed to host a web admin dashboard, backend APIs, device log ingestion, video processing, SMS/email sending, and asynchronous communication between in-venue devices and backend services.

I used Cloudflare at the edge, Azure Application Gateway WAF as the Azure entry point, AKS for containers, Event Hubs for device logs, Service Bus for async jobs, Blob Storage for videos/logs, PostgreSQL for business data/audit logs, and Key Vault for secrets.

## What I Can Demo Locally

I can run the platform locally with Docker Compose.

Command:

    make up

Then I can run:

    make smoke

The smoke test proves:

- the web dashboard is reachable
- the backend API is healthy
- the ingestion API is healthy
- device logs can be accepted
- the log worker processes device logs
- SMS/email jobs are queued
- the notification worker processes jobs
- video jobs are queued
- the video worker processes jobs

## Why Local Mocks Exist

The local demo uses file-backed queues.

This avoids needing a paid Azure subscription during the interview.

In production:

- the mock Event Hub file becomes Azure Event Hubs
- the mock Service Bus file becomes Azure Service Bus
- local SQLite becomes Azure PostgreSQL
- local Docker Compose becomes AKS with Helm

The service boundaries stay the same.

## Infrastructure as Code

Terraform is under:

    infra/terraform/

It validates successfully.

It includes modules for:

- Resource Group
- Network
- AKS
- ACR
- Key Vault
- Storage
- Event Hubs
- Service Bus
- PostgreSQL
- Monitoring
- Application Gateway WAF
- Cloudflare design marker

## AKS Deployment

Helm is under:

    infra/helm/venueops/

It defines:

- Deployments
- Services
- Ingress
- HPA
- KEDA ScaledObjects
- PodDisruptionBudgets
- NetworkPolicy
- ServiceAccount
- SecretProviderClass

Helm lint passes and Helm template renders.

## CI/CD

GitHub Actions workflows are under:

    .github/workflows/

The workflows separate:

- local CI and smoke tests
- Terraform validation
- Helm validation
- security scanning
- dev deployment
- prod deployment
- KEDA/AKS hardening

Production deployment uses manual triggers and GitHub environment approval.

## Observability

Locally, Prometheus and Grafana run through Docker Compose.

Prometheus scrapes:

- backend API
- ingestion API
- log processor
- video processor
- notification worker

Grafana is available at:

    http://localhost:3001

In production, the design uses:

- Azure Monitor
- Log Analytics
- Application Insights
- Managed Prometheus
- Managed Grafana
- structured JSON logs
- audit logs
- alert rules

## Security

Security controls include:

- Cloudflare WAF/DDoS/rate limiting/bot protection
- Azure Application Gateway WAF
- Azure Key Vault
- Managed Identity / Workload Identity
- Kubernetes NetworkPolicies
- Pod Security restricted namespace labels
- container resource limits
- secret scanning
- image scanning
- Terraform scanning
- audit logs

## Scalability

The design uses:

- HPA for web/API/ingestion APIs
- KEDA for queue/event-driven workers
- AKS Cluster Autoscaler for nodes
- Event Hubs partitions for high-volume device logs
- Service Bus queues for reliable business jobs
- Blob Storage for large files/videos

## Reliability and Resiliency

Reliability comes from:

- multiple replicas
- health probes
- queue-based async processing
- dead-letter queues
- pod disruption budgets
- backups
- smoke tests
- deployment evidence
- rollback-ready Helm deployment

## Honest Limitations

This is not a live Azure deployment.

Real Cloudflare resources, Key Vault secret mounting, KEDA runtime scaling, App Gateway routing, and Azure managed service connections require a real Azure subscription and Cloudflare zone.

The repo is designed so those can be enabled without changing the architecture.

## Closing Statement

This project proves the full DevOps thinking path: local runnable service demo, infrastructure as code, AKS deployment packaging, CI/CD automation, security controls, observability, evidence, and documentation. It is intentionally lightweight in business logic because the test is focused on cloud infrastructure and DevOps engineering.
