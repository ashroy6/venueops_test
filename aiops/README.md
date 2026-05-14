# VenueOps AI Ops Service

AI Ops is a separate microservice for incident analysis and controlled self-healing demos.

## Local demo responsibilities

- Collect evidence from service health endpoints
- Query Prometheus for platform metrics
- Send structured evidence to Ollama when available
- Recommend only predefined runbooks
- Record all analysis decisions to an audit log
- Simulate runbook approval/execution for interview demo

## Production positioning

For production, Ollama can be replaced with Azure OpenAI or a private model endpoint.

The AI service must not execute arbitrary commands. Remediation must go through policy checks, approval gates, predefined runbooks, and audit logging.
