# Product Requirements Document: Fix MCP Memory Server

> ⚠️**Auto-Skip Note**> This PRD was generated because either `points≥5` or `score_total<3.0`.
> Remove this banner if you manually forced PRD creation.

## 0. Project Context & Implementation Guide

### Current Tech Stack
- **Backend**: Python 3.12, FastAPI, PostgreSQL, pgvector
- **MCP Integration**: Custom MCP server for memory rehydration
- **Infrastructure**: macOS LaunchAgent, Python virtual environments
- **Development**: Poetry, pytest, pre-commit hooks, Ruff

### Repository Layout
```
ai-dev-tasks/
├── scripts/                    # Utility scripts and automation
│   ├── mcp_memory_server.py   # MCP server implementation
│   ├── memory_up.sh           # Memory rehydration script
│   └── unified_memory_orchestrator.py
├── dspy-rag-system/           # DSPy RAG system
│   └── src/utils/
│       └── memory_rehydrator.py
├── Library/LaunchAgents/      # macOS LaunchAgent configuration
└── artifacts/                 # Generated artifacts and PRDs
```

### Development Patterns
- **MCP Servers**: `scripts/` - MCP protocol implementations
- **Memory Systems**: `dspy-rag-system/src/utils/` - Memory rehydration and context management
- **Automation**: `scripts/` - Shell scripts and Python automation
- **Configuration**: `Library/LaunchAgents/` - macOS service configuration

### Local Development
```bash
# Setup virtual environment
python3 -m venv venv
source .venv/bin/activate

# Install dependencies
pip install -r dspy-rag-system/requirements.txt

# Test MCP server
python3 scripts/mcp_memory_server.py --test

# Check LaunchAgent status
launchctl list | grep mcp
```

### Common Tasks
- **Fix port conflicts**: Check for existing processes, kill if needed, update port configuration
- **Update Python version**: Ensure LaunchAgent uses Python 3.12, not 3.9
- **Restore missing functions**: Add build_hydration_bundle function to memory rehydrator
- **Fix LaunchAgent loop**: Update plist configuration to prevent restart loops

## 1. Problem Statement

### What's broken?
The MCP memory server is completely non-functional due to multiple critical issues:

1. **Port Conflict**: `OSError: [Errno 48] Address already in use` - The MCP server cannot start because port 8080 (or configured port) is already occupied
2. **Missing Function**: `build_hydration_bundle` function doesn't exist in the memory rehydrator module
3. **Python Version Mismatch**: LaunchAgent is using Python 3.9 instead of the project's Python 3.12
4. **LaunchAgent Loop**: The system keeps trying to restart a broken server, creating a restart loop

### Why does it matter?
The MCP memory server is a critical component for:
- **Memory Rehydration**: Provides role-based context retrieval for AI agents
- **Cursor Integration**: Enables Cursor to access project memory and context
- **Development Workflow**: Essential for the AI development ecosystem's memory system
- **Tool Availability**: Without it, MCP tools are not available to AI agents

### What's the opportunity?
Fixing the MCP memory server will:
- **Restore MCP Tool Access**: Enable web search and other MCP tools for AI agents
- **Improve Development Experience**: Provide seamless memory rehydration in Cursor
- **Enhance AI Capabilities**: Give AI agents access to comprehensive project context
- **Stabilize Infrastructure**: Prevent LaunchAgent restart loops and system instability

## 2. Solution Overview

### What are we building?
A comprehensive fix for the MCP memory server that addresses all critical issues and restores full functionality.

### How does it work?
1. **Port Management**: Implement proper port detection, conflict resolution, and fallback mechanisms
2. **Function Restoration**: Add the missing `build_hydration_bundle` function to the memory rehydrator
3. **Python Version Fix**: Update LaunchAgent configuration to use Python 3.12
4. **LaunchAgent Stabilization**: Fix the restart loop and add proper error handling

### What are the key features?
- **Robust Port Management**: Automatic port detection, conflict resolution, and fallback
- **Complete Function Set**: All required memory rehydration functions available
- **Python 3.12 Compatibility**: Full compatibility with project's Python version
- **Stable LaunchAgent**: No restart loops, proper error handling and logging
- **Health Monitoring**: Server health checks and status reporting

## 3. Acceptance Criteria

### How do we know it's done?
- [ ] MCP memory server starts successfully without port conflicts
- [ ] `build_hydration_bundle` function exists and works correctly
- [ ] LaunchAgent uses Python 3.12 instead of 3.9
- [ ] LaunchAgent stops restarting the broken server
- [ ] MCP tools are available to AI agents (web search, etc.)
- [ ] Memory rehydration works in Cursor chat

### What does success look like?
- **Server Stability**: MCP server runs continuously without crashes or restart loops
- **Tool Availability**: All MCP tools (web search, memory rehydration) are accessible
- **Performance**: Memory rehydration completes in <5 seconds
- **Integration**: Seamless integration with Cursor and AI development workflow

### What are the quality gates?
- [ ] All existing tests pass with the fixed MCP server
- [ ] No port conflicts or address-in-use errors
- [ ] LaunchAgent configuration is correct and stable
- [ ] Memory rehydration provides accurate context
- [ ] MCP tools respond within acceptable time limits

## 4. Technical Approach

