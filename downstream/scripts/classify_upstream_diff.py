#!/usr/bin/env python3
"""DOWNSTREAM-LOCAL: classify upstream path changes into governance categories.

Usage:
  classify_upstream_diff.py <old_sha> <new_sha>
  classify_upstream_diff.py --files path1 path2 ...
  classify_upstream_diff.py --gh-compare-json <file|->

Emits JSON:
  {
    "categories": [...],
    "possible_breaking_change": bool,
    "isolation_impact": bool,
    "evaluator_impact": bool,
    "generic_aar_impact": bool,
    "per_file": [{"path": "...", "categories": [...]}],
    "file_count": N
  }
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

CATEGORIES = (
    "HARNESS_CORE",
    "GENERIC_AAR",
    "EVALUATOR",
    "ISOLATION",
    "MONITOR",
    "TRANSPORT",
    "CONFIG",
    "PROMPT",
    "DEPENDENCY",
    "TEST",
    "DOCS_ONLY",
    "BREAKING_OR_UNKNOWN",
)

# Ordered rules: first matching rule(s) accumulate; a path can have multiple labels.
RULES: list[tuple[str, re.Pattern[str]]] = [
    ("ISOLATION", re.compile(r"(^|/)ISOLATION\.md$|(^|/)_holdout|(^|/)_heldout|heldout_isolation|verify_heldout|publish_holdout|purge_heldout", re.I)),
    ("GENERIC_AAR", re.compile(r"^generic_aar/")),
    ("EVALUATOR", re.compile(r"^aar/eval_pod/|^configs/|judges\.py|refusal_judges|model_fingerprint|run_eval")),
    ("HARNESS_CORE", re.compile(r"^aar/research_loop/|^aar/ideas/|^aar/ideas_archive/|^aar/litreview/|^aar/infrastructure/|^run\.py$|^run\.sh$|^HARNESS\.md$|^LAUNCH\.md$")),
    ("TRANSPORT", re.compile(r"^aar/transport\.py$|eval_job\.sh|eval_worker|eval_watcher|slurm_")),
    ("MONITOR", re.compile(r"^downstream/|^\.github/workflows/upstream-monitor|upstream_updates/")),
    ("DEPENDENCY", re.compile(r"(^|/)pyproject\.toml$|(^|/)uv\.lock$|(^|/)requirements.*\.txt$|(^|/)Dockerfile$")),
    ("CONFIG", re.compile(r"^configs/|(^|/)entrypoint\.sh$|(^|/)\.env\.example$")),
    ("PROMPT", re.compile(r"briefing\.md|prompt|system_prompt|judge_prompt", re.I)),
    ("TEST", re.compile(r"^tests/|(^|/)smoke_|_test\.py$|\.test\.|test_")),
    ("DOCS_ONLY", re.compile(r"\.md$|^benchmark_docs/|^REPRODUCE\.md$|^PORTABILITY\.md$|^README\.md$")),
]


def classify_path(path: str) -> list[str]:
    path = path.replace("\\", "/").lstrip("./")
    hits: list[str] = []
    for cat, rx in RULES:
        if rx.search(path):
            hits.append(cat)
    if not hits:
        hits.append("BREAKING_OR_UNKNOWN")
    # Deduplicate preserving order
    seen: set[str] = set()
    out: list[str] = []
    for h in hits:
        if h not in seen:
            seen.add(h)
            out.append(h)
    return out


def files_from_git_diff(old_sha: str, new_sha: str) -> list[str]:
    r = subprocess.run(
        ["git", "diff", "--name-only", f"{old_sha}...{new_sha}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        # fallback: two-dot
        r = subprocess.run(
            ["git", "diff", "--name-only", old_sha, new_sha],
            capture_output=True,
            text=True,
            check=True,
        )
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]


def files_from_gh_compare(obj: dict) -> list[str]:
    files = obj.get("files") or []
    return [f.get("filename") or f.get("path") for f in files if f.get("filename") or f.get("path")]


def build_result(paths: Iterable[str]) -> dict:
    paths = [p for p in paths if p]
    per_file = [{"path": p, "categories": classify_path(p)} for p in paths]
    cats: set[str] = set()
    for item in per_file:
        cats.update(item["categories"])

    isolation_impact = "ISOLATION" in cats
    evaluator_impact = "EVALUATOR" in cats
    generic_aar_impact = "GENERIC_AAR" in cats

    # Breaking heuristics
    possible_breaking = "BREAKING_OR_UNKNOWN" in cats
    for item in per_file:
        p = item["path"]
        if p.endswith("pyproject.toml") or p.endswith("uv.lock"):
            possible_breaking = True
        if re.search(r"^aar/.+\.py$", p) and "DOCS_ONLY" not in item["categories"]:
            # core python churn is elevated risk
            if any(c in item["categories"] for c in ("HARNESS_CORE", "EVALUATOR", "TRANSPORT", "GENERIC_AAR")):
                possible_breaking = possible_breaking or False  # keep explicit
        if re.search(r"(^|/)__init__\.py$", p) or "breaking" in p.lower() or "removed" in p.lower():
            possible_breaking = True

    # If only DOCS_ONLY (and maybe MONITOR), not breaking
    non_doc = cats - {"DOCS_ONLY", "MONITOR"}
    if not non_doc and cats:
        possible_breaking = False
    if "BREAKING_OR_UNKNOWN" in cats:
        possible_breaking = True

    ordered = [c for c in CATEGORIES if c in cats]
    return {
        "categories": ordered,
        "possible_breaking_change": bool(possible_breaking),
        "isolation_impact": bool(isolation_impact),
        "evaluator_impact": bool(evaluator_impact),
        "generic_aar_impact": bool(generic_aar_impact),
        "per_file": per_file,
        "file_count": len(paths),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="DOWNSTREAM-LOCAL upstream diff classifier")
    ap.add_argument("old_sha", nargs="?", help="old / pinned SHA")
    ap.add_argument("new_sha", nargs="?", help="new / latest SHA")
    ap.add_argument("--files", nargs="*", help="explicit file list")
    ap.add_argument("--gh-compare-json", help="path to gh compare JSON, or - for stdin")
    ap.add_argument("--repo-root", default=None)
    args = ap.parse_args()

    if args.repo_root:
        import os

        os.chdir(args.repo_root)

    paths: list[str] = []
    if args.gh_compare_json:
        raw = sys.stdin.read() if args.gh_compare_json == "-" else Path(args.gh_compare_json).read_text()
        obj = json.loads(raw)
        paths = files_from_gh_compare(obj)
    elif args.files is not None and len(args.files) > 0:
        paths = list(args.files)
    elif args.old_sha and args.new_sha:
        paths = files_from_git_diff(args.old_sha, args.new_sha)
    else:
        ap.error("provide old_sha new_sha, or --files, or --gh-compare-json")

    result = build_result(paths)
    json.dump(result, sys.stdout, indent=2, sort_keys=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
