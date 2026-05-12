# Assumptions and Trade-Offs

## Assumptions

I made the following assumptions because the test brief does not provide full business details.

The business operates multiple physical venues.

Each venue may have devices such as cameras, kiosks, tablets, game devices, screens, or sensors.

Devices may send frequent logs and events.

Video processing may be slower and heavier than normal API requests.

SMS and email providers may occasionally fail or be slow.

The platform needs to be secure, repeatable, observable, and scalable.

A live Azure deployment may not be available during the interview, so the repo includes a local Docker Compose demo and validation evidence.

## AKS vs Azure Container Apps

I chose AKS for the production design.

AKS is stronger for a production platform with multiple services, workers, ingress, autoscaling, network policies, pod disruption budgets, workload identity, and advanced deployment patterns.

Azure Container Apps would be simpler and cheaper for a smaller MVP.

The trade-off is that AKS has more operational complexity, but it gives better control for a serious platform engineering design.

## Event Hubs vs Service Bus

Event Hubs is used for high-volume device logs and telemetry.

Service Bus is used for reliable business jobs such as SMS, email, video processing, and device commands.

Event Hubs is better for streaming many events.

Service Bus is better when every job matters and needs retry, locking, and dead-letter handling.

## Cloudflare plus Azure Application Gateway

Cloudflare is used at the global edge.

Azure Application Gateway WAF is used inside Azure as the controlled entry point into AKS.

This gives layered protection.

Cloudflare handles edge security and CDN behavior.

Application Gateway handles Azure-native ingress, WAF policies, TLS integration, and private routing into AKS.

The trade-off is more moving parts, but this is stronger for production security.

## PostgreSQL vs Cosmos DB

PostgreSQL is used for relational business data.

This includes venues, devices, guests, configuration, audit logs, and job records.

Cosmos DB could be useful for globally distributed device state, but it is not required for the core design.

PostgreSQL is a better default because the data model is relational and audit-heavy.

## Local Mock Queues

The local demo uses file-backed queues instead of real Azure Event Hubs and Service Bus.

This is intentional.

It proves the service boundaries and worker flow without cloud cost or credentials.

In production, the queue implementation is replaced by Azure Event Hubs and Azure Service Bus.

The trade-off is that the local demo does not prove Azure throughput, but it does prove the application shape and deployment logic.
