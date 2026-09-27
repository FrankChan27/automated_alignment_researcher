"""Portable eval entry (generic_aar/eval.py pattern).

Registers POC-002 benchmarks, installs VectorModel load_model shim, then calls
aar.eval_pod.run_eval.run. Not an agent / research loop.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _ensure_import_path() -> None:
    """Allow `import aar` and `import aar_poc_002` when launched as a script."""
    here = Path(__file__).resolve()
    poc_dir = here.parents[2]   # .../downstream/poc
    repo_root = here.parents[4]  # .../automated_alignment_researcher
    for p in (str(repo_root), str(poc_dir)):
        if p not in sys.path:
            sys.path.insert(0, p)


def main(argv: list[str] | None = None) -> None:
    _ensure_import_path()
    from aar_poc_002.adapter.models_vector import install_vector_loader

    install_vector_loader()
    import aar_poc_002.adapter.benchmarks  # noqa: F401 — register plugins
    from aar.eval_pod.run_eval import run

    default_secret = os.environ.get("POC002_SECRET_DIR", "/home/box/aar-poc-002-secrets")
    default_heldout = os.environ.get(
        "HELDOUT_SCORES_DIR",
        str(Path(default_secret) / "heldout_scores"),
    )
    suite_default = str(Path(__file__).resolve().parent / "suite.yaml")

    ap = argparse.ArgumentParser(description="POC-002 vector suite eval (native run_eval).")
    ap.add_argument("--suite", default=suite_default)
    ap.add_argument(
        "--model",
        required=True,
        help="model_path dir containing vector.json (or stub:*)",
    )
    ap.add_argument(
        "--secret-dir",
        default=default_secret,
        help="eval-only dir with train.json / heldout.json (outside git)",
    )
    ap.add_argument("--out", default="scores.json", help="research-readable (held-out stripped)")
    ap.add_argument(
        "--heldout-dir",
        default=default_heldout,
        help="eval-private dir for FULL scores incl held-out (mode 700)",
    )
    args = ap.parse_args(argv)
    run(args.suite, args.model, args.secret_dir, args.out, args.heldout_dir)


if __name__ == "__main__":
    main()
