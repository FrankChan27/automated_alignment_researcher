# Downstream (DOWNSTREAM-LOCAL)

This directory is **downstream-local governance** for the
[`FrankChan27/automated_alignment_researcher`](https://github.com/FrankChan27/automated_alignment_researcher)
fork. It is **not** upstream-native and must not be presented as part of the
YuehHanChen/automated_alignment_researcher engine.

Contents:

- `DOWNSTREAM_POLICY.md` — numbered governance rules (pin, classify, smoke, merge, rollback)
- `UPSTREAM_PIN.json` — machine-readable immutable pin (`PINNED_UPSTREAM_SHA`)
- `scripts/` — classify, manifest writer, Layer-1 smoke, Layer-2 integrity, `monitor_once.sh`
- `artifacts/` — local/CI run outputs (gitignored; never commit secrets)


- `github-workflows/upstream-monitor.yml` — staged copy of the Actions workflow.
  Install into `.github/workflows/` via `scripts/install_monitor_workflow.sh` when the
  git credential has the GitHub `workflow` OAuth scope (OAuth apps without that scope
  cannot create/update workflow files on push).

Related:

- `../upstream_updates/` — machine-readable update manifests produced on sync branches
- `../.github/workflows/upstream-monitor.yml` — daily schedule + `workflow_dispatch`

See `DOWNSTREAM_POLICY.md` for full rules. Auto-merge of upstream into `main` is forbidden.
