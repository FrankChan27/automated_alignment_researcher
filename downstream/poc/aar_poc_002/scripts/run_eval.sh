#!/usr/bin/env bash
# Score a model_path (dir with vector.json) on the POC-002 suite.
# Usage: scripts/run_eval.sh <model_path> [out_json]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "$ROOT/scripts/env.sh"
# shellcheck source=/dev/null
source "$POC002_VENV/bin/activate"
MODEL="${1:?model_path dir required}"
OUT="${2:-$POC002_RUNS_DIR/research_scores/scores.json}"
exec python -m aar_poc_002.adapter.eval \
  --suite "$SUITE_CONFIG" \
  --model "$MODEL" \
  --secret-dir "$POC002_SECRET_DIR" \
  --out "$OUT" \
  --heldout-dir "$HELDOUT_SCORES_DIR"
