# EXECUTION_PATH — AAR-xAI-adapter-001

```
run.py agent | scripts/run_native_loop.py
  └─ AAR_AGENT_PROVIDER=grok_cli  (skips ANTHROPIC_API_KEY gate)
  └─ AutonomousAgentLoop.run  (upstream control-flow)
       └─ _run_session  (iteration = fresh provider session)
            └─ BaseAgent.execute
                 └─ get_agent_provider() → GrokCLIProvider (downstream)
                      └─ grok --single … --verbatim --model grok-4.7
                           --permission-mode … --cwd … [--tools …]
                           └─ reads local OIDC ~/.grok/auth.json
                           └─ Grok inference (cli_native)
                 └─ AssistantEvent / ResultEvent → session log
       └─ session_count++ ; optional findings/S3 (local_mode: off)
       └─ next iteration until max_iterations | timeout
```

Eval (PHASE 5): agent Bash → `python -m aar_poc_002.adapter.eval` (POC-002 native), not homemade scorer.

Contrast POC-001: **not** `harness/run_loop.py` / proposer scheduler.
