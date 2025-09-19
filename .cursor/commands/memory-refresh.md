curl -sS -X POST http://localhost:3000/mcp/tools/call \
  -H 'Content-Type: application/json' \
  -d "$(jq -n \
    --arg q    "${prompt:query|current project status and core documentation}" \
    --arg role "${prompt:role|planner}" \
    --argjson systems '["ltst","cursor","go_cli"]' \
    '{tool_name:"query_memory",arguments:{query:$q,role:$role,systems:$systems}}')" | jq .
