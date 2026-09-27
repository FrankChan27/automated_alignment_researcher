#!/usr/bin/env bash
# Boot upstream Flask server with POC-002 env (no substitute loop).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "$ROOT/scripts/env.sh"
# shellcheck source=/dev/null
source "$POC002_VENV/bin/activate"
cd "$AAR_POC002_REPO"
exec python run.py server --port "${PORT:-8000}"
