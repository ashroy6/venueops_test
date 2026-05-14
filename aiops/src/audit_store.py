from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import AIOPS_AUDIT_LOG_PATH


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_audit(event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    path = Path(AIOPS_AUDIT_LOG_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": utc_now(),
        "event_type": event_type,
        "payload": payload,
    }

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")

    return record


def read_audit(limit: int = 50) -> dict[str, Any]:
    path = Path(AIOPS_AUDIT_LOG_PATH)

    if not path.exists():
        return {"items": []}

    records: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            clean = line.strip()
            if not clean:
                continue

            try:
                records.append(json.loads(clean))
            except json.JSONDecodeError:
                records.append({"raw": clean})

    return {"items": records[-limit:]}
