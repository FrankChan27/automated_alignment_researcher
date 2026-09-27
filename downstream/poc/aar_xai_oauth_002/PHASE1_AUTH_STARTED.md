# PHASE 1 — Official OAuth started (Human Gate)

**Date:** 2026-09-28T02:13:38+0800 (UTC+8)  
**Branch:** `downstream/aar-xai-oauth-002`  
**POC:** `downstream/poc/aar_xai_oauth_002/`  
**HUMAN_GATE:** `WAITING_FOR_USER_CONSENT`  
**PHASE_2_TO_5:** **NOT STARTED**

## 1) Current official install method (fetched this shift)

| Field | Value |
|-------|-------|
| Access date | 2026-09-28 (UTC+8) |
| Primary docs URL | https://docs.x.ai/build/overview |
| Install (Linux/macOS) | `curl -fsSL https://x.ai/cli/install.sh \| bash` |
| Install (Windows) | `irm https://x.ai/cli/install.ps1 \| iex` |
| Marketing page | https://x.ai/cli |
| CLI reference | https://docs.x.ai/build/cli/reference |
| Enterprise / auth | https://docs.x.ai/build/enterprise |
| Auth guide (source) | https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/docs/user-guide/02-authentication.md |
| Stable channel | https://x.ai/cli/stable → **1.0.41** |
| npm alternative (docs) | `npm install -g @xai-official/grok` |

Evidence: `evidence/OFFICIAL_INSTALL_SOURCE.txt`

## 2) CLI install record

| Field | Value |
|-------|-------|
| `GROK_CLI_SOURCE` | official_xai |
| `VERSION` | grok 1.0.41 (4220f3b224a6) |
| `PATH` | `/home/box/.grok/bin/grok` (also `~/.local/bin/grok` symlink) |
| `INSTALL_METHOD` | Official `x.ai/cli` install layout (`~/.grok/config.toml` `installer = "internal"`); binary MD5+size match official artifact |
| `OFFICIAL_SOURCE_VERIFIED` | **true** (MD5 `a0ad7ff0132e5a7bb6b661163400e5f5` = x-goog-hash of `https://x.ai/cli/grok-1.0.41-linux-x86_64`; bytes 165967424) |
| Third-party OAuth bridge | **not used** |

Evidence: `evidence/CLI_INSTALL_RECORD.txt`, `evidence/grok_version.txt`, `evidence/grok_login_help.txt`

Commands exercised: `grok --version`, `grok version`, `grok --help`, `grok login --help`.

## 3) Authorization start

| Field | Value |
|-------|-------|
| `AUTHORIZATION_STARTED` | **true** |
| Command | `grok login --device-auth` |
| Flow | `DEVICE_CODE_FLOW` (RFC 8628) |
| `BROWSER_AUTH_URL` host/path | `accounts.x.ai` + `/oauth2/device` |
| Query param **names** only | `user_code` |
| Codes / full URL with secrets | **REDACTED** (not committed) |
| `~/.grok/auth.json` | **ABSENT** (consent not completed) |
| Live waiter | process left running for human consent (PID ephemeral; re-run command if expired) |

Evidence: `evidence/device_auth_started_redacted.txt`, `evidence/device_auth_url_meta.json`

## 4) Human steps to complete consent (NO automation)

1. On this box, ensure `PATH` includes `$HOME/.grok/bin` (or use `~/.local/bin/grok`).
2. If the existing `grok login --device-auth` waiter is still running, read **its** printed URL + user code from that terminal (do not paste codes into git).
3. If expired / missing: run `grok login --device-auth` again; open the printed URL (host `accounts.x.ai`, path `/oauth2/device`).
4. In the browser, confirm the code shown by the CLI (only a code you requested).
5. After success, confirm `~/.grok/auth.json` exists (mode 0600) — **do not** commit it.
6. Stop. Do **not** start PHASE 2–5 until coordinator opens the next gate.

## 5) Stop condition

```
HUMAN_GATE=WAITING_FOR_USER_CONSENT
CONSENT_COMPLETED=false
PHASE2_STARTED=false
```

## Constraints honored

- No Cursor CloudAgent; no Anthropic; no xAI API key create; no cookie auth; no `aar/` edits; no adapter
- No third-party OAuth bridge
- Secrets: device/user codes and full auth URLs with query values not committed
