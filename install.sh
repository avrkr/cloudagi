#!/usr/bin/env bash
# Install cloudagi AGI scripts into Asterisk agi-bin
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
AGI_BIN="${ASTERISK_AGI_BIN:-/var/lib/asterisk/agi-bin}"

mkdir -p "$AGI_BIN"
for f in agi_call_start.py agi_call_end.py agi_call_answered.py; do
  ln -sfn "$ROOT/$f" "$AGI_BIN/$f"
  chmod +x "$ROOT/$f"
done

# Shared modules must be importable — symlink package helpers next to scripts
for f in agi_lib.py call_db.py config.py db.py; do
  ln -sfn "$ROOT/$f" "$AGI_BIN/$f"
done

if [[ -f "$ROOT/.env" ]]; then
  ln -sfn "$ROOT/.env" "$AGI_BIN/.env"
elif [[ -f "$ROOT/../backend/.env" ]]; then
  ln -sfn "$ROOT/../backend/.env" "$AGI_BIN/.env"
fi

python3 -m pip install -q -r "$ROOT/requirements.txt" 2>/dev/null || true
echo "Installed AGI scripts into $AGI_BIN"
ls -la "$AGI_BIN"/agi_call_*.py
