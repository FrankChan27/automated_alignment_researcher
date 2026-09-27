# AAR-POC-002 — Native upstream AAR (submit-model) proof

Downstream-only adapters to prove **CAN_WE_RUN_UPSTREAM_NATIVE_AAR**.

| Path | Purpose |
|------|---------|
| `execution_path.md` | Cited native hops |
| `blocker_probe.md` | Env / deps / server / CLI blockers |
| `design.md` | Adapter design |
| `briefing.md` | Agent-facing task brief (no secrets) |
| `env.example` | Launch env (paths only) |
| `adapter/` | Suite + VectorModel shim + benches + `eval.py` |
| `scripts/` | `env.sh`, `run_eval.sh`, smoke / server wrappers |
| `method_templates/vector_submit/` | Idea `run.py` template (not a research loop) |
| `evidence/` | Install / smoke / secret-absent / server transcripts |

**Secrets (never in git):** `/home/box/aar-poc-002-secrets/` mode 0700 (`train.json`, `heldout.json`)  
**Runtime:** `/home/box/aar-poc-002-runs/`  
**Venv:** `/home/box/aar-poc-002-venv`

### Quick smoke (no Anthropic)

```bash
source /home/box/aar-poc-002-venv/bin/activate
bash downstream/poc/aar_poc_002/scripts/run_eval.sh \
  downstream/poc/aar_poc_002/adapter/fixtures/example_vector_dir \
  /home/box/aar-poc-002-runs/research_scores/out.json
```

Research scores strip held-out; full scores land only under `$HELDOUT_SCORES_DIR`.
