from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient
from pythonjsonlogger import jsonlogger

from src.telemetry import WORKER_MESSAGES_PROCESSED_TOTAL, setup_worker_metrics

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MESSAGE_MODE = os.getenv("MESSAGE_MODE", "local").strip().lower()

LOCAL_QUEUE_PATH = Path(os.getenv("MOCK_SERVICEBUS_QUEUE", "/data/queues/jobs.jsonl"))
OUTPUT_PATH = Path(os.getenv("VIDEO_OUTPUT_PATH", "/data/processed/video_jobs.jsonl"))

SERVICEBUS_NAMESPACE = os.getenv("SERVICEBUS_FULLY_QUALIFIED_NAMESPACE", "").strip()
VIDEO_QUEUE = os.getenv("SERVICEBUS_VIDEO_QUEUE", "video-jobs").strip()

logger = logging.getLogger("venueops.video_processor")
logger.setLevel(LOG_LEVEL)
handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
logger.handlers.clear()
logger.addHandler(handler)


def append_jsonl(path: Path, item: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(item, separators=(",", ":")) + "\n")


def process_job(job: dict[str, Any]) -> None:
    payload = job.get("payload", {})
    result = {
        "job_id": job.get("job_id"),
        "job_type": "process_video",
        "venue_id": payload.get("venue_id"),
        "source_blob": payload.get("source_blob"),
        "processed_blob": f"processed/{job.get('job_id')}.mp4",
        "thumbnail_blob": f"processed/{job.get('job_id')}.jpg",
        "status": "processed_mock",
        "processed_at_ms": int(time.time() * 1000),
    }

    append_jsonl(OUTPUT_PATH, result)
    WORKER_MESSAGES_PROCESSED_TOTAL.labels(worker="video-processor", message_type="process_video", status="processed").inc()
    logger.info("video_job_processed", extra={"job_id": job.get("job_id"), "mode": MESSAGE_MODE})


def split_local_jobs(path: Path) -> list[dict[str, Any]]:
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.touch()
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    remaining: list[str] = []
    selected: list[dict[str, Any]] = []

    for line in lines:
        clean = line.strip()
        if not clean:
            continue

        try:
            job = json.loads(clean)
        except json.JSONDecodeError:
            logger.error("invalid_json_line", extra={"line": clean[:200]})
            continue

        if job.get("job_type") == "process_video":
            selected.append(job)
        else:
            remaining.append(clean)

    path.write_text("\n".join(remaining) + ("\n" if remaining else ""), encoding="utf-8")
    return selected


def run_local() -> None:
    logger.info("video_processor_started", extra={"queue_path": str(LOCAL_QUEUE_PATH), "mode": "local"})

    while True:
        jobs = split_local_jobs(LOCAL_QUEUE_PATH)
        for job in jobs:
            process_job(job)

        time.sleep(3)


def run_azure() -> None:
    if not SERVICEBUS_NAMESPACE:
        raise RuntimeError("SERVICEBUS_FULLY_QUALIFIED_NAMESPACE is required when MESSAGE_MODE=azure")

    logger.info(
        "video_processor_started",
        extra={"namespace": SERVICEBUS_NAMESPACE, "queue": VIDEO_QUEUE, "mode": "azure"},
    )

    credential = DefaultAzureCredential()

    with ServiceBusClient(
        fully_qualified_namespace=SERVICEBUS_NAMESPACE,
        credential=credential,
    ) as client:
        receiver = client.get_queue_receiver(queue_name=VIDEO_QUEUE, max_wait_time=10)

        with receiver:
            while True:
                messages = receiver.receive_messages(max_message_count=5, max_wait_time=10)

                for message in messages:
                    try:
                        body = b"".join(bytes(part) for part in message.body)
                        job = json.loads(body.decode("utf-8"))
                        process_job(job)
                        receiver.complete_message(message)
                    except Exception as exc:
                        logger.exception("video_job_failed", extra={"error": str(exc)})
                        receiver.abandon_message(message)


def main() -> None:
    setup_worker_metrics(default_port=9102)
    if MESSAGE_MODE == "azure":
        run_azure()
    else:
        run_local()


if __name__ == "__main__":
    main()
