from __future__ import annotations

import json
import re
from typing import Any

from src.ollama_client import build_incident_prompt, call_ollama
from src.runbook_registry import choose_default_runbook, get_runbook, list_runbooks


def _normalize_runbook_id(value: Any) -> str:
    clean = str(value or "").strip()

    if clean.endswith(".yaml"):
        clean = clean.removesuffix(".yaml")

    if clean.endswith(".yml"):
        clean = clean.removesuffix(".yml")

    valid_ids = {runbook.get("id") for runbook in list_runbooks()}

    if clean in valid_ids:
        return clean

    return ""


def _extract_json_object(raw_response: str) -> str:
    clean = (raw_response or "").strip()

    if clean.startswith("```"):
        clean = re.sub(r"^```(?:json)?", "", clean, flags=re.IGNORECASE).strip()
        clean = re.sub(r"```$", "", clean).strip()

    start = clean.find("{")
    end = clean.rfind("}")

    if start == -1 or end == -1 or end <= start:
        return clean

    return clean[start:end + 1]


def _repair_common_json_errors(raw_response: str) -> str:
    clean = _extract_json_object(raw_response)

    # Remove trailing commas before object/array close.
    clean = re.sub(r",\s*([}\]])", r"\1", clean)

    # Repair common unquoted confidence values from small local models.
    clean = re.sub(
        r'("confidence"\s*:\s*)(low|medium|high)(\s*[,}])',
        r'\1"\2"\3',
        clean,
        flags=re.IGNORECASE,
    )

    clean = re.sub(
        r'("risk_level"\s*:\s*)(low|medium|high)(\s*[,}])',
        r'\1"\2"\3',
        clean,
        flags=re.IGNORECASE,
    )

    clean = re.sub(
        r'("approval_required"\s*:\s*)(true|false)(\s*[,}])',
        r'\1"\2"\3',
        clean,
        flags=re.IGNORECASE,
    )

    return clean


def _parse_llm_json(raw_response: str) -> tuple[dict[str, Any], bool]:
    extracted = _extract_json_object(raw_response)

    try:
        parsed = json.loads(extracted)
        if not isinstance(parsed, dict):
            raise ValueError("LLM response was not a JSON object")
        return parsed, False
    except Exception:
        repaired = _repair_common_json_errors(raw_response)
        parsed = json.loads(repaired)
        if not isinstance(parsed, dict):
            raise ValueError("LLM response was not a JSON object after repair")
        return parsed, True


def _fallback_analysis(evidence: dict[str, Any], reason: str, raw_response: str | None = None) -> dict[str, Any]:
    runbook_id = choose_default_runbook(evidence)
    runbook = get_runbook(runbook_id)

    result = {
        "incident_summary": "AI Ops reviewed the available platform evidence.",
        "likely_root_cause": evidence.get(
            "likely_signal",
            "Insufficient evidence for a precise root cause.",
        ),
        "confidence": "medium" if evidence.get("source") == "simulated_incident" else "low",
        "evidence": evidence,
        "risk_level": runbook.get("risk", "medium") if runbook else "medium",
        "recommended_runbook": runbook_id,
        "recommended_runbook_details": runbook,
        "approval_required": runbook.get("approval_required", "true") if runbook else "true",
        "verification_steps": runbook.get(
            "verification_steps",
            [
                "Check service health endpoints.",
                "Check Prometheus metrics.",
                "Confirm error rate and queue backlog are improving.",
            ],
        ) if runbook else [],
        "llm_status": {
            "called": bool(raw_response),
            "accepted": False,
            "used": False,
            "fallback_used": True,
            "reason": reason,
        },
    }

    if raw_response:
        result["raw_llm_response"] = raw_response

    return result


def analyze_incident(evidence: dict[str, Any]) -> dict[str, Any]:
    runbooks = list_runbooks()
    prompt = build_incident_prompt(evidence, runbooks)
    llm_result = call_ollama(prompt)

    if not llm_result.get("ok"):
        return _fallback_analysis(
            evidence,
            llm_result.get("error", "Ollama unavailable"),
            raw_response=None,
        )

    raw_response = llm_result.get("response", "")

    try:
        parsed, repaired = _parse_llm_json(raw_response)

        llm_runbook_id = _normalize_runbook_id(parsed.get("recommended_runbook"))
        policy_runbook_id = choose_default_runbook(evidence)

        # Policy wins over the LLM. The LLM can reason, but deterministic
        # approved runbook mapping controls the final action recommendation.
        normalized_runbook_id = policy_runbook_id or llm_runbook_id

        runbook = get_runbook(normalized_runbook_id)

        # Preserve original system evidence. Do not let the LLM rewrite evidence,
        # because small local models may add formatting artifacts or mutate facts.
        parsed["evidence"] = evidence

        parsed["recommended_runbook"] = normalized_runbook_id
        parsed["recommended_runbook_details"] = runbook

        if runbook:
            parsed["risk_level"] = runbook.get("risk", parsed.get("risk_level", "medium"))
            parsed["approval_required"] = runbook.get(
                "approval_required",
                parsed.get("approval_required", "true"),
            )
            parsed["verification_steps"] = runbook.get(
                "verification_steps",
                parsed.get("verification_steps", []),
            )

        parsed["llm_status"] = {
            "called": True,
            "accepted": True,
            "used": True,
            "fallback_used": False,
            "json_repaired": repaired,
            "model": llm_result.get("model"),
        }

        return parsed

    except Exception as exc:
        return _fallback_analysis(
            evidence,
            f"LLM returned non-JSON or invalid response: {exc}",
            raw_response=raw_response,
        )
