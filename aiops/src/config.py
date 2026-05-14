from __future__ import annotations

import os


APP_ENV = os.getenv("APP_ENV", "local")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")
INGESTION_BASE_URL = os.getenv("INGESTION_BASE_URL", "http://ingestion-api:8001")
PROMETHEUS_BASE_URL = os.getenv("PROMETHEUS_BASE_URL", "http://prometheus:9090")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

DATA_DIR = os.getenv("DATA_DIR", "/data")
AIOPS_AUDIT_LOG_PATH = os.getenv(
    "AIOPS_AUDIT_LOG_PATH",
    f"{DATA_DIR}/audit/aiops_audit.jsonl",
)

RUNBOOK_DIR = os.getenv("RUNBOOK_DIR", "/app/runbooks")


# Purpose:

# Keeps URLs and paths out of business logic.
# Makes the service configurable by environment variables.
# Allows Docker Compose to inject service addresses.