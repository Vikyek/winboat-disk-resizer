#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"

echo "=== Installing WinBoat Disk Resizer ==="

mkdir -p "${BIN_DIR}"
install -Dm755 "${SCRIPT_DIR}/winboat-disk-resizer.py" "${BIN_DIR}/winboat-disk-resizer"

echo "Installed winboat-disk-resizer to ${BIN_DIR}/winboat-disk-resizer"
