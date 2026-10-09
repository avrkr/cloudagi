#!/usr/bin/env python3
"""AGI: insert/update live_calls when a call starts (calltoagent)."""
from __future__ import annotations

import os
import sys
import traceback

# Ensure this directory is on sys.path when installed as symlink in agi-bin
_HERE = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from agi_lib import AgiSession  # noqa: E402
from call_db import upsert_live_call  # noqa: E402


def main() -> int:
    agi = AgiSession()
    agi.read_env()
    try:
        callid = agi.channel_var("callid") or agi.get("agi_arg_1")
        tenantid = agi.channel_var("tenantid") or "unknown"
        agent = agi.channel_var("agent_number") or agi.channel_var("AGENT_NUMBER")
        user = agi.channel_var("user_number") or agi.channel_var("USER_NUMBER")
        callerid = agi.channel_var("CALLERID(all)") or agi.get("agi_callerid")
        linkedid = agi.get("agi_uniqueid")
        channel = agi.get("agi_channel")

        if not callid:
            agi.verbose("agi_call_start: missing callid", 1)
            return 0

        upsert_live_call(
            callid=callid,
            tenantid=tenantid or "unknown",
            agent_number=agent or None,
            user_number=user or None,
            caller_id=callerid or None,
            direction="outbound",
            status="ringing",
            linkedid=linkedid or None,
            channel=channel or None,
        )
        agi.verbose(f"agi_call_start: live call {callid} tenant={tenantid}", 1)
    except Exception as exc:
        agi.verbose(f"agi_call_start error: {exc}", 1)
        traceback.print_exc(file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
