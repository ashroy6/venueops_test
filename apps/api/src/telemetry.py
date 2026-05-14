from __future__ import annotations

import time
from collections.abc import Callable

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware

HTTP_REQUESTS_TOTAL = Counter(
    "venueops_api_http_requests_total",
    "Total HTTP requests handled by the backend API.",
    ["method", "path", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "venueops_api_http_request_duration_seconds",
    "HTTP request duration in seconds for backend API.",
    ["method", "path"],
)

JOBS_QUEUED_TOTAL = Counter(
    "venueops_api_jobs_queued_total",
    "Total jobs queued by backend API.",
    ["job_type"],
)

AUDIT_EVENTS_TOTAL = Counter(
    "venueops_api_audit_events_total",
    "Total audit events recorded by backend API.",
    ["action"],
)

QUEUE_BACKLOG = Gauge(
    "venueops_api_queue_backlog",
    "Current local mock async queue backlog.",
)

QUEUE_BACKLOG_THRESHOLD = Gauge(
    "venueops_api_queue_backlog_threshold",
    "Queue backlog threshold that triggers AI Ops alerting.",
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        path = request.url.path

        if path != "/metrics":
            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                path=path,
                status=str(response.status_code),
            ).inc()

            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=request.method,
                path=path,
            ).observe(duration)

        return response


def setup_telemetry(app: FastAPI) -> None:
    app.add_middleware(PrometheusMiddleware)

    @app.get("/metrics")
    def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)



API_FAULT_ACTIVE = Gauge(
    "venueops_api_fault_active",
    "Whether the local bad API release / 5xx fault simulation is active. 1 means active.",
)



DEVICES_OFFLINE = Gauge(
    "venueops_devices_offline",
    "Number of venue devices currently marked offline.",
)
