# Independent adversarial review — grok_build_provider

**Verdict: PASS**

The negative result is honest. There is no workspace-callable Build Agent invocation surface (layer C). `GrokBuildAgentProvider` was not added, `AutonomousAgentLoop` was not run, and grok CLI / XAI API / Claude were not used. AAR core is untouched. I did not find a hidden C-layer interface that this writeup concealed.

Re-review after the doc update: README flag block sets `WORKSPACE_CAN_INVOKE_BUILD_AGENT=false` and `GROK_BUILD_NATIVE_AAR_PASS=false`. Spot-check (diag GET `/ready` 200, GET `/spawn_subagent` 404, preview-state `agent_spawned=false`, both socket paths inode 263646, ANSI-stripped log `tool_count=34` with `spawn_subagent` and `total_hooks=0`) matches those docs. No new Python, no core diff, no C-layer surface, no false pass.

## What I re-ran

Checkout `/tmp/aar-src`, branch `downstream/aar-provider-002`, HEAD `01067d70f001ee99b229089acd0dba63e7f3a5ed` (matches the expected pin). `downstream/UPSTREAM_PIN.json` pins `02dbe9d2cadc553720d17cdf6259c0b8727e6cde`. `git diff HEAD` is empty. `git status` shows only untracked files under `downstream/poc/grok_build_provider/` (markdown + `evidence/PROBES.txt`). No Python in that directory. No diff to `aar/` or `run.py`.

Provider seam (read, not executed):

- `aar/research_loop/provider.py:89` `get_agent_provider`. Built-ins are only `_BUILTIN_CLAUDE = {claude, claude_sdk, anthropic}` → `ClaudeSDKProvider`. Any other name requires `AAR_AGENT_PROVIDER_MODULE`. No grok/xAI branch.
- `aar/research_loop/agent.py:229` `BaseAgent`; `:313` `provider.session` then query/receive; `:375` `class AutonomousAgentLoop`. Not instantiated.

Vendor string count, case-insensitive `grok|xai|grok_cli|AAR_GROK|aar_xai_adapter`, Python files only under `aar/research_loop` plus `run.py`: **0 matches in 21 files**.

Live sandbox (no secrets printed, no auth file read, hub websocket not opened):

- `xai-workspace-server --help`: outbound `--hub-url` default `wss://computer-hub.grok.com/v1/tools`. `--diag-socket` is an in-guest diagnostics HTTP server (`/ready`, `/statusz`) only. `--capabilities` prints `{"diag": true}` and exits. No agent subcommand.
- Running process is that binary dialing the hub (`--auth-config` path noted, file not read), plus preview proxy on 6014/6015 and `grok-files` FUSE. Log: "diagnostics server listening addr=unix:/tmp/workspace-server.sock"; "sessions created dynamically via server bind"; hooks discovered `total_hooks=0` including `user_prompt_submit=0` and `subagent_start=0`.
- Named unix socket in `/proc/net/unix`: only `/tmp/workspace-server.sock`. `/var/tmp/workspace-server/tmp/workspace-server.sock` is the **same inode** (263646), not a second service.
- TCP listeners: `0.0.0.0:6014` (preview) and `127.0.0.1:6015` (preview control). No UDP listeners.
- Diag GET `/ready` → 200 `state=connected` `version=1.0.63`. GET `/statusz` → 200 with image capability names only. GET and empty POST of `/`, `/agent`, `/v1/chat/completions`, `/v1/messages`, `/prompt`, `/spawn_subagent`, `/tools`, `/rpc`, `/hooks`, and the other paths in the coordinator list → **404**. Non-404 diag routes: `/ready` and `/statusz` only.
- Preview control GET `/__control/activity`, `/__control/metrics`, `/__control/preview-state` → 200 status documents. `preview-state` body is `server_running=false`, `agent_spawned=false`, `candidate_count=0`, `frameworks=[]`. That `agent_spawned` flag is preview-target discovery, not an LLM prompt API. GET `/` and `/agent` on `:6015` → 404. `:6014` GET `/` and `/agent` → 403 (owner gate), not a completions route.
- `command -v grok|grok-cli|xai|claude|anthropic` → absent. No such binaries under `/usr`, `/opt`, `/root`, `/workspace` (names only). `python3` imports of `grok`, `xai`, `xai_sdk`, `openai`, `anthropic`, `claude_agent_sdk`, `claude_sdk` → `ModuleNotFoundError`. No matching site-packages.
- Hub tool catalog registered by the workspace server (names only, from the server log): includes `spawn_subagent` among ~33 tools (`tool_count` logged as 34). Those tools are advertised **to the hub**. Guest Python has no socket, route, or module that invokes them. Binary protobuf text mentions `.chat.SubAgentTool`, `task` / `spawn_subagent`, and Grok Bot `bot_send_prompt`; those are linked descriptors, not a local RPC. No `/ready`-style route string for spawn/prompt survived in the binary candidate scan.
- `GROK_CLI_CHAT_PROXY_BASE_URL` is a remote `https://cli-chat-proxy.grok.com/v1` URL. `XAI_API_KEY` is set in the environment. Neither was called. `/etc/grok` is absent. `~/.grok/auth.json` exists and was not read.

