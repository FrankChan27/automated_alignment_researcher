"""Auto-applied when scripts/preload is on PYTHONPATH (agent launch).

Registers POC-002 benches + VectorModel load_model shim at interpreter start.
Does not edit aar/*.py on disk.
"""
try:
    from aar_poc_002.adapter.models_vector import install_vector_loader
    install_vector_loader()
    import aar_poc_002.adapter.benchmarks  # noqa: F401
except Exception as exc:  # pragma: no cover — agent may start before path ready
    import sys
    print(f"[poc002 sitecustomize] skip: {exc}", file=sys.stderr)
