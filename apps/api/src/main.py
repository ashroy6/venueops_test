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


def enqueue_job(job_type: str, payload: dict[str, Any], *, count_backlog: bool = True) -> dict[str, Any]:
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


# ---- AI Ops local demo operations endpoints ----

from src.ops_state import backlog_status as _aiops_backlog_status
from src.ops_state import drain_backlog as _aiops_drain_backlog
from src.ops_state import increment_backlog as _aiops_increment_backlog
from src.telemetry import QUEUE_BACKLOG as _AIOPS_QUEUE_BACKLOG
from src.telemetry import QUEUE_BACKLOG_THRESHOLD as _AIOPS_QUEUE_BACKLOG_THRESHOLD


class AiOpsQueueLoadRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=100)
    job_type: str = "send_sms"


class AiOpsDrainQueueRequest(BaseModel):
    target_backlog: int = Field(default=0, ge=0)


def _aiops_sync_backlog_metrics() -> dict[str, Any]:
    status = _aiops_backlog_status()
    _AIOPS_QUEUE_BACKLOG.set(status["queue_backlog"])
    _AIOPS_QUEUE_BACKLOG_THRESHOLD.set(status["threshold"])
    return status


@app.get("/ops/backlog")
def aiops_get_backlog() -> dict[str, Any]:
    return _aiops_sync_backlog_metrics()


@app.post("/ops/load/queue")
def aiops_generate_queue_load(request: AiOpsQueueLoadRequest) -> dict[str, Any]:
    allowed_job_types = {"send_sms", "send_email", "process_video"}

    if request.job_type not in allowed_job_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported job_type. Allowed: {sorted(allowed_job_types)}",
        )

    jobs: list[dict[str, Any]] = []

    for index in range(request.count):
        if request.job_type == "send_email":
            payload = {
                "guest_id": f"guest-load-{index + 1}",
                "email": "guest@example.com",
                "subject": "Load test email",
                "body": "Generated queue load for AI Ops demo.",
            }
        elif request.job_type == "process_video":
            payload = {
                "venue_id": "venue-london-001",
                "source_blob": f"landing/load-video-{index + 1}.mp4",
                "requested_by": "admin-demo",
            }
        else:
            payload = {
                "guest_id": f"guest-load-{index + 1}",
                "phone_number": "+440000000000",
                "message": "Generated queue load for AI Ops demo.",
            }

        job = enqueue_job(request.job_type, payload, count_backlog=False)
        jobs.append(job)

    state = _aiops_increment_backlog(request.count)
    _AIOPS_QUEUE_BACKLOG.set(state["queue_backlog"])
    _AIOPS_QUEUE_BACKLOG_THRESHOLD.set(state["queue_backlog_threshold"])

    status = _aiops_sync_backlog_metrics()

    audit(
        "ops.queue_load.generated",
        "admin-demo",
        {
            "count": request.count,
            "job_type": request.job_type,
            "backlog": status,
        },
    )

    return {
        "status": "queued",
        "message": f"Generated {request.count} {request.job_type} jobs.",
        "backlog": status,
        "items": jobs,
    }


@app.post("/ops/remediate/drain-queue")
def aiops_remediate_drain_queue(request: AiOpsDrainQueueRequest) -> dict[str, Any]:
    result = _aiops_drain_backlog(target=request.target_backlog)
    _AIOPS_QUEUE_BACKLOG.set(result["queue_backlog"])
    _AIOPS_QUEUE_BACKLOG_THRESHOLD.set(result["queue_backlog_threshold"])

    audit(
        "ops.queue_backlog.drained",
        "aiops-runbook",
        {
            "before": result.get("before"),
            "after": result.get("after"),
            "drained": result.get("drained"),
        },
    )

    return {
        "status": "drained",
        "message": "Local mock queue backlog was reduced by the approved AI Ops runbook.",
        "result": result,
    }



# ---- AI Ops local demo API 5xx / bad release endpoints ----

