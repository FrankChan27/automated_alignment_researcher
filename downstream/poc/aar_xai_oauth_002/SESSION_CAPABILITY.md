# SESSION_CAPABILITY — AAR-xAI-OAuth-002

Probe basis: official Grok CLI 1.0.41 help + PHASE3/4 runtime. Extra inference beyond the ONE smoke **not** run. UNKNOWN ok.

| Capability | Result | Basis |
|------------|--------|-------|
| **MULTI_TURN** | SUPPORTED_DOCUMENTED / runtime UNKNOWN_NOT_SMOKED | `--max-turns`, interactive TUI, `agent` subcommand; not separately smoked |
| **MACHINE_READABLE** | **SUPPORTED** | `--output-format plain\|json\|streaming-json\|streaming-messages-json`; `--json-schema`; PHASE4 used `plain` successfully |
| **TOOLS** | SUPPORTED_DOCUMENTED / runtime UNKNOWN_NOT_SMOKED | `--tools`, `--allow`/`--deny`, `--disallowed-tools`, `--permission-mode`; PHASE4 exercised deny-list flags only |
| **SESSION_RESUME** | SUPPORTED_DOCUMENTED / runtime UNKNOWN_NOT_SMOKED | `--resume`, `--continue`, `sessions list/search`; not runtime-smoked |
| **NONINTERACTIVE** | **SUPPORTED** | `--single` / `-p`; PHASE4 exit 0 exact token |
| **PROGRAMMATIC** | **SUPPORTED** | Official CLI binary; `models` + `--single` scripted with OAuth session; no TTY consent in PHASE 2–5 |

## Summary

Native noninteractive programmatic inference via official CLI + local OIDC session is **proven**. Multi-turn / tools / resume are **documented** on the same CLI; not re-smoked (inference budget = 1).

Evidence: `evidence/PHASE5_capability_probe.txt`, `evidence/PHASE5_cli_flags_grep.txt`
