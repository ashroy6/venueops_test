from __future__ import annotations

import logging
import os
import time
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pythonjsonlogger import jsonlogger

from src import db
from src.messaging import JobPublisher
from src.telemetry import AUDIT_EVENTS_TOTAL, JOBS_QUEUED_TOTAL, setup_telemetry

APP_ENV = os.getenv("APP_ENV", "local")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logger = logging.getLogger("venueops.api")
logger.setLevel(LOG_LEVEL)
handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
logger.handlers.clear()
logger.addHandler(handler)

publisher = JobPublisher()

app = FastAPI(
    title="VenueOps Backend API",
    version="1.0.0",
    description="Backend API for venue config, device commands, notifications, video jobs, and audit logs.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if APP_ENV == "local" else [],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_telemetry(app)


class ConfigUpdate(BaseModel):
    venue_id: str = Field(min_length=1)
    key: str = Field(min_length=1)
    value: str = Field(min_length=1)
    changed_by: str = "demo-admin"


class SmsRequest(BaseModel):
    guest_id: str = Field(min_length=1)
    phone_number: str = Field(min_length=1)
    message: str = Field(min_length=1)


class EmailRequest(BaseModel):
    guest_id: str = Field(min_length=1)
    email: str = Field(min_length=3)
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)


class DeviceCommand(BaseModel):
    venue_id: str = Field(min_length=1)
    device_id: str = Field(min_length=1)
    command: str = Field(min_length=1)
    requested_by: str = "demo-admin"


class VideoJob(BaseModel):
    venue_id: str = Field(min_length=1)
    source_blob: str = Field(min_length=1)
    requested_by: str = "demo-admin"


@app.on_event("startup")
def startup() -> None:
    db.init_db()
    logger.info("database_initialized", extra={"database_url": os.getenv("DATABASE_URL", "sqlite:////data/db/venueops.db")})


def now_ms() -> int:
    return int(time.time() * 1000)


def audit(action: str, actor: str, payload: dict[str, Any]) -> None:
    event = {
        "audit_id": str(uuid.uuid4()),
        "timestamp_ms": now_ms(),
        "service": "backend-api",
        "action": action,
        "actor": actor,
        "payload": payload,
    }

    db.record_audit(event)
    AUDIT_EVENTS_TOTAL.labels(action=action).inc()
    logger.info("audit_event", extra={"action": action, "actor": actor})


def enqueue_job(job_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    job = {
        "job_id": str(uuid.uuid4()),
        "job_type": job_type,
        "created_at_ms": now_ms(),
        "status": "queued",
        "payload": payload,
    }

    db.record_job(job)
    JOBS_QUEUED_TOTAL.labels(job_type=job_type).inc()
    publisher.publish(job_type=job_type, payload=payload, job=job)

    logger.info("job_queued", extra={"job_id": job["job_id"], "job_type": job_type})

    return job


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "backend-api",
        "environment": APP_ENV,
        "message_mode": os.getenv("MESSAGE_MODE", "local"),
        "database_mode": os.getenv("DATABASE_MODE", "sqlite"),
        "timestamp_ms": now_ms(),
    }


@app.get("/venues")
def venues() -> dict[str, Any]:
    return {"items": db.list_venues()}


@app.get("/devices")
def devices() -> dict[str, Any]:
    return {"items": db.list_devices()}


@app.get("/jobs")
def jobs() -> dict[str, Any]:
    return {"items": db.list_jobs()}


@app.post("/config")
def update_config(request: ConfigUpdate) -> dict[str, Any]:
    audit("config.updated", request.changed_by, request.model_dump())
    return {
        "status": "accepted",
        "message": "Configuration update recorded",
        "venue_id": request.venue_id,
        "key": request.key,
    }


@app.post("/notifications/sms")
def send_sms(request: SmsRequest) -> dict[str, Any]:
    job = enqueue_job("send_sms", request.model_dump())
    audit("notification.sms.requested", request.guest_id, {"job_id": job["job_id"]})
    return {"status": "queued", "job": job}


@app.post("/notifications/email")
def send_email(request: EmailRequest) -> dict[str, Any]:
    job = enqueue_job("send_email", request.model_dump())
    audit("notification.email.requested", request.guest_id, {"job_id": job["job_id"]})
    return {"status": "queued", "job": job}


@app.post("/device-command")
def device_command(request: DeviceCommand) -> dict[str, Any]:
    allowed_commands = {"restart", "refresh_config", "upload_diagnostics"}

    if request.command not in allowed_commands:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported command '{request.command}'. Allowed: {sorted(allowed_commands)}",
        )

    job = enqueue_job("device_command", request.model_dump())
    audit("device.command.requested", request.requested_by, {"job_id": job["job_id"], **request.model_dump()})
    return {"status": "queued", "job": job}


@app.post("/videos/process")
def process_video(request: VideoJob) -> dict[str, Any]:
    job = enqueue_job("process_video", request.model_dump())
    audit("video.processing.requested", request.requested_by, {"job_id": job["job_id"], **request.model_dump()})
    return {"status": "queued", "job": job}


@app.get("/audit")
def read_audit() -> dict[str, Any]:
    return {"items": db.list_audit_logs()}
