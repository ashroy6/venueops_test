# Evidence

This folder stores command output proving the local platform works.

Local mode uses Docker Compose and mock queues:

- Mock Event Hub = local file-backed device log queue
- Mock Service Bus = local file-backed job queue
- SMS/email/video processing = simulated workers

In production:

- Mock Event Hub is replaced by Azure Event Hubs
- Mock Service Bus is replaced by Azure Service Bus
- Local containers are deployed to AKS using Helm
- Images are stored in Azure Container Registry
- Logs, metrics, and traces are sent to Azure Monitor, Log Analytics, Application Insights, Prometheus, and Grafana
