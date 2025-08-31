# 🔄 Memory Rehydration & Context Management

<!-- ANCHOR_KEY: memory-rehydration-context-management -->
<!-- ANCHOR_PRIORITY: 3 -->
<!-- ROLE_PINS: ["researcher", "implementer"] -->

## 🔍 TL;DR

| what this file is | read when | do next |
|---|---|---|
| How to rehydrate memory context and manage AI session continuity | Need to restore project context, start a new session, or troubleshoot memory issues | Use the memory rehydration commands and continue with Phase 2 (Codebase) |

- **what this file is**: Complete guide to memory rehydration and context management for AI sessions.

- **read when**: When you need to restore project context, start a new session, or troubleshoot memory issues.

- **do next**: Use the memory rehydration commands and continue with Phase 2 (Codebase) or Phase 3 (Backlog).

## 🎯 **Current Status**
- **Priority**: 🔥 **HIGH** - Essential for session continuity
- **Phase**: 1 of 4 (Memory System Foundation)
- **Dependencies**: 00 (Memory System Overview), 01 (Memory System Architecture)

## 🧠 **Memory Rehydration System**

### **Core Philosophy**
The memory rehydration system uses **Lean Hybrid with Kill-Switches** approach with **Industry-Grade Observability**:

- **Semantic-first**: Vector search does the heavy lifting
- **Tiny pins**: Only 200 tokens for guardrails (style, conventions, repo map)
- **Kill-switches**: Simple CLI flags to disable features when needed
- **Observability**: Stanford/Berkeley/Anthropic-grade structured tracing and verification

### **Four-Slot Model**
1. **Pinned Invariants** (≤200 tokens, hard cap)
   - Project style TL;DR, repo topology, naming conventions
   - Always present, pre-compressed micro-summaries

2. **Anchor Priors** (0-20% tokens, dynamic)
   - Used for query expansion (not included in bundle)
   - Soft inclusion only if they truly match query scope

3. **Semantic Evidence** (50-80% tokens)
   - Top chunks from HybridVectorStore (vector + BM25 fused)
   - RRF fusion with deterministic tie-breaking

4. **Recency/Diff Shots** (0-10% tokens)
   - Recent changes, changelogs, "what moved lately"

### **Observability Features**
- **Structured Tracing**: Complete trace with cryptographic hashes
- **Echo Verification**: Bundle integrity verification for models
- **Self-Critique**: Anthropic-style reflection checkpoints

## 🔧 **Essential Commands**

### **Memory Rehydration (Choose One)**
```bash
# Standard memory rehydration
./scripts/memory_up.sh

# With custom stability (lower = more diverse results)
./scripts/memory_up.sh -q "current project status" -r planner

# Minimal mode for debugging
./scripts/memory_up.sh -q "memory context" -r researcher
```

### **Role-Specific Memory Rehydration**
```bash
# Planner role - strategic context
./scripts/memory_up.sh -r planner "current project status"

# Coder role - implementation context
./scripts/memory_up.sh -r coder "implement authentication function"

# Researcher role - analysis context
./scripts/memory_up.sh -r researcher "performance analysis"

# Implementer role - system context
./scripts/memory_up.sh -r implementer "database optimization"
```

### **DSPy Role Communication & Memory Access**
```bash
# Set non-SSL connection for Go CLI compatibility
export POSTGRES_DSN="mock://test"

# Access specific DSPy roles for context and insights
python3 scripts/unified_memory_orchestrator.py --systems cursor --role planner "query"
python3 scripts/unified_memory_orchestrator.py --systems cursor --role implementer "query"
python3 scripts/unified_memory_orchestrator.py --systems cursor --role researcher "query"
python3 scripts/unified_memory_orchestrator.py --systems cursor --role coder "query"

# Full memory context with all systems
python3 scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "current project status and core documentation"
```

### **Configuration Options**
```bash
# Stability slider (0.0-1.0, default 0.6)
./scripts/memory_up.sh -q "current project status" -r planner

# Kill-switches for debugging
./scripts/memory_up.sh -q "memory context" -r researcher

# Environment variables
export REHYDRATE_STABILITY=0.6
export REHYDRATE_USE_RRF=1
export REHYDRATE_DEDUPE="file+overlap"
export REHYDRATE_EXPAND_QUERY="auto"
```

## 🎭 **DSPy Role Capabilities**

### **Planner Role**
- **Strategic analysis**: High-level planning and architecture decisions
- **PRD creation**: Product requirements and specifications
- **Roadmap planning**: Long-term project direction
- **Resource allocation**: Strategic resource planning

