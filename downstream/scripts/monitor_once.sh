#!/usr/bin/env bash
# DOWNSTREAM-LOCAL upstream monitor (Actions + local dry-run).
# Never merges PRs. Never updates PINNED_UPSTREAM_SHA.
# Never prints tokens/secrets.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

DRY_RUN="${DRY_RUN:-0}"

UPSTREAM_REPO="YuehHanChen/automated_alignment_researcher"
UPSTREAM_BRANCH="main"
DOWNSTREAM_REPO="${GITHUB_REPOSITORY:-FrankChan27/automated_alignment_researcher}"
PIN_FILE="$ROOT/downstream/UPSTREAM_PIN.json"
ART_DIR="${AAR_SMOKE_ART_DIR:-$ROOT/downstream/artifacts}"
SCRIPTS="$ROOT/downstream/scripts"
mkdir -p "$ART_DIR"

log() { printf '[monitor] %s\n' "$*"; }
die() { log "ERROR: $*"; exit 1; }

redact() {
  sed -E \
    -e 's/ghp_[A-Za-z0-9]{20,}/[REDACTED_GHP]/g' \
    -e 's/github_pat_[A-Za-z0-9_]{20,}/[REDACTED_PAT]/g' \
    -e 's/xox[baprs]-[A-Za-z0-9-]{10,}/[REDACTED_SLACK]/g' \
    -e 's/Bearer [A-Za-z0-9._\-]+/Bearer [REDACTED]/g'
}

require_cmd() { command -v "$1" >/dev/null 2>&1 || die "missing command: $1"; }

require_cmd git
require_cmd python3
require_cmd gh

[[ -f "$PIN_FILE" ]] || die "missing $PIN_FILE"

