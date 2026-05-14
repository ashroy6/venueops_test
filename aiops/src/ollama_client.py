from __future__ import annotations

import json
from typing import Any

import requests

from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL


OLLAMA_TIMEOUT_SECONDS = 120


def call_ollama(prompt: str) -> dict[str, Any]:
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.0,
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=OLLAMA_TIMEOUT_SECONDS)
        response.raise_for_status()
        body = response.json()

        return {
            "ok": True,
            "model": OLLAMA_MODEL,
            "response": body.get("response", "").strip(),
        }
    except Exception as exc:
        return {
            "ok": False,
            "model": OLLAMA_MODEL,
            "error": str(exc),
        }


def build_incident_prompt(evidence: dict[str, Any], runbooks: list[dict[str, Any]]) -> str:
    return f"""
You are the AI Ops analyst for a cloud-native VenueOps platform.

Return ONLY valid JSON.
Do not use Markdown.
Do not use comments.
Do not use trailing commas.
Do not repeat keys.
All string values must be quoted.
The field "confidence" must be one of: "low", "medium", "high".
The field "risk_level" must be one of: "low", "medium", "high".
The field "approval_required" must be a string: "true" or "false".
The field "recommended_runbook" must be one of the runbook id values, not the filename.

Rules:
- Do not suggest arbitrary shell commands.
- Recommend only one provided runbook id.
- If evidence is weak, set confidence to "low".
- Production remediation must go through approval.
- Return concise JSON only.

Required JSON object shape:
{{
  "incident_summary": "short summary",
  "likely_root_cause": "short root cause",
  "confidence": "low|medium|high",
  "evidence": {{
    "source": "source",
    "kind": "kind",
    "symptoms": ["symptom 1"],
    "metrics": {{}}
  }},
  "risk_level": "low|medium|high",
  "recommended_runbook": "runbook_id_only",
  "approval_required": "true|false",
  "verification_steps": ["step 1"]
}}

Evidence:
{json.dumps(evidence, indent=2, sort_keys=True)}

Available runbooks:
{json.dumps(runbooks, indent=2, sort_keys=True)}
""".strip()
