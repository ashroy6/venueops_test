# Observability

## Overview

Observability is designed across metrics, logs, traces, alerts, and audit logs.

The goal is to know what is happening before users complain.

## Metrics

Prometheus collects Kubernetes and application metrics.

Grafana displays dashboards.

Important metrics:

- API request count
- API latency
- API error rate
- pod CPU and memory
- pod restarts
- Service Bus queue backlog
- Event Hub consumer lag
- video job duration
- notification success/failure count

## Logs

Azure Log Analytics stores platform and container logs.

Logs should be structured as JSON where possible.

Useful log fields:

- timestamp
- service name
- environment
- request ID
- venue ID
- device ID
- job ID
- status
- error message

## Traces

OpenTelemetry is used for distributed tracing.

Application Insights receives trace data.

A useful trace example:

Backend API
  -> Service Bus
  -> notification worker
  -> SMS provider

This helps engineers find where time was spent or where a failure happened.

## Alerts

Alerts should be configured for:

- API 5xx rate
- high API latency
- pod crash loops
- AKS node not ready
- Service Bus backlog
- Event Hub consumer lag
- video processing failures
- SMS/email provider failures
- PostgreSQL CPU or storage pressure
- Cloudflare WAF attack spike

## Dashboards

Production dashboards should include:

- AKS overview
- API health
- ingestion health
- worker processing
- queue backlog
- Event Hub lag
- video jobs
- notification jobs
- business health

## Audit Logs

Audit logs are different from technical logs.

They answer who did what.

Examples:

- who changed venue config
- who sent a device command
- who triggered a notification
- what changed
- when it changed

Audit logs are stored in PostgreSQL and can be shown in the admin dashboard.
