from __future__ import annotations

import time
from collections.abc import Callable

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware

HTTP_REQUESTS_TOTAL = Counter(
    "venueops_ingestion_http_requests_total",
    "Total HTTP requests handled by ingestion API.",
    ["method", "path", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "venueops_ingestion_http_request_duration_seconds",
    "HTTP request duration in seconds for ingestion API.",
    ["method", "path"],
)

DEVICE_LOGS_INGESTED_TOTAL = Counter(
    "venueops_device_logs_ingested_total",
    "Total device logs accepted by ingestion API.",
    ["venue_id", "event_type"],
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
