from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import requests

from src.config import PROMETHEUS_BASE_URL


PROMETHEUS_TIMEOUT_SECONDS = 5


def query_prometheus(query: str) -> dict[str, Any]:
    url = f"{PROMETHEUS_BASE_URL.rstrip('/')}/api/v1/query?{urlencode({'query': query})}"

    try:
        response = requests.get(url, timeout=PROMETHEUS_TIMEOUT_SECONDS)
        response.raise_for_status()
        body = response.json()

        return {
            "query": query,
            "ok": True,
            "status": body.get("status"),
            "result": body.get("data", {}).get("result", []),
        }
    except Exception as exc:
        return {
            "query": query,
            "ok": False,
            "error": str(exc),
            "result": [],
        }


def collect_prometheus_snapshot() -> dict[str, Any]:
    queries = {
        "targets_up": "up",
        "api_requests": "sum(venueops_api_requests_total)",
        "ingestion_requests": "sum(venueops_ingestion_requests_total)",
        "jobs_queued": "sum(venueops_jobs_queued_total)",
        "device_logs_ingested": "sum(venueops_ingestion_logs_total)",
        "worker_messages_processed": "sum(venueops_worker_messages_processed_total)",
    }

    return {
        name: query_prometheus(query)
        for name, query in queries.items()
    }
