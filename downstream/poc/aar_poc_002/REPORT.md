# AAR-POC-002 REPORT (freeze-and-stop)

**Date:** 2026-09-28 (UTC+8)  
**Branch:** `downstream/aar-poc-002-native`  
**HEAD_SHA:** `13a7d2ed75cf471b926f19405a905548a3ea98c3`  
**BASE_SHA:** `c145825e096547ea7f42014aa3474041ec64a643`  
**PINNED_UPSTREAM_SHA:** `02dbe9d2cadc553720d17cdf6259c0b8727e6cde`

## Verdict

| Claim | Result |
|-------|--------|
| `UPSTREAM_NATIVE_UNPATCHED` (native `run.py agent` ≥5 iters) | **BLOCKED** |
| `CAN_WE_SCORE_VECTOR_VIA_NATIVE_EVAL` | **PASS** |
| `REPO_SECRET_PRESENT` | **false** |
| Reviewer | **deferred by user** |

## Why agent is BLOCKED

Official entrypoint hard-binds Anthropic / Claude Agent SDK:

- `run.py:33-34` — exits unless `ANTHROPIC_API_KEY`
- `aar/research_loop/agent.py` — `ClaudeSDKClient` / Claude models / `claude` CLI

User decision 2026-09-28: freeze eval evidence only; no Anthropic; no Reviewer; no agent loop; no PATCHED provider swap; no POC-001 substitute loop.

Evidence: `evidence/anthropic_hard_bind.md`, `evidence/unpatched_failures/UPSTREAM_NATIVE_UNPATCHED_BLOCKED.md`, `evidence/FREEZE_VERDICT.md`.

## What eval evidence proves (frozen)

Downstream-only adapter under `downstream/poc/aar_poc_002/adapter/` scores the 8-d vector suite via native `aar.eval_pod.run_eval` (monkeypatch loader; no `aar/` / `generic_aar/` edit):

- hillclimb + held-out + capability roles
- research scores strip held-out; full held-out only under `/home/box/aar-poc-002-secrets/` (0700, outside repo)
- smoke PASS: `evidence/freeze_eval_only_smoke.txt`, `evidence/smoke/`

## Secrets

Secrets live only in `/home/box/aar-poc-002-secrets/` (not in git). Scan: `evidence/repo_secret_absent.txt` → `REPO_SECRET_PRESENT=false`.

## Explicitly not done

- No Reviewer
- No agent loop / Anthropic calls
- No provider swap or 001-style substitute loop
- Stop after this freeze commit + push
