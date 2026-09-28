# PROVIDER_PROBE

## Result
- PROBE_OK: True
- EXACT_MATCH: True
- duration_s: 7.21
- reply: `GROK_BOT_AAR_PROVIDER_OK`

## Provider
- name: grok_bot_gateway
- module: aar_grok_bot_smoke.providers.grok_bot_gateway
- requires_anthropic_key: False
- supports_inprocess_mcp: False
- researcher_agent_id: fac98a36-f560-43b8-9ac8-1ddacbbd16ed
- auth_mechanism: grok_bot_sand_gateway_bearer
- oauth_used: False
- xai_api_key_used: False

## Evidence paths
- `/workspace/aar_grok_bot_smoke_work/evidence/provider_probe/probe_result.json`
- `/workspace/aar_grok_bot_smoke_work/evidence/provider_probe/reply.txt`
- mirrored under `downstream/poc/aar_grok_bot_smoke/evidence/provider_probe/`

## Method
Unique marker `GROK_BOT_AAR_PROVIDER_OK` requested via `AgentProvider.session` only
(coordinator did not fabricate the string).
