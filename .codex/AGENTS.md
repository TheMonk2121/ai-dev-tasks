# Codex Memory Discipline

After you deliver your final answer to the user, immediately call the MCP tool `record_chat_history` with a JSON payload of the form:

```
{
  "thread_id": "<stable conversation id>",
  "user_input": "<user's latest message>",
  "system_output": "<your final answer>",
  "llm_name": "<model identifier>",
  "file_operations": "<files/tools touched or 'none'>"
}
```

Use the same conversation identifiers throughout the session so downstream systems can correlate turns. If you edited or inspected files, list them in `file_operations`; otherwise send "none".
