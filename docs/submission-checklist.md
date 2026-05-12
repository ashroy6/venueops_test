# Submission Checklist

## Local Application

- [x] Web admin dashboard runs locally
- [x] Backend API runs locally
- [x] Device ingestion API runs locally
- [x] Log processor worker runs locally
- [x] Video processor worker runs locally
- [x] Notification worker runs locally
- [x] Docker Compose starts the platform
- [x] Smoke test validates the full local flow

## Cloud Infrastructure

- [x] Terraform root module exists
- [x] Terraform modules exist for Azure platform services
- [x] Resource Group module exists
- [x] Network module exists
- [x] AKS module exists
- [x] ACR module exists
- [x] Key Vault module exists
- [x] Storage module exists
- [x] Event Hubs module exists
- [x] Service Bus module exists
- [x] PostgreSQL module exists
- [x] Monitoring module exists
- [x] Application Gateway WAF module exists
- [x] Cloudflare design marker module exists
- [x] Terraform validate passes

## Kubernetes and AKS

- [x] Helm chart exists
- [x] Deployments are defined
- [x] Services are defined
- [x] Ingress is defined
- [x] HPA is defined
- [x] KEDA ScaledObjects are defined
- [x] PodDisruptionBudgets are defined
- [x] NetworkPolicy is defined
- [x] ServiceAccount is defined
- [x] SecretProviderClass is defined
- [x] Helm lint passes
- [x] Helm template renders successfully

## CI/CD

- [x] CI workflow exists
- [x] Terraform validation workflow exists
- [x] Helm validation workflow exists
- [x] Security scan workflow exists
- [x] Dev deployment workflow exists
- [x] Prod deployment workflow exists
- [x] KEDA/AKS hardening workflow exists

## Observability

- [x] Structured JSON logs exist
- [x] API `/metrics` endpoint exists
- [x] Ingestion API `/metrics` endpoint exists
- [x] Worker metrics ports exist
- [x] Prometheus runs locally
- [x] Grafana runs locally
- [x] Grafana dashboard is provisioned
- [x] Prometheus alert rules exist
- [x] Log Analytics KQL examples exist
- [x] Application Insights Terraform resource exists

## Documentation

- [x] README exists
- [x] Architecture doc exists
- [x] Security doc exists
- [x] Scalability doc exists
- [x] Reliability doc exists
- [x] Resiliency doc exists
- [x] Observability doc exists
- [x] Automation doc exists
- [x] Trade-offs doc exists
- [x] Database doc exists
- [x] Cloudflare/Application Gateway doc exists
- [x] AKS hardening doc exists
- [x] Interview walkthrough exists

## Honest Limitations

These items are production-designed but not live-deployed in this local repo:

- [ ] Real Azure deployment has not been run
- [ ] Real Cloudflare DNS/WAF rules are not enabled because no real account/zone details are provided
- [ ] Real SMS/email provider integration is mocked locally
- [ ] Real video transcoding is mocked locally
- [ ] Real Azure Key Vault secret mounting requires live AKS, CSI driver, and managed identity
- [ ] Real KEDA scaling requires live AKS, KEDA installed, and Azure queues/event hubs
