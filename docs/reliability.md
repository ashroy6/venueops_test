# Reliability

## Health Checks

Each API container has a health endpoint.

Kubernetes uses readiness and liveness probes.

Readiness checks decide if a pod should receive traffic.

Liveness checks decide if a pod should be restarted.

## Multiple Replicas

Production uses multiple replicas for web, API, and ingestion services.

This avoids a single pod becoming a single point of failure.

## Pod Disruption Budgets

PDBs help keep a minimum number of pods available during node upgrades or voluntary disruptions.

This is important for production AKS maintenance.

## Retry and Dead-Lettering

Service Bus queues use retry and dead-letter behavior.

If a message keeps failing, it should move to a dead-letter queue instead of blocking the whole system.

This is important for SMS, email, video, and device command jobs.

## Queue-First Design

Slow work is moved out of the main request path.

Examples:

- SMS sending
- email sending
- video processing
- device commands

The API accepts the request and queues a job.

A worker processes the job separately.

This keeps the API reliable even when downstream providers are slow.

## Backups

PostgreSQL should have backups enabled.

Blob Storage should use soft delete, versioning, and lifecycle rules.

Terraform state should be stored remotely with locking and backup.

## Deployment Safety

Production deployment should use:

- immutable image tags
- manual approval
- smoke tests
- rollback plan
- deployment evidence

This reduces the chance of bad deployments reaching users.
