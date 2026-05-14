from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
OPS_STATE_PATH = DATA_DIR / "ops" / "ops_state.json"
MOCK_SERVICEBUS_QUEUE = Path(os.getenv("MOCK_SERVICEBUS_QUEUE", "/data/queues/jobs.jsonl"))


DEFAULT_STATE: dict[str, Any] = {
    "queue_backlog": 0,
    "queue_backlog_threshold": 10,
    "offline_devices": 0,
    "offline_device_id": "",
    "api_fault_active": False,
    "api_fault_reason": "",
    "last_updated_ms": 0,
}


def now_ms() -> int:
    return int(time.time() * 1000)


def _ensure_parent() -> None:
    OPS_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)


def read_state() -> dict[str, Any]:
    _ensure_parent()

    if not OPS_STATE_PATH.exists():
        write_state(DEFAULT_STATE.copy())

    try:
        data = json.loads(OPS_STATE_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return DEFAULT_STATE.copy()
        return {**DEFAULT_STATE, **data}
    except Exception:
        return DEFAULT_STATE.copy()


def write_state(state: dict[str, Any]) -> dict[str, Any]:
    _ensure_parent()
    clean = {**DEFAULT_STATE, **state}
    clean["last_updated_ms"] = now_ms()
    OPS_STATE_PATH.write_text(json.dumps(clean, indent=2, sort_keys=True), encoding="utf-8")
    return clean


def increment_backlog(amount: int) -> dict[str, Any]:
    state = read_state()
    current = int(state.get("queue_backlog", 0))
    state["queue_backlog"] = max(0, current + int(amount))
    return write_state(state)


def drain_backlog(target: int = 0) -> dict[str, Any]:
    state = read_state()
    before = int(state.get("queue_backlog", 0))
    target_clean = max(0, int(target))

    state["queue_backlog"] = target_clean

    MOCK_SERVICEBUS_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    MOCK_SERVICEBUS_QUEUE.write_text("", encoding="utf-8")

    updated = write_state(state)
    updated["before"] = before
    updated["after"] = target_clean
    updated["drained"] = max(0, before - target_clean)
    return updated


def backlog_status() -> dict[str, Any]:
    state = read_state()
    backlog = int(state.get("queue_backlog", 0))
    threshold = int(state.get("queue_backlog_threshold", 10))

    return {
        "queue_backlog": backlog,
        "threshold": threshold,
        "breached": backlog >= threshold,
        "last_updated_ms": state.get("last_updated_ms", 0),
    }



def set_api_fault(active: bool, reason: str = "") -> dict[str, Any]:
    state = read_state()
    state["api_fault_active"] = bool(active)
    state["api_fault_reason"] = reason if active else ""
    return write_state(state)


def api_fault_status() -> dict[str, Any]:
    state = read_state()
    return {
        "api_fault_active": bool(state.get("api_fault_active", False)),
        "api_fault_reason": state.get("api_fault_reason", ""),
        "last_updated_ms": state.get("last_updated_ms", 0),
    }



def set_device_offline(device_id: str = "camera-01") -> dict[str, Any]:
    state = read_state()
    state["offline_devices"] = 1
    state["offline_device_id"] = device_id
    return write_state(state)


def recover_device() -> dict[str, Any]:
    state = read_state()
    previous_device = state.get("offline_device_id", "")
    state["offline_devices"] = 0
    state["offline_device_id"] = ""
    updated = write_state(state)
    updated["recovered_device_id"] = previous_device
    return updated


def device_health_status() -> dict[str, Any]:
    state = read_state()
    offline_devices = int(state.get("offline_devices", 0))
    return {
        "offline_devices": offline_devices,
        "offline_device_id": state.get("offline_device_id", ""),
        "healthy": offline_devices == 0,
        "last_updated_ms": state.get("last_updated_ms", 0),
    }
