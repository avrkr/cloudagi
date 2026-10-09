"""MySQL access for AGI scripts (avrkrcloud_app)."""
from __future__ import annotations

import pymysql
from pymysql.cursors import DictCursor

from config import DbConfig, get_db_config


def connect(cfg: DbConfig | None = None) -> pymysql.connections.Connection:
    c = cfg or get_db_config()
    return pymysql.connect(
        host=c.host,
        port=c.port,
        user=c.user,
        password=c.password,
        database=c.database,
        cursorclass=DictCursor,
        connect_timeout=5,
        read_timeout=10,
        write_timeout=10,
        autocommit=False,
    )


def ensure_schema(cfg: DbConfig | None = None) -> None:
    conn = connect(cfg)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS live_calls (
                  callid VARCHAR(32) NOT NULL PRIMARY KEY,
                  tenantid VARCHAR(80) NOT NULL,
                  agent_number VARCHAR(40) NULL,
                  user_number VARCHAR(40) NULL,
                  caller_id VARCHAR(128) NULL,
                  direction VARCHAR(16) NOT NULL DEFAULT 'outbound',
                  status VARCHAR(32) NOT NULL DEFAULT 'initiated',
                  started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                  linkedid VARCHAR(64) NULL,
                  channel VARCHAR(128) NULL,
                  INDEX idx_live_calls_tenant (tenantid),
                  INDEX idx_live_calls_started (started_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS call_history (
                  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                  callid VARCHAR(32) NOT NULL,
                  tenantid VARCHAR(80) NOT NULL,
                  agent_number VARCHAR(40) NULL,
                  user_number VARCHAR(40) NULL,
                  caller_id VARCHAR(128) NULL,
                  direction VARCHAR(16) NOT NULL DEFAULT 'outbound',
                  status VARCHAR(32) NOT NULL DEFAULT 'completed',
                  started_at DATETIME NOT NULL,
                  ended_at DATETIME NOT NULL,
                  duration_seconds INT UNSIGNED NULL,
                  hangup_cause VARCHAR(64) NULL,
                  INDEX idx_call_history_tenant_ended (tenantid, ended_at),
                  INDEX idx_call_history_callid (callid)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
