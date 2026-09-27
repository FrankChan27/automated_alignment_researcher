#!/usr/bin/env bash
# End-to-end fixture smoke: build vector.json near the hill-climb secret (without
# reading held-out into the research artifact), score, prove held-out strip.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "$ROOT/scripts/env.sh"
# shellcheck source=/dev/null
source "$POC002_VENV/bin/activate"

EVIDENCE="$AAR_POC002_ROOT/evidence"
mkdir -p "$EVIDENCE" "$POC002_RUNS_DIR/smoke_models/near_hillclimb"

python << PY
import json, os
from pathlib import Path

secret = Path(os.environ["POC002_SECRET_DIR"])
hc = json.loads((secret / "hillclimb_target.json").read_text())["vector"]
# Research-side fixture: perturb hill-climb target slightly (still well-formed).
# Do NOT read heldout_target into the fixture content committed under the repo —
# this smoke writes only under /home/box/aar-poc-002-runs/.
vec = list(hc)
vec[0] = max(0, min(100, vec[0] - 5))
vec[3] = max(0, min(100, vec[3] + 3))
out_dir = Path(os.environ["POC002_RUNS_DIR"]) / "smoke_models" / "near_hillclimb"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "vector.json").write_text(json.dumps({"vector": vec}, indent=2) + "\n")
print("wrote", out_dir / "vector.json", "(vector redacted from log)")
PY

OUT_RESEARCH="$POC002_RUNS_DIR/research_scores/smoke_near_hc.json"
# Clear prior heldout smoke file with same basename if present
rm -f "$HELDOUT_SCORES_DIR/smoke_near_hc.json"

bash "$ROOT/scripts/run_eval.sh" \
  "$POC002_RUNS_DIR/smoke_models/near_hillclimb" \
  "$OUT_RESEARCH" | tee "$EVIDENCE/vector_eval_smoke.txt"

python << PY
import json, os
from pathlib import Path

research = Path(os.environ["POC002_RUNS_DIR"]) / "research_scores" / "smoke_near_hc.json"
held = Path(os.environ["HELDOUT_SCORES_DIR"]) / "smoke_near_hc.json"
r = json.loads(research.read_text())
h = json.loads(held.read_text())
print("=== STRIP PROOF ===")
print("research keys:", sorted(r.keys()))
print("research per_benchmark:", sorted((r.get("per_benchmark") or {}).keys()))
print("research has held_out_pct?", "held_out_pct" in r)
print("research has poc002_heldout?", "poc002_heldout" in (r.get("per_benchmark") or {}))
print("heldout keys:", sorted(h.keys()))
print("heldout per_benchmark:", sorted((h.get("per_benchmark") or {}).keys()))
print("heldout has held_out_pct?", "held_out_pct" in h)
print("heldout has poc002_heldout?", "poc002_heldout" in (h.get("per_benchmark") or {}))
assert "poc002_heldout" not in (r.get("per_benchmark") or {}), "HELD-OUT LEAKED into research scores"
assert "held_out_pct" not in r, "held_out_pct leaked into research scores"
assert "poc002_heldout" in (h.get("per_benchmark") or {}), "held-out missing from private full scores"
assert "held_out_pct" in h, "held_out_pct missing from private full scores"
assert r.get("passes_filter") is True, "capability gate should pass for well-formed vector"
print("STRIP_PROOF=PASS")
print("headline_pct=", r.get("headline_pct"), "passes_filter=", r.get("passes_filter"))
print("held_out_pct=", h.get("held_out_pct"))
PY
