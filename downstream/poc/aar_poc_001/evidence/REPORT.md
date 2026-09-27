# AAR-POC-001 Report

- Completed at: `2026-09-27T17:26:52.314177+00:00`
- Iterations: **25** / 25
- First train score: `-22330.1`
- Best train score: `-159.5` (iteration 23)
- Improved across iterations: **True** (first improvement at iter 3)
- Best artifact vector: `[67, 73, 27, 57, 41, 32, 55, 43]`
- Held-out score (once): `2938.3999999999996`

## Score trajectory

| iter | ok | score | strategy |
|------|----|-------|----------|
| 1 | True | -22330.1 | init_zeros |
| 3 | True | -20669.6 | mutate_best |
| 4 | True | -17213.3 | mutate_best |
| 5 | True | -17213.3 | coord_probe |
| 6 | True | -17213.3 | mutate_best |
| 7 | True | -14501.599999999999 | mutate_best |
| 8 | True | -14323.8 | mutate_best |
| 9 | True | -13075.2 | mutate_best |
| 10 | True | -13075.2 | coord_probe |
| 11 | True | -17863.2 | mutate_best |
| 12 | True | -14041.2 | mutate_best |
| 13 | True | -12861.5 | mutate_best |
| 14 | True | -7847.200000000001 | mutate_best |
| 15 | True | -5680.9 | random_restart |
| 16 | True | -5656.9 | mutate_best |
| 17 | True | -4671.299999999999 | mutate_best |
| 18 | True | -4786.5 | mutate_best |
| 19 | True | -6866.299999999999 | mutate_best |
| 20 | True | -3033.7999999999993 | coord_probe |
| 21 | True | -1479.7999999999993 | mutate_best |
| 22 | True | -497.0 | mutate_best |
| 23 | True | -159.5 | mutate_best |
| 24 | True | -1157.5 | mutate_best |
| 25 | True | -421.89999999999964 | coord_probe |

## Failures / recoveries

- iter 2: vector[0]=150 out of bounds [0,100] (recovered=True)

## Isolation

Researcher subprocess runs without AAR_POC_SECRET_PATH; evaluator subprocess receives it. Score JSON omits target/weights. Held-out run exactly once after the train loop.
- eval_secret mode: `0o700`

## Git / upstream untouched

- branch: `downstream/aar-poc-001`
- aar/ + generic_aar diff empty: **True**
- status summary: `?? downstream/poc/`

## Paths

- `run_dir`: `/workspace/aar-infra/automated_alignment_researcher/downstream/poc/aar_poc_001/runs/AAR-POC-001`
- `state`: `/workspace/aar-infra/automated_alignment_researcher/downstream/poc/aar_poc_001/runs/AAR-POC-001/state.json`
- `trajectory`: `/workspace/aar-infra/automated_alignment_researcher/downstream/poc/aar_poc_001/runs/AAR-POC-001/trajectory.jsonl`
- `failures`: `/workspace/aar-infra/automated_alignment_researcher/downstream/poc/aar_poc_001/runs/AAR-POC-001/failures.jsonl`
- `heldout`: `/workspace/aar-infra/automated_alignment_researcher/downstream/poc/aar_poc_001/runs/AAR-POC-001/heldout/result.json`
- `report_json`: `/workspace/aar-infra/automated_alignment_researcher/downstream/poc/aar_poc_001/runs/AAR-POC-001/report.json`
- `report_md`: `/workspace/aar-infra/automated_alignment_researcher/downstream/poc/aar_poc_001/runs/AAR-POC-001/REPORT.md`
