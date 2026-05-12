# Interview Walkthrough

## 1. Explain the problem

The system needs to host a central web dashboard, backend APIs, device ingestion, video processing, SMS/email sending, and async communication between devices and backend.

The platform must be secure, scalable, reliable, observable, and automated.

## 2. Explain the architecture

Traffic enters through Cloudflare.

Cloudflare protects the edge.

Azure Application Gateway WAF routes traffic into AKS.

AKS runs the web app, APIs, and workers.

Event Hubs handles high-volume device logs.

Service Bus handles reliable business jobs.

Blob Storage stores logs and videos.

PostgreSQL stores relational business data and audit logs.

Key Vault stores secrets.

Azure Monitor, Log Analytics, Application Insights, Prometheus, Grafana, and OpenTelemetry provide observability.

## 3. Explain local proof

I created a lightweight local version of the app using Docker Compose.

This proves the service boundaries and async flows without requiring a live Azure subscription.

Local mocks:

- Event Hubs is mocked with a file-backed device log queue.
- Service Bus is mocked with a file-backed job queue.
- SMS/email/video providers are simulated.

## 4. Show commands

Start local platform:

    make up

Run smoke test:

    make smoke

Generate evidence:

    make evidence

Validate Terraform:

    terraform -chdir=infra/terraform validate

Validate Helm:

    helm lint infra/helm/venueops

Render Helm:

    helm template venueops infra/helm/venueops --values infra/helm/venueops/values-dev.yaml

## 5. Explain deployment

In production, GitHub Actions builds Docker images and pushes them to Azure Container Registry.

Helm deploys the images into AKS.

Terraform creates the Azure and Cloudflare infrastructure.

Production deployment requires manual approval.

## 6. Explain why app code is minimal

The test is about DevOps and infrastructure design.

The app is intentionally lightweight.

It proves containerization, health checks, async workers, smoke tests, Helm deployment, and CI/CD flow without wasting time on business logic.

## 7. Strong closing statement

I designed this as a production-shaped Azure platform protected by Cloudflare at the edge. The local demo proves the application flow, Terraform proves the infrastructure structure, Helm proves the AKS deployment shape, and GitHub Actions proves the CI/CD automation path.
