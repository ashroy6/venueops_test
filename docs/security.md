# Security

## Edge Security

Cloudflare sits in front of Azure.

It provides:

- DNS protection
- TLS termination
- WAF rules
- DDoS protection
- rate limiting
- bot protection
- CDN caching where appropriate

Only Cloudflare should be allowed to reach the Azure origin in production.

## Azure Entry Layer

Azure Application Gateway WAF is used as the Azure entry point.

It routes traffic into AKS through ingress.

This gives another security layer after Cloudflare.

## Private Access

Production resources should not be exposed publicly unless required.

PostgreSQL, Key Vault, Storage, and internal platform services should use private networking where possible.

AKS workloads should access Azure services through private endpoints and managed identities.

## Identity

The design uses Azure Managed Identity and AKS Workload Identity.

Application containers should not store long-lived Azure credentials.

Workloads get identity from Azure and use RBAC to access only what they need.

## Secrets

Secrets are stored in Azure Key Vault.

Examples:

- SMS provider credentials
- email provider credentials
- database credentials
- certificates
- API tokens

Secrets should not be committed to GitHub.

GitHub Actions should use OIDC federation to Azure instead of long-lived service principal secrets where possible.

## Container Security

Container images should be built in CI and scanned before deployment.

Recommended checks:

- Trivy image scan
- Gitleaks secret scan
- Semgrep SAST
- Checkov Terraform scan
- dependency scanning

Images should be tagged immutably using the Git commit SHA.

Production should not use the `latest` tag.

## Kubernetes Security

The Helm chart includes production-oriented Kubernetes controls:

- resource requests and limits
- readiness probes
- liveness probes
- non-root containers where possible
- dropped Linux capabilities
- service accounts
- network policies
- pod disruption budgets

In a full production rollout, I would also add Kyverno or OPA/Gatekeeper policies.

## Audit Logs

Admin actions should be audited.

The audit log should record:

- who made the change
- what was changed
- old value
- new value
- timestamp
- request ID
- source IP where appropriate

This is important for operations, security, and compliance.
