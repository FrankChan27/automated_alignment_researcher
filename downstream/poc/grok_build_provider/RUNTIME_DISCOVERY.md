# RUNTIME_DISCOVERY

Date: 2026-09-28 (UTC). Host role: Grok Build app-builder sandbox
(`GROK_SANDBOX_PROFILE=off`, `SANDBOX_SERVICE_ENV=prod`).
No secrets, auth files, or API key values are recorded here.

## Question

Does workspace Python (the process an AAR external provider would be)
have a supported way to submit a researcher prompt to the **current**
Grok Build Agent/runtime and receive the model response?

Layers, kept separate:

| Layer | Meaning | Found? |
|---|---|---|
| A | The current Build Agent can execute this task | yes |
| B | That agent can dispatch other agents/subagents | yes, harness-only |
| C | Workspace Python can programmatically invoke A or B | **no** |

A and B are not C. A coordinator that answers a prompt itself, or that
manually relays a file queue into the `task` tool, is not an invocation
surface the provider can call.

## What is actually running

Process (cmdline, secrets stripped):

- PID of `xai-workspace-server` (`/usr/local/bin/xai-workspace-server`,
  binary also at `/opt/workspace-server/xai-workspace-server-1.0.63`,
  version reported by diag: `1.0.63`).
- Flags that matter: `--hub-url wss://computer-hub.grok.com/v1/tools`,
  `--require-explicit-toolset`, `--daemonize`, preview proxy supervision.
- Direction: the server **dials out** to the computer hub and **executes
  tool calls the hub sends in**. It is not an inbound agent runner.
- Log evidence (redacted): `before_turn hook received` for the current
  chat session, `model=grok-chat-app-builder`. Hooks arrive **from** the
  hub when a turn already exists. No local API starts a turn.
- Companion processes: `xai-grok-preview-proxy` (preview only),
  `grok-files` FUSE. No `grok` CLI process.

`xai-workspace-server --help` documents `--diag-socket` as:

> Unix-socket path for the in-guest diagnostics HTTP server
> (`/ready`, `/statusz`). Default: `/tmp/workspace-server.sock`.

`--capabilities` prints `{"diag": true}` and exits. It is a feature probe
for the launcher, not an agent catalog.

## Probes (all from this sandbox)

1. **Unix sockets** (`/proc/net/unix` paths): only
   `/tmp/workspace-server.sock` (inode 263646).
   `/var/tmp/workspace-server/tmp/workspace-server.sock` is the **same
   inode**, not a second service.
2. **TCP listeners**: `0.0.0.0:6014` (preview proxy) and `127.0.0.1:6015`
   (preview control). `GET /` and `GET /agent` on `:6015` → 404.
   `:6014` `GET /` and `GET /agent` → 403 (owner gate), not a
   completions route.
3. **Preview control is not an agent API.**
   `GET http://127.0.0.1:6015/__control/preview-state` returns:

   ```json
   {"server_running":false,"agent_spawned":false,"candidate_count":0,"frameworks":[],"agent_target_set":false,"generation":1}
   ```

   `agent_spawned` means the preview proxy has not seen a dev server.
   It is not an LLM prompt API and accepts no prompt body.
4. **Diag HTTP** (Unix socket, real status lines):
   - `GET /ready` → `200` JSON `state=connected`, `version=1.0.63`
   - `GET /statusz` → `200` plus image capability names
     (`agent-browser.cli`, `app-builder.*`, `git.present`, `node.22`, …).
     None of those capabilities is an agent-prompt API.
   - `GET` `/`, `/health`, `/healthz`, `/metrics`, `/tools`, `/v1`,
     `/v1/agent`, `/v1/chat/completions`, `/agent`, `/api/agent`,
     `/subagent`, `/spawn_subagent`, `/rpc`, `/hooks`, `/status`,
     `/debug`, `/debug/pprof` → `404`.
     Independent review also POSTed several of these, including
     `/spawn_subagent`, and got 404.
5. **Binaries on `PATH`**: `python3`, `xai-workspace-server`,
   `xai-grok-preview-proxy`, `grok-files`, `grove` (git virtual FS, not
   an LLM). `command -v grok` → absent. No `grok` / `grok-cli` / `xai`
   executable under `/usr`, `/opt`, `/root`, `/workspace`.
6. **Python imports**: `grok`, `xai`, `xai_sdk`, `openai` →
   `ModuleNotFoundError`. No site-package client. Reviewer also checked
   `anthropic`, `claude_agent_sdk`, `claude_sdk` → `ModuleNotFoundError`.
7. **`/etc/grok`**: absent. `~/.grok` contains `auth.json` (not read, not
   used), `server-skills/`, `workspace/upload_queue/`. Auth file is the
   CLI/OIDC store; this experiment does not call the CLI.
8. **Env present but unused**: `XAI_API_KEY` is set (value never read).
   `GROK_CLI_CHAT_PROXY_BASE_URL` points at the CLI chat proxy. Both are
   the forbidden CLI/API transports, not a Build-native provider surface,
   and neither was called.
9. **Binary string scan** of `xai-workspace-server`: protobuf descriptors
   include `.chat.SubAgentTool`, `subagent_completed`, `agent_spawned`.
   These are linked chat-stack types / telemetry names, not a guest HTTP
   route. No diag or local RPC path for `spawn` / `agent.run` survived
   the route probe.
10. **Live hub tool catalog** (workspace-server log, names only): at
    startup the server registers its catalog **on the hub** with
    `tool_count=34`, including `spawn_subagent` next to
    `run_terminal_command` and `read_file`. Hook discovery in the same
    log: `total_hooks=0`, `user_prompt_submit=0`, `subagent_start=0`.
    Those tools are offered to the hub. Guest Python has no socket,
    route, or module that calls them.

## Image capabilities vs agent invocation

`/usr/share/grok/capabilities.d/` declares preview, browser, git, node,
ffmpeg, grove, and `app-builder.xai-api-token`. The xAI API token
capability is explicitly **not** the native Build Agent runtime and was
not used (forbidden by the experiment).

## Harness tools that are not C

The coordinating model in this session has a `task` tool that can start
a subagent. That tool is implemented in the **model harness**. The
workspace server also advertises `spawn_subagent` to the hub (probe 10).
Guest code cannot import either one or HTTP-call them
(`POST /spawn_subagent` on the diag socket → 404).

Using the harness tool as a manual bridge (provider writes a file,
coordinator calls `task`, coordinator writes the answer back) is layer B
operated by the coordinator. It does not make
`WORKSPACE_CAN_INVOKE_BUILD_AGENT` true, and it would be a false
positive under review attacks 1 and 11.

Hijacking the live hub websocket to inject a user prompt was **not**
attempted: the socket is owned by the tool server, the protocol is
tool-call ingress, and forging a chat turn would be an unsupported
second session rather than a documented provider seam.

## Missing layer

The missing interface is a **supported, workspace-callable invocation
API** (local RPC, SDK, or sanctioned runtime hook) with roughly:

- input: researcher prompt (and optional system/tool bounds)
- effect: the current Grok Build Agent runtime executes that prompt
- output: the agent text/result returned to the calling process

Until that exists, an external provider can implement the AAR
`AgentProvider` protocol and then has nowhere honest to send `query()`.

## Explicit non-use

- grok CLI: not invoked (binary not installed)
- `XAI_API_KEY` / chat-completions: not called
- Anthropic / Claude API / Claude CLI: not called
- `GrokCLIProvider`: not imported, not executed
- AAR `AutonomousAgentLoop.run`: not started (doing so without a real
  provider would hit the Claude legacy default or a stub)
