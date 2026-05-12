# Resiliency

## Failure Is Expected

The design assumes that failures will happen.

Devices may go offline.

SMS or email providers may fail.

Video processing may take longer than expected.

Pods may crash.

Nodes may be upgraded or replaced.

The platform is designed to absorb these failures.

## Device Resiliency

Devices should not depend on instant backend responses for every operation.

Where possible, commands and processing should be asynchronous.

If a device is temporarily offline, the backend can queue work and retry later.

## Worker Resiliency

Workers process messages from queues.

If a worker crashes, Kubernetes restarts it.

If a message fails repeatedly, it goes to a dead-letter queue.

This prevents poison messages from breaking the whole system.

## Provider Resiliency

SMS and email providers should be called from workers, not directly from the API request path.

Workers can retry with backoff.

If one provider is unavailable, the design can support fallback providers later.

## Video Resiliency

Video processing should be asynchronous.

A failed video job should be retried or moved to a failed state.

Users should not lose the original uploaded video.

Raw and processed videos should be stored in Blob Storage with safe lifecycle and retention settings.

## AKS Resiliency

AKS should use:

- multiple replicas
- multiple availability zones where available
- pod disruption budgets
- readiness/liveness probes
- autoscaling
- monitored node health

## Data Resiliency

PostgreSQL should use backups.

Blob Storage should use soft delete and versioning.

Logs should be written to durable storage.

Critical admin actions should be audit logged.
