#!/usr/bin/env bash
# DOWNSTREAM-LOCAL helper: copy staged workflow into .github/workflows/.
# Required when the pushing credential lacks the GitHub `workflow` OAuth scope.
# After copy, commit+push with a token that has `workflow` scope (or use the GitHub UI).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="$ROOT/downstream/github-workflows/upstream-monitor.yml"
DST="$ROOT/.github/workflows/upstream-monitor.yml"
mkdir -p "$(dirname "$DST")"
cp "$SRC" "$DST"
echo "Installed $DST from $SRC"
echo "Commit and push with a credential that includes the workflow scope."
