# Cursor Role System Alignment Guide

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Essential guide for aligning Cursor's role system with existing memory infrastructure | Starting new session, configuring roles, or troubleshooting role integration | Use the alignment patterns to ensure seamless integration between Cursor roles and memory system |

<!-- ANCHOR_KEY: tldr -->
<!-- ANCHOR_PRIORITY: 5 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher", "coder"] -->

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Role system alignment guide maintained
- **Priority**: 🔥 Critical - Essential for effective AI collaboration and context retrieval
- **Points**: 5 - High importance for user experience and system efficiency
- **Dependencies**: `scripts/unified_memory_orchestrator.py`, `100_memory/100_dspy-role-communication-guide.md`, memory systems
- **Next Steps**: Ensure all Cursor roles are properly aligned with memory infrastructure

## 🚨 **CRITICAL: Role System Alignment is Essential**

**Why This Matters**: Cursor's role system operates as a high-level memory layer that must be seamlessly integrated with our existing memory infrastructure. Without proper alignment, AI agents cannot provide consistent, role-specific guidance or leverage the full power of the memory system.

## 🎭 **Cursor Role System Overview**

### **Role System Architecture**

#### **Multi-File Role System (New)**
```bash
# Cursor's new multi-file role system
.cursorrules                           # Main role configuration
.vscode/settings.json                  # VS Code role settings
role-specific configuration files      # Individual role configurations
```

#### **Single-File Role System (Legacy)**
```bash
# Cursor's legacy single-file role system
.cursorrules                           # All role configurations in one file
```

### **Role System Components**

#### **Core Role Types**
1. **Planner Role** - Strategic analysis, planning, and high-level decision making
2. **Implementer Role** - Technical implementation and workflow design
3. **Researcher Role** - Research methodology and evidence-based analysis
4. **Coder Role** - Code implementation and technical patterns

#### **Role System Features**
- **Context-Aware Responses**: Role-specific context and insights
- **Memory Integration**: Seamless access to memory system
- **Workflow Alignment**: Role-specific workflows and processes
- **Performance Optimization**: Role-specific performance tuning

## 🔗 **Alignment Patterns**

### **1. Memory System Integration**

#### **Unified Memory Orchestrator Integration**
```bash
# Role-specific memory access
python3 scripts/unified_memory_orchestrator.py --systems cursor --role planner "query"
python3 scripts/unified_memory_orchestrator.py --systems cursor --role implementer "query"
python3 scripts/unified_memory_orchestrator.py --systems cursor --role researcher "query"
python3 scripts/unified_memory_orchestrator.py --systems cursor --role coder "query"
```

#### **Memory Context Alignment**
```bash
# Role-specific memory context
export POSTGRES_DSN="mock://test"
python3 scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "current project status"
```

### **2. Role-Specific Context Patterns**

#### **Planner Role Context**
```bash
# Strategic planning context
python3 scripts/unified_memory_orchestrator.py --systems cursor --role planner "development priorities and roadmap"
python3 scripts/unified_memory_orchestrator.py --systems cursor --role planner "PRD creation and task generation"
```

#### **Implementer Role Context**
```bash
# Implementation context
python3 scripts/unified_memory_orchestrator.py --systems cursor --role implementer "development workflow and technical integration"
python3 scripts/unified_memory_orchestrator.py --systems cursor --role implementer "system architecture and component integration"
```

#### **Researcher Role Context**
```bash
# Research context
python3 scripts/unified_memory_orchestrator.py --systems cursor --role researcher "research methodology and evidence-based analysis"
python3 scripts/unified_memory_orchestrator.py --systems cursor --role researcher "memory system optimization and performance analysis"
```

#### **Coder Role Context**
```bash
# Technical implementation context
python3 scripts/unified_memory_orchestrator.py --systems cursor --role coder "technical implementation patterns and code components"
python3 scripts/unified_memory_orchestrator.py --systems cursor --role coder "DSPy RAG system architecture and implementation"
```

### **3. Configuration Alignment**

#### **Cursor Rules Integration**
```bash
# .cursorrules configuration for role alignment
export POSTGRES_DSN="mock://test"
veetopython3 scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "current project status and core documentation"
```

#### **VS Code Settings Integration**
```json
{
  "cursor.role": "planner",
  "cursor.memorySystem": "unified",
  "cursor.contextRetrieval": "automatic"
}
```

## 🔧 **Implementation Strategies**

### **1. Role System Configuration**

#### **Multi-File Role System Setup**
```bash
# Create role-specific configuration files
.cursorrules-planner
.cursorrules-implementer
.cursorrules-researcher
.cursorrules-coder
```

#### **Role Switching Mechanism**
```bash
# Role switching commands
python3 scripts/unified_memory_orchestrator.py --switch-role planner
python3 scripts/unified_memory_orchestrator.py --switch-role implementer
python3 scripts/unified_memory_orchestrator.py --switch-role researcher
python3 scripts/unified_memory_orchestrator.py --switch-role coder
```

