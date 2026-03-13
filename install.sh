#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/loom"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}"

mkdir -p "$BIN_DIR"
mkdir -p "$STATE_DIR"
mkdir -p "$CONFIG_DIR/dunst"
mkdir -p "$CONFIG_DIR/picom"
mkdir -p "$CONFIG_DIR/gtk-3.0"
mkdir -p "$CONFIG_DIR/gtk-4.0"

ln -snf "$REPO_DIR/loom" "$BIN_DIR/loom"

echo "Installed loom -> $BIN_DIR/loom"
