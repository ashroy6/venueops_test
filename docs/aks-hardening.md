# AKS Hardening

## Purpose

This document explains how the production AKS deployment is hardened.

## Namespace Security

The `venueops` namespace uses Kubernetes Pod Security labels set to `restricted`.

This is a strong default because application workloads should not run privileged containers.

## Workload Identity

The Helm chart uses a dedicated service account:

    venueops-workload

In production, this service account is annotated with the Azure workload identity client ID.

This allows pods to access Azure services without hardcoded credentials.

## Key Vault Secrets

Secrets are not committed to Git.

Production secrets are stored in Azure Key Vault.

The AKS deployment can use the Secrets Store CSI driver and SecretProviderClass to mount selected secrets into pods.

Secrets include:

- Application Insights connection string
- database URL
- SMS provider API key
- email provider API key

## KEDA

KEDA is used for event-driven autoscaling.

The Helm chart contains:

- ScaledObject for log processor using Event Hub backlog
- ScaledObject for video processor using Service Bus queue length
- ScaledObject for notification worker using Service Bus queue length
- TriggerAuthentication using Azure workload identity

KEDA should be installed in AKS before applying the VenueOps Helm chart.

Install command:

    bash scripts/install-keda.sh

## HPA

HPA is used for request-driven services:

- web
- backend API
- ingestion API

KEDA is used for worker services.

## Pod Disruption Budgets

PDBs are included so voluntary disruptions do not take all replicas down at once.

## Network Policies

Network policies are included to reduce unrestricted pod-to-pod traffic.

In production, these policies should be tightened further after service communication paths are finalized.

## Resource Limits

Each service has CPU and memory requests and limits.

This prevents one service from starving the cluster.

## Production Notes

Before live deployment, verify:

- AKS has Workload Identity enabled
- KEDA is installed
- Secrets Store CSI driver is installed
- Key Vault access policies or RBAC are configured
- managed identity has only required permissions
- ingress and WAF are tested
- autoscaling rules are tested with queue backlog
