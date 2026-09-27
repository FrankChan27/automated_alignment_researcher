#!/usr/bin/env bash
# DOWNSTREAM-LOCAL Layer-1 smoke (no-GPU preferred).
# Never claims PASS if not actually run. Records BLOCKED with reason when env missing.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"

ART_DIR="${AAR_SMOKE_ART_DIR:-$ROOT/downstream/artifacts}"
mkdir -p "$ART_DIR"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_JSON="${ART_DIR}/layer1_smoke_${STAMP}.json"
LATEST_JSON="${ART_DIR}/layer1_smoke_latest.json"
META_JSON="${ART_DIR}/layer1_smoke_meta_${STAMP}.json"

SMOKE_STATUS="BLOCKED"
SMOKE_REASON="not started"
GENERIC_STATUS="BLOCKED"
GENERIC_REASON="not started"
SMOKE_LOG="${ART_DIR}/layer1_eval_${STAMP}.log"
GENERIC_LOG="${ART_DIR}/layer1_generic_${STAMP}.log"

echo "[layer1] DOWNSTREAM-LOCAL smoke starting at $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# --- eval pod smoke ---
set +e
python3 -m aar.eval_pod.run_eval --suite configs/toy.yaml --model stub:perfect \
  >"$SMOKE_LOG" 2>&1
rc=$?
set -e
if [[ $rc -eq 0 ]]; then
  SMOKE_STATUS="PASS"
  SMOKE_REASON="python -m aar.eval_pod.run_eval --suite configs/toy.yaml --model stub:perfect exited 0"
elif grep -qiE 'ModuleNotFoundError|ImportError|No module named' "$SMOKE_LOG"; then
  SMOKE_STATUS="BLOCKED"
  SMOKE_REASON="eval smoke not runnable: missing Python modules (see log). Never claim PASS."
else
  SMOKE_STATUS="FAIL"
  SMOKE_REASON="eval smoke exited ${rc}"
fi

# --- generic_aar smoke ---
if [[ ! -f "$ROOT/generic_aar/run_example.sh" ]]; then
  GENERIC_STATUS="BLOCKED"
  GENERIC_REASON="generic_aar/run_example.sh missing"
  echo "$GENERIC_REASON" >"$GENERIC_LOG"
else
  set +e
  bash "$ROOT/generic_aar/run_example.sh" >"$GENERIC_LOG" 2>&1
  rc=$?
  set -e
  if [[ $rc -eq 0 ]]; then
    GENERIC_STATUS="PASS"
    GENERIC_REASON="bash generic_aar/run_example.sh exited 0"
  elif grep -qiE 'ModuleNotFoundError|ImportError|No module named' "$GENERIC_LOG"; then
    GENERIC_STATUS="BLOCKED"
    GENERIC_REASON="generic_aar smoke not runnable: missing Python modules (see log). Never claim PASS."
  else
    GENERIC_STATUS="FAIL"
    GENERIC_REASON="generic_aar/run_example.sh exited ${rc}"
  fi
fi

OVERALL="PASS"
if [[ "$SMOKE_STATUS" == "FAIL" || "$GENERIC_STATUS" == "FAIL" ]]; then
  OVERALL="FAIL"
elif [[ "$SMOKE_STATUS" == "BLOCKED" || "$GENERIC_STATUS" == "BLOCKED" ]]; then
  OVERALL="BLOCKED"
fi

# Write JSON via python with argv to avoid injection/quoting issues
python3 - "$OUT_JSON" "$LATEST_JSON" "$STAMP" "$OVERALL" \
  "$SMOKE_STATUS" "$SMOKE_REASON" "$SMOKE_LOG" \
  "$GENERIC_STATUS" "$GENERIC_REASON" "$GENERIC_LOG" <<'PY'
import json, sys
from pathlib import Path
(out, latest, stamp, overall,
 smoke_s, smoke_r, smoke_l,
 gen_s, gen_r, gen_l) = sys.argv[1:11]
doc = {
  "layer": 1,
  "kind": "smoke",
  "downstream_local": True,
  "recorded_at": stamp,
  "overall": overall,
  "eval_pod_smoke": {
    "status": smoke_s,
    "reason": smoke_r,
    "log": smoke_l,
    "command": "python -m aar.eval_pod.run_eval --suite configs/toy.yaml --model stub:perfect",
  },
  "generic_aar_smoke": {
    "status": gen_s,
    "reason": gen_r,
    "log": gen_l,
    "command": "bash generic_aar/run_example.sh",
  },
  "note": "Never claim PASS if not run. BLOCKED means environment could not execute the test.",
}
text = json.dumps(doc, indent=2) + "\n"
Path(out).write_text(text)
Path(latest).write_text(text)
print(text, end="")
PY

echo "[layer1] overall=${OVERALL} eval=${SMOKE_STATUS} generic=${GENERIC_STATUS}"
echo "[layer1] wrote ${OUT_JSON}"

if [[ "$OVERALL" == "FAIL" ]]; then
  exit 1
fi
exit 0
