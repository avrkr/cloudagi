#!/usr/bin/env python3
"""AGI: move live call to call_history on hangup (idempotent)."""
from __future__ import annotations

import os
import sys
import traceback

_HERE = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from agi_lib import AgiSession  # noqa: E402
from call_db import finalize_call  # noqa: E402


def main() -> int:
    agi = AgiSession()
    agi.read_env()
    try:
        callid = agi.channel_var("callid") or agi.get("agi_arg_1")
        cause = agi.channel_var("HANGUPCAUSE") or agi.get("agi_arg_2")
        if not callid:
            agi.verbose("agi_call_end: missing callid", 1)
            return 0
        moved = finalize_call(callid=callid, hangup_cause=cause or None, status="completed")
        agi.verbose(
            f"agi_call_end: callid={callid} moved={moved} cause={cause}",
            1,
        )
    except Exception as exc:
        agi.verbose(f"agi_call_end error: {exc}", 1)
        traceback.print_exc(file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
