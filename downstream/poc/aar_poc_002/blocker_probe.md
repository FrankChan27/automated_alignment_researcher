# AAR-POC-002 — Environment blocker probe

**Probed at:** 2026-09-28T01:48:18+08:00 (box = user zone UTC+8)  
**Repo:** `/workspace/aar-infra/automated_alignment_researcher` @ `c145825`  
**Branch:** `downstream/aar-poc-002-native`  
**HUMAN=0** — raw transcripts under `evidence/unpatched_failures/`.

---

## Summary

| Check | Result |
|-------|--------|
| `ANTHROPIC_API_KEY` | **absent** |
| System Python | 3.13.5 (`/usr/local/bin/python`, `/usr/bin/python3`) |
| `uv` | present (`uv 0.12.19`) |
| Project `.venv` | **absent** (no `uv sync` / venv under repo) |
| `VIRTUAL_ENV` | unset (until POC smoke venv) |
| `claude_agent_sdk` | **missing** |
| `anthropic` | **missing** |
| `fastapi` | **missing** (listed in `pyproject.toml`; **server actually uses Flask**) |
| `uvicorn` | **missing** |
| `flask` | **missing** (required by `aar/web_ui/backend/app.py`) |
| `PyYAML` / `jinja2` | **missing** on system Python |
| Full Task-B agent loop unpatched | **false** (blocked — see below) |
| Portable stub eval (after minimal venv+PyYAML) | **true** (see `evidence/generic_aar_run_example.txt`, `evidence/toy_run_eval.txt`) |

---

## ANTHROPIC_API_KEY

```
ANTHROPIC_API_KEY=absent
```

`run.py:cmd_agent` exits before importing the agent if unset:

```text
Error: ANTHROPIC_API_KEY is required for agent mode
EXIT=1
```

Transcript: `evidence/unpatched_failures/agent_local.txt`

With a **fake** key set, the next hard fail is import of `claude_agent_sdk`:

```text
ModuleNotFoundError: No module named 'claude_agent_sdk'
```

Transcript: `evidence/unpatched_failures/agent_local_with_fake_key.txt`

---

## Packages / uv / venv

**System interpreter (unpatched):** every probed import failed:

- `claude_agent_sdk`, `anthropic`, `fastapi`, `uvicorn`, `flask`, `yaml` (PyYAML), `jinja2`

**Repo lockfile exists** (`uv.lock`, `pyproject.toml` lists agent + server + ML stack) but **no environment was created** on this box for the project.

**POC smoke venv (out of git, out of secrets):**  
`/home/box/aar-poc-002-venv` — created for stub eval only; installed `PyYAML==6.0.3`. Not a full `uv sync`.

**Note on FastAPI vs Flask:** `pyproject.toml` depends on `fastapi` + `uvicorn`, but `run.py:cmd_server` launches Flask `aar/web_ui/backend/app.py`. Unpatched `python run.py server` fails on `flask`, not fastapi.

Raw: `evidence/unpatched_failures/env_probe.txt`

---

## Unpatched command failures

### `python run.py agent --idea-uid poc002 --idea-name poc002 --local`

1. **Immediate:** missing `ANTHROPIC_API_KEY` → exit 1 (`run.py:33-35`).
2. **If key present:** `from aar.research_loop.agent import AutonomousAgentLoop` → `ModuleNotFoundError: claude_agent_sdk` (`aar/research_loop/agent.py:21`).
3. **Further (not yet reached):** would need `anthropic`, working Claude Agent SDK / `claude` CLI (`BaseAgent` uses `cli_path=shutil.which("claude")`), and a live `python run.py server` on `:8000` for local mode MCP tools.

### `python run.py server`

```text
Starting server on port 8000...
ModuleNotFoundError: No module named 'flask'
  File ".../aar/web_ui/backend/app.py", line 7, in <module>
    from flask import Flask, ...
```

Transcript: `evidence/unpatched_failures/server.txt`

---

## Full Task-B agent loop runnable unpatched?

**false**

**Exact blockers (ordered):**

1. `ANTHROPIC_API_KEY` absent (`run.py:cmd_agent`).
2. No project venv / deps: `claude_agent_sdk`, `anthropic`, `flask`, `jinja2`, `PyYAML`, … not installed.
3. Server cannot start without Flask (+ SQLAlchemy stack from `pyproject.toml`).
4. Even after deps: real Anthropic API access required for `ClaudeSDKClient` sessions; integrity monitor (`submit_idea_proposal`) also expects Opus-class API.

Stub **eval** path does **not** need Anthropic and works after installing PyYAML only (see smoke evidence).

---

## Smoke (portable eval, no Anthropic) — PASS

Created `/home/box/aar-poc-002-venv`, installed PyYAML, then:

```bash
source /home/box/aar-poc-002-venv/bin/activate
export PYTHONPATH="$PWD"
bash generic_aar/run_example.sh
# stub:perfect → HEADLINE +100.00% passes_filter=True
# stub:weak    → HEADLINE +55.28% passes_filter=False
python -m aar.eval_pod.run_eval --suite configs/toy.yaml --model stub:perfect
# HEADLINE +100.00% passes_filter=True
```

Evidence:

- `evidence/generic_aar_run_example.txt`
- `evidence/toy_run_eval.txt`

Proves: `generic_aar.eval:main` → `aar.eval_pod.run_eval.run` + registry/composite path execute on this host without Anthropic/GPU.

---

## Secrets location (created, outside git)

```
/home/box/aar-poc-002-secrets/   mode 0700
```

Not under the repo. Placeholder README only (no targets committed).
