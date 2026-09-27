#!/usr/bin/env bash
# (b) Native AutonomousAgentLoop — requires ANTHROPIC_API_KEY + claude CLI.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common_env.sh"

if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  echo "BLOCKED: ANTHROPIC_API_KEY unset — cannot run native agent loop." >&2
  exit 2
fi
if ! command -v claude >/dev/null 2>&1; then
  echo "BLOCKED: claude CLI not on PATH (BaseAgent uses shutil.which('claude'))." >&2
  exit 3
fi

# Process-start monkeypatch + benchmark registration via sitecustomize-style preload
export PYTHONPATH="${REPO_ROOT}/downstream/poc/aar_poc_002/scripts/preload:${PYTHONPATH}"
MAX_IT="${1:-${MAX_ITERATIONS:-5}}"
exec "${VENV}/bin/python" run.py agent \
  --idea-uid poc002-vector \
  --idea-name poc002_vector \
  --local \
  --max-iterations "${MAX_IT}"