## Attack table

HIT = the false-positive pattern is present in this experiment. MISS = it is not.

| # | Attack | Result | Evidence |
|---|---|---|---|
| 1 | Coordinator did the research task and claimed a provider called an agent | MISS | `SMOKE_RESULT.md` leaves the `sorted()` goal unexecuted and sets `AAR_RESEARCHER_EXECUTED=false`. No provider module exists. |
| 2 | `GROK_BUILD_PROVIDER_OK` printed by the coordinator, not via a provider | MISS | String appears only as a refusal ("emitting it would not be evidence"). No success line, no probe script. |
| 3 | Homemade loop impersonating `AutonomousAgentLoop` | MISS | No new Python. Class remains only in `aar/research_loop/agent.py`. Not started. |
| 4 | Bypassing the existing provider seam | MISS | No `AAR_AGENT_PROVIDER_MODULE` plugin added. Seam still requires a module for non-Claude names. |
| 5 | Sneaking `GrokCLIProvider` | MISS | Pre-existing `downstream/poc/aar_provider_002/providers/grok_cli.py` is on the branch and was not imported or executed. `grok` is not on `PATH`. |
| 6 | Sneaking XAI API key | MISS | Key is present in the environment. No poc code reads or sends it. No local or remote completions call was made by this experiment's files. |
| 7 | Sneaking Claude/Anthropic | MISS | No `claude` binary, no `anthropic` import, no Anthropic call in the poc. Legacy `ClaudeSDKProvider` remains in core and was not constructed. |
| 8 | Mock/fake agent response | MISS | No stub session, no canned researcher answer, no `GROK_BUILD_PROVIDER_OK` payload. |
| 9 | AAR state claimed advanced when it was not | MISS | Docs claim `AAR_STATE_ADVANCED=false`, `AAR_ITERATIONS=0`, `SMOKE_RUN_ID=none`. No state file was written. |
| 10 | Insufficient Build Agent invocation evidence for a PASS | MISS | They do **not** claim a native AAR pass. The negative flags are the result. There is no invocation transcript because there was no invocation. |
| 11 | Equating harness subagent spawn with a workspace provider call | MISS | `RUNTIME_DISCOVERY.md` separates A (this chat), B (harness `task` / hub `spawn_subagent`), and C (guest Python). They mark only C as the provider question and answer no. |
| 12 | Build-specific logic written into vendor-neutral AAR core | MISS | `git diff` for `aar/` and `run.py` is empty. Vendor grep count is 0. |

## C-layer surface

**No.**

What would count: a binary, unix socket path, local HTTP route, or Python module that accepts a researcher prompt and returns a model completion without the grok CLI and without `XAI_API_KEY`.

What exists instead, and why it is not C:

- Layer A: this chat session works. Not callable from guest Python.
- Layer B: the model harness `task` tool, and the workspace server's hub-registered `spawn_subagent` tool. I am a subagent; that only proves the harness can spawn me. The server executes hub tool calls; it does not expose `spawn_subagent` on the diag socket (POST `/spawn_subagent` → 404).
- Diag socket `/tmp/workspace-server.sock`: `/ready` and `/statusz` only.
- Preview ports 6014/6015: reverse proxy and control plane. `agent_spawned` is a preview discovery boolean, currently false, with no prompt body accepted on those paths.
- Remote CLI chat proxy URL and `XAI_API_KEY`: forbidden transports, not a Build-native provider surface, and not used.
- Outbound hub websocket: tool-call ingress from the hub. Not opened. Not a documented guest prompt API.

Missing interface: a supported in-guest RPC/SDK/hook whose input is a prompt and whose output is the Build Agent's response, callable from the same Python process that would implement `AgentProvider.session()`.

## Nits (re-review)

1. CLOSED. `README.md` flag block now assigns `WORKSPACE_CAN_INVOKE_BUILD_AGENT=false` and `GROK_BUILD_NATIVE_AAR_PASS=false`.
2. CLOSED. `RUNTIME_DISCOVERY.md` probe 10 and `evidence/PROBES.txt` cite hub `tool_count=34`, `spawn_subagent`, and `total_hooks=0` (`user_prompt_submit=0`, `subagent_start=0`). Confirmed in the workspace-server log after stripping ANSI.
3. CLOSED. Preview-state `agent_spawned=false` is documented as dev-server discovery, not an LLM API. Live GET still returns that JSON.
4. CLOSED. Same-inode alias `/var/tmp/workspace-server/tmp/workspace-server.sock` (inode 263646) is documented. Live `stat` matches. `/proc/net/unix` still names only `/tmp/workspace-server.sock`.
5. CLOSED. `REVIEW.md` exists at `downstream/poc/grok_build_provider/REVIEW.md`.

No nit remains open. None of the closed nits was a C-layer surface, a core edit, or a fake pass.

## Non-use (this reviewer)

I did not invoke the grok CLI, did not read or send `XAI_API_KEY`, did not call Claude or Anthropic, did not read `~/.grok/auth.json` or other secret files, did not attach to the hub websocket, did not implement a provider, and did not start `AutonomousAgentLoop`.
