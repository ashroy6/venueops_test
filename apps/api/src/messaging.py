from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient, ServiceBusMessage


class JobPublisher:
    def __init__(self) -> None:
        self.mode = os.getenv("MESSAGE_MODE", "local").strip().lower()
        self.local_queue = Path(os.getenv("MOCK_SERVICEBUS_QUEUE", "/data/queues/jobs.jsonl"))

        self.servicebus_namespace = os.getenv("SERVICEBUS_FULLY_QUALIFIED_NAMESPACE", "").strip()
        self.notification_queue = os.getenv("SERVICEBUS_NOTIFICATION_QUEUE", "notification-jobs").strip()
        self.video_queue = os.getenv("SERVICEBUS_VIDEO_QUEUE", "video-jobs").strip()
        self.device_command_queue = os.getenv("SERVICEBUS_DEVICE_COMMAND_QUEUE", "device-commands").strip()

    def publish(self, *, job_type: str, payload: dict[str, Any], job: dict[str, Any]) -> None:
        if self.mode == "azure":
            self._publish_azure(job_type=job_type, job=job)
            return

        self._publish_local(job)

    def _publish_local(self, job: dict[str, Any]) -> None:
        self.local_queue.parent.mkdir(parents=True, exist_ok=True)
        with self.local_queue.open("a", encoding="utf-8") as file:
            file.write(json.dumps(job, separators=(",", ":")) + "\n")

    def _queue_for_job_type(self, job_type: str) -> str:
        if job_type in {"send_sms", "send_email"}:
            return self.notification_queue

        if job_type == "process_video":
            return self.video_queue

        if job_type == "device_command":
            return self.device_command_queue

        raise ValueError(f"Unsupported job type for Service Bus routing: {job_type}")

    def _publish_azure(self, *, job_type: str, job: dict[str, Any]) -> None:
        if not self.servicebus_namespace:
            raise RuntimeError("SERVICEBUS_FULLY_QUALIFIED_NAMESPACE is required when MESSAGE_MODE=azure")

        queue_name = self._queue_for_job_type(job_type)
        credential = DefaultAzureCredential()

        with ServiceBusClient(
            fully_qualified_namespace=self.servicebus_namespace,
            credential=credential,
        ) as client:
            sender = client.get_queue_sender(queue_name=queue_name)
            with sender:
                sender.send_messages(ServiceBusMessage(json.dumps(job)))
