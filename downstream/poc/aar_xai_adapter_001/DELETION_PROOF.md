# DELETION_PROOF — AAR-xAI-adapter-001 PHASE 4

Destructive copy tests in scratch dir (formal branch worktree untouched).

| Test | Result |
|------|--------|
| A delete upstream research-loop core (`agent.py`+`provider.py`) | BREAKS import — see evidence/deletion_A.txt |
| B delete Grok provider package | BREAKS `get_agent_provider()` for grok_cli — see evidence/deletion_B.txt |

| Field | Value |
|-------|-------|
| UPSTREAM_LOOP_DELETION_BREAKS_RUN | true |
| GROK_PROVIDER_DELETION_BREAKS_RUN | true |

Both true ⇒ native loop + grok provider are jointly required for xAI OAuth path.