### **Implementer Role**
- **Technical implementation**: Code and system implementation
- **Workflow design**: Process and workflow optimization
- **System integration**: Component integration and APIs
- **Execution planning**: Detailed implementation planning

### **Researcher Role**
- **Research methodology**: Systematic research approaches
- **Analysis frameworks**: Data analysis and evaluation
- **Evidence-based decision making**: Research-driven insights
- **Technology evaluation**: Framework and tool assessment

### **Coder Role**
- **Code implementation**: Direct code development
- **Debugging**: Problem identification and resolution
- **Optimization**: Performance and code optimization
- **Technical patterns**: Best practices and patterns

## 🔄 **Context Management Workflow**

### **Session Start Workflow**
1. **Rehydrate Memory**: Run `./scripts/memory_up.sh` or DSPy orchestrator
2. **Check Current State**: Review `100_cursor-memory-context.md`
3. **Verify Priorities**: Check `000_core/000_backlog.md`
4. **Understand Architecture**: Review `400_guides/400_03_system-overview-and-architecture.md`
5. **Continue Work**: Resume from where you left off

### **Context Preservation**
- **Cross-session continuity**: Maintain context across development sessions
- **Decision tracking**: Preserve rationale and decisions
- **State persistence**: Save current work state and progress
- **Knowledge retention**: Maintain learned patterns and insights

### **Context Validation**
- **Quality checks**: Ensure context relevance and accuracy
- **Cross-reference validation**: Verify links and references
- **Completeness assessment**: Check for missing context
- **Performance monitoring**: Track context retrieval performance

## 🛠️ **Implementation Differences**

### **Python Implementation (`memory_rehydrator.py`)**
**Primary implementation with full DSPy integration and advanced features.**

**Features:**
- ✅ **Entity Expansion**: Automatic entity detection and related chunk expansion
- ✅ **Self-Critique**: Built-in bundle quality assessment and verification
- ✅ **Structured Tracing**: OpenTelemetry integration for observability
- ✅ **DSPy Integration**: Native integration with DSPy workflows
- ✅ **Full RRF Fusion**: Complete Reciprocal Rank Fusion algorithm
- ✅ **Query Expansion**: Advanced anchor term mining
- ✅ **Comprehensive Deduplication**: File-level + overlap detection

**Use Cases:**
- Production DSPy workflows
- Complex AI reasoning tasks
- Full observability requirements
- Entity-aware context expansion

**Performance:**
- **Startup Time**: ~3-5 seconds (includes DSPy initialization)
- **Memory Usage**: Higher (includes AI framework overhead)
- **Features**: Complete feature set

### **Go Implementation (`memory_rehydration_cli.go`)**
**Lightweight, performance-focused alternative for simple rehydration tasks.**

**Features:**
- ✅ **Fast Startup**: Minimal initialization time
- ✅ **Low Memory**: Lightweight footprint
- ✅ **Basic RRF Fusion**: Simplified fusion algorithm
- ✅ **File Deduplication**: Basic deduplication support
- ✅ **CLI Interface**: Simple command-line interface
- ❌ **Entity Expansion**: Not implemented
- ❌ **Self-Critique**: Not implemented
- ❌ **Structured Tracing**: Basic logging only

**Use Cases:**
- Simple rehydration tasks
- Performance-critical scenarios
- Minimal resource environments
- Basic context retrieval

**Performance:**
- **Startup Time**: <1 second
- **Memory Usage**: Low (minimal overhead)
- **Features**: Core functionality only

## 🔧 **How-To**

### **Working with Memory Rehydration**
1. **Understand the four-slot model** and how context is assembled
2. **Use role-specific commands** for targeted context retrieval
3. **Configure stability settings** for different use cases
4. **Monitor performance** and adjust settings as needed
5. **Validate context quality** and relevance

### **Context Management**
1. **Preserve context** across sessions and interactions
2. **Validate context quality** and completeness
3. **Monitor context performance** and optimization
4. **Handle context failures** with fallback strategies
5. **Integrate context** into AI workflows

### **Troubleshooting Memory Issues**
1. **Check database connectivity** and PostgreSQL status
2. **Verify environment variables** and configuration
3. **Test with minimal queries** to isolate issues
4. **Use kill-switches** to disable problematic features
5. **Check logs** for detailed error information

## 📋 **Checklists**

