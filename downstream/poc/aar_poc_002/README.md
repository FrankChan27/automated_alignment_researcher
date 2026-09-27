# AAR-POC-002 — Native upstream AAR (submit-model) proof

Downstream-only adapters proving **CAN_WE_RUN_UPSTREAM_NATIVE_AAR** for an 8-d integer
vector hill-climb. Uses official `AutonomousAgentLoop` + MCP `evaluate_model` +
`aar.eval_pod.run_eval` / `generic_aar`-style suite surfaces.

**Does not** copy `aar_poc_001` `run_loop` / `proposer`. **Does not** edit `aar/` or
`generic_aar/` on disk (VectorModel is a process-start monkeypatch only).

| Path | Purpose |
|------|---------|
| `execution_path.md` | Cited native ENTRYPOINT→NEXT ITERATION map |
| `DESIGN.md` / `design.md` | Adapter design + score semantics |
| `STATUS.md` | Current pass/blockers |
| `briefing.md` | Agent briefing (no secrets) |
| `adapter/` | Suite, VectorModel shim, RuleBenchmarks, eval entry |
| `method_templates/vector_submit/` | Fixture method writing `vector.json` |
| `scripts/` | Eval smoke, server/agent launch, deletion proof |
| `env.example` | Env vars (secret *paths* only) |
| `evidence/` | Unpatched failures, deps log, smoke scores |

## Secrets (out of git)

```
/workspace/aar-infra/poc002_eval_secret/   # mode 700 — train.json, heldout.json
/workspace/aar-infra/poc002_holdout/       # HOLDOUT_DIR / held-out scores
/home/box/aar-poc-002-secrets/            # mirror of the same params
```

Never commit secrets; never put secret values in researcher env/prompt/logs.

## Venv

`/home/box/aar-poc-002-venv` (also `/workspace/aar-infra/.venv-poc002` → symlink).

## How to launch

```bash
# (a) Eval smoke (no API key)
bash downstream/poc/aar_poc_002/scripts/eval_smoke.sh

# (b) Native server + agent (needs ANTHROPIC_API_KEY + `claude` CLI)
bash downstream/poc/aar_poc_002/scripts/launch_server.sh   # term 1
bash downstream/poc/aar_poc_002/scripts/launch_agent.sh 5 # term 2

# (c) Deletion proof
bash downstream/poc/aar_poc_002/scripts/deletion_proof.sh --exec
```

## Scoring (POC-001 semantics)

`score = base - Σ w_i (clamp(v_i)-T_i)² - oob_penalty · n_oob`, normalized by `base`
for suite closed%. Capability requires length-8 ints in `[0,100]`.