PINNED_UPSTREAM_SHA="$(python3 -c 'import json; print(json.load(open("downstream/UPSTREAM_PIN.json"))["pinned_upstream_sha"])')"
[[ ${#PINNED_UPSTREAM_SHA} -eq 40 ]] || die "PINNED_UPSTREAM_SHA not 40-char hex"

log "DOWNSTREAM-LOCAL monitor_once starting"
log "downstream_repo=${DOWNSTREAM_REPO}"
log "upstream_repo=${UPSTREAM_REPO} branch=${UPSTREAM_BRANCH}"
log "PINNED_UPSTREAM_SHA=${PINNED_UPSTREAM_SHA}"
log "DRY_RUN=${DRY_RUN}"
log "AUTO_MERGE_UPSTREAM=false"
log "UPDATE_STORM_PROTECTION=true"

if ! git remote get-url upstream >/dev/null 2>&1; then
  git remote add upstream "https://github.com/${UPSTREAM_REPO}.git"
fi

log "fetching upstream ${UPSTREAM_BRANCH}..."
git fetch --quiet upstream "${UPSTREAM_BRANCH}" 2>&1 | redact || true

set +e
LATEST_UPSTREAM_SHA="$(gh api "repos/${UPSTREAM_REPO}/commits/${UPSTREAM_BRANCH}" --jq .sha 2>/dev/null)"
gh_rc=$?
set -e
if [[ $gh_rc -ne 0 || -z "${LATEST_UPSTREAM_SHA}" ]]; then
  LATEST_UPSTREAM_SHA="$(git rev-parse "upstream/${UPSTREAM_BRANCH}")"
fi
[[ ${#LATEST_UPSTREAM_SHA} -eq 40 ]] || die "could not resolve LATEST_UPSTREAM_SHA"

log "LATEST_UPSTREAM_SHA=${LATEST_UPSTREAM_SHA}"
log "AAR_UPSTREAM_SHA context: PINNED=${PINNED_UPSTREAM_SHA} LATEST=${LATEST_UPSTREAM_SHA}"

if [[ "$PINNED_UPSTREAM_SHA" == "$LATEST_UPSTREAM_SHA" ]]; then
  log "UPSTREAM_CHANGE=false (pin equals latest immutable SHA)"
  log "no PR, no issue, no empty commit"
  SUMMARY_JSON="$ART_DIR/monitor_once_latest.json"
  python3 -c "
import json
from pathlib import Path
from datetime import datetime, timezone
doc = {
  'downstream_local': True,
  'UPSTREAM_CHANGE': False,
  'PINNED_UPSTREAM_SHA': '${PINNED_UPSTREAM_SHA}',
  'LATEST_UPSTREAM_SHA': '${LATEST_UPSTREAM_SHA}',
  'detected_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
  'action': 'none',
  'AUTO_MERGE_UPSTREAM': False,
  'UPDATE_STORM_PROTECTION': True,
  'note': 'Pin equals latest. DO_NOT_AUTO_MERGE. Pin unchanged.',
}
Path('${SUMMARY_JSON}').write_text(json.dumps(doc, indent=2) + chr(10))
print(json.dumps(doc, indent=2))
"
  exit 0
fi

log "UPSTREAM_CHANGE=true"
OLD_SHA="$PINNED_UPSTREAM_SHA"
NEW_SHA="$LATEST_UPSTREAM_SHA"
OLD_SHORT="${OLD_SHA:0:7}"
NEW_SHORT="${NEW_SHA:0:7}"
BRANCH="upstream-sync/${NEW_SHA:0:12}"

git fetch --quiet upstream "${UPSTREAM_BRANCH}" 2>&1 | redact || true
git fetch --quiet origin main 2>&1 | redact || true
git fetch --quiet upstream "$NEW_SHA" 2>&1 | redact || true
git fetch --quiet upstream "$OLD_SHA" 2>&1 | redact || true

COMPARE_JSON="$ART_DIR/compare_${OLD_SHORT}_${NEW_SHORT}.json"
set +e
gh api "repos/${UPSTREAM_REPO}/compare/${OLD_SHA}...${NEW_SHA}" >"$COMPARE_JSON" 2>"$ART_DIR/compare_err.txt"
cmp_rc=$?
set -e
if [[ $cmp_rc -ne 0 ]]; then
  log "gh compare failed; attempting git-only stats"
  COMMIT_COUNT="$(git rev-list --count "${OLD_SHA}..${NEW_SHA}" 2>/dev/null || echo 0)"
  CHANGED_FILE_COUNT="$(git diff --name-only "${OLD_SHA}...${NEW_SHA}" 2>/dev/null | wc -l | tr -d ' ')"
  ADDITIONS=0
  DELETIONS=0
else
  COMMIT_COUNT="$(python3 -c "import json; d=json.load(open('${COMPARE_JSON}')); print(d.get('total_commits') or len(d.get('commits') or []))")"
  CHANGED_FILE_COUNT="$(python3 -c "import json; d=json.load(open('${COMPARE_JSON}')); print(len(d.get('files') or []))")"
  ADDITIONS="$(python3 -c "import json; d=json.load(open('${COMPARE_JSON}')); print(sum(f.get('additions',0) for f in (d.get('files') or [])))")"
  DELETIONS="$(python3 -c "import json; d=json.load(open('${COMPARE_JSON}')); print(sum(f.get('deletions',0) for f in (d.get('files') or [])))")"
fi

log "commit_count=${COMMIT_COUNT} changed_files=${CHANGED_FILE_COUNT} +${ADDITIONS}/-${DELETIONS}"

CLASSIFY_JSON="$ART_DIR/classify_${OLD_SHORT}_${NEW_SHORT}.json"
if [[ -f "$COMPARE_JSON" && $cmp_rc -eq 0 ]]; then
  python3 "$SCRIPTS/classify_upstream_diff.py" --gh-compare-json "$COMPARE_JSON" >"$CLASSIFY_JSON"
else
  python3 "$SCRIPTS/classify_upstream_diff.py" "$OLD_SHA" "$NEW_SHA" >"$CLASSIFY_JSON"
fi

POSSIBLE_BREAKING="$(python3 -c "import json; print(json.load(open('${CLASSIFY_JSON}')).get('possible_breaking_change'))")"
ISOLATION_IMPACT="$(python3 -c "import json; print(json.load(open('${CLASSIFY_JSON}')).get('isolation_impact'))")"
EVALUATOR_IMPACT="$(python3 -c "import json; print(json.load(open('${CLASSIFY_JSON}')).get('evaluator_impact'))")"
GENERIC_AAR_IMPACT="$(python3 -c "import json; print(json.load(open('${CLASSIFY_JSON}')).get('generic_aar_impact'))")"

DETECTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
MANIFEST_PATH="$(
  python3 "$SCRIPTS/write_update_manifest.py" \
    --old-sha "$OLD_SHA" \
    --new-sha "$NEW_SHA" \
    --commit-count "$COMMIT_COUNT" \
    --changed-files "$CHANGED_FILE_COUNT" \
    --additions "$ADDITIONS" \
    --deletions "$DELETIONS" \
    --categories-json "[]" \
    --possible-breaking-change "$POSSIBLE_BREAKING" \
    --isolation-impact "$ISOLATION_IMPACT" \
    --evaluator-impact "$EVALUATOR_IMPACT" \
    --generic-aar-impact "$GENERIC_AAR_IMPACT" \
    --recommended-action "OPEN_OR_UPDATE_DRAFT_PR_DO_NOT_AUTO_MERGE" \
    --detected-at "$DETECTED_AT" \
    --classify-file "$CLASSIFY_JSON" \
    --out-dir "$ROOT/upstream_updates"
)"
log "wrote manifest ${MANIFEST_PATH}"

set +e
bash "$SCRIPTS/run_layer1_smoke.sh"
L1_RC=$?
bash "$SCRIPTS/run_layer2_integrity.sh"
L2_RC=$?
set -e

L1_SUMMARY="see downstream/artifacts/layer1_smoke_latest.json (rc=${L1_RC})"
L2_SUMMARY="see downstream/artifacts/layer2_integrity_latest.json (rc=${L2_RC})"
if [[ -f "$ART_DIR/layer1_smoke_latest.json" ]]; then
  L1_SUMMARY="$(python3 -c "import json; d=json.load(open('${ART_DIR}/layer1_smoke_latest.json')); print('overall=%s eval=%s generic=%s' % (d.get('overall'), d['eval_pod_smoke']['status'], d['generic_aar_smoke']['status']))")"
fi
if [[ -f "$ART_DIR/layer2_integrity_latest.json" ]]; then
  L2_SUMMARY="$(python3 -c "import json; d=json.load(open('${ART_DIR}/layer2_integrity_latest.json')); print('overall=%s checks=%d' % (d.get('overall'), len(d.get('checks') or [])))")"
fi
log "layer1: ${L1_SUMMARY}"
log "layer2: ${L2_SUMMARY}"

write_monitor_summary() {
  local action="$1"
  local branch="${2:-}"
  local existing_pr="${3:-}"
  python3 -c "
import json
from pathlib import Path
from datetime import datetime, timezone
clf = json.load(open('${CLASSIFY_JSON}'))
doc = {
  'downstream_local': True,
  'UPSTREAM_CHANGE': True,
  'DRY_RUN': ${DRY_RUN},
  'PINNED_UPSTREAM_SHA': '${OLD_SHA}',
  'LATEST_UPSTREAM_SHA': '${NEW_SHA}',
  'branch': '''${branch}''' or None,
  'existing_pr': '''${existing_pr}''' or None,
  'commit_count': int('${COMMIT_COUNT}'),
  'changed_files': int('${CHANGED_FILE_COUNT}'),
  'categories': clf.get('categories'),
  'possible_breaking_change': clf.get('possible_breaking_change'),
  'isolation_impact': clf.get('isolation_impact'),
  'evaluator_impact': clf.get('evaluator_impact'),
  'generic_aar_impact': clf.get('generic_aar_impact'),
  'layer1': '''${L1_SUMMARY}''',
  'layer2': '''${L2_SUMMARY}''',
  'manifest': '''${MANIFEST_PATH}''',
  'action': '''${action}''',
  'AUTO_MERGE_UPSTREAM': False,
  'UPDATE_STORM_PROTECTION': True,
  'detected_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
  'note': 'DO_NOT_AUTO_MERGE. Pin NOT updated.',
}
Path('${ART_DIR}/monitor_once_latest.json').write_text(json.dumps(doc, indent=2) + chr(10))
print(json.dumps(doc, indent=2))
"
}

if [[ "$DRY_RUN" == "1" ]]; then
  log "DRY_RUN=1 — skipping branch/PR creation"
  # Manifest from a dry-run against a changed upstream should not dirty main;
  # leave the file in working tree / artifacts only — remove from index intent.
  # Keep manifest file for inspection but do not commit on main.
  write_monitor_summary "dry_run_no_pr"
  exit 0
fi

log "preparing branch ${BRANCH}"
git checkout -B "$BRANCH" origin/main 2>&1 | redact

set +e
git merge --no-ff -m "chore(downstream): merge upstream ${NEW_SHORT} into ${BRANCH} (DO_NOT_AUTO_MERGE)" "$NEW_SHA" 2>"$ART_DIR/merge_err.txt"
merge_rc=$?
set -e
if [[ $merge_rc -ne 0 ]]; then
  if [[ -d "$ROOT/downstream" ]]; then
    git checkout --ours -- downstream/ 2>/dev/null || true
    git add downstream/ 2>/dev/null || true
  fi
  git checkout --theirs -- aar generic_aar configs 2>/dev/null || true
  git add -A
  set +e
  git -c core.editor=true merge --continue 2>/dev/null \
    || git commit --no-edit -m "chore(downstream): merge upstream ${NEW_SHORT} (conflict-resolved; DO_NOT_AUTO_MERGE)" 2>/dev/null
  set -e
fi

git add upstream_updates/ downstream/ .github/workflows/upstream-monitor.yml 2>/dev/null || true
if ! git diff --cached --quiet 2>/dev/null; then
  git commit -m "downstream: record upstream update manifest for ${NEW_SHORT}" || true
fi

git push -u origin "$BRANCH" --force-with-lease 2>&1 | redact

EXISTING_PR_JSON="$ART_DIR/existing_sync_prs.json"
gh api "repos/${DOWNSTREAM_REPO}/pulls?state=open&per_page=50" >"$EXISTING_PR_JSON"

EXISTING_PR_NUMBER="$(python3 -c "
import json
from pathlib import Path
prs = json.loads(Path('${EXISTING_PR_JSON}').read_text())
found = None
for pr in prs:
    head = (pr.get('head') or {}).get('ref') or ''
    if head.startswith('upstream-sync/') and bool(pr.get('draft')):
        found = pr.get('number')
        break
if found is None:
    for pr in prs:
        head = (pr.get('head') or {}).get('ref') or ''
        if head.startswith('upstream-sync/'):
            found = pr.get('number')
            break
print(found or '')
")"

PREV_CANDIDATE=""
if [[ -n "$EXISTING_PR_NUMBER" ]]; then
  log "UPDATE_STORM_PROTECTION: reusing open sync PR #${EXISTING_PR_NUMBER}"
  PREV_BODY="$(gh api "repos/${DOWNSTREAM_REPO}/pulls/${EXISTING_PR_NUMBER}" --jq .body)"
  PREV_CANDIDATE="$(printf '%s\n' "$PREV_BODY" | sed -n 's/.*NEW_UPSTREAM_SHA[=: *`]*\([0-9a-f]\{40\}\).*/\1/p' | head -1 || true)"
  EXISTING_HEAD="$(gh api "repos/${DOWNSTREAM_REPO}/pulls/${EXISTING_PR_NUMBER}" --jq .head.ref)"
  if [[ "$EXISTING_HEAD" != "$BRANCH" ]]; then
    log "updating existing head branch ${EXISTING_HEAD} to newest upstream candidate"
    git push origin "${BRANCH}:refs/heads/${EXISTING_HEAD}" --force-with-lease 2>&1 | redact
    BRANCH="$EXISTING_HEAD"
  fi
fi

PR_TITLE="upstream sync: ${OLD_SHORT} → ${NEW_SHORT}"
PR_BODY_FILE="$ART_DIR/pr_body_${NEW_SHORT}.md"
export PR_BODY_FILE CLASSIFY_JSON ART_DIR OLD_SHA NEW_SHA COMMIT_COUNT CHANGED_FILE_COUNT ADDITIONS DELETIONS DETECTED_AT MANIFEST_PATH PREV_CANDIDATE
python3 <<'PY'
import json, os
from pathlib import Path
clf = json.load(open(os.environ["CLASSIFY_JSON"]))
art = os.environ["ART_DIR"]
l1, l2 = {}, {}
try:
    l1 = json.load(open(f"{art}/layer1_smoke_latest.json"))
except Exception:
    pass
try:
    l2 = json.load(open(f"{art}/layer2_integrity_latest.json"))
except Exception:
    pass
cats = ", ".join(clf.get("categories") or []) or "(none)"
prev = (os.environ.get("PREV_CANDIDATE") or "").strip()
old = os.environ["OLD_SHA"]
new = os.environ["NEW_SHA"]
lines = [
    "<!-- DOWNSTREAM-LOCAL upstream sync Draft PR. DO_NOT_AUTO_MERGE. -->",
    "",
    "## Upstream sync (DOWNSTREAM-LOCAL)",
    "",
    f"- **OLD_UPSTREAM_SHA** (PINNED): `{old}`",
    f"- **NEW_UPSTREAM_SHA** (LATEST): `{new}`",
    f"- **AAR_UPSTREAM_SHA** (candidate): `{new}`",
    f"- **commit_count**: {os.environ['COMMIT_COUNT']}",
    f"- **changed_file_count**: {os.environ['CHANGED_FILE_COUNT']}",
    f"- **additions/deletions**: +{os.environ['ADDITIONS']} / -{os.environ['DELETIONS']}",
    f"- **categories**: {cats}",
    f"- **possible_breaking_change**: {clf.get('possible_breaking_change')}",
    f"- **isolation_impact**: {clf.get('isolation_impact')}",
    f"- **evaluator_impact**: {clf.get('evaluator_impact')}",
    f"- **generic_aar_impact**: {clf.get('generic_aar_impact')}",
    "",
    "## Smoke / integrity",
    "",
    f"- **Layer1 smoke**: overall={l1.get('overall')} eval={((l1.get('eval_pod_smoke') or {}).get('status'))} generic={((l1.get('generic_aar_smoke') or {}).get('status'))}",
    f"- **Layer2 integrity**: overall={l2.get('overall')}",
    "",
    "## Reviewer verdict",
    "",
    "- [ ] ACCEPT upstream upgrade (then human updates `downstream/UPSTREAM_PIN.json`)",
    "- [ ] REJECT / close without pin change",
    "- Verdict: _pending_",
    "",
    "## Rollback point",
    "",
    f"- Restore / keep pin at `PINNED_UPSTREAM_SHA={old}`",
    "- Close this Draft PR; do not merge",
    "",
    "## Policy",
    "",
    "- **DO_NOT_AUTO_MERGE**",
    "- `AUTO_MERGE_UPSTREAM=false`",
    "- `UPDATE_STORM_PROTECTION=true`",
    "- Detection does **not** change `PINNED_UPSTREAM_SHA`",
    "- Never use the word \"latest\" as a version id; SHAs above are immutable commits",
    "",
    "## Cumulative notes (update storm)",
    "",
]
if prev:
    lines.append(f"- Previous candidate SHA retained: `{prev}`")
else:
    lines.append("- Initial detection for this storm window.")
lines.append(f"- Current candidate: `{new}` at {os.environ['DETECTED_AT']}")
lines.append("")
lines.append(f"Manifest: `{Path(os.environ['MANIFEST_PATH']).name}` under `upstream_updates/`.")
Path(os.environ["PR_BODY_FILE"]).write_text("\n".join(lines) + "\n")
PY

if [[ -n "$EXISTING_PR_NUMBER" ]]; then
  # Use --input to avoid shell-escaping body issues; never echo tokens
  jq -n --arg title "$PR_TITLE" --arg body "$(cat "$PR_BODY_FILE")" \
    '{title:$title, body:$body}' \
    | gh api -X PATCH "repos/${DOWNSTREAM_REPO}/pulls/${EXISTING_PR_NUMBER}" --input - \
      --jq '{number:.number, html_url:.html_url, draft:.draft}' 2>&1 | redact
  log "updated PR #${EXISTING_PR_NUMBER} (not merged)"
  write_monitor_summary "updated_existing_draft_pr" "$BRANCH" "$EXISTING_PR_NUMBER"
else
  gh pr create --repo "$DOWNSTREAM_REPO" \
    --base main \
    --head "$BRANCH" \
    --title "$PR_TITLE" \
    --body-file "$PR_BODY_FILE" \
    --draft 2>&1 | redact
  log "created NEW Draft PR (not merged)"
  write_monitor_summary "created_draft_pr" "$BRANCH" ""
fi

log "PINNED_UPSTREAM_SHA unchanged (= ${PINNED_UPSTREAM_SHA})"
log "DO_NOT_AUTO_MERGE — exiting after Draft PR create/update"

git checkout main 2>&1 | redact || true
exit 0
