from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from azure.eventhub import EventHubConsumerClient
from azure.identity import DefaultAzureCredential
from pythonjsonlogger import jsonlogger

from src.telemetry import WORKER_MESSAGES_PROCESSED_TOTAL, setup_worker_metrics

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MESSAGE_MODE = os.getenv("MESSAGE_MODE", "local").strip().lower()

LOCAL_QUEUE_PATH = Path(os.getenv("MOCK_EVENTHUB_QUEUE", "/data/queues/device_logs.jsonl"))
OUTPUT_PATH = Path(os.getenv("PROCESSED_LOG_PATH", "/data/processed/processed_device_logs.jsonl"))

EVENTHUB_NAMESPACE = os.getenv("EVENTHUB_FULLY_QUALIFIED_NAMESPACE", "").strip()
EVENTHUB_NAME = os.getenv("EVENTHUB_NAME", "device-logs").strip()
EVENTHUB_CONSUMER_GROUP = os.getenv("EVENTHUB_CONSUMER_GROUP", "log-processors").strip()

logger = logging.getLogger("venueops.log_processor")
logger.setLevel(LOG_LEVEL)
handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
logger.handlers.clear()
logger.addHandler(handler)


def append_jsonl(path: Path, item: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(item, separators=(",", ":")) + "\n")


def process_event(event: dict[str, Any]) -> None:
    processed = {
        "processed_at_ms": int(time.time() * 1000),
        "processor": "log-processor",
        "event_id": event.get("event_id"),
        "venue_id": event.get("venue_id"),
        "device_id": event.get("device_id"),
        "event_type": event.get("event_type"),
        "level": event.get("level"),
        "status": "processed",
    }

    append_jsonl(OUTPUT_PATH, processed)
    WORKER_MESSAGES_PROCESSED_TOTAL.labels(worker="log-processor", message_type=str(event.get("event_type")), status="processed").inc()

    logger.info(
        "device_log_processed",
        extra={
            "event_id": processed.get("event_id"),
            "venue_id": processed.get("venue_id"),
            "device_id": processed.get("device_id"),
            "mode": MESSAGE_MODE,
        },
    )


def read_and_clear_local(path: Path) -> list[dict[str, Any]]:
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.touch()
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("", encoding="utf-8")

    items: list[dict[str, Any]] = []

    for line in lines:
        clean = line.strip()
        if not clean:
            continue

        try:
            items.append(json.loads(clean))
        except json.JSONDecodeError:
            logger.error("invalid_json_line", extra={"line": clean[:200]})

    return items


def run_local() -> None:
    logger.info("log_processor_started", extra={"queue_path": str(LOCAL_QUEUE_PATH), "mode": "local"})

    while True:
        events = read_and_clear_local(LOCAL_QUEUE_PATH)

        for event in events:
            process_event(event)

        time.sleep(3)


def on_event(partition_context, event) -> None:
    try:
        body = event.body_as_str(encoding="UTF-8")
        payload = json.loads(body)
        process_event(payload)

        if partition_context is not None:
            partition_context.update_checkpoint(event)

    except Exception as exc:
        logger.exception("eventhub_message_failed", extra={"error": str(exc)})


def run_azure() -> None:
    if not EVENTHUB_NAMESPACE:
        raise RuntimeError("EVENTHUB_FULLY_QUALIFIED_NAMESPACE is required when MESSAGE_MODE=azure")

    logger.info(
        "log_processor_started",
        extra={
            "namespace": EVENTHUB_NAMESPACE,
            "eventhub": EVENTHUB_NAME,
            "consumer_group": EVENTHUB_CONSUMER_GROUP,
            "mode": "azure",
        },
    )

    credential = DefaultAzureCredential()

    client = EventHubConsumerClient(
        fully_qualified_namespace=EVENTHUB_NAMESPACE,
        eventhub_name=EVENTHUB_NAME,
        consumer_group=EVENTHUB_CONSUMER_GROUP,
        credential=credential,
    )

    with client:
        client.receive(on_event=on_event, starting_position="-1")


def main() -> None:
    setup_worker_metrics(default_port=9101)
    if MESSAGE_MODE == "azure":
        run_azure()
    else:
        run_local()


if __name__ == "__main__":
    main()
