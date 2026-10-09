"""Minimal Asterisk AGI protocol helpers (stdin/stdout)."""
from __future__ import annotations

import sys
from typing import TextIO


class AgiSession:
    def __init__(self, stdin: TextIO | None = None, stdout: TextIO | None = None) -> None:
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout
        self.env: dict[str, str] = {}

    def read_env(self) -> dict[str, str]:
        while True:
            line = self.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                break
            if ":" in line:
                key, value = line.split(":", 1)
                self.env[key.strip()] = value.strip()
        return self.env

    def get(self, key: str, default: str = "") -> str:
        return self.env.get(key, default)

    def channel_var(self, name: str) -> str:
        """GET VARIABLE name."""
        self.stdout.write(f'GET VARIABLE "{name}"\n')
        self.stdout.flush()
        line = self.stdin.readline().strip()
        # 200 result=1 (value)
        if "result=1" in line and "(" in line and line.endswith(")"):
            return line[line.find("(") + 1 : -1]
        return ""

    def verbose(self, message: str, level: int = 1) -> None:
        safe = message.replace('"', "'")
        self.stdout.write(f'VERBOSE "{safe}" {level}\n')
        self.stdout.flush()
        self.stdin.readline()
