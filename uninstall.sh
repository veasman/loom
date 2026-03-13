#!/usr/bin/env bash
set -euo pipefail

BIN_PATH="${HOME}/.local/bin/loom"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/loom"

PURGE=0
if [[ "${1:-}" == "--purge" ]]; then
    PURGE=1
fi

rm -f "$BIN_PATH"

if [[ "$PURGE" -eq 1 ]]; then
    rm -rf "$STATE_DIR"
    echo "Removed loom and purged state: $STATE_DIR"
else
    rm -rf "$STATE_DIR/generated"
    rm -f "$STATE_DIR"/preview_*
    echo "Removed loom launcher and generated runtime files"
    echo "Preserved loom state in: $STATE_DIR"
fi
