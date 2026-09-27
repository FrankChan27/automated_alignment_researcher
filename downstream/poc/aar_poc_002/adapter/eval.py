"""Phase-2 portable eval entry (generic_aar/eval.py pattern).

Registers adapter benchmarks, installs vector load_model shim, then calls
aar.eval_pod.run_eval.run. Not an agent / research loop.
"""
from __future__ import annotations

import argparse


def main() -> None:
    raise SystemExit(
        "phase-1 scaffold only: implement benches + wire install_vector_loader "
        "before calling aar.eval_pod.run_eval.run (see design.md)."
    )


if __name__ == "__main__":
    main()
