from __future__ import annotations

import logging
import os
import time
import uuid
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pythonjsonlogger import jsonlogger

from src.eventhub_client import DeviceEventPublisher
from src.telemetry import DEVICE_LOGS_INGESTED_TOTAL, setup_telemetry

APP_ENV = os.getenv("APP_ENV", "local")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logger = logging.getLogger("venueops.ingestion")
logger.setLevel(LOG_LEVEL)
handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
logger.handlers.clear()
logger.addHandler(handler)

publisher = DeviceEventPublisher()

app = FastAPI(
    title="VenueOps Device Ingestion API",
    version="1.0.0",
    description="Receives logs/events from in-venue devices and writes them to the ingestion stream.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if APP_ENV == "local" else [],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_telemetry(app)


class DeviceLog(BaseModel):
    venue_id: str = Field(min_length=1)
    device_id: str = Field(min_length=1)
    level: str = "INFO"
    event_type: str = Field(min_length=1)
    message: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


def now_ms() -> int:
    return int(time.time() * 1000)


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "device-ingestion-api",
        "environment": APP_ENV,
        "message_mode": os.getenv("MESSAGE_MODE", "local"),
        "timestamp_ms": now_ms(),
    }


@app.post("/ingest/logs")
def ingest_log(request: DeviceLog) -> dict[str, Any]:
    event = {
        "event_id": str(uuid.uuid4()),
        "received_at_ms": now_ms(),
        "source": "device-ingestion-api",
        **request.model_dump(),
    }

    publisher.publish(event)
    DEVICE_LOGS_INGESTED_TOTAL.labels(venue_id=request.venue_id, event_type=request.event_type).inc()

    logger.info(
        "device_log_ingested",
        extra={
            "event_id": event["event_id"],
            "venue_id": request.venue_id,
            "device_id": request.device_id,
            "event_type": request.event_type,
        },
    )

    return {
        "status": "accepted",
        "event_id": event["event_id"],
        "message": "Device log accepted into ingestion stream",
    }
