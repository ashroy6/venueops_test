from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    DateTime,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    func,
    insert,
    select,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////data/db/venueops.db")

if DATABASE_URL.startswith("sqlite:///"):
    sqlite_path = DATABASE_URL.replace("sqlite:///", "", 1)
    Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)

engine: Engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

metadata = MetaData()

venues = Table(
    "venues",
    metadata,
    Column("venue_id", String(100), primary_key=True),
    Column("name", String(255), nullable=False),
    Column("status", String(50), nullable=False, default="active"),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)

devices = Table(
    "devices",
    metadata,
    Column("device_id", String(100), primary_key=True),
    Column("venue_id", String(100), nullable=False),
    Column("device_type", String(100), nullable=False),
    Column("status", String(50), nullable=False, default="online"),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)

jobs = Table(
    "jobs",
    metadata,
    Column("job_id", String(100), primary_key=True),
    Column("job_type", String(100), nullable=False),
    Column("status", String(50), nullable=False),
    Column("payload", JSON, nullable=False),
    Column("created_at_ms", BigInteger, nullable=False),
    Column("updated_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)

audit_logs = Table(
    "audit_logs",
    metadata,
    Column("audit_id", String(100), primary_key=True),
    Column("timestamp_ms", BigInteger, nullable=False),
    Column("service", String(100), nullable=False),
    Column("action", String(150), nullable=False),
    Column("actor", String(255), nullable=False),
    Column("payload", JSON, nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)


def init_db() -> None:
    metadata.create_all(engine)
    seed_reference_data()


@contextmanager
def session_scope() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def seed_reference_data() -> None:
    with session_scope() as session:
        existing_venue = session.execute(select(venues.c.venue_id).limit(1)).first()

        if existing_venue:
            return

        session.execute(
            insert(venues),
            [
                {
                    "venue_id": "venue-london-001",
                    "name": "London Arena",
                    "status": "active",
                },
                {
                    "venue_id": "venue-manchester-001",
                    "name": "Manchester Game Hub",
                    "status": "active",
                },
            ],
        )

        session.execute(
            insert(devices),
            [
                {
                    "device_id": "camera-01",
                    "venue_id": "venue-london-001",
                    "device_type": "camera",
                    "status": "online",
                },
                {
                    "device_id": "kiosk-01",
                    "venue_id": "venue-london-001",
                    "device_type": "kiosk",
                    "status": "online",
                },
                {
                    "device_id": "game-07",
                    "venue_id": "venue-manchester-001",
                    "device_type": "game-device",
                    "status": "warning",
                },
            ],
        )


def list_venues() -> list[dict]:
    with session_scope() as session:
        rows = session.execute(select(venues)).mappings().all()
        return [dict(row) for row in rows]


def list_devices() -> list[dict]:
    with session_scope() as session:
        rows = session.execute(select(devices)).mappings().all()
        return [
            {
                "device_id": row["device_id"],
                "venue_id": row["venue_id"],
                "type": row["device_type"],
                "status": row["status"],
            }
            for row in rows
        ]


def record_job(job: dict) -> None:
    with session_scope() as session:
        session.execute(
            insert(jobs).values(
                job_id=job["job_id"],
                job_type=job["job_type"],
                status=job["status"],
                payload=job["payload"],
                created_at_ms=job["created_at_ms"],
            )
        )


def record_audit(event: dict) -> None:
    with session_scope() as session:
        session.execute(
            insert(audit_logs).values(
                audit_id=event["audit_id"],
                timestamp_ms=event["timestamp_ms"],
                service=event["service"],
                action=event["action"],
                actor=event["actor"],
                payload=event["payload"],
            )
        )


def list_audit_logs(limit: int = 100) -> list[dict]:
    with session_scope() as session:
        rows = (
            session.execute(
                select(audit_logs)
                .order_by(audit_logs.c.timestamp_ms.desc())
                .limit(limit)
            )
            .mappings()
            .all()
        )

        return [dict(row) for row in rows]


def list_jobs(limit: int = 100) -> list[dict]:
    with session_scope() as session:
        rows = (
            session.execute(
                select(jobs)
                .order_by(jobs.c.created_at_ms.desc())
                .limit(limit)
            )
            .mappings()
            .all()
        )

        return [dict(row) for row in rows]
