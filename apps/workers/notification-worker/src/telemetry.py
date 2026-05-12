from __future__ import annotations

import os

from prometheus_client import Counter, start_http_server

WORKER_MESSAGES_PROCESSED_TOTAL = Counter(
    "venueops_worker_messages_processed_total",
    "Total worker messages processed.",
    ["worker", "message_type", "status"],
)


def setup_worker_metrics(default_port: int) -> None:
    port = int(os.getenv("METRICS_PORT", str(default_port)))
    start_http_server(port)
