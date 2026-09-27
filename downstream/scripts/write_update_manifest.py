#!/usr/bin/env python3
"""DOWNSTREAM-LOCAL: write upstream_updates/<date>-<newsha12>.json manifest."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="DOWNSTREAM-LOCAL write update manifest")
    ap.add_argument("--old-sha", required=True)
    ap.add_argument("--new-sha", required=True)
    ap.add_argument("--commit-count", type=int, required=True)
    ap.add_argument("--changed-files", type=int, required=True)
    ap.add_argument("--additions", type=int, default=0)
    ap.add_argument("--deletions", type=int, default=0)
    ap.add_argument("--categories-json", required=True, help="JSON array or classify output file/object")
    ap.add_argument("--possible-breaking-change", type=str, required=True)
    ap.add_argument("--isolation-impact", type=str, required=True)
    ap.add_argument("--evaluator-impact", type=str, required=True)
    ap.add_argument("--generic-aar-impact", type=str, required=True)
    ap.add_argument("--recommended-action", default="OPEN_OR_UPDATE_DRAFT_PR_DO_NOT_AUTO_MERGE")
    ap.add_argument("--detected-at", default=None, help="ISO8601 UTC; default now")
    ap.add_argument("--out-dir", default="upstream_updates")
    ap.add_argument("--classify-file", default=None, help="optional full classify JSON to merge categories/flags from")
    args = ap.parse_args()

    def as_bool(v: str) -> bool:
        return str(v).strip().lower() in ("1", "true", "yes", "y")

    categories = None
    possible_breaking = as_bool(args.possible_breaking_change)
    isolation = as_bool(args.isolation_impact)
    evaluator = as_bool(args.evaluator_impact)
    generic = as_bool(args.generic_aar_impact)

    if args.classify_file:
        clf = json.loads(Path(args.classify_file).read_text())
        categories = clf.get("categories", [])
        possible_breaking = bool(clf.get("possible_breaking_change", possible_breaking))
        isolation = bool(clf.get("isolation_impact", isolation))
        evaluator = bool(clf.get("evaluator_impact", evaluator))
        generic = bool(clf.get("generic_aar_impact", generic))
    else:
        raw = args.categories_json
        if raw.startswith("@"):
            raw = Path(raw[1:]).read_text()
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            categories = parsed.get("categories", [])
            possible_breaking = bool(parsed.get("possible_breaking_change", possible_breaking))
            isolation = bool(parsed.get("isolation_impact", isolation))
            evaluator = bool(parsed.get("evaluator_impact", evaluator))
            generic = bool(parsed.get("generic_aar_impact", generic))
        else:
            categories = parsed

    detected_at = args.detected_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_part = detected_at[:10]
    short = args.new_sha[:12]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{date_part}-{short}.json"

    manifest = {
        "detected_at": detected_at,
        "old_sha": args.old_sha,
        "new_sha": args.new_sha,
        "AAR_UPSTREAM_SHA": args.new_sha,
        "PINNED_UPSTREAM_SHA": args.old_sha,
        "LATEST_UPSTREAM_SHA": args.new_sha,
        "commit_count": args.commit_count,
        "changed_files": args.changed_files,
        "additions": args.additions,
        "deletions": args.deletions,
        "categories": categories,
        "possible_breaking_change": possible_breaking,
        "isolation_impact": isolation,
        "evaluator_impact": evaluator,
        "generic_aar_impact": generic,
        "recommended_action": args.recommended_action,
        "note": "DOWNSTREAM-LOCAL manifest. Does not update PINNED_UPSTREAM_SHA. DO_NOT_AUTO_MERGE.",
    }

    out_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