from src.ops_state import api_fault_status as _aiops_api_fault_status
from src.ops_state import set_api_fault as _aiops_set_api_fault
from src.telemetry import API_FAULT_ACTIVE as _AIOPS_API_FAULT_ACTIVE


class AiOpsApiFaultRequest(BaseModel):
    reason: str = "simulated bad API release"


def _aiops_sync_api_fault_metric() -> dict[str, Any]:
    status = _aiops_api_fault_status()
    _AIOPS_API_FAULT_ACTIVE.set(1 if status["api_fault_active"] else 0)
    return status


@app.get("/ops/faults/api-5xx/status")
def aiops_api_fault_status() -> dict[str, Any]:
    return _aiops_sync_api_fault_metric()


@app.post("/ops/faults/api-5xx/enable")
def aiops_enable_api_fault(request: AiOpsApiFaultRequest) -> dict[str, Any]:
    status = _aiops_set_api_fault(True, request.reason)
    _AIOPS_API_FAULT_ACTIVE.set(1)

    audit(
        "ops.api_5xx_fault.enabled",
        "admin-demo",
        {
            "reason": request.reason,
            "status": status,
        },
    )

    return {
        "status": "enabled",
        "message": "Controlled API 5xx fault is now active.",
        "fault": _aiops_sync_api_fault_metric(),
    }


@app.post("/ops/faults/api-5xx/disable")
def aiops_disable_api_fault() -> dict[str, Any]:
    status = _aiops_set_api_fault(False, "")
    _AIOPS_API_FAULT_ACTIVE.set(0)

    audit(
        "ops.api_5xx_fault.disabled",
        "aiops-runbook",
        {
            "status": status,
        },
    )

    return {
        "status": "disabled",
        "message": "Controlled API 5xx fault has been disabled.",
        "fault": _aiops_sync_api_fault_metric(),
    }


@app.get("/ops/test-api")
def aiops_test_api() -> dict[str, Any]:
    status = _aiops_sync_api_fault_metric()

    if status["api_fault_active"]:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Controlled API 5xx fault is active.",
                "reason": status.get("api_fault_reason", "simulated bad release"),
            },
        )

    return {
        "status": "ok",
        "message": "API test endpoint is healthy.",
        "fault": status,
    }



# ---- AI Ops local demo device offline endpoints ----

from src.ops_state import device_health_status as _aiops_device_health_status
from src.ops_state import recover_device as _aiops_recover_device
from src.ops_state import set_device_offline as _aiops_set_device_offline
from src.telemetry import DEVICES_OFFLINE as _AIOPS_DEVICES_OFFLINE


class AiOpsDeviceOfflineRequest(BaseModel):
    device_id: str = "camera-01"


def _aiops_sync_device_metric() -> dict[str, Any]:
    status = _aiops_device_health_status()
    _AIOPS_DEVICES_OFFLINE.set(status["offline_devices"])
    return status


@app.get("/ops/devices/offline/status")
def aiops_device_offline_status() -> dict[str, Any]:
    return _aiops_sync_device_metric()


@app.post("/ops/devices/offline/mark")
def aiops_mark_device_offline(request: AiOpsDeviceOfflineRequest) -> dict[str, Any]:
    state = _aiops_set_device_offline(request.device_id)
    _AIOPS_DEVICES_OFFLINE.set(1)

    audit(
        "ops.device_offline.marked",
        "admin-demo",
        {
            "device_id": request.device_id,
            "state": state,
        },
    )

    return {
        "status": "offline",
        "message": f"Device {request.device_id} was marked offline for AI Ops demo.",
        "device_health": _aiops_sync_device_metric(),
    }


@app.post("/ops/devices/offline/recover")
def aiops_recover_offline_device() -> dict[str, Any]:
    state = _aiops_recover_device()
    _AIOPS_DEVICES_OFFLINE.set(0)

    audit(
        "ops.device_offline.recovered",
        "aiops-runbook",
        {
            "state": state,
        },
    )

    return {
        "status": "recovered",
        "message": "Offline device was recovered by the approved AI Ops runbook.",
        "device_health": _aiops_sync_device_metric(),
    }
