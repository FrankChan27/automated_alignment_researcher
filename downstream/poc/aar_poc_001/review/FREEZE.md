# AAR-POC-001 FREEZE

Status: FROZEN for independent review
Frozen at: 2026-09-28 (orchestrator)

## Canonical frozen run (use this)
`/workspace/aar-infra/automated_alignment_researcher/downstream/poc/aar_poc_001/runs/AAR-POC-001-frozen-25/`

Files:
- trajectory.jsonl
- state.json
- report.json + REPORT.md
- heldout/result.json
- failures.jsonl
- best/artifact.json
- submissions/ + scores/ (full per-iter artifacts)
- FROZEN marker

## Mirror summary (same content)
`/workspace/aar-infra/automated_alignment_researcher/downstream/poc/aar_poc_001/evidence/`

## Review write path
`/workspace/aar-infra/automated_alignment_researcher/downstream/poc/aar_poc_001/review/AAR_MINIMAL_LOOP.json`
`/workspace/aar-infra/automated_alignment_researcher/downstream/poc/aar_poc_001/review/AAR_MINIMAL_LOOP.md`

## Notes
- Do NOT use any live `runs/AAR-POC-001` directory if present (may be mid-extension).
- Canonical freeze is **25** autonomous iterations (≥20). Researcher callback mentioning 45 is a later extension — ignore for adjudication unless separately frozen.
- aar/ and generic_aar unmodified.
