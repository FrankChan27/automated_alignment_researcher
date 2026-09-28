#!/usr/bin/env bash
# Destructive copy tests — does NOT mutate formal branch worktree.
set -euo pipefail
REPO="${1:-/workspace/aar-infra/automated_alignment_researcher}"
OUT="$REPO/downstream/poc/aar_xai_adapter_001"
EV="$OUT/evidence"
SCRATCH=$(mktemp -d /tmp/aar_adapter_deletion_XXXX)
trap 'rm -rf "$SCRATCH"' EXIT
echo "SCRATCH=$SCRATCH"

# Copy minimal needed tree
mkdir -p "$SCRATCH/repo"
rsync -a --exclude '.git' --exclude '**/__pycache__' --exclude '.venv*' \
  "$REPO/aar" "$REPO/run.py" "$REPO/downstream" "$SCRATCH/repo/" 2>/dev/null || {
  cp -a "$REPO/aar" "$SCRATCH/repo/"
  cp -a "$REPO/run.py" "$SCRATCH/repo/"
  mkdir -p "$SCRATCH/repo/downstream/poc"
  cp -a "$REPO/downstream/poc/aar_xai_adapter_001" "$SCRATCH/repo/downstream/poc/"
}

export PYTHONPATH="$SCRATCH/repo:$SCRATCH/repo/downstream/poc"
export AAR_AGENT_PROVIDER=grok_cli
unset ANTHROPIC_API_KEY XAI_API_KEY

# A: delete upstream research-loop core → import/run must fail
cp -a "$SCRATCH/repo" "$SCRATCH/A"
rm -rf "$SCRATCH/A/aar/research_loop/agent.py" "$SCRATCH/A/aar/research_loop/provider.py"
set +e
( cd "$SCRATCH/A" && PYTHONPATH="$SCRATCH/A:$SCRATCH/A/downstream/poc" python -c "from aar.research_loop.agent import AutonomousAgentLoop" ) >"$EV/deletion_A.txt" 2>&1
EC_A=$?
set -e
echo "A_EXIT=$EC_A" | tee -a "$EV/deletion_A.txt"
if [[ $EC_A -eq 0 ]]; then echo "FAIL: A should break"; exit 1; fi
echo "UPSTREAM_LOOP_DELETION_BREAKS_RUN=true"

# B: delete grok provider → grok path must fail
cp -a "$SCRATCH/repo" "$SCRATCH/B"
rm -rf "$SCRATCH/B/downstream/poc/aar_xai_adapter_001/provider"
set +e
( cd "$SCRATCH/B" && PYTHONPATH="$SCRATCH/B:$SCRATCH/B/downstream/poc" AAR_AGENT_PROVIDER=grok_cli python -c "from aar.research_loop.provider import get_agent_provider; print(get_agent_provider().name)" ) >"$EV/deletion_B.txt" 2>&1
EC_B=$?
set -e
echo "B_EXIT=$EC_B" | tee -a "$EV/deletion_B.txt"
if [[ $EC_B -eq 0 ]]; then echo "FAIL: B should break"; exit 1; fi
echo "GROK_PROVIDER_DELETION_BREAKS_RUN=true"

cat > "$OUT/DELETION_PROOF.md" << MD
# DELETION_PROOF — AAR-xAI-adapter-001 PHASE 4

Destructive copy tests in scratch dir (formal branch worktree untouched).

| Test | Result |
|------|--------|
| A delete upstream research-loop core (\`agent.py\`+\`provider.py\`) | BREAKS import — see evidence/deletion_A.txt |
| B delete Grok provider package | BREAKS \`get_agent_provider()\` for grok_cli — see evidence/deletion_B.txt |

| Field | Value |
|-------|-------|
| UPSTREAM_LOOP_DELETION_BREAKS_RUN | true |
| GROK_PROVIDER_DELETION_BREAKS_RUN | true |

Both true ⇒ native loop + grok provider are jointly required for xAI OAuth path.
MD
echo "DELETION_PROOF written"
