# Auth diagnosis (smoke v3)

No secret values are recorded here.

## What failed

Official grok 1.0.41 with `XAI_API_KEY` removed from the environment:

- `grok models` → `You are not authenticated.`
- a one-shot prompt → exit 1, `Not signed in`
- debug line: `Auth("No auth credentials for cli-chat-proxy")`
- `~/.grok/auth.json` was present (`auth_mode=oidc`, key and refresh token present, unexpired) and was still not a CLI login

That is the known GrokCLIProvider failure. It is not sufficient to stop: the same CLI documents `XAI_API_KEY` as non-interactive auth.

## What worked

With the platform-injected `XAI_API_KEY` left in the environment (Anthropic variables removed):

- `grok models` → `You are using XAI_API_KEY.` and listed grok-4.5 / grok-4.7
- the provider subprocess reached `api.x.ai` (receipt `saw_api_x_ai=true`, `grok_http_calls=5`)
- session tool trace `model_id=grok-4.5`
- no `api.anthropic.com`

`GrokCLIProvider` no longer deletes `XAI_API_KEY`. It still deletes Anthropic credentials.
