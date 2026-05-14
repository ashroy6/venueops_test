from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Literal

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from pydantic import BaseModel
from starlette.responses import Response

from src.audit_store import append_audit, read_audit, utc_now
from src.config import APP_ENV, API_BASE_URL, OLLAMA_BASE_URL, OLLAMA_MODEL
from src.evidence_collector import collect_current_evidence, simulated_incident
from src.incident_analyzer import analyze_incident
from src.runbook_registry import get_runbook, list_runbooks
from src.verifier import verify_platform_health


DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
LATEST_INCIDENT_PATH = DATA_DIR / "audit" / "aiops_latest_incident.json"


app = FastAPI(
    title="VenueOps AI Ops Service",
    version="0.1.0",
    description="Incident analysis, runbook recommendation, approval, verification, and audit service.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

ANALYSES_TOTAL = Counter(
    "venueops_aiops_analyses_total",
    "Total number of AI Ops incident analyses.",
)

ALERT_WEBHOOKS_TOTAL = Counter(
    "venueops_aiops_alert_webhooks_total",
    "Total Alertmanager webhooks received by AI Ops.",
    ["alertname", "status"],
)


ALERT_DUPLICATES_TOTAL = Counter(
    "venueops_aiops_alert_duplicates_total",
    "Repeated Alertmanager webhooks ignored because an active incident already exists.",
    ["alertname", "incident_kind"],
)

APPROVALS_TOTAL = Counter(
    "venueops_aiops_runbook_approvals_total",
    "Total number of AI Ops runbook approvals.",
)

REMEDIATIONS_TOTAL = Counter(
    "venueops_aiops_remediations_total",
    "Total number of AI Ops local remediations performed.",
    ["runbook_id", "status"],
)

VERIFICATIONS_TOTAL = Counter(
    "venueops_aiops_verifications_total",
    "Total number of AI Ops post-runbook verifications.",
)


class SimulateRequest(BaseModel):
    kind: Literal["api_5xx_spike", "ingestion_slowdown", "queue_backlog", "generic"] = "generic"


class AnalyzeRequest(BaseModel):
    incident_kind: str | None = None
    evidence: dict[str, Any] | None = None


class ApproveRunbookRequest(BaseModel):
    runbook_id: str
    approved_by: str = "admin-demo"
    execute: bool = True
    verify: bool = True


def _save_latest_incident(payload: dict[str, Any]) -> None:
    LATEST_INCIDENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    LATEST_INCIDENT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _read_latest_incident() -> dict[str, Any]:
    if not LATEST_INCIDENT_PATH.exists():
        return {"status": "empty", "message": "No AI Ops incident has been created yet."}

    try:
        return json.loads(LATEST_INCIDENT_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def _update_latest_incident_lifecycle(
    *,
    lifecycle_status: str,
    remediation: dict[str, Any] | None = None,
    verification: dict[str, Any] | None = None,
    closed_by: str | None = None,
) -> dict[str, Any]:
    incident = _read_latest_incident()

    if incident.get("status") in {"empty", "error"}:
        return incident

    incident["lifecycle_status"] = lifecycle_status
    incident["updated_at"] = utc_now()

    if remediation is not None:
        incident["remediation"] = remediation

    if verification is not None:
        incident["verification"] = verification

    if lifecycle_status in {"verified_resolved", "closed"}:
        incident["resolved"] = True
        incident["resolved_at"] = utc_now()

    if lifecycle_status == "closed":
        incident["closed"] = True
        incident["closed_by"] = closed_by or "admin-demo"
        incident["closed_at"] = utc_now()

    _save_latest_incident(incident)
    return incident


def _alert_to_incident_kind(alert: dict[str, Any]) -> str:
    labels = alert.get("labels", {}) if isinstance(alert, dict) else {}
    alertname = str(labels.get("alertname", "")).strip()

    incident_kind = str(labels.get("incident_kind", "")).strip()
    if incident_kind:
        return incident_kind

    mapping = {
        "QueueBacklogHigh": "queue_backlog",
        "DeviceOffline": "device_offline",
        "Api5xxFaultActive": "api_5xx_spike",
        "VenueOpsApiHighErrorRate": "api_5xx_spike",
        "VenueOpsIngestionHighErrorRate": "ingestion_slowdown",
    }

    return mapping.get(alertname, "generic")


def _build_evidence_from_alert(alert_payload: dict[str, Any]) -> dict[str, Any]:
    alerts = alert_payload.get("alerts", [])
    first_alert = alerts[0] if alerts else {}
    labels = first_alert.get("labels", {}) if isinstance(first_alert, dict) else {}
    annotations = first_alert.get("annotations", {}) if isinstance(first_alert, dict) else {}

    incident_kind = _alert_to_incident_kind(first_alert)
    base = simulated_incident(incident_kind)

    base["source"] = "alertmanager"
    base["alertmanager"] = {
        "status": alert_payload.get("status"),
        "receiver": alert_payload.get("receiver"),
        "group_labels": alert_payload.get("groupLabels", {}),
        "common_labels": alert_payload.get("commonLabels", {}),
        "alert_labels": labels,
        "alert_annotations": annotations,
    }
    if incident_kind == "device_offline":
        base.update(
            {
                "kind": "device_offline",
                "source": "alertmanager",
                "likely_signal": "A venue device stopped sending heartbeat events.",
                "symptoms": [
                    "A venue camera/kiosk/sensor is marked offline.",
                    "Device heartbeat is missing or stale.",
                    "Venue operations may have partial device coverage.",
                ],
                "metrics": {
                    "offline_devices": "1",
                    "device_health": "degraded",
                },
            }
        )

    base["symptoms"] = list(base.get("symptoms", [])) + [
        annotations.get("summary", "Prometheus alert fired."),
        annotations.get("description", "Alertmanager routed this alert to AI Ops."),
    ]

    return base


def _is_duplicate_active_alert(*, alertname: str, incident_kind: str) -> tuple[bool, dict[str, Any]]:
    latest = _read_latest_incident()

    if not isinstance(latest, dict):
        return False, {}

    lifecycle_status = latest.get("lifecycle_status")
    if lifecycle_status not in {"active", "runbook_reviewed", "remediated"}:
        return False, latest

    analysis = latest.get("analysis", {})
    evidence = analysis.get("evidence", {}) if isinstance(analysis, dict) else {}
    alertmanager = evidence.get("alertmanager", {}) if isinstance(evidence, dict) else {}
    alert_labels = alertmanager.get("alert_labels", {}) if isinstance(alertmanager, dict) else {}

    latest_alertname = str(alert_labels.get("alertname", ""))
    latest_kind = str(evidence.get("kind", ""))

    if latest_alertname == alertname and latest_kind == incident_kind:
        return True, latest

    return False, latest


def _record_duplicate_alert(*, alertname: str, incident_kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    latest = _read_latest_incident()
    duplicate_count = int(latest.get("duplicate_alert_count", 0)) + 1 if isinstance(latest, dict) else 1

    if isinstance(latest, dict) and latest.get("status") not in {"empty", "error"}:
        latest["duplicate_alert_count"] = duplicate_count
        latest["last_duplicate_alert_at"] = utc_now()
        latest["last_duplicate_alert_payload_status"] = payload.get("status")
        _save_latest_incident(latest)

    ALERT_DUPLICATES_TOTAL.labels(
        alertname=alertname,
        incident_kind=incident_kind,
    ).inc()

    record = append_audit(
        "aiops_duplicate_alert_ignored",
        {
            "alertname": alertname,
            "incident_kind": incident_kind,
            "duplicate_alert_count": duplicate_count,
            "reason": "Active incident already exists; skipped repeated Ollama analysis.",
        },
    )

    return {
        "status": "duplicate_active_incident_ignored",
        "message": "Active incident already exists. Repeated alert webhook was recorded but not re-analyzed.",
        "duplicate_alert_count": duplicate_count,
        "incident": latest,
        "audit": record,
    }


def _apply_policy_overrides(result: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    kind = evidence.get("kind")

    if kind == "device_offline":
        runbook = get_runbook("investigate_device_connectivity")
        result.update(
            {
                "incident_summary": "Venue device is offline",
                "likely_root_cause": "A camera, kiosk, or IoT device stopped sending heartbeat events.",
                "confidence": "high",
                "risk_level": "medium",
                "recommended_runbook": "investigate_device_connectivity",
                "recommended_runbook_details": runbook,
                "approval_required": "true",
                "verification_steps": (runbook or {}).get("verification_steps", []),
            }
        )

    return result


def _run_local_remediation(runbook_id: str) -> dict[str, Any]:
    if runbook_id in {"investigate_provider_failure", "scale_ingestion_api"}:
        try:
            response = requests.post(
                f"{API_BASE_URL.rstrip('/')}/ops/remediate/drain-queue",
                json={"target_backlog": 0},
                timeout=10,
            )
            response.raise_for_status()
            body = response.json()
            REMEDIATIONS_TOTAL.labels(runbook_id=runbook_id, status="success").inc()
            return {
                "status": "success",
                "mode": "local_safe_remediation",
                "message": "Local mock queue backlog was drained through the backend remediation endpoint.",
                "backend_response": body,
            }
        except Exception as exc:
            REMEDIATIONS_TOTAL.labels(runbook_id=runbook_id, status="failed").inc()
            return {
                "status": "failed",
                "mode": "local_safe_remediation",
                "message": str(exc),
            }

    if runbook_id == "rollback_release":
        try:
            response = requests.post(
                f"{API_BASE_URL.rstrip('/')}/ops/faults/api-5xx/disable",
                timeout=10,
            )
            response.raise_for_status()
            body = response.json()
            REMEDIATIONS_TOTAL.labels(runbook_id=runbook_id, status="success").inc()
            return {
                "status": "success",
                "mode": "local_safe_remediation",
                "message": "Local bad API release simulation was rolled back by disabling the API 5xx fault flag.",
                "backend_response": body,
            }
        except Exception as exc:
            REMEDIATIONS_TOTAL.labels(runbook_id=runbook_id, status="failed").inc()
            return {
                "status": "failed",
                "mode": "local_safe_remediation",
                "message": str(exc),
            }

    if runbook_id == "investigate_device_connectivity":
        try:
            response = requests.post(
                f"{API_BASE_URL.rstrip('/')}/ops/devices/offline/recover",
                timeout=10,
            )
            response.raise_for_status()
            body = response.json()
            REMEDIATIONS_TOTAL.labels(runbook_id=runbook_id, status="success").inc()
            return {
                "status": "success",
                "mode": "local_safe_remediation",
                "message": "Local device connectivity remediation simulated heartbeat recovery.",
                "backend_response": body,
            }
        except Exception as exc:
            REMEDIATIONS_TOTAL.labels(runbook_id=runbook_id, status="failed").inc()
            return {
                "status": "failed",
                "mode": "local_safe_remediation",
                "message": str(exc),
            }

    REMEDIATIONS_TOTAL.labels(runbook_id=runbook_id, status="simulated").inc()
    return {
        "status": "simulated_success",
        "mode": "simulated",
        "message": "No real production command was executed for this runbook.",
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "aiops",
        "environment": APP_ENV,
        "llm_provider": "ollama",
        "ollama_base_url": OLLAMA_BASE_URL,
        "ollama_model": OLLAMA_MODEL,
    }


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/runbooks")
def runbooks() -> dict[str, Any]:
    return {"items": list_runbooks()}


@app.get("/runbooks/{runbook_id}")
def runbook_by_id(runbook_id: str) -> dict[str, Any]:
    runbook = get_runbook(runbook_id)
    if not runbook:
        raise HTTPException(status_code=404, detail="Runbook not found")

    append_audit(
        "aiops_runbook_viewed",
        {
            "runbook_id": runbook_id,
            "source": "admin-ui",
        },
    )

    return {"runbook": runbook}


@app.get("/incidents/latest")
def latest_incident(include_closed: bool = False) -> dict[str, Any]:
    incident = _read_latest_incident()

    if incident.get("status") in {"empty", "error"}:
        return incident

    if incident.get("lifecycle_status") == "closed" and not include_closed:
        return {
            "status": "empty",
            "message": "No active AI Ops incidents.",
            "last_closed_incident": {
                "lifecycle_status": incident.get("lifecycle_status"),
                "closed": incident.get("closed"),
                "closed_by": incident.get("closed_by"),
                "closed_at": incident.get("closed_at"),
                "resolved_at": incident.get("resolved_at"),
            },
        }

    return incident


@app.post("/incidents/from-alert")
async def incident_from_alert(request: Request) -> dict[str, Any]:
    payload = await request.json()
    alerts = payload.get("alerts", [])
    first_alert = alerts[0] if alerts else {}
    labels = first_alert.get("labels", {}) if isinstance(first_alert, dict) else {}
    alertname = str(labels.get("alertname", "unknown"))
    status = str(payload.get("status", "unknown"))

    ALERT_WEBHOOKS_TOTAL.labels(alertname=alertname, status=status).inc()

    if status == "resolved":
        record = append_audit(
            "aiops_alert_resolved",
            {
                "alertname": alertname,
                "payload": payload,
            },
        )
        return {"status": "resolved_recorded", "audit": record}

    incident_kind = _alert_to_incident_kind(first_alert)
    is_duplicate, _latest = _is_duplicate_active_alert(
        alertname=alertname,
        incident_kind=incident_kind,
    )

    if is_duplicate:
        return _record_duplicate_alert(
            alertname=alertname,
            incident_kind=incident_kind,
            payload=payload,
        )

    evidence = _build_evidence_from_alert(payload)
    result = _apply_policy_overrides(analyze_incident(evidence), evidence)
    ANALYSES_TOTAL.inc()

    record = append_audit(
        "aiops_incident_created_from_alert",
        {
            "alertname": alertname,
            "incident_kind": evidence.get("kind"),
            "recommended_runbook": result.get("recommended_runbook"),
            "risk_level": result.get("risk_level"),
            "approval_required": result.get("approval_required"),
            "llm_status": result.get("llm_status"),
        },
    )

    response_payload = {
        "status": "incident_created",
        "lifecycle_status": "active",
        "resolved": False,
        "trigger": "alertmanager",
        "analysis": result,
        "audit": record,
        "alert": payload,
    }
    _save_latest_incident(response_payload)
    return response_payload


@app.post("/incidents/simulate")
def simulate_incident_endpoint(payload: SimulateRequest) -> dict[str, Any]:
    evidence = simulated_incident(payload.kind)

    record = append_audit(
        "aiops_incident_simulated",
        {
            "kind": payload.kind,
            "evidence": evidence,
        },
    )

    return {
        "incident": evidence,
        "audit": record,
    }


@app.post("/incidents/analyze")
def analyze(payload: AnalyzeRequest) -> dict[str, Any]:
    if payload.evidence:
        evidence = payload.evidence
    elif payload.incident_kind:
        evidence = simulated_incident(payload.incident_kind)
    else:
        evidence = collect_current_evidence()

    result = _apply_policy_overrides(analyze_incident(evidence), evidence)
    ANALYSES_TOTAL.inc()

    record = append_audit(
        "aiops_incident_analyzed",
        {
            "evidence_source": evidence.get("source"),
            "incident_kind": evidence.get("kind"),
            "recommended_runbook": result.get("recommended_runbook"),
            "risk_level": result.get("risk_level"),
            "approval_required": result.get("approval_required"),
            "llm_status": result.get("llm_status"),
            "llm_called": result.get("llm_status", {}).get("called"),
            "llm_accepted": result.get("llm_status", {}).get("accepted"),
            "fallback_used": result.get("llm_status", {}).get("fallback_used"),
        },
    )

    response_payload = {
        "analysis": result,
        "audit": record,
    }
    _save_latest_incident({
        "status": "incident_created",
        "lifecycle_status": "active",
        "resolved": False,
        "trigger": "manual_analysis",
        **response_payload,
    })
    return response_payload


@app.post("/runbooks/approve")
def approve_runbook(payload: ApproveRunbookRequest) -> dict[str, Any]:
    runbook = get_runbook(payload.runbook_id)

    if not runbook:
        raise HTTPException(status_code=404, detail="Runbook not found")

    APPROVALS_TOTAL.inc()

    execution_result = _run_local_remediation(payload.runbook_id) if payload.execute else {
        "status": "approval_recorded",
        "mode": "approval_only",
        "message": "Runbook approval was recorded. Execution was not requested.",
    }

    verification = None
    if payload.verify:
        verification = verify_platform_health()
        VERIFICATIONS_TOTAL.inc()

    lifecycle_status = "remediated"
    if verification and verification.get("status") == "passed":
        lifecycle_status = "verified_resolved"

    updated_incident = _update_latest_incident_lifecycle(
        lifecycle_status=lifecycle_status,
        remediation={
            "runbook_id": payload.runbook_id,
            "approved_by": payload.approved_by,
            "execution_mode": execution_result.get("mode"),
            "execution_result": execution_result,
        },
        verification=verification,
    )

    record = append_audit(
        "aiops_runbook_approved",
        {
            "runbook_id": payload.runbook_id,
            "approved_by": payload.approved_by,
            "execution_mode": execution_result.get("mode"),
            "execution_result": execution_result,
            "verification": verification,
            "lifecycle_status": lifecycle_status,
        },
    )

    response_payload = {
        "runbook": runbook,
        "execution_mode": execution_result.get("mode"),
        "execution_result": execution_result,
        "verification": verification,
        "incident": updated_incident,
        "audit": record,
    }
    return response_payload


@app.post("/runbooks/verify")
def verify_runbook_result() -> dict[str, Any]:
    verification = verify_platform_health()
    VERIFICATIONS_TOTAL.inc()

    record = append_audit(
        "aiops_runbook_verified",
        {
            "verification": verification,
        },
    )

    return {
        "verification": verification,
        "audit": record,
    }


@app.post("/incidents/close")
def close_latest_incident(closed_by: str = "admin-demo") -> dict[str, Any]:
    updated_incident = _update_latest_incident_lifecycle(
        lifecycle_status="closed",
        closed_by=closed_by,
    )

    record = append_audit(
        "aiops_incident_closed",
        {
            "closed_by": closed_by,
            "incident_status": updated_incident.get("status"),
            "lifecycle_status": updated_incident.get("lifecycle_status"),
        },
    )

    return {
        "status": "closed",
        "incident": updated_incident,
        "audit": record,
    }


@app.get("/audit")
def audit(limit: int = 50) -> dict[str, Any]:
    return read_audit(limit=limit)


# Main responsibilities:

# Start the AI Ops API.
# Receive Alertmanager webhooks.
# Create incident records.
# Trigger analysis.
# Return incident status to the Admin UI.
# Handle approval requests.
# Execute approved runbooks.
# Return audit history.