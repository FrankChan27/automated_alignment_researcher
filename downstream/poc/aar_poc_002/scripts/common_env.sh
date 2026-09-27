#!/usr/bin/env bash
# Shared env for POC-002 launch helpers. Secrets stay on disk; do not cat them.
set -euo pipefail
REPO_ROOT="${REPO_ROOT:-/workspace/aar-infra/automated_alignment_researcher}"
VENV="${VENV:-/home/box/aar-poc-002-venv}"
POC002="${REPO_ROOT}/downstream/poc/aar_poc_002"
# shellcheck disable=SC1091
set -a
source "${POC002}/env.example"
set +a
export PATH="${VENV}/bin:${PATH}"
export VIRTUAL_ENV="${VENV}"
# Process-start registration of VectorModel + poc002 benches (inherited by eval Popen)
export PYTHONPATH="${POC002}/scripts/preload:${REPO_ROOT}/downstream/poc:${REPO_ROOT}:${PYTHONPATH:-}"
mkdir -p "${SUBMISSIONS_DIR}" "${SCORES_DIR}" "${HOLDOUT_DIR}" "${HELDOUT_SCORES_DIR}"
# Publish suite into holdout layout expected by entrypoint resolve_suite_dir
SUITE_PUBLISH="${HOLDOUT_DIR}/poc002_vector"
mkdir -p "${SUITE_PUBLISH}"
cp -f "${POC002}/adapter/suite.yaml" "${SUITE_PUBLISH}/poc002_vector.yaml"
# Also expose train/heldout params names entrypoint secret_dir may pass
# (benches also resolve absolute POC002_*_SECRET paths)
cd "${REPO_ROOT}"
