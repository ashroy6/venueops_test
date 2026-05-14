from __future__ import annotations

from pathlib import Path
from typing import Any

from src.config import RUNBOOK_DIR


def _parse_simple_yaml(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()

        if not line or line.lstrip().startswith("#"):
            continue

        if not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if value:
                data[key] = value
                current_key = None
            else:
                data[key] = []
                current_key = key

            continue

        if current_key and line.strip().startswith("- "):
            item = line.strip()[2:].strip().strip('"').strip("'")
            if isinstance(data.get(current_key), list):
                data[current_key].append(item)

    data["file"] = path.name
    return data


def list_runbooks() -> list[dict[str, Any]]:
    root = Path(RUNBOOK_DIR)

    if not root.exists():
        return []

    runbooks: list[dict[str, Any]] = []

    for path in sorted(root.glob("*.yaml")):
        runbooks.append(_parse_simple_yaml(path))

    return runbooks


def get_runbook(runbook_id: str) -> dict[str, Any] | None:
    clean = (runbook_id or "").strip()

    if not clean:
        return None

    for runbook in list_runbooks():
        if runbook.get("id") == clean:
            return runbook

    return None


def choose_default_runbook(evidence: dict[str, Any]) -> str:
    incident_kind = str(evidence.get("kind", "")).strip().lower()
    text = str(evidence).lower()

    if incident_kind == "ingestion_slowdown":
        return "scale_ingestion_api"

    if incident_kind == "api_5xx_spike":
        return "rollback_release"

    if incident_kind == "queue_backlog":
        return "investigate_provider_failure"

    if "5xx" in text or "bad api deployment" in text or "runtime exception" in text:
        return "rollback_release"

    if "ingestion" in text and ("slow" in text or "latency" in text or "backlog" in text):
        return "scale_ingestion_api"

    if "queue" in text or "worker" in text or "provider" in text:
        return "investigate_provider_failure"

    return "restart_api"