### What technology?
- **MCP Protocol**: Model Context Protocol for tool integration
- **FastAPI**: Web framework for the MCP server
- **Python 3.12**: Target Python version for compatibility
- **macOS LaunchAgent**: Service management for automatic startup
- **PostgreSQL**: Database for memory storage and retrieval

### How does it integrate?
- **Cursor Integration**: MCP server provides tools to Cursor AI
- **Memory System**: Integrates with existing LTST memory system
- **DSPy RAG**: Connects to DSPy RAG system for document retrieval
- **LaunchAgent**: Automatic startup and management via macOS services

### What are the constraints?
- **Port Availability**: Must find available port or handle conflicts gracefully
- **Python Version**: Must use Python 3.12 for compatibility
- **macOS Specific**: LaunchAgent configuration is macOS-specific
- **Memory Limits**: Must work within available system memory
- **Network Access**: Requires network access for MCP protocol communication

## 5. Risks and Mitigation

### What could go wrong?
- **Port Conflicts Persist**: Other services might be using the same port range
- **Python Version Issues**: LaunchAgent might still use wrong Python version
- **Function Dependencies**: `build_hydration_bundle` might have missing dependencies
- **LaunchAgent Loop**: Configuration might still cause restart loops
- **Memory System Integration**: Fixed server might not integrate with existing memory system

### How do we handle it?
- **Port Management**: Implement port scanning and automatic fallback to available ports
- **Python Path**: Use absolute paths in LaunchAgent configuration to ensure correct Python version
- **Dependency Check**: Verify all dependencies for `build_hydration_bundle` function
- **LaunchAgent Testing**: Test LaunchAgent configuration thoroughly before deployment
- **Integration Testing**: Comprehensive testing of memory system integration

### What are the unknowns?
- **Other Port Usage**: What other services might be using the target ports
- **LaunchAgent Behavior**: Exact behavior of LaunchAgent with different configurations
- **Memory System Dependencies**: Full dependency tree for memory rehydration functions
- **Performance Impact**: How the fixed server will perform under load

## 6. Testing Strategy

### What needs testing?
- **Port Management**: Port conflict detection and resolution
- **Function Availability**: `build_hydration_bundle` function functionality
- **LaunchAgent Configuration**: Proper startup and stability
- **MCP Protocol**: Tool availability and response times
- **Memory Integration**: Integration with existing memory systems

### How do we test it?
- **Unit Tests**: Test individual components (port management, function calls)
- **Integration Tests**: Test MCP server with Cursor and memory systems
- **LaunchAgent Tests**: Test LaunchAgent configuration and startup
- **Performance Tests**: Test memory rehydration performance and response times
- **End-to-End Tests**: Test complete workflow from Cursor to memory retrieval

### What's the coverage target?
- **Code Coverage**: >90% for new and modified code
- **Integration Coverage**: All MCP tools and memory system integration points
- **LaunchAgent Coverage**: All LaunchAgent configuration scenarios
- **Performance Coverage**: Response time and memory usage under various loads

## 7. Implementation Plan

### What are the phases?
1. **Phase 1: Port Conflict Resolution** (2 hours)
   - Implement port detection and conflict resolution
   - Add fallback port mechanisms
   - Test port management functionality

2. **Phase 2: Function Restoration** (2 hours)
   - Add `build_hydration_bundle` function to memory rehydrator
   - Verify function dependencies and imports
   - Test function functionality

3. **Phase 3: Python Version Fix** (1 hour)
   - Update LaunchAgent configuration to use Python 3.12
   - Test LaunchAgent startup with correct Python version
   - Verify Python path configuration

4. **Phase 4: LaunchAgent Stabilization** (2 hours)
   - Fix LaunchAgent restart loop
   - Add proper error handling and logging
   - Test LaunchAgent stability

5. **Phase 5: Integration and Testing** (1 hour)
   - Test complete MCP server functionality
   - Verify integration with Cursor and memory systems
   - Performance testing and optimization

### What are the dependencies?
- **Port Management**: No dependencies, can be implemented first
- **Function Restoration**: Depends on understanding memory rehydrator structure
- **Python Version Fix**: Depends on LaunchAgent configuration access
- **LaunchAgent Stabilization**: Depends on Python version fix
- **Integration Testing**: Depends on all previous phases

### What's the timeline?
- **Total Estimated Time**: 8 hours
- **Phase 1-2**: 4 hours (port management and function restoration)
- **Phase 3-4**: 3 hours (Python version and LaunchAgent fixes)
- **Phase 5**: 1 hour (integration testing and optimization)

---

## **Performance Metrics Summary**

> 📊 **Workflow Performance Data**
> - **Workflow ID**: `B-1033-MCP-Memory-Server-Fix`
> - **Total Duration**: `8 hours estimated`
> - **Performance Score**: `8.5/10`
> - **Success**: `Pending`
> - **Error Count**: `0`

> 🔍 **Performance Analysis**
> - **Bottlenecks**: `Port conflicts, Python version mismatch`
> - **Warnings**: `LaunchAgent restart loop`
> - **Recommendations**: `Implement robust port management, fix Python version`

> 📈 **Collection Points**
> - **Workflow Start**: `Port conflict detection`
> - **Section Analysis**: `Function restoration requirements`
> - **Template Processing**: `MCP server configuration`
> - **Context Integration**: `Memory system integration`
> - **Validation Check**: `LaunchAgent stability`
> - **Workflow Complete**: `Integration testing`
