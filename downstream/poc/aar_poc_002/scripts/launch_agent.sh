#!/usr/bin/env bash
# Native AutonomousAgentLoop launcher — UPSTREAM IS CLAUDE-HARD-BOUND.
# Per POC-002 policy: do NOT run when Anthropic/A-company is forbidden.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "UPSTREAM_NATIVE_UNPATCHED=BLOCKED" >&2
echo "Agent loop hard-bound to Anthropic: ANTHROPIC_API_KEY + claude_agent_sdk + claude CLI" >&2
echo "See STATUS.md and evidence/unpatched_failures/claude_hardbind_probe.txt" >&2
echo "Refusing to start agent (no rewrite to fake native)." >&2
exit 2
