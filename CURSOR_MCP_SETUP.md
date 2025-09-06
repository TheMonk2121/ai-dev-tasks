# Cursor MCP Integration Setup

## 🎯 **For Codex: MCP Server Access Information**

### **MCP Server Details**
- **URL**: `http://localhost:3000`
- **Health Check**: `http://localhost:3000/health`
- **Tools List**: `http://localhost:3000/mcp/tools`
- **Tool Call**: `POST http://localhost:3000/mcp/tools/call`

### **Available MCP Tools**

#### 1. **get_project_context** ✅ Working
```json
{
  "tool_name": "get_project_context",
  "arguments": {}
}
```
**Returns**: Project root, backlog, system overview, memory context

#### 2. **run_precision_eval** ✅ Working
```json
{
  "tool_name": "run_precision_eval",
  "arguments": {
    "config_file": "configs/precision_evidence_filter.env",
    "script": "scripts/run_precision_with_env_file.sh"
  }
}
```
**Returns**: Precision evaluation results

#### 3. **query_memory** ⚠️ Partial
```json
{
  "tool_name": "query_memory",
  "arguments": {
    "query": "current project status",
    "role": "planner"
  }
}
```
**Status**: Import issue with memory orchestrator

## 🔧 **Cursor Configuration**

### **Option 1: Direct MCP Server Connection**
Add to your Cursor settings:

```json
{
  "mcpServers": {
    "ai-dev-tasks": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", "@-",
        "http://localhost:3000/mcp/tools/call"
      ]
    }
  }
}
```

### **Option 2: Test Endpoint (Recommended)**
Run the simple test server:
```bash
python3 simple_mcp_test.py
```

Then use:
- **Test URL**: `http://localhost:8000/quick-test`
- **Tool Test**: `POST http://localhost:8000/test-tool`

## 🧪 **Verification Steps**

### **1. Check MCP Server Status**
```bash
curl http://localhost:3000/health
```

### **2. List Available Tools**
```bash
curl http://localhost:3000/mcp/tools
```

### **3. Test Project Context**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"tool_name": "get_project_context", "arguments": {}}' \
  http://localhost:3000/mcp/tools/call
```

### **4. Run Full Test Suite**
```bash
python3 test_mcp_for_codex.py
```

## 📊 **Current Status**

| Component | Status | Notes |
|-----------|--------|-------|
| MCP Server | ✅ Running | Port 3000, healthy |
| Project Context | ✅ Working | Reads project files |
| Precision Eval | ✅ Working | Executes evaluation scripts |
| Memory Query | ⚠️ Partial | Import issue with orchestrator |
| Database | ✅ Ready | New schema with content_tsv |

## 🚀 **Quick Start for Codex**

1. **Verify server is running**:
   ```bash
   curl http://localhost:3000/health
   ```

2. **Test project context**:
   ```bash
   curl -X POST -H "Content-Type: application/json" \
     -d '{"tool_name": "get_project_context", "arguments": {}}' \
     http://localhost:3000/mcp/tools/call
   ```

3. **Run precision evaluation**:
   ```bash
   curl -X POST -H "Content-Type: application/json" \
     -d '{"tool_name": "run_precision_eval", "arguments": {"config_file": "configs/precision_evidence_filter.env"}}' \
     http://localhost:3000/mcp/tools/call
   ```

## 🔍 **Troubleshooting**

### **If MCP server not responding**:
1. Check if running: `ps aux | grep mcp_memory_server`
2. Restart: `launchctl unload ~/Library/LaunchAgents/com.ai.mcp-memory-server.plist && launchctl load ~/Library/LaunchAgents/com.ai.mcp-memory-server.plist`
3. Check logs: `tail -f .mcp-server.out`

### **If tools not working**:
1. Check server logs: `tail -10 .mcp-server.out`
2. Verify database connection: `python3 scripts/db_readiness_check.py`
3. Test individual tools with curl commands above

## 📝 **For Cursor IDE Integration**

1. **Open Cursor Settings**
2. **Add MCP Configuration**:
   ```json
   {
     "mcpServers": {
       "ai-dev-tasks-memory": {
         "command": "python3",
         "args": ["scripts/mcp_memory_server.py", "--port", "3000"],
         "env": {
           "POSTGRES_DSN": "postgresql://danieljacobs@localhost:5432/ai_agency"
         }
       }
     }
   }
   ```
3. **Restart Cursor**
4. **Check Tools Panel** for MCP tools
5. **Verify in Console** that tools are registered

---

**The MCP integration is ready for Codex to use!** 🎉
