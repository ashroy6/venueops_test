# Scalability

## API Scaling

The web app, backend API, and device ingestion API run as Kubernetes deployments in AKS.

They scale horizontally using HPA.

HPA can scale pods based on CPU, memory, or custom metrics.

For example, if the ingestion API receives more device traffic, AKS can increase the number of ingestion API pods.

## Worker Scaling

Workers scale differently from APIs.

Workers are driven by queue or event backlog.

KEDA is used for this.

Examples:

- log processor scales from Event Hub backlog
- notification worker scales from Service Bus queue length
- video processor scales from Service Bus queue length

This is better than CPU-only scaling because workers may have thousands of messages waiting even when CPU is not high.

## Node Scaling

AKS node pools use Cluster Autoscaler.

HPA and KEDA add pods.

Cluster Autoscaler adds nodes when the cluster does not have enough capacity to run those pods.

This gives two layers of scaling:

- pod scaling
- node scaling

## Event Hubs Scaling

Event Hubs is used for high-volume device logs.

It supports partitioned event streams.

More partitions allow more parallel consumers.

The log processor worker can scale out across Event Hub partitions.

## Service Bus Scaling

Service Bus handles reliable jobs.

Separate queues are used for different job types:

- notification jobs
- video jobs
- device commands

This prevents one job type from blocking another.

Workers can scale independently for each queue.

## Storage Scaling

Azure Blob Storage handles raw logs, uploaded videos, and processed videos.

Blob Storage is a better fit for large unstructured files than a relational database.

Cloudflare can cache public or signed media access where appropriate.

## Database Scaling

PostgreSQL stores relational business data.

Scaling options include:

- appropriate SKU sizing
- indexes
- connection pooling
- read replicas if needed
- separating hot device state into Redis

The database should not be used for high-volume raw logs. Those belong in Event Hubs and Blob Storage.
