#!/usr/bin/env python3
"""AGI: mark live call answered (optional dialplan hook)."""
from __future__ import annotations

import os
import sys
import traceback

_HERE = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from agi_lib import AgiSession  # noqa: E402
from call_db import update_live_status  # noqa: E402


def main() -> int:
    agi = AgiSession()
    agi.read_env()
    try:
        callid = agi.channel_var("callid") or agi.get("agi_arg_1")
        if not callid:
            return 0
        update_live_status(callid, "answered", linkedid=agi.get("agi_uniqueid") or None)
        agi.verbose(f"agi_call_answered: {callid}", 1)
    except Exception as exc:
        agi.verbose(f"agi_call_answered error: {exc}", 1)
        traceback.print_exc(file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
