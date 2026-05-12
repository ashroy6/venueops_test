# Architecture

## Overview

VenueOps is designed as a production-grade Azure platform for a business that operates physical venues.

The platform supports:

- a web admin dashboard for central configuration
- backend APIs
- device log ingestion from in-venue devices
- log processing
- video processing
- SMS and email notification jobs
- asynchronous communication between backend systems and devices

The design uses Cloudflare at the edge, Azure for the application platform, and AKS for running containerized services.

## High-Level Flow

External traffic enters through Cloudflare first.

Cloudflare handles DNS, TLS, WAF, DDoS protection, rate limiting, bot protection, and CDN behavior.

After Cloudflare, traffic reaches Azure Application Gateway WAF.

Application Gateway routes traffic into AKS through Kubernetes ingress.

AKS runs the application containers:

- web admin frontend
- backend API
- device ingestion API
- log processor worker
- video processor worker
- notification worker

## Main Request Flow

Admin users access the web dashboard through Cloudflare.

The web dashboard calls the backend API.

The backend API reads and writes business data such as venues, devices, configuration, guests, job status, and audit records.

In production, this data is stored in Azure PostgreSQL.

## Device Log Flow

In-venue devices send logs and events to the device ingestion API.

The ingestion API publishes high-volume device events to Azure Event Hubs.

The log processor worker consumes events from Event Hubs.

Processed logs can be written to Blob Storage, PostgreSQL, and observability systems.

## Video Flow

Video upload or processing requests are handled asynchronously.

A video job is queued through Azure Service Bus.

The video processor worker picks up the job, processes the video, and writes output to Azure Blob Storage.

The final video can be served through signed URLs and Cloudflare CDN.

## Notification Flow

SMS and email requests are not sent directly from the API request path.

The backend API places notification jobs onto Azure Service Bus.

The notification worker consumes these jobs and calls the SMS/email provider.

This keeps the main API fast and protects users from provider delays.

## Asynchronous Device Communication

Backend-to-device commands are queued through Service Bus.

This avoids tight coupling between the backend and physical venue devices.

If a device is offline or slow, the backend can still accept the command and process delivery later.

## Local Demo

The local demo uses Docker Compose.

Azure Event Hubs and Azure Service Bus are mocked with local file-backed queues.

This allows the service flow to be tested without requiring a live Azure subscription.

The production architecture stays the same, but the local mock queues are replaced by Azure managed services.
