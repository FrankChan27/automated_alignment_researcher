# AAR-POC-002 STATUS

**Updated:** 2026-09-28 ~01:54 UTC+8  
**Branch:** `downstream/aar-poc-002-native`  
**HUMAN=0** — no Anthropic key; A-company forbidden; **no agent-loop attempts**.

## Verdict

| Flag | Value |
|------|--------|
| **UPSTREAM_NATIVE_UNPATCHED** (agent loop) | **BLOCKED** — Claude hard-bind |
| Eval/adapter smoke (vector → `run_eval`) | **PASS** |
| Deletion proof (`aar/`+`generic_aar/` required) | **PASS** (`DELETION_PROOF_OK`) |
| Fake/native substitute loop | **NOT USED** (no POC-001 `run_loop`/`proposer`) |

## Claude hard-bind (why agent loop is BLOCKED)

Verified in-tree (evidence: `evidence/unpatched_failures/claude_hardbind_probe.txt`):

1. **`run.py:cmd_agent`** — exits if `ANTHROPIC_API_KEY` unset (`Error: ANTHROPIC_API_KEY is required for agent mode`).
2. **`aar/research_loop/agent.py`** — imports `claude_agent_sdk` (`ClaudeSDKClient`, `ClaudeAgentOptions`); default model `claude-opus-4-8`.
3. **`AutonomousAgentLoop._create_agent`** — `cli_path=shutil.which("claude")` (Claude CLI required on PATH).

This environment: **no API key**, **`claude` CLI ABSENT**. Per policy we do **not** request keys or rewrite the loop to fake native. Agent ≥5-iter run is **not claimed**.

UNPATCHED transcripts: `evidence/unpatched_failures/agent_local.txt` (key gate), `agent_local_with_fake_key.txt` (sdk missing before venv), `claude_hardbind_probe.txt`.

## PASS (no-agent path)

| Item | Evidence |
|------|----------|
| Task adapters (hillclimb/heldout/capability) | `adapter/benchmarks/*.py` |
| VectorModel monkeypatch (process-start only) | `adapter/models_vector.py` |
| Suite + briefing + env | `adapter/suite.yaml`, `briefing.md`, `env.example` |
| Method template (fixture, not a loop) | `method_templates/vector_submit/` |
| Secrets out-of-tree mode 700 | `/workspace/aar-infra/poc002_eval_secret/{train,heldout}.json` |
| Eval smoke: near > mid; oob fails capability | `evidence/smoke/` (`SMOKE_OK`) |
| Venv deps | `evidence/deps_install.log`; `/home/box/aar-poc-002-venv` |
| Server import smoke (Flask + agent import) | `evidence/server_import_smoke.txt` |
| Deletion proof | `evidence/deletion_proof/result.txt` |

## Launch (eval only)

```bash
bash downstream/poc/aar_poc_002/scripts/eval_smoke.sh
bash downstream/poc/aar_poc_002/scripts/deletion_proof.sh --exec
```

Do **not** run `launch_agent.sh` without an allowed non-A-company path; upstream loop is Claude-hard-bound.
