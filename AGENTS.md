# AI Development Agents

## Project Context

This is the AI Dev Tasks project - a comprehensive AI development ecosystem with:
- Memory systems (LTST, Cursor, Go CLI, Prime)
- RAGChecker evaluation system
- DSPy integration
- PostgreSQL database with conversation storage
- MCP server for tool integration

This project uses a sophisticated multi-agent AI development ecosystem. Follow these role-specific guidelines:

## 🤖 Agent Roles

### **Planner** (Strategic)
- High-level architecture and project planning
- System design and technology decisions
- Cross-component integration strategies
- Memory rehydration and context management

### **Implementer** (Execution)
- Code implementation and integration
- Feature development and deployment
- Database migrations and schema changes
- Performance optimization

### **Researcher** (Analysis)
- Technical investigation and analysis
- Performance evaluation and benchmarking
- Technology research and recommendations
- Documentation and knowledge management

### **Coder** (Development)
- Specific coding tasks and debugging
- Test implementation and maintenance
- Code refactoring and optimization
- Bug fixes and feature implementation

## 🔄 Workflow Patterns

### **Memory-First Development**
Always run memory rehydration before major tasks:
```bash
export POSTGRES_DSN="mock://test" && uv run python scripts/utilities/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "current project status and core documentation"
```

### **Quality Gates**
- Run `make quality-check` before commits
- Ensure all tests pass: `make test-all`
- Verify database health: `make db-health`
- Check linting: `make lint`
- Verify MCP server status: `make mcp-status`

### **Tool Usage**
- Prefer `codebase_search` over `grep` for semantic searches
- Use `todo_write` for multi-step task tracking
- Use `update_memory` for important project decisions
- Always use `uv run python scripts/` for Python execution

## 🎯 Project-Specific Guidelines

### **AI Development Ecosystem**
- Memory systems: LTST, Cursor, Go CLI, Prime
- RAGChecker evaluation system with baseline enforcement
- DSPy integration for neural program synthesis
- PostgreSQL with pgvector for conversation storage
- MCP server for tool integration

### **MCP Memory Server**
- **URL**: http://localhost:3000
- **Health Check**: http://localhost:3000/health
- **MCP Tools**: http://localhost:3000/mcp/tools
- **Management**: Use `make mcp-start`, `make mcp-stop`, `make mcp-restart`
- **Status**: `make mcp-status` to check server health
- **Testing**: `make mcp-test` to verify functionality
- **Logs**: `make mcp-logs` to view server logs
- **Integration**: Fully functional with Cursor and all memory systems

### **Code Quality Standards**
- Type hints required in all Python files
- Maximum function length: 50 lines (100 for complex logic)
- Use black for formatting (120 character line length)
- Document all public functions and classes
- Unit tests required for new features

### **Database Standards**
- Use `common.db_dsn.resolve_dsn` for DSN resolution
- Target pgvector ≥ 0.8 with HNSW indexes
- Use pydantic-settings for typed configuration
- Follow precedence: env vars → profile env → .env.local → defaults

## 🚨 Critical Protocols

### **Execution Protocol**
The `record_chat_history` tool is MANDATORY before any concluding action. This maintains project context and enables memory rehydration across sessions.

### **Code Copying Safety**
Before copying any code, check the criticality guide and sanitize Unicode characters, shebang lines, and deprecated imports.

### **Documentation Governance**
Fold new content into existing 400_ guides using anchors rather than creating new files. Maintain cross-references and update TOCs.

## 📋 Quick Reference

**Essential Commands:**
- `make test-all` - Run full test suite
- `make quality-check` - Complete quality gates
- `make db-health` - Database health check
- `make eval-gold` - Production baseline evaluation
- `make mcp-status` - Check MCP server status
- `make mcp-test` - Test MCP server functionality

**Key Files:**
- `400_guides/` - Project documentation
- `scripts/core/` - Core system components
- `tests/` - Test suite
- `src/` - Source code

**Memory Systems:**
- LTST: Long-term semantic tracking
- Cursor: IDE integration memory
- Go CLI: Command-line interface memory
- Prime: Primary memory orchestrator