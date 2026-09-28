#!/usr/bin/env bash
# LIVE deletion proofs — baseline enters AutonomousAgentLoop.run(), then disable, same cmd fails.
set -euo pipefail
REPO="${1:-/workspace/aar-infra/automated_alignment_researcher}"
OUT="$REPO/downstream/poc/aar_provider_002"
EV="$OUT/evidence"
mkdir -p "$EV"
SCRATCH=$(mktemp -d /tmp/aar_provider002_deletion_XXXX)
trap 'rm -rf "$SCRATCH"' EXIT
echo "SCRATCH=$SCRATCH" | tee "$EV/live_deletion_run.txt"

copy_tree() {
  local dest="$1"
  mkdir -p "$dest/downstream/poc"
  cp -a "$REPO/aar" "$REPO/run.py" "$dest/"
  cp -a "$REPO/downstream/poc/aar_provider_002" "$dest/downstream/poc/"
  # strip pycache for clean imports
  find "$dest" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
}

copy_tree "$SCRATCH/repo"

export AAR_AGENT_PROVIDER=external
export AAR_AGENT_PROVIDER_MODULE=aar_provider_002.providers.fast_stub
unset ANTHROPIC_API_KEY XAI_API_KEY
PYBIN=/home/box/aar-poc-002-venv/bin/python

############################################
# A: core research_loop deletion BREAKS RUN
############################################
cp -a "$SCRATCH/repo" "$SCRATCH/A"
export DELETION_REPO="$SCRATCH/A"
export DELETION_MARKER="$EV/deletion_A_entered.json"
export DELETION_RUNS="$SCRATCH/A_runs"
export PYTHONPATH="$SCRATCH/A:$SCRATCH/A/downstream/poc"
export AAR_AGENT_PROVIDER_PATH="$SCRATCH/A/downstream/poc"
HARNESS="$SCRATCH/A/downstream/poc/aar_provider_002/scripts/live_deletion_harness.py"

echo "=== A BASELINE (enter loop.run) ===" | tee "$EV/deletion_A.txt"
set +e
( cd "$SCRATCH/A" && "$PYBIN" "$HARNESS" ) >>"$EV/deletion_A.txt" 2>&1
EC_A0=$?
set -e
echo "A_BASELINE_EXIT=$EC_A0" | tee -a "$EV/deletion_A.txt"
if [[ $EC_A0 -ne 0 ]]; then echo "FAIL: A baseline must succeed"; exit 1; fi
grep -q ENTERED_LOOP_RUN "$EV/deletion_A.txt" || { echo "FAIL: A did not enter run"; exit 1; }

rm -f "$SCRATCH/A/aar/research_loop/agent.py" "$SCRATCH/A/aar/research_loop/provider.py"
find "$SCRATCH/A/aar/research_loop" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

echo "=== A AFTER CORE DELETE ===" | tee -a "$EV/deletion_A.txt"
export DELETION_MARKER="$EV/deletion_A_after_marker.json"
export DELETION_RUNS="$SCRATCH/A_runs_after"
set +e
( cd "$SCRATCH/A" && "$PYBIN" "$HARNESS" ) >>"$EV/deletion_A.txt" 2>&1
EC_A1=$?
set -e
echo "A_AFTER_EXIT=$EC_A1" | tee -a "$EV/deletion_A.txt"
if [[ $EC_A1 -eq 0 ]]; then echo "FAIL: A after delete should fail"; exit 1; fi
echo "UPSTREAM_LOOP_DELETION_BREAKS_RUN=true" | tee -a "$EV/deletion_A.txt"
echo "A_LIVE_PROOF=true" | tee -a "$EV/deletion_A.txt"

############################################
# B: external provider deletion BREAKS RUN
############################################
cp -a "$SCRATCH/repo" "$SCRATCH/B"
export DELETION_REPO="$SCRATCH/B"
export DELETION_MARKER="$EV/deletion_B_entered.json"
export DELETION_RUNS="$SCRATCH/B_runs"
export PYTHONPATH="$SCRATCH/B:$SCRATCH/B/downstream/poc"
export AAR_AGENT_PROVIDER_PATH="$SCRATCH/B/downstream/poc"
export AAR_AGENT_PROVIDER_MODULE=aar_provider_002.providers.fast_stub
HARNESS="$SCRATCH/B/downstream/poc/aar_provider_002/scripts/live_deletion_harness.py"

echo "=== B BASELINE (enter loop.run) ===" | tee "$EV/deletion_B.txt"
set +e
( cd "$SCRATCH/B" && "$PYBIN" "$HARNESS" ) >>"$EV/deletion_B.txt" 2>&1
EC_B0=$?
set -e
echo "B_BASELINE_EXIT=$EC_B0" | tee -a "$EV/deletion_B.txt"
if [[ $EC_B0 -ne 0 ]]; then echo "FAIL: B baseline must succeed"; exit 1; fi
grep -q ENTERED_LOOP_RUN "$EV/deletion_B.txt" || { echo "FAIL: B did not enter run"; exit 1; }

rm -rf "$SCRATCH/B/downstream/poc/aar_provider_002/providers"

echo "=== B AFTER PROVIDER DELETE ===" | tee -a "$EV/deletion_B.txt"
export DELETION_MARKER="$EV/deletion_B_after_marker.json"
export DELETION_RUNS="$SCRATCH/B_runs_after"
set +e
( cd "$SCRATCH/B" && "$PYBIN" "$HARNESS" ) >>"$EV/deletion_B.txt" 2>&1
EC_B1=$?
set -e
echo "B_AFTER_EXIT=$EC_B1" | tee -a "$EV/deletion_B.txt"
if [[ $EC_B1 -eq 0 ]]; then echo "FAIL: B after delete should fail"; exit 1; fi
echo "EXTERNAL_PROVIDER_DELETION_BREAKS_RUN=true" | tee -a "$EV/deletion_B.txt"
echo "B_LIVE_PROOF=true" | tee -a "$EV/deletion_B.txt"

cat > "$OUT/LIVE_DELETION_PROOF.md" << MD
# LIVE_DELETION_PROOF — AAR-provider-002 PHASE 5

Scratch-tree tests (formal branch worktree untouched). Baseline **enters** \`AutonomousAgentLoop.run()\` (see ENTERED_LOOP_RUN), then component deleted, same harness fails.

| Test | Baseline | After delete | Claim |
|------|----------|--------------|-------|
| A delete core \`agent.py\`+\`provider.py\` | EXIT=$EC_A0 entered run | EXIT=$EC_A1 fail | \`UPSTREAM_LOOP_DELETION_BREAKS_RUN=true\` (LIVE) |
| B delete OUT \`providers/\` | EXIT=$EC_B0 entered run | EXIT=$EC_B1 fail | \`EXTERNAL_PROVIDER_DELETION_BREAKS_RUN=true\` (LIVE) |

Evidence: \`evidence/deletion_A.txt\`, \`evidence/deletion_B.txt\`, \`evidence/deletion_*_entered.json\`

Fast stub provider used only to make live run path cheap; still invokes \`AutonomousAgentLoop.run()\` (not import-only). Formal PHASE4 sessions used real grok_cli OIDC.
MD
echo "LIVE_DELETION_PROOF written"
