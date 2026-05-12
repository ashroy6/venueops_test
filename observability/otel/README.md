# OpenTelemetry

Application code supports optional Azure Monitor OpenTelemetry.

Set this environment variable in AKS:

    APPLICATIONINSIGHTS_CONNECTION_STRING=<connection string>

When set, the FastAPI services configure Azure Monitor OpenTelemetry and instrument FastAPI requests.

Local mode does not require this variable.
