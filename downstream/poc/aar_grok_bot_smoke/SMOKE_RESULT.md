# SMOKE_RESULT

## Acceptance
| Field | Value |
|-------|-------|
| SMOKE_RUN_ID | `2b3da386-46d1-46d9-8073-75c6f38c69cc` |
| AAR_STATE_ADVANCED | True |
| AAR_ITERATIONS | 1 |
| PROVIDER_CALLS | 1 |
| GROK_RESEARCHER_CALLS | 1 |
| EXPERIMENT_EXECUTED | True |
| AUTH_MECHANISM | `grok_bot_sand_gateway_bearer` |
| OAUTH_USED | False |
| XAI_API_KEY_USED | False |
| ANTHROPIC_USED | False |
| ERROR | None |

## STATE hashes
- STATE_BEFORE fingerprint: `fecc6ec5c6511bfe`
- STATE_AFTER fingerprint: `69756fb9cc9a5926`
- BEFORE files: `{"findings.json": "124218f3a4698ec4", "STATE.json": "e0014317d5496406", "experiment/stable_sort_test.py": "EMPTY", "experiment/output.txt": "EMPTY", "experiment/conclusion.json": "EMPTY"}`
- AFTER files: `{"findings.json": "70746f59d72feaa0", "STATE.json": "e0014317d5496406", "experiment/stable_sort_test.py": "b7053bb499a1eaf5", "experiment/output.txt": "48e19380c24a633e", "experiment/conclusion.json": "ae3ff4fff65d02cb"}`

## Experiment
- stable: **True**
- summary: list.sort() preserved original relative order for equal keys on (key, original_index) pairs; Timsort is stable.
- code: `/workspace/aar_grok_bot_smoke_work/runs/2b3da386-46d1-46d9-8073-75c6f38c69cc/experiment/stable_sort_test.py`
- output: `/workspace/aar_grok_bot_smoke_work/runs/2b3da386-46d1-46d9-8073-75c6f38c69cc/experiment/output.txt`
- conclusion: `/workspace/aar_grok_bot_smoke_work/runs/2b3da386-46d1-46d9-8073-75c6f38c69cc/experiment/conclusion.json`

## Loop
```json
{
  "run_id": "2b3da386-46d1-46d9-8073-75c6f38c69cc",
  "idea_uid": "aar-grok-bot-smoke-sort",
  "idea_name": "list_sort_stability",
  "sessions": 1,
  "duration_seconds": 36.276063680648804,
  "stop_reason": "max_iterations"
}
```

## Workspace
`/workspace/aar_grok_bot_smoke_work/runs/2b3da386-46d1-46d9-8073-75c6f38c69cc`

## Provider
- name: `grok_bot_gateway`
- module: `aar_grok_bot_smoke.providers.grok_bot_gateway`
- researcher: `fac98a36-f560-43b8-9ac8-1ddacbbd16ed`
