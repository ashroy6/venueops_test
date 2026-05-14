from __future__ import annotations

from typing import Any

from src.config import API_BASE_URL, INGESTION_BASE_URL
from src.evidence_collector import fetch_json
from src.prometheus_client import query_prometheus


def _passed(ok: bool) -> str:
    return "passed" if ok else "failed"


def _extract_prometheus_value(result: dict[str, Any]) -> float | None:
    try:
        items = result.get("result", [])
        if not items:
            return None
        return float(items[0]["value"][1])
    except Exception:
        return None


def verify_platform_health() -> dict[str, Any]:
    api_health = fetch_json("backend_api_health", f"{API_BASE_URL.rstrip('/')}/health")
    ingestion_health = fetch_json(
        "ingestion_api_health",
        f"{INGESTION_BASE_URL.rstrip('/')}/health",
    )
    backlog = fetch_json("queue_backlog", f"{API_BASE_URL.rstrip('/')}/ops/backlog")
    api_fault = fetch_json("api_fault_status", f"{API_BASE_URL.rstrip('/')}/ops/faults/api-5xx/status")
    device_health = fetch_json("device_health_status", f"{API_BASE_URL.rstrip('/')}/ops/devices/offline/status")

    prometheus_up = query_prometheus("up")
    aiops_metric = query_prometheus("venueops_aiops_runbook_approvals_total")
    backlog_metric = query_prometheus("venueops_api_queue_backlog")
    api_fault_metric = query_prometheus("venueops_api_fault_active")
    devices_offline_metric = query_prometheus("venueops_devices_offline")

    backlog_value = None
    backlog_threshold = None

    if backlog.get("ok"):
        body = backlog.get("body", {})
        backlog_value = int(body.get("queue_backlog", 999999))
        backlog_threshold = int(body.get("threshold", 10))

    prometheus_backlog_value = _extract_prometheus_value(backlog_metric)

    checks = [
        {
            "name": "backend_api_health",
            "status": _passed(
                bool(api_health.get("ok"))
                and api_health.get("body", {}).get("status") == "ok"
            ),
            "details": api_health,
        },
        {
            "name": "ingestion_api_health",
            "status": _passed(
                bool(ingestion_health.get("ok"))
                and ingestion_health.get("body", {}).get("status") == "ok"
            ),
            "details": ingestion_health,
        },
        {
            "name": "queue_backlog_below_threshold",
            "status": _passed(
                backlog_value is not None
                and backlog_threshold is not None
                and backlog_value < backlog_threshold
            ),
            "details": backlog,
        },
        {
            "name": "api_5xx_fault_disabled",
            "status": _passed(
                bool(api_fault.get("ok"))
                and api_fault.get("body", {}).get("api_fault_active") is False
            ),
            "details": api_fault,
        },
        {
            "name": "device_offline_count_zero",
            "status": _passed(
                bool(device_health.get("ok"))
                and int(device_health.get("body", {}).get("offline_devices", 1)) == 0
            ),
            "details": device_health,
        },
        {
            "name": "prometheus_targets_query",
            "status": _passed(
                bool(prometheus_up.get("ok"))
                and len(prometheus_up.get("result", [])) > 0
            ),
            "details": prometheus_up,
        },
        {
            "name": "prometheus_queue_backlog_metric",
            "status": _passed(
                bool(backlog_metric.get("ok"))
                and prometheus_backlog_value is not None
            ),
            "details": backlog_metric,
        },
        {
            "name": "prometheus_api_fault_metric",
            "status": _passed(bool(api_fault_metric.get("ok"))),
            "details": api_fault_metric,
        },
        {
            "name": "prometheus_devices_offline_metric",
            "status": _passed(bool(devices_offline_metric.get("ok"))),
            "details": devices_offline_metric,
        },
        {
            "name": "aiops_approval_metric_query",
            "status": _passed(bool(aiops_metric.get("ok"))),
            "details": aiops_metric,
        },
    ]

    failed = [check for check in checks if check["status"] != "passed"]

    return {
        "status": "passed" if not failed else "failed",
        "summary": (
            "Platform health and queue backlog verification passed."
            if not failed
            else "Platform health verification failed for one or more checks."
        ),
        "checks": checks,
    }
