"""Load DB settings for Avrkr Cloud AGI scripts."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent
# Prefer cloudagi/.env, then backend/.env
load_dotenv(_ROOT / ".env")
load_dotenv(_ROOT.parent / "backend" / ".env", override=False)


@dataclass(frozen=True)
class DbConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


def get_db_config() -> DbConfig:
    return DbConfig(
        host=os.getenv("APP_DB_HOST", os.getenv("DB_HOST", "localhost")),
        port=int(os.getenv("APP_DB_PORT", os.getenv("DB_PORT", "3306"))),
        user=os.getenv("APP_DB_USER", os.getenv("DB_USER", "asterisk")),
        password=os.getenv("APP_DB_PASSWORD", os.getenv("DB_PASSWORD", "asterisk")),
        database=os.getenv("APP_DB_NAME", "avrkrcloud_app"),
    )


def get_notify_url() -> str:
    """Optional HTTP ping so the FastAPI hub pushes WebSocket updates."""
    return os.getenv(
        "LIVE_CALLS_NOTIFY_URL",
        "http://127.0.0.1:8000/internal/live-calls/notify",
    ).rstrip("/")
