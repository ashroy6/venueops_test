from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from azure.eventhub import EventData, EventHubProducerClient
from azure.identity import DefaultAzureCredential


class DeviceEventPublisher:
    def __init__(self) -> None:
        self.mode = os.getenv("MESSAGE_MODE", "local").strip().lower()
        self.local_queue = Path(os.getenv("MOCK_EVENTHUB_QUEUE", "/data/queues/device_logs.jsonl"))
        self.eventhub_namespace = os.getenv("EVENTHUB_FULLY_QUALIFIED_NAMESPACE", "").strip()
        self.eventhub_name = os.getenv("EVENTHUB_NAME", "device-logs").strip()

    def publish(self, event: dict[str, Any]) -> None:
        if self.mode == "azure":
            self._publish_azure(event)
            return

        self._publish_local(event)

    def _publish_local(self, event: dict[str, Any]) -> None:
        self.local_queue.parent.mkdir(parents=True, exist_ok=True)
        with self.local_queue.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event, separators=(",", ":")) + "\n")

    def _publish_azure(self, event: dict[str, Any]) -> None:
        if not self.eventhub_namespace:
            raise RuntimeError("EVENTHUB_FULLY_QUALIFIED_NAMESPACE is required when MESSAGE_MODE=azure")

        credential = DefaultAzureCredential()

        producer = EventHubProducerClient(
            fully_qualified_namespace=self.eventhub_namespace,
            eventhub_name=self.eventhub_name,
            credential=credential,
        )

        with producer:
            batch = producer.create_batch()
            batch.add(EventData(json.dumps(event)))
            producer.send_batch(batch)
