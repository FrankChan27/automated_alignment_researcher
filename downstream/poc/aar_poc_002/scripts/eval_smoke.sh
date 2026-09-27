#!/usr/bin/env bash
# (a) Eval smoke via adapter.eval + fixture vector — no API key.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common_env.sh"

POC="${REPO_ROOT}/downstream/poc/aar_poc_002"
EVID="${POC}/evidence/smoke"
mkdir -p "${EVID}" /tmp/poc002_smoke_models

MID="${POC}/adapter/fixtures/mid_vector"
OOB="${POC}/adapter/fixtures/oob_vector"

echo "=== mid vector eval ===" | tee "${EVID}/eval_mid.txt"
"${VENV}/bin/python" -m aar_poc_002.adapter.eval \
  --suite "${POC}/adapter/suite.yaml" \
  --model "${MID}" \
  --secret-dir "${POC002_SECRET_DIR}" \
  --out "${EVID}/scores_mid.json" \
  --heldout-dir "${HOLDOUT_DIR}" \
  2>&1 | tee -a "${EVID}/eval_mid.txt"

echo "=== oob vector eval ===" | tee "${EVID}/eval_oob.txt"
"${VENV}/bin/python" -m aar_poc_002.adapter.eval \
  --suite "${POC}/adapter/suite.yaml" \
  --model "${OOB}" \
  --secret-dir "${POC002_SECRET_DIR}" \
  --out "${EVID}/scores_oob.json" \
  --heldout-dir "${HOLDOUT_DIR}" \
  2>&1 | tee -a "${EVID}/eval_oob.txt"

# Runtime near-T vector (NOT committed — reads secret in eval-only process)
"${VENV}/bin/python" - <<'PY' | tee "${EVID}/eval_near.txt"
import json, os, tempfile
from pathlib import Path
secret = json.loads(Path(os.environ["POC002_TRAIN_SECRET"]).read_text())
T = secret["target"]
near = [max(0, min(100, t + (2 if i % 2 == 0 else -2))) for i, t in enumerate(T)]
d = Path(tempfile.mkdtemp(prefix="poc002_near_", dir="/tmp/poc002_smoke_models"))
(d / "vector.json").write_text(json.dumps({"vector": near}) + "\n")
print("NEAR_DIR", d)
print("NEAR_VEC", near)
import subprocess, sys
poc = Path(os.environ["REPO_ROOT"]) / "downstream/poc/aar_poc_002"
cmd = [
    sys.executable, "-m", "aar_poc_002.adapter.eval",
    "--suite", str(poc / "adapter/suite.yaml"),
    "--model", str(d),
    "--secret-dir", os.environ["POC002_SECRET_DIR"],
    "--out", str(poc / "evidence/smoke/scores_near.json"),
    "--heldout-dir", os.environ["HOLDOUT_DIR"],
]
print("CMD", " ".join(cmd))
subprocess.check_call(cmd)
PY

"${VENV}/bin/python" - <<'PY' | tee "${EVID}/compare.txt"
import json
from pathlib import Path
base = Path("/workspace/aar-infra/automated_alignment_researcher/downstream/poc/aar_poc_002/evidence/smoke")
def load(name):
    d = json.loads((base / name).read_text())
    return d.get("headline_pct"), d.get("passes_filter"), d.get("closed_pct"), d.get("per_benchmark", {})
for n in ("scores_mid.json", "scores_near.json", "scores_oob.json"):
    h, p, c, pb = load(n)
    hill = (pb.get("poc002_hillclimb") or {}).get("mean")
    print(f"{n}: headline_pct={h} passes_filter={p} closed={c} hillclimb_mean={hill}")
mid_h = load("scores_mid.json")[0]
near_h = load("scores_near.json")[0]
assert near_h is not None and mid_h is not None
assert near_h > mid_h, f"expected near > mid ({near_h} vs {mid_h})"
oob = json.loads((base / "scores_oob.json").read_text())
assert oob.get("passes_filter") is False, "oob should fail capability"
print("SMOKE_OK near_headline > mid_headline; oob fails filter")
PY