### **2. Memory Context Alignment**

#### **Role-Specific Memory Context**
```python
def get_role_specific_context(role: str, query: str) -> Dict[str, Any]:
    """Get role-specific memory context."""
    if role == "planner":
        return get_planner_context(query)
    elif role == "implementer":
        return get_implementer_context(query)
    elif role == "researcher":
        return get_researcher_context(query)
    elif role == "coder":
        return get_coder_context(query)
    else:
        return get_default_context(query)
```

#### **Context Integration Patterns**
```python
def integrate_role_context(role: str, base_context: Dict[str, Any]) -> Dict[str, Any]:
    """Integrate role-specific context with base memory context."""
    role_context = get_role_specific_context(role)
    return merge_contexts(base_context, role_context)
```

### **3. Performance Optimization**

#### **Role-Specific Performance Tuning**
```python
def optimize_for_role(role: str) -> Dict[str, Any]:
    """Optimize memory system performance for specific role."""
    optimizations = {
        "planner": {"context_depth": "strategic", "response_style": "high_level"},
        "implementer": {"context_depth": "technical", "response_style": "detailed"},
        "researcher": {"context_depth": "analytical", "response_style": "evidence_based"},
        "coder": {"context_depth": "implementation", "response_style": "code_focused"}
    }
    return optimizations.get(role, optimizations["planner"])
```

## 📊 **Alignment Status Tracking**

### **Integration Status**
- ✅ **Memory System Integration**: Unified Memory Orchestrator integration complete
- ✅ **Role-Specific Context**: Role-specific context patterns implemented
- ✅ **Configuration Alignment**: Cursor rules and VS Code settings aligned
- 🔄 **Multi-File Role System**: New multi-file role system integration (in progress)
- 🔄 **Performance Optimization**: Role-specific performance tuning (in progress)
- 🔄 **Advanced Features**: Advanced role system features (in progress)

### **Performance Metrics**
- **Role Context Accuracy**: Target 95% accuracy
- **Memory Access Speed**: Target 40% improvement
- **Role Switching Speed**: Target <2 seconds
- **Context Relevance**: Target 90% relevance

## 🛠️ **Implementation Patterns**

### **1. Role System Discovery**
```python
def discover_role_system():
    """Discover and catalog role system components."""
    roles = {
        "planner": discover_planner_role(),
        "implementer": discover_implementer_role(),
        "researcher": discover_researcher_role(),
        "coder": discover_coder_role()
    }
    return roles
```

### **2. Role Context Integration**
```python
def integrate_role_context(role_system):
    """Integrate role system with memory context."""
    for role, components in role_system.items():
        integrate_role_with_memory(role, components)
```

### **3. Role Performance Optimization**
```python
def optimize_role_performance(role):
    """Optimize performance for specific role."""
    optimizations = get_role_optimizations(role)
    apply_role_optimizations(role, optimizations)
```

## 🔍 **Troubleshooting Role Alignment**

### **Common Issues**
1. **Role Context Missing**: Run role-specific memory context retrieval
2. **Role Switching Issues**: Verify role system configuration
3. **Memory Integration Issues**: Check Unified Memory Orchestrator
4. **Performance Issues**: Run role-specific performance optimization

### **Debugging Commands**
```bash
# Debug role system alignment
python3 scripts/unified_memory_orchestrator.py --systems cursor --role planner "debug role system alignment"

# Check role-specific context
python3 scripts/unified_memory_orchestrator.py --systems cursor --role coder "check technical context integration"

# Validate role configuration
python3 scripts/validate_config.py --role-system

# Monitor role performance
python3 scripts/performance_optimization.py --role-specific
```

## 📈 **Success Metrics & Monitoring**

### **Alignment Success Criteria**
- ✅ Role system integrated with memory infrastructure
- ✅ Role-specific context accessible via memory system
- ✅ Configuration alignment between Cursor and memory system
- 🔄 Multi-file role system integration complete
- 🔄 Performance optimization complete
- 🔄 Advanced role system features complete

### **Performance Monitoring**
```bash
# Monitor role system performance
python3 scripts/monitoring_dashboard.py --role-system

# Track role-specific performance
python3 scripts/ragus_evaluation.py --role-specific

# Monitor role switching performance
python3 scripts/system_health_check.py --role-alignment
```

## 🔗 **Cross-References**

- See `100_memory/100_cursor-memory-context.md` for core memory context
- See `100_memory/100_dspy-role-communication-guide.md` for DSPy role communication
- See `100_memory/100_technical-artifacts-integration-guide.md` for technical artifacts integration
- See `scripts/unified_memory_orchestrator.py` for memory orchestration
- See `.cursorrules` for Cursor role configuration
- See `400_guides/400_06_memory-and-context-systems.md` for memory system guide

---

*This guide ensures seamless alignment between Cursor's role system and our existing memory infrastructure for optimal AI collaboration and context retrieval.*
