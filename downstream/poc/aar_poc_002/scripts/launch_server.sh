#!/usr/bin/env bash
# (b) Start Flask dashboard/API for local agent mode.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common_env.sh"
exec "${VENV}/bin/python" run.py server --port "${PORT:-8000}"
