# Automation

## Infrastructure Automation

Terraform manages Azure and Cloudflare infrastructure.

Terraform creates:

- resource group
- virtual network and subnets
- AKS
- Azure Container Registry
- Key Vault
- PostgreSQL
- Storage Account
- Event Hubs
- Service Bus
- Log Analytics
- Application Insights
- Azure Monitor Workspace
- Cloudflare placeholder resources

Terraform is validated with:

    terraform fmt -recursive
    terraform init -backend=false
    terraform validate

## Application Deployment Automation

GitHub Actions builds and validates the application.

The app is packaged as Docker images.

Images are pushed to Azure Container Registry in production.

Helm deploys the containers to AKS.

## CI/CD Workflows

The repo includes separate workflows:

- ci.yml
- terraform-validate.yml
- helm-validate.yml
- security-scan.yml
- deploy-dev.yml
- deploy-prod.yml

I separated them because application validation, infrastructure validation, security checks, and deployments should not be mixed together.

## Security Automation

Security checks include:

- secret scanning
- image scanning
- Terraform scanning
- dependency/code scanning

The goal is to catch problems before deployment.

## Evidence Automation

The local project can generate evidence with:

    make evidence

This captures:

- Docker Compose status
- API health
- ingestion API health
- smoke test output
- worker logs

In production, similar evidence would come from CI/CD artifacts, Terraform plan output, deployment logs, and monitoring dashboards.
