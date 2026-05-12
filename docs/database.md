# Database

## Overview

The production design uses Azure PostgreSQL Flexible Server.

The local demo uses SQLite so the project can run without cloud services.

The same database abstraction is used by the backend API.

## Local mode

Local mode uses:

    DATABASE_MODE=sqlite
    DATABASE_URL=sqlite:////data/db/venueops.db

The SQLite database is stored inside the Docker volume.

## Production mode

Production mode uses Azure PostgreSQL:

    DATABASE_MODE=postgres
    DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:5432/venueops

In production, credentials should come from Azure Key Vault and be injected into AKS through workload identity or secret provider integration.

## Tables

### venues

Stores physical venues.

Example:

- venue-london-001
- venue-manchester-001

### devices

Stores in-venue devices.

Example:

- cameras
- kiosks
- game devices
- tablets
- screens

### jobs

Stores asynchronous jobs.

Examples:

- send_sms
- send_email
- process_video
- device_command

### audit_logs

Stores admin and system audit events.

Examples:

- configuration changed
- SMS requested
- email requested
- device command requested
- video processing requested

## Why PostgreSQL

PostgreSQL is a good default because the business data is relational.

Venue, device, guest, config, job, and audit data are easier to query and govern in a relational database.

High-volume raw logs and videos should not be stored directly in PostgreSQL.

Raw logs and videos belong in Event Hubs and Blob Storage.
