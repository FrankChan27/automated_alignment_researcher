#!/usr/bin/env python3
"""AAR-POC-001 harness: autonomous Researcher → artifact → isolated TRAIN
evaluator → score → persistent state, for N≥20 iterations, then ONE held-out
eval on the best train artifact.

Isolation:
  - Evaluator runs in a subprocess with AAR_POC_SECRET_PATH set.
  - Researcher subprocess does NOT receive AAR_POC_SECRET_PATH.
  - Researcher modules must not open eval_secret/.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def run_researcher(python: str, proposer: Path, state: Path, artifact: Path, poc_root: Path) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env.pop("AAR_POC_SECRET_PATH", None)  # never pass secrets to researcher
    return subprocess.run(
        [
            python,
            str(proposer),
            "--state", str(state),
            "--out", str(artifact),
            "--poc-root", str(poc_root),
        ],
        env=env,
        capture_output=True,
        text=True,
    )


def run_evaluator(
    python: str,
    scorer: Path,
    artifact: Path,
    score_out: Path,
    secret_path: Path,
    role: str,
    iteration: int,
) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["AAR_POC_SECRET_PATH"] = str(secret_path)
    return subprocess.run(
        [
            python,
            str(scorer),
            "--artifact", str(artifact),
            "--out", str(score_out),
            "--secret", str(secret_path),
            "--role", role,
            "--iteration", str(iteration),
        ],
        env=env,
        capture_output=True,
        text=True,
    )


def default_state(seed: int = 42) -> dict[str, Any]:
    return {
        "experiment": "AAR-POC-001",
        "iteration": 0,
        "history": [],
        "best_vector": None,
        "best_score": None,
        "best_iteration": None,
        "last_vector": None,
        "last_score": None,
        "injected_oob_failure": False,
        "rng_seed": seed,
        "failures": [],
        "updated_at": None,
    }


def build_report(
    run_dir: Path,
    state: dict[str, Any],
    heldout: dict[str, Any] | None,
    n_target: int,
    poc_root: Path,
    git_notes: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    history = state.get("history", [])
    scores = [h.get("score") for h in history if h.get("ok") and h.get("score") is not None]
    first_score = scores[0] if scores else None
    best_score = state.get("best_score")
    improved = (
        first_score is not None
        and best_score is not None
        and best_score > first_score
    )
    first_improve_iter = None
    if improved and first_score is not None:
        for h in history:
            if h.get("ok") and h.get("score") is not None and h["score"] > first_score:
                first_improve_iter = h.get("iteration")
                break

    report = {
        "experiment": "AAR-POC-001",
        "completed_at": utc_now(),
        "iterations_requested": n_target,
        "iterations_completed": state.get("iteration", 0),
        "score_trajectory": [
            {"iteration": h.get("iteration"), "score": h.get("score"), "ok": h.get("ok"), "strategy": h.get("strategy")}
            for h in history
        ],
        "first_score": first_score,
        "best_train_score": best_score,
        "best_artifact": {"vector": state.get("best_vector")},
        "best_iteration": state.get("best_iteration"),
        "improved": improved,
        "first_improvement_iteration": first_improve_iter,
        "heldout": heldout,
        "failures": state.get("failures", []),
        "isolation": {
            "researcher_env_has_secret": False,
            "evaluator_env_has_secret": True,
            "eval_secret_mode": oct((poc_root / "eval_secret").stat().st_mode & 0o777),
            "notes": (
                "Researcher subprocess runs without AAR_POC_SECRET_PATH; "
                "evaluator subprocess receives it. Score JSON omits target/weights. "
                "Held-out run exactly once after the train loop."
            ),
        },
        "paths": {
            "run_dir": str(run_dir),
            "state": str(run_dir / "state.json"),
            "trajectory": str(run_dir / "trajectory.jsonl"),
            "failures": str(run_dir / "failures.jsonl"),
            "heldout": str(run_dir / "heldout" / "result.json"),
            "report_json": str(run_dir / "report.json"),
            "report_md": str(run_dir / "REPORT.md"),
        },
        "git": git_notes,
    }

    lines = [
        "# AAR-POC-001 Report",
        "",
        f"- Completed at: `{report['completed_at']}`",
        f"- Iterations: **{report['iterations_completed']}** / {n_target}",
        f"- First train score: `{first_score}`",
        f"- Best train score: `{best_score}` (iteration {state.get('best_iteration')})",
        f"- Improved across iterations: **{improved}**"
        + (f" (first improvement at iter {first_improve_iter})" if first_improve_iter else ""),
        f"- Best artifact vector: `{state.get('best_vector')}`",
        f"- Held-out score (once): `{None if heldout is None else heldout.get('score')}`",
        "",
        "## Score trajectory",
        "",
        "| iter | ok | score | strategy |",
        "|------|----|-------|----------|",
    ]
    for h in history:
        lines.append(
            f"| {h.get('iteration')} | {h.get('ok')} | {h.get('score')} | {h.get('strategy')} |"
        )
    lines += [
        "",
        "## Failures / recoveries",
        "",
    ]
    fails = state.get("failures", [])
    if not fails:
        lines.append("_None recorded._")
    else:
        for frow in fails:
            lines.append(
                f"- iter {frow.get('iteration')}: {frow.get('error')} "
                f"(recovered={frow.get('recovered')})"
            )
    lines += [
        "",
        "## Isolation",
        "",
        report["isolation"]["notes"],
        f"- eval_secret mode: `{report['isolation']['eval_secret_mode']}`",
        "",
        "## Git / upstream untouched",
        "",
        f"- branch: `{git_notes.get('branch')}`",
        f"- aar/ + generic_aar diff empty: **{git_notes.get('upstream_untouched')}**",
        f"- status summary: `{git_notes.get('status_summary')}`",
        "",
        "## Paths",
        "",
    ]
    for k, v in report["paths"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    return report, "\n".join(lines)


def gather_git_notes(repo: Path) -> dict[str, Any]:
    def _run(args: list[str]) -> str:
        r = subprocess.run(args, cwd=str(repo), capture_output=True, text=True)
        return (r.stdout or r.stderr or "").strip()

    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    status = _run(["git", "status", "--short"])
    diff_stat = _run(["git", "diff", "--stat", "aar", "generic_aar"])
    # also check staged+unstaged vs HEAD for those paths
    diff_stat_all = _run(["git", "diff", "HEAD", "--stat", "--", "aar", "generic_aar"])
    untouched = (diff_stat == "" and diff_stat_all == "")
    return {
        "branch": branch,
        "status_summary": status[:500] if status else "(clean or only untracked outside short?)",
        "aar_generic_diff_stat": diff_stat_all or "(empty)",
        "upstream_untouched": untouched,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="AAR-POC-001 harness loop")
    ap.add_argument(
        "--poc-root",
        default=str(Path(__file__).resolve().parents[1]),
        help="path to aar_poc_001/",
    )
    ap.add_argument("--n", type=int, default=25, help="train iterations (default 25, min 20)")
    ap.add_argument("--run-id", default="AAR-POC-001")
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--resume", action="store_true", help="resume from existing state.json")
    args = ap.parse_args(argv)

    if args.n < 20:
        print("ERROR: N must be >= 20", file=sys.stderr)
        return 2

    poc_root = Path(args.poc_root).resolve()
    repo = poc_root.parents[2]  # .../automated_alignment_researcher
    run_dir = poc_root / "runs" / args.run_id
    submissions = run_dir / "submissions"
    scores_dir = run_dir / "scores"
    heldout_dir = run_dir / "heldout"
    state_path = run_dir / "state.json"
    traj_path = run_dir / "trajectory.jsonl"
    fail_path = run_dir / "failures.jsonl"

    proposer = poc_root / "researcher" / "proposer.py"
    scorer = poc_root / "evaluator" / "score_artifact.py"
    train_secret = poc_root / "eval_secret" / "train_params.json"
    heldout_secret = poc_root / "eval_secret" / "heldout_params.json"

    for p in (train_secret, heldout_secret, proposer, scorer):
        if not p.exists():
            print(f"ERROR: missing {p}", file=sys.stderr)
            return 2

    run_dir.mkdir(parents=True, exist_ok=True)
    submissions.mkdir(parents=True, exist_ok=True)
    scores_dir.mkdir(parents=True, exist_ok=True)
    heldout_dir.mkdir(parents=True, exist_ok=True)

    if args.resume and state_path.is_file():
        state = load_json(state_path, default_state(args.seed))
        print(f"Resuming from iteration {state.get('iteration')}")
    else:
        # Fresh run: clear trajectory logs but keep directory
        if traj_path.exists():
            traj_path.unlink()
        if fail_path.exists():
            fail_path.unlink()
        state = default_state(args.seed)
        write_json(state_path, state)

    python = args.python
    start_iter = int(state.get("iteration", 0)) + 1

    print(f"=== AAR-POC-001 harness: iterations {start_iter}..{args.n} ===")
    print(f"run_dir={run_dir}")
    print(f"python={python}")

    for i in range(start_iter, args.n + 1):
        iter_tag = f"iter_{i:03d}"
        sub_dir = submissions / iter_tag
        sub_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = sub_dir / "artifact.json"
        score_path = scores_dir / f"{iter_tag}.json"

        # 1) Researcher proposes
        t0 = time.time()
        rp = run_researcher(python, proposer, state_path, artifact_path, poc_root)
        if rp.returncode != 0:
            err = {
                "iteration": i,
                "phase": "researcher",
                "error": (rp.stderr or rp.stdout or "researcher failed")[:800],
                "recovered": False,
                "ts": utc_now(),
            }
            state.setdefault("failures", []).append(err)
            append_jsonl(fail_path, err)
            write_json(state_path, state)
            print(f"[{iter_tag}] RESEARCHER FAIL: {err['error']}")
            return 1

        artifact = load_json(artifact_path, {})
        strategy = artifact.get("strategy", "unknown")
        vector = artifact.get("vector")

        # 2) Isolated TRAIN evaluator
        ep = run_evaluator(
            python, scorer, artifact_path, score_path, train_secret, "train", i
        )
        score_payload = load_json(score_path, {"ok": False, "error": "no score file", "score": None})
        ok = bool(score_payload.get("ok"))
        score = score_payload.get("score")
        elapsed = time.time() - t0

        traj_row = {
            "iteration": i,
            "ok": ok,
            "score": score,
            "vector": vector,
            "strategy": strategy,
            "elapsed_s": round(elapsed, 4),
            "evaluator_returncode": ep.returncode,
            "ts": utc_now(),
        }
        append_jsonl(traj_path, traj_row)

        if not ok:
            err = {
                "iteration": i,
                "phase": "evaluator",
                "error": score_payload.get("error") or (ep.stderr or "eval failed"),
                "vector": vector,
                "strategy": strategy,
                "recovered": True,  # loop continues
                "ts": utc_now(),
            }
            state.setdefault("failures", []).append(err)
            append_jsonl(fail_path, err)
            if strategy == "inject_oob_failure":
                state["injected_oob_failure"] = True
            print(f"[{iter_tag}] EVAL FAIL (recoverable): {err['error']}")
        else:
            print(f"[{iter_tag}] score={score:.4f} strategy={strategy} vec={vector}")
            state["last_vector"] = vector
            state["last_score"] = score
            hist_entry = {
                "iteration": i,
                "ok": True,
                "score": score,
                "vector": vector,
                "strategy": strategy,
            }
            state.setdefault("history", []).append(hist_entry)
            if state.get("best_score") is None or score > state["best_score"]:
                state["best_score"] = score
                state["best_vector"] = vector
                state["best_iteration"] = i
                # Save best artifact copy
                best_dir = run_dir / "best"
                best_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(artifact_path, best_dir / "artifact.json")
                write_json(best_dir / "score.json", score_payload)

        state["iteration"] = i
        state["updated_at"] = utc_now()
        write_json(state_path, state)

    # --- Held-out: exactly once on best artifact ---
    print("=== Held-out eval (once) on best train artifact ===")
    best_artifact = run_dir / "best" / "artifact.json"
    if not best_artifact.is_file():
        # Fallback: last successful history entry
        for h in reversed(state.get("history", [])):
            it = h["iteration"]
            cand = submissions / f"iter_{it:03d}" / "artifact.json"
            if cand.is_file():
                best_dir = run_dir / "best"
                best_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(cand, best_artifact)
                state["best_vector"] = h["vector"]
                state["best_score"] = h["score"]
                state["best_iteration"] = it
                break

    heldout_payload = None
    if best_artifact.is_file():
        heldout_out = heldout_dir / "result.json"
        hp = run_evaluator(
            python,
            scorer,
            best_artifact,
            heldout_out,
            heldout_secret,
            "heldout",
            int(state.get("best_iteration") or -1),
        )
        heldout_payload = load_json(heldout_out, {"ok": False, "error": "heldout failed", "score": None})
        heldout_payload["evaluator_returncode"] = hp.returncode
        heldout_payload["note"] = "Held-out run exactly once after train loop; never shown to researcher during loop."
        write_json(heldout_out, heldout_payload)
        print(f"heldout score={heldout_payload.get('score')}")
    else:
        print("WARNING: no best artifact for held-out", file=sys.stderr)

    git_notes = gather_git_notes(repo)
    report, report_md = build_report(
        run_dir, state, heldout_payload, args.n, poc_root, git_notes
    )
    write_json(run_dir / "report.json", report)
    (run_dir / "REPORT.md").write_text(report_md, encoding="utf-8")
    write_json(state_path, state)

    print("=== Done ===")
    print(f"report: {run_dir / 'REPORT.md'}")
    print(f"best_train={state.get('best_score')} heldout={None if heldout_payload is None else heldout_payload.get('score')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
