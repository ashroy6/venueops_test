from __future__ import annotations

from typing import Any

import requests

from src.config import API_BASE_URL, INGESTION_BASE_URL
from src.prometheus_client import collect_prometheus_snapshot


HTTP_TIMEOUT_SECONDS = 5


def fetch_json(name: str, url: str) -> dict[str, Any]:
    try:
        response = requests.get(url, timeout=HTTP_TIMEOUT_SECONDS)
        response.raise_for_status()

        return {
            "name": name,
            "url": url,
            "ok": True,
            "status_code": response.status_code,
            "body": response.json(),
        }
    except Exception as exc:
        return {
            "name": name,
            "url": url,
            "ok": False,
            "error": str(exc),
        }


def collect_current_evidence() -> dict[str, Any]:
    return {
        "source": "current_platform_health",
        "service_health": {
            "api": fetch_json("api", f"{API_BASE_URL.rstrip('/')}/health"),
            "ingestion_api": fetch_json(
                "ingestion-api",
                f"{INGESTION_BASE_URL.rstrip('/')}/health",
            ),
        },
        "prometheus": collect_prometheus_snapshot(),
        "notes": [
            "Evidence was collected from service health endpoints and Prometheus.",
            "This local demo uses mock queues and SQLite-backed data.",
        ],
    }


def simulated_incident(kind: str) -> dict[str, Any]:
    clean_kind = (kind or "").strip().lower()

    if clean_kind == "api_5xx_spike":
        return {
            "source": "simulated_incident",
            "kind": clean_kind,
            "symptoms": [
                "Backend API 5xx rate increased after a recent deployment.",
                "Users may see failed admin/dashboard operations.",
                "Ingestion API remains healthy.",
            ],
            "metrics": {
                "api_5xx_rate": "high",
                "api_latency_p95": "elevated",
                "ingestion_api_health": "ok",
                "queue_backlog": "normal",
            },
            "likely_signal": "Bad API deployment or runtime exception in backend API.",
        }

    if clean_kind == "ingestion_slowdown":
        return {
            "source": "simulated_incident",
            "kind": clean_kind,
            "symptoms": [
                "Device logs are arriving slower than expected.",
                "Ingestion API latency is elevated.",
                "Log processor is still running but backlog is growing.",
            ],
            "metrics": {
                "ingestion_latency_p95": "high",
                "device_log_backlog": "growing",
                "api_health": "ok",
                "log_processor_status": "running",
            },
            "likely_signal": "Traffic spike or under-scaled ingestion/log processing path.",
        }

    if clean_kind == "queue_backlog":
        return {
            "source": "simulated_incident",
            "kind": clean_kind,
            "symptoms": [
                "SMS, email, and video jobs are queued faster than workers process them.",
                "Backend API remains healthy.",
                "Worker throughput is below queue growth rate.",
            ],
            "metrics": {
                "jobs_queued": "high",
                "worker_messages_processed": "low",
                "queue_backlog": "growing",
            },
            "likely_signal": "Worker capacity issue or downstream provider delay.",
        }

    return {
        "source": "simulated_incident",
        "kind": clean_kind or "generic",
        "symptoms": [
            "Generic platform incident simulation requested.",
        ],
        "metrics": {
            "risk": "unknown",
        },
        "likely_signal": "Needs investigation.",
    }


# For a real production system, this file would also collect:

# Kubernetes pod status
# Deployment version
# Recent rollout events
# Container restart count
# Error logs from Loki/ELK
# Trace samples
# Cloud provider health events
# Queue depth
# Dead-letter queue count
# Provider API status
# SLO burn rate
# Recent GitHub Actions deployment
# Feature flag changes