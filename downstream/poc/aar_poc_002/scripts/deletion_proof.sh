#!/usr/bin/env bash
# (c) Deletion proof: loop must FAIL if aar/ + generic_aar/ removed.
#
# Usage:
#   bash scripts/deletion_proof.sh          # print expected procedure (safe)
#   bash scripts/deletion_proof.sh --exec   # rename aar+generic_aar, attempt import, restore
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-/workspace/aar-infra/automated_alignment_researcher}"
POC="${REPO_ROOT}/downstream/poc/aar_poc_002"
EVID="${POC}/evidence/deletion_proof"
VENV="${VENV:-/home/box/aar-poc-002-venv}"
mkdir -p "${EVID}"

cat <<'DOC' | tee "${EVID}/procedure.md"
# Deletion proof (UPSTREAM_NATIVE_AAR)

Expectation: after temporarily renaming `aar/` and `generic_aar/`, the same launch
wrapper / eval smoke MUST fail (ImportError), proving the POC depends on upstream
packages rather than a forked loop under aar_poc_002.

Safe procedure:
1. `mv aar /tmp/aar.bak-poc002 && mv generic_aar /tmp/generic_aar.bak-poc002`
2. Attempt `python -c 'import aar'` / eval_smoke → expect import failure
3. Restore: `mv /tmp/aar.bak-poc002 aar && mv /tmp/generic_aar.bak-poc002 generic_aar`

If smoke still PASSES with aar/+generic_aar gone → UPSTREAM_NATIVE_AAR=false (do not claim PASS).
DOC

if [[ "${1:-}" != "--exec" ]]; then
  echo "Wrote ${EVID}/procedure.md (dry-run). Pass --exec to run rename+restore."
  exit 0
fi

cd "${REPO_ROOT}"
restore() {
  if [[ -d /tmp/aar.bak-poc002 && ! -d "${REPO_ROOT}/aar" ]]; then
    mv /tmp/aar.bak-poc002 "${REPO_ROOT}/aar"
  fi
  if [[ -d /tmp/generic_aar.bak-poc002 && ! -d "${REPO_ROOT}/generic_aar" ]]; then
    mv /tmp/generic_aar.bak-poc002 "${REPO_ROOT}/generic_aar"
  fi
}
trap restore EXIT

[[ -d aar ]] && mv aar /tmp/aar.bak-poc002
[[ -d generic_aar ]] && mv generic_aar /tmp/generic_aar.bak-poc002

set +e
PYTHONPATH="${POC}/scripts/preload:${REPO_ROOT}/downstream/poc:${REPO_ROOT}" \
  "${VENV}/bin/python" -c "import aar" \
  >"${EVID}/import_aar_after_delete.txt" 2>&1
EC=$?
set -e
{
  echo "import_aar_exit=${EC}"
  if [[ "${EC}" -eq 0 ]]; then
    echo "UNEXPECTED: aar still importable after rename → UPSTREAM_NATIVE_AAR=false"
    exit 1
  fi
  echo "DELETION_PROOF_OK: aar import failed as expected → supports UPSTREAM_NATIVE_AAR"
} | tee "${EVID}/result.txt"
