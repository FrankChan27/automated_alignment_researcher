# Shared env for POC-002 launch wrappers. Source from repo root or any cwd.
# Secrets and runtime dirs live OUTSIDE the git checkout.
export AAR_POC002_REPO="${AAR_POC002_REPO:-/workspace/aar-infra/automated_alignment_researcher}"
export AAR_POC002_ROOT="${AAR_POC002_ROOT:-$AAR_POC002_REPO/downstream/poc/aar_poc_002}"
export AAR_POC002_POC_DIR="${AAR_POC002_POC_DIR:-$AAR_POC002_REPO/downstream/poc}"
export POC002_SECRET_DIR="${POC002_SECRET_DIR:-/home/box/aar-poc-002-secrets}"
export POC002_RUNS_DIR="${POC002_RUNS_DIR:-/home/box/aar-poc-002-runs}"
export HELDOUT_SCORES_DIR="${HELDOUT_SCORES_DIR:-$POC002_SECRET_DIR/heldout_scores}"
export SUBMISSIONS_DIR="${SUBMISSIONS_DIR:-$POC002_RUNS_DIR/submissions}"
export SCORES_DIR="${SCORES_DIR:-$POC002_RUNS_DIR/scores}"
export HOLDOUT_DIR="${HOLDOUT_DIR:-$POC002_SECRET_DIR}"
export HARNESS_TRANSPORT="${HARNESS_TRANSPORT:-fs}"
export SUITE_NAME="${SUITE_NAME:-poc002_vector}"
export SUITE_CONFIG="${SUITE_CONFIG:-$AAR_POC002_ROOT/adapter/suite.yaml}"
export POC002_VENV="${POC002_VENV:-/home/box/aar-poc-002-venv}"
# Repo + downstream/poc so `import aar` and `import aar_poc_002` both work
export PYTHONPATH="${AAR_POC002_REPO}:${AAR_POC002_POC_DIR}${PYTHONPATH:+:$PYTHONPATH}"
mkdir -p "$SUBMISSIONS_DIR" "$SCORES_DIR" "$HELDOUT_SCORES_DIR" \
  "$POC002_RUNS_DIR/research_scores" "$POC002_RUNS_DIR/smoke_models"
chmod 700 "$POC002_SECRET_DIR" "$HELDOUT_SCORES_DIR" "$POC002_RUNS_DIR" 2>/dev/null || true
