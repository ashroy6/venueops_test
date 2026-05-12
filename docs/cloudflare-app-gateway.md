# Cloudflare and Azure Application Gateway

## Purpose

This design uses two edge/security layers.

Cloudflare is the global edge.

Azure Application Gateway WAF is the Azure entry point.

The reason for using both is layered protection.

Cloudflare handles global DNS, TLS, CDN, DDoS protection, bot protection, WAF rules, and rate limiting.

Application Gateway WAF controls the Azure origin and routes traffic into AKS.

## Production Traffic Flow

Users and devices reach Cloudflare first.

Cloudflare forwards allowed traffic to Azure Application Gateway.

Application Gateway routes traffic to AKS ingress.

AKS ingress routes traffic to web, backend API, and ingestion API services.

Flow:

    User / Device
      -> Cloudflare
      -> Azure Application Gateway WAF
      -> AKS Ingress
      -> AKS Service
      -> Pod

## Why Cloudflare

Cloudflare provides:

- DNS
- CDN
- DDoS protection
- WAF rules
- bot protection
- rate limiting
- TLS edge controls
- security analytics

This protects the app before traffic reaches Azure.

## Why Application Gateway

Application Gateway provides:

- Azure-native WAF
- controlled origin entry
- routing into AKS
- autoscaling
- health probes
- TLS integration
- integration path for AKS ingress

It acts as the Azure boundary before traffic enters the Kubernetes platform.

## Origin Lockdown

In production, Azure origin should not be open to the whole internet.

Recommended controls:

- allow only Cloudflare IP ranges to reach Application Gateway where feasible
- use Cloudflare Full Strict TLS
- use WAF rules on both Cloudflare and Application Gateway
- block direct origin access if the platform design allows it
- log Cloudflare and Application Gateway access/security events

## Current Repo Status

Terraform now creates:

- Application Gateway public IP
- Application Gateway WAF_v2
- Application Gateway WAF policy
- backend pool placeholder
- HTTP listener
- routing rule
- health probe

Cloudflare is represented as a safe Terraform design marker.

Real Cloudflare DNS/WAF/rate-limit resources are intentionally not hardcoded yet because the real zone ID, account ID, hostname, and policy requirements are not available in this local interview environment.

## Production Follow-Up

When real Cloudflare details are available, add:

- proxied DNS record for the app hostname
- WAF managed rules
- custom WAF rules for API and ingestion paths
- rate limits for sensitive routes
- bot protection
- Cloudflare Logpush
- origin lockdown rules