### **Memory Rehydration Checklist**
- [ ] **Memory system understood** and configured
- [ ] **Role-specific commands** tested and working
- [ ] **Context quality validated** and verified
- [ ] **Performance optimized** and tuned
- [ ] **Fallback strategies** implemented and tested
- [ ] **Monitoring and alerting** configured

### **Context Management Checklist**
- [ ] **Context preservation** mechanisms in place
- [ ] **Cross-session continuity** working properly
- [ ] **Context validation** and quality checks implemented
- [ ] **Performance monitoring** and optimization active
- [ ] **Error handling** and recovery procedures tested
- [ ] **Integration with workflows** verified

### **Troubleshooting Checklist**
- [ ] **Database connectivity** verified and working
- [ ] **Environment variables** properly configured
- [ ] **Kill-switches tested** and functional
- [ ] **Logs reviewed** for error information
- [ ] **Fallback strategies** tested and working
- [ ] **Performance benchmarks** established

## 🔗 **Interfaces**

### **Memory Rehydration**
- **CLI Commands**: `./scripts/memory_up.sh` and DSPy orchestrator
- **Configuration**: Environment variables and CLI flags
- **Monitoring**: Performance metrics and health checks
- **Fallbacks**: Alternative implementations and strategies

### **Context Management**
- **Context Assembly**: Four-slot model and semantic evidence
- **Context Validation**: Quality checks and relevance assessment
- **Context Persistence**: Cross-session storage and retrieval
- **Context Integration**: Workflow and AI system integration

### **DSPy Integration**
- **Role Communication**: Role-specific context and capabilities
- **Memory Orchestrator**: Unified access to all memory systems
- **Context Enhancement**: Role-aware context assembly
- **Performance Optimization**: Caching and efficiency improvements

## 📚 **Examples**

### **Memory Rehydration Example**
```bash
# Get strategic context for planning
./scripts/memory_up.sh -r planner "project roadmap and strategic planning"

# Get implementation context
./scripts/memory_up.sh -r implementer "system architecture and implementation patterns"

# Get coding context
./scripts/memory_up.sh -r coder "coding standards and implementation details"

# Get research context
./scripts/memory_up.sh -r researcher "research findings and analysis patterns"
```

### **DSPy Role Communication Example**
```bash
# Strategic planning with DSPy Planner
python3 scripts/unified_memory_orchestrator.py --systems cursor --role planner "analyze current project status and recommend next priorities"

# Technical implementation with DSPy Implementer
python3 scripts/unified_memory_orchestrator.py --systems cursor --role implementer "design implementation strategy for new feature"

# Research analysis with DSPy Researcher
python3 scripts/unified_memory_orchestrator.py --systems cursor --role researcher "evaluate different AI frameworks for our use case"

# Code development with DSPy Coder
python3 scripts/unified_memory_orchestrator.py --systems cursor --role coder "implement authentication function with best practices"
```

### **Context Management Example**
```markdown
## Context Assembly Process

### 1. Pinned Invariants (200 tokens)
- Project style and conventions
- Repository topology
- Naming conventions
- Core principles

### 2. Anchor Priors (0-20% tokens)
- Query expansion terms
- Related concepts
- Context hints
- Semantic anchors

### 3. Semantic Evidence (50-80% tokens)
- Vector search results
- BM25 text search
- RRF fusion results
- Relevance-ranked content

### 4. Recency/Diff Shots (0-10% tokens)
- Recent changes
- Changelog entries
- Latest updates
- Current status
```

## 🔗 **Related Guides**

- **Memory System Overview**: `400_guides/400_00_memory-system-overview.md`
- **Memory System Architecture**: `400_guides/400_01_memory-system-architecture.md`
- **System Overview**: `400_guides/400_03_system-overview-and-architecture.md`
- **Development Workflow**: `400_guides/400_04_development-workflow-and-standards.md`

## 📚 **References**

- **Memory Context**: `100_memory/100_cursor-memory-context.md`
- **DSPy Development**: `100_memory/104_dspy-development-context.md`
- **Unified Memory Orchestrator**: `scripts/unified_memory_orchestrator.py`
- **Memory Rehydrator**: `scripts/memory_rehydrator.py`

## 📋 **Changelog**

- **2025-01-XX**: Created as part of Phase 1 documentation restructuring
- **2025-01-XX**: Extracted from `100_memory/100_cursor-memory-context.md`
- **2025-01-XX**: Integrated with DSPy role communication patterns
- **2025-01-XX**: Added implementation comparison and troubleshooting

---

*This file provides comprehensive guidance for memory rehydration and context management, ensuring seamless AI session continuity.*
