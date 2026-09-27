#!/usr/bin/env bash
# DOWNSTREAM-LOCAL Layer-2 integrity / regression checks.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

ART_DIR="${AAR_SMOKE_ART_DIR:-$ROOT/downstream/artifacts}"
mkdir -p "$ART_DIR"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_JSON="${ART_DIR}/layer2_integrity_${STAMP}.json"
LATEST_JSON="${ART_DIR}/layer2_integrity_latest.json"

CHECKS_FILE="$(mktemp)"
trap 'rm -f "$CHECKS_FILE"' EXIT

pass() { printf '%s\tPASS\t%s\n' "$1" "$2" >>"$CHECKS_FILE"; }
fail() { printf '%s\tFAIL\t%s\n' "$1" "$2" >>"$CHECKS_FILE"; }

echo "[layer2] DOWNSTREAM-LOCAL integrity starting at $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# 1) Fork relationship via gh api
FORK_JSON=""
if command -v gh >/dev/null 2>&1; then
  set +e
  FORK_JSON="$(gh api repos/FrankChan27/automated_alignment_researcher 2>/dev/null)"
  rc=$?
  set -e
  if [[ $rc -ne 0 || -z "$FORK_JSON" ]]; then
    fail "fork_relationship" "gh api repos/FrankChan27/automated_alignment_researcher failed"
  else
    python3 - "$FORK_JSON" <<'PY' >>"$CHECKS_FILE" || true
import json, sys
data = json.loads(sys.argv[1])
ok = bool(data.get("fork")) and (data.get("parent") or {}).get("full_name") == "YuehHanChen/automated_alignment_researcher"
print(f"fork_relationship\t{'PASS' if ok else 'FAIL'}\tfork={data.get('fork')} parent={(data.get('parent') or {}).get('full_name')}")
PY
  fi
else
  fail "fork_relationship" "gh not available"
fi

# 2) Governance files exist
REQUIRED=(
  "downstream/DOWNSTREAM_POLICY.md"
  "downstream/UPSTREAM_PIN.json"
  "downstream/README.md"
  "downstream/scripts/classify_upstream_diff.py"
  "downstream/scripts/write_update_manifest.py"
  "downstream/scripts/run_layer1_smoke.sh"
  "downstream/scripts/run_layer2_integrity.sh"
  "downstream/scripts/monitor_once.sh"
  "upstream_updates/.gitkeep"
  "upstream_updates/README.md"
  "downstream/github-workflows/upstream-monitor.yml"
)

# Prefer installed Actions path; staged mirror is acceptable when OAuth lacks workflow scope
if [[ -f "$ROOT/.github/workflows/upstream-monitor.yml" ]]; then
  pass "monitor_workflow_installed" ".github/workflows/upstream-monitor.yml present"
elif [[ -f "$ROOT/downstream/github-workflows/upstream-monitor.yml" ]]; then
  pass "monitor_workflow_staged" "staged mirror present; run install_monitor_workflow.sh when credential has workflow scope"
else
  fail "monitor_workflow" "no upstream-monitor.yml installed or staged"
fi

for f in "${REQUIRED[@]}"; do
  if [[ -f "$ROOT/$f" ]]; then
    pass "governance_file:$f" "present"
  else
    fail "governance_file:$f" "missing"
  fi
done

# 3) Pin present and immutable SHA shape
if [[ -f "$ROOT/downstream/UPSTREAM_PIN.json" ]]; then
  set +e
  PIN_MSG="$(python3 - <<'PY'
import json, re, sys
from pathlib import Path
p = json.loads(Path("downstream/UPSTREAM_PIN.json").read_text())
sha = p.get("pinned_upstream_sha", "")
ok = bool(re.fullmatch(r"[0-9a-f]{40}", sha or ""))
repo_ok = p.get("upstream_repo") == "YuehHanChen/automated_alignment_researcher"
branch_ok = p.get("upstream_default_branch") == "main"
if ok and repo_ok and branch_ok:
    print(f"PASS\tpin sha={sha} repo={p.get('upstream_repo')} branch={p.get('upstream_default_branch')}")
    sys.exit(0)
print(f"FAIL\tinvalid pin fields sha={sha!r} repo={p.get('upstream_repo')!r} branch={p.get('upstream_default_branch')!r}")
sys.exit(1)
PY
)"
  rc=$?
  set -e
  if [[ $rc -eq 0 ]]; then
    pass "upstream_pin" "${PIN_MSG#PASS	}"
  else
    fail "upstream_pin" "${PIN_MSG#FAIL	}"
  fi
else
  fail "upstream_pin" "UPSTREAM_PIN.json missing"
fi

# 4) No accidental secrets patterns in new downstream files
SECRET_HITS=0
SECRET_DETAIL=""
while IFS= read -r -d '' f; do
  # skip binary-ish; scan text
  if grep -a -nEi \
    'api[_-]?key\s*=\s*['\''\"][a-zA-Z0-9_-]{16,}|secret[_-]?key\s*=\s*['\''\"][^'\''\"]+|BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}' \
    "$f" >/dev/null 2>&1; then
    SECRET_HITS=$((SECRET_HITS + 1))
    SECRET_DETAIL="${SECRET_DETAIL};$f"
  fi
done < <(find "$ROOT/downstream" "$ROOT/upstream_updates" "$ROOT/.github/workflows" -type f \
  ! -path '*/artifacts/*' ! -name '*.pyc' -print0 2>/dev/null)

if [[ "$SECRET_HITS" -eq 0 ]]; then
  pass "no_accidental_secrets" "no high-confidence secret patterns in downstream governance paths"
else
  fail "no_accidental_secrets" "hits=${SECRET_HITS}${SECRET_DETAIL}"
fi

# 5) Isolation docs still present
if [[ -f "$ROOT/ISOLATION.md" ]]; then
  pass "isolation_docs" "ISOLATION.md present"
else
  fail "isolation_docs" "ISOLATION.md missing"
fi

# Aggregate
python3 - "$CHECKS_FILE" "$OUT_JSON" "$LATEST_JSON" "$STAMP" <<'PY'
import json, sys
from pathlib import Path
checks_path, out, latest, stamp = sys.argv[1:5]
checks = []
overall = "PASS"
with open(checks_path) as fh:
    for line in fh:
        line = line.rstrip("\n")
        if not line:
            continue
        parts = line.split("\t", 2)
        name, status = parts[0], parts[1]
        detail = parts[2] if len(parts) > 2 else ""
        checks.append({"name": name, "status": status, "detail": detail})
        if status != "PASS":
            overall = "FAIL"
doc = {
  "layer": 2,
  "kind": "integrity",
  "downstream_local": True,
  "recorded_at": stamp,
  "overall": overall,
  "checks": checks,
  "note": "DOWNSTREAM-LOCAL integrity. FAIL blocks recommending merge.",
}
text = json.dumps(doc, indent=2) + "\n"
Path(out).write_text(text)
Path(latest).write_text(text)
print(text, end="")
sys.exit(0 if overall == "PASS" else 1)
PY
rc=$?
echo "[layer2] wrote ${OUT_JSON}"
exit $rc
