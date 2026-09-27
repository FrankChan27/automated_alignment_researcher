# Deletion proof (UPSTREAM_NATIVE_AAR)

Expectation: after temporarily renaming `aar/` and `generic_aar/`, the same launch
wrapper / eval smoke MUST fail (ImportError), proving the POC depends on upstream
packages rather than a forked loop under aar_poc_002.

Safe procedure:
1. `mv aar /tmp/aar.bak-poc002 && mv generic_aar /tmp/generic_aar.bak-poc002`
2. Attempt `python -c 'import aar'` / eval_smoke → expect import failure
3. Restore: `mv /tmp/aar.bak-poc002 aar && mv /tmp/generic_aar.bak-poc002 generic_aar`

If smoke still PASSES with aar/+generic_aar gone → UPSTREAM_NATIVE_AAR=false (do not claim PASS).
