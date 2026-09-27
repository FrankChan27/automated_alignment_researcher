# AAR-POC-002 — Native upstream AAR (submit-model) proof

Downstream-only scaffolding to prove **CAN_WE_RUN_UPSTREAM_NATIVE_AAR**.

- **Does use:** official `AutonomousAgentLoop` + MCP `evaluate_model` + `aar.eval_pod.run_eval` / `generic_aar` extension surface.
- **Does not:** copy `aar_poc_001` run_loop/proposer; does not rewrite `aar/` or `generic_aar/` in phase 1.

| Doc | Purpose |
|-----|---------|
| `execution_path.md` | Cited ENTRYPOINT→…→NEXT ITERATION hops |
| `blocker_probe.md` | Env probe + unpatched failure transcripts |
| `design.md` | 8-d `[0,100]` vector adapter on suite YAML + submit-model |
| `evidence/` | Raw smoke / failure logs |
| `adapter/` | Phase-2 package skeleton (no research loop) |

Secrets: `/home/box/aar-poc-002-secrets/` (mode 0700, outside git).  
Smoke venv: `/home/box/aar-poc-002-venv` (PyYAML for stub eval).
