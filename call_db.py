"""Live calls + call history writes used by Asterisk AGI."""
from __future__ import annotations

from datetime import datetime
from urllib import error, request

from config import get_notify_url
from db import connect, ensure_schema


def notify_backend() -> None:
    url = get_notify_url()
    if not url:
        return
    try:
        req = request.Request(url, data=b"{}", method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("X-Avrkr-Internal", "agi")
        with request.urlopen(req, timeout=2) as resp:
            resp.read()
    except (error.URLError, TimeoutError, OSError):
        pass


def upsert_live_call(
    *,
    callid: str,
    tenantid: str,
    agent_number: str | None = None,
    user_number: str | None = None,
    caller_id: str | None = None,
    direction: str = "outbound",
    status: str = "ringing",
    linkedid: str | None = None,
    channel: str | None = None,
) -> None:
    if not callid:
        return
    ensure_schema()
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO live_calls (
                  callid, tenantid, agent_number, user_number, caller_id,
                  direction, status, started_at, linkedid, channel
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, UTC_TIMESTAMP(), %s, %s)
                ON DUPLICATE KEY UPDATE
                  tenantid = VALUES(tenantid),
                  agent_number = COALESCE(VALUES(agent_number), agent_number),
                  user_number = COALESCE(VALUES(user_number), user_number),
                  caller_id = COALESCE(VALUES(caller_id), caller_id),
                  direction = VALUES(direction),
                  status = VALUES(status),
                  linkedid = COALESCE(VALUES(linkedid), linkedid),
                  channel = COALESCE(VALUES(channel), channel),
                  updated_at = UTC_TIMESTAMP()
                """,
                (
                    callid,
                    tenantid or "unknown",
                    agent_number or None,
                    user_number or None,
                    caller_id or None,
                    direction or "outbound",
                    status or "ringing",
                    linkedid or None,
                    channel or None,
                ),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    notify_backend()


def update_live_status(callid: str, status: str, linkedid: str | None = None) -> None:
    if not callid:
        return
    ensure_schema()
    conn = connect()
    try:
        with conn.cursor() as cur:
            if linkedid:
                cur.execute(
                    """
                    UPDATE live_calls
                    SET status = %s, linkedid = COALESCE(%s, linkedid),
                        updated_at = UTC_TIMESTAMP()
                    WHERE callid = %s
                    """,
                    (status, linkedid, callid),
                )
            else:
                cur.execute(
                    """
                    UPDATE live_calls SET status = %s, updated_at = UTC_TIMESTAMP()
                    WHERE callid = %s
                    """,
                    (status, callid),
                )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    notify_backend()


def finalize_call(
    *,
    callid: str,
    hangup_cause: str | None = None,
    status: str = "completed",
) -> bool:
    """Move live_calls → call_history and delete live row. Idempotent."""
    if not callid:
        return False
    ensure_schema()
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM call_history WHERE callid = %s LIMIT 1",
                (callid,),
            )
            if cur.fetchone():
                cur.execute("DELETE FROM live_calls WHERE callid = %s", (callid,))
                conn.commit()
                notify_backend()
                return False

            cur.execute("SELECT * FROM live_calls WHERE callid = %s LIMIT 1", (callid,))
            live = cur.fetchone()
            if not live:
                return False

            started = live["started_at"]
            ended = datetime.utcnow()
            duration = int((ended - started).total_seconds()) if started else 0
            cur.execute(
                """
                INSERT INTO call_history (
                  callid, tenantid, agent_number, user_number, caller_id,
                  direction, status, started_at, ended_at, duration_seconds, hangup_cause
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    live["callid"],
                    live["tenantid"],
                    live.get("agent_number"),
                    live.get("user_number"),
                    live.get("caller_id"),
                    live.get("direction") or "outbound",
                    status,
                    started,
                    ended,
                    max(0, duration),
                    hangup_cause,
                ),
            )
            cur.execute("DELETE FROM live_calls WHERE callid = %s", (callid,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    notify_backend()
    return True
