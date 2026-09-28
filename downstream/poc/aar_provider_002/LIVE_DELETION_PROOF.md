# LIVE_DELETION_PROOF — AAR-provider-002 PHASE 5

Scratch-tree tests (formal branch worktree untouched). Baseline **enters** `AutonomousAgentLoop.run()` (see ENTERED_LOOP_RUN), then component deleted, same harness fails.

| Test | Baseline | After delete | Claim |
|------|----------|--------------|-------|
| A delete core `agent.py`+`provider.py` | EXIT=0 entered run | EXIT=1 fail | `UPSTREAM_LOOP_DELETION_BREAKS_RUN=true` (LIVE) |
| B delete OUT `providers/` | EXIT=0 entered run | EXIT=1 fail | `EXTERNAL_PROVIDER_DELETION_BREAKS_RUN=true` (LIVE) |

Evidence: `evidence/deletion_A.txt`, `evidence/deletion_B.txt`, `evidence/deletion_*_entered.json`

Fast stub provider used only to make live run path cheap; still invokes `AutonomousAgentLoop.run()` (not import-only). Formal PHASE4 sessions used real grok_cli OIDC.
