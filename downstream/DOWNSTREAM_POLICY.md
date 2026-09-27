# Downstream Policy (DOWNSTREAM-LOCAL)

**DOWNSTREAM-LOCAL** governance for
[`FrankChan27/automated_alignment_researcher`](https://github.com/FrankChan27/automated_alignment_researcher).
These rules are **not** upstream-native. Do not disguise them as part of the
YuehHanChen engine.

---

## UPSTREAM ENGINE vs DOWNSTREAM ADAPTER

| Layer | What it is | Where it lives |
|-------|------------|----------------|
| **UPSTREAM ENGINE** | Core AAR harness, eval pod, generic_aar template, isolation docs, research loop | `aar/`, `generic_aar/`, `configs/`, root docs (`ISOLATION.md`, etc.) owned by YuehHanChen |
| **DOWNSTREAM ADAPTER** | Fork-local governance, pin, monitor, sync Draft PRs, update manifests | `downstream/`, `upstream_updates/`, `.github/workflows/upstream-monitor.yml` |

Downstream must not silently rewrite engine semantics. Prefer preserving upstream
paths on sync branches; resolve conflicts by keeping downstream adapter files
intact.

---

## Numbered rules

### 1. Upstream repository

`upstream_repo` = **YuehHanChen/automated_alignment_researcher**

### 2. Upstream default branch

`upstream_default_branch` = **main**

### 3. Current pinned upstream SHA

Read from `downstream/UPSTREAM_PIN.json` → field `pinned_upstream_sha`.

At fork time this was:

`AAR_UPSTREAM_SHA=02dbe9d2cadc553720d17cdf6259c0b8727e6cde`

(immutable commit id — never use the word “latest” as a version id)

### 4. Update detection rules

1. Fetch `LATEST_UPSTREAM_SHA` from YuehHanChen/... `main` (immutable commit SHA).
2. Read `PINNED_UPSTREAM_SHA` from `downstream/UPSTREAM_PIN.json`.
3. If equal → `UPSTREAM_CHANGE=false`; no PR, no issue, no empty commit; exit 0.
4. If unequal → `UPSTREAM_CHANGE=true`; compare `PINNED_UPSTREAM_SHA...LATEST_UPSTREAM_SHA`,
   classify paths, write a manifest under `upstream_updates/`, open or update a
   **Draft** PR on branch `upstream-sync/<short-sha>`.
5. Detection alone **must not** change `PINNED_UPSTREAM_SHA`.

### 5. Update classification categories

Changed paths are classified into exactly these categories (multi-label allowed):

| Category | Typical path signals |
|----------|----------------------|
| `HARNESS_CORE` | `aar/research_loop/`, `aar/ideas/`, core harness orchestration |
| `GENERIC_AAR` | `generic_aar/` |
| `EVALUATOR` | `aar/eval_pod/`, eval judges/models, `configs/` eval suites |
| `ISOLATION` | `ISOLATION.md`, holdout/heldout isolation scripts/docs |
| `MONITOR` | Downstream monitor/workflows (usually our own; rare upstream) |
| `TRANSPORT` | `aar/transport.py`, remote/job transport |
| `CONFIG` | `configs/`, `pyproject.toml`, Docker/entrypoint (non-secret) |
| `PROMPT` | briefing / prompt / judge-prompt text under aar or generic_aar |
| `DEPENDENCY` | `pyproject.toml`, `uv.lock`, lockfiles |
| `TEST` | `tests/`, `*_test*`, smoke scripts |
| `DOCS_ONLY` | `*.md` at root or docs with no code/config lock change |
| `BREAKING_OR_UNKNOWN` | unclear blast radius, API renames, removed public entrypoints, or unclassified high-risk churn |

Classifier emits: `categories`, `possible_breaking_change`, and impact flags
`isolation_impact`, `evaluator_impact`, `generic_aar_impact`.

### 6. Smoke test (Layer 1)

Prefer the official no-GPU smoke:

```bash
python -m aar.eval_pod.run_eval --suite configs/toy.yaml --model stub:perfect
bash generic_aar/run_example.sh
```

If the environment cannot run them (missing deps, GPU-only wheels, etc.), record
**BLOCKED** with reason. **Never claim PASS if not actually run.**

Results JSON under `downstream/artifacts/` (gitignored) or `/tmp`.

### 7. Regression / integrity test (Layer 2)

Verify at least:

- Fork relationship via `gh api` (`fork=true`, parent = YuehHanChen/...)
- Governance files exist: policy, pin, README, scripts, workflow, `upstream_updates/`
- Pin present and SHA looks like an immutable 40-char hex
- No accidental secrets patterns in new downstream files
- Isolation docs still present (`ISOLATION.md`)

Emit PASS/FAIL JSON. Failures block recommending merge.

### 8. Merge policy (Draft PR only; DO_NOT_AUTO_MERGE)

- Sync work lands only as a **Draft** pull request.
- Title: `upstream sync: <old-short> → <new-short>`
- Body must include OLD/NEW SHAs, counts, categories, breaking assessment,
  isolation/evaluator/generic_aar impact, smoke results, reviewer verdict
  placeholder, rollback point, and **DO_NOT_AUTO_MERGE**.
- **Never** auto-merge into `main`.
- **Never** update `PINNED_UPSTREAM_SHA` in the monitor path.
- Human review + formal acceptance required before pin advancement.

`AUTO_MERGE_UPSTREAM = false` (hard rule).

### 9. Rollback policy

- Rollback point for a sync attempt = previous `PINNED_UPSTREAM_SHA` (and the
  fork `main` commit before any accepted upgrade merge).
- To abandon a sync: close the Draft PR; delete or leave `upstream-sync/*`
  branch; leave pin unchanged.
- After a bad accepted upgrade: revert the merge commit on `main` and restore
  `downstream/UPSTREAM_PIN.json` to the prior pin in a follow-up commit.

### 10. Provenance requirements

- Record `AAR_UPSTREAM_SHA=<immutable sha>` in manifests and PR bodies.
- Distinguish:
  - **`LATEST_UPSTREAM_SHA`**: tip of upstream `main` at detection time
  - **`PINNED_UPSTREAM_SHA`**: last formally accepted upstream baseline (from pin file)
- Never use “latest” as a version identifier in pins, tags, or manifests.

---

## Update storm protection

If an open Draft PR already exists whose head branch matches `upstream-sync/*`:

1. **Reuse** that PR (do not open a second competing sync PR).
2. Update the PR branch to the newest upstream HEAD.
3. Keep previous candidate SHA(s) and **cumulative notes** in the PR body.

`UPDATE_STORM_PROTECTION = true`.

---

## Secrets

Do not put secrets/tokens in the repo, workflows, artifacts, or logs.
Use `GITHUB_TOKEN` in Actions without printing it. Downstream scripts must
redact token-like strings in logged output.


---

## Monitor workflow install note (DOWNSTREAM-LOCAL)

Canonical workflow YAML is committed at:

`downstream/github-workflows/upstream-monitor.yml`

It defines `schedule: cron: "20 20 * * *"` and `workflow_dispatch`.

Installing into `.github/workflows/upstream-monitor.yml` (via
`downstream/scripts/install_monitor_workflow.sh` + push) requires a git
credential with the GitHub **`workflow`** OAuth scope. OAuth apps with only
`repo` scope are refused by GitHub when creating/updating workflow files.
Until installed, Actions will not schedule; `monitor_once.sh` remains usable locally.

---

## Live monitor trigger (DOWNSTREAM-LOCAL amendment)

As of 2026-09-28 Human chose **Grok Bot Routine** (Beijing 04:20) instead of installing GitHub Actions. See `downstream/MONITOR_TRIGGER.md`. Detection/classify/Draft-PR policy above is unchanged.
