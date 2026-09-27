# Monitor trigger (DOWNSTREAM-LOCAL)

**Live trigger (chosen):** Grok Bot Routine「AAR每日upstream监控」

- Schedule: `CRON_TZ=Asia/Shanghai 20 4 * * *` (Beijing 04:20 daily)
- Runner: this Bot wakes and executes `downstream/scripts/monitor_once.sh` via existing `gh` OAuth (`repo` scope).
- Same policy as Actions path: detect → classify → Draft PR only; **DO_NOT_AUTO_MERGE**; never update `PINNED_UPSTREAM_SHA` on detection alone.

**Not installed (deferred):** `.github/workflows/upstream-monitor.yml`

- Canonical YAML kept at `downstream/github-workflows/upstream-monitor.yml` for documentation / optional future install.
- GitHub OAuth Apps cannot create/update `.github/workflows/*` without the extra `workflow` scope; Human chose Bot Routine instead (same pattern as 收纳Bot daily shouna).

Manual run anytime:

```bash
DRY_RUN=0 bash downstream/scripts/monitor_once.sh
# or dry:
DRY_RUN=1 bash downstream/scripts/monitor_once.sh
```
