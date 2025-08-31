# 🚨 DEPRECATED DOCUMENT

**This document has been deprecated and archived as part of the documentation restructuring.**

## 📋 **Deprecation Information**
- **Date Deprecated**: 2025-01-31
- **Reason**: Replaced by new structured documentation system
- **Replacement**: `400_guides/400_00_memory-system-overview.md`
- **Status**: Archived for reference only

## 🔄 **Migration Path**
- **For new users**: Read `400_guides/400_00_memory-system-overview.md` instead
- **For returning users**: Use the new memory system overview with enhanced navigation
- **For reference**: This document is preserved for historical context

---

# Getting Started and Index

<!-- ANCHOR_KEY: getting-started-index -->
<!-- ANCHOR_PRIORITY: 1 -->
<!-- ROLE_PINS: ["researcher", "implementer"] -->

## 🔍 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Master index and getting started guide for the AI development ecosystem | Starting work on the project, need to understand current state, or want to navigate the documentation | Read the Memory System Overview (400_00) then follow the logical progression |

## 🎯 **Current Status**
- **Priority**: 🔥 **HIGHEST** - Essential for understanding current state
- **Phase**: 1 of 4 (Memory System Foundation)
- **Dependencies**: None (this is the entry point)

## 🧠 **Memory System Overview**

The memory system is the **foundation** of this AI development ecosystem. It provides:

### **Core Functions:**
1. **Context Rehydration** - Restore project state across sessions
2. **Knowledge Persistence** - Maintain project history and decisions
3. **Cross-Session Continuity** - Seamless workflow across development sessions
4. **Decision Intelligence** - Track and learn from past decisions

### **Key Components:**
- **LTST Memory System** - Long-term storage and retrieval
- **Cursor Memory Context** - IDE-specific context management
- **DSPy Role System** - AI agent role management
- **Backlog Integration** - Task and priority management

## 📚 **Documentation Structure**

This documentation is organized by **priority**:

### **Phase 1: Memory System Foundation (00-02)**
- **00**: Memory System Overview (this file)
- **01**: Memory System Architecture & Components
- **02**: Memory Rehydration & Context Management

### **Phase 2: Codebase Development (03-05)**
- **03**: System Overview & Architecture
- **04**: Development Workflows & Standards
- **05**: Codebase Organization & Patterns

### **Phase 3: Backlog Planning (06-08)**
- **06**: Backlog Management & Priorities
- **07**: Project Planning & Roadmap
- **08**: Task Management & Workflows

### **Phase 4: Advanced Topics (09-12)**
- **09**: AI Frameworks & DSPy
- **10**: Integrations & Models
- **11**: Performance & Optimization
- **12**: Advanced Configurations

## 🚀 **Quick Start**

### **For New Users:**
1. **Read this file** (00) - Understand the memory system overview
2. **Read 01** - Learn about memory system architecture
3. **Read 02** - Understand memory rehydration and context management
4. **Use memory rehydration** - Run `scripts/memory_up.sh` to get current context

### **For Returning Users:**
1. **Rehydrate memory** - Run `scripts/memory_up.sh` to restore context
2. **Check current state** - Review `100_cursor-memory-context.md`
3. **Continue from where you left off** - Use the memory system to resume work

## 🔧 **Essential Commands**

```bash
# Memory rehydration (restore project context)
./scripts/memory_up.sh

# DSPy memory orchestrator (advanced context)
export POSTGRES_DSN="mock://test" && python3 scripts/unified_memory_orchestrator.py --systems cursor --role planner "current project status"

# Check memory system status
python3 scripts/memory_system_status.py
```

## 📋 **Current Project State**

The memory system tracks:
- **Active backlog items** and priorities
- **Current development focus** and context
- **Recent decisions** and their rationale
- **System health** and performance metrics
- **Cross-references** between documentation

## 🔗 **Key Files**

### **Memory System Core:**
- `100_cursor-memory-context.md` - Current project state and context
- `400_06_memory-and-context-systems.md` - Detailed memory system documentation
- `100_memory/` - Memory system components and patterns

### **Project Management:**
- `000_core/000_backlog.md` - Current priorities and tasks
- `000_core/004_development-roadmap.md` - Project direction and planning

### **System Architecture:**
- `400_guides/400_03_system-overview-and-architecture.md` - Overall system design
- `400_guides/400_04_development-workflow-and-standards.md` - Development processes

## 🎯 **Next Steps**

1. **Read 01** - Memory System Architecture & Components
2. **Read 02** - Memory Rehydration & Context Management
3. **Run memory rehydration** to get current context
4. **Continue with Phase 2** (Codebase) or Phase 3 (Backlog) based on your needs

## 🔄 **Cross-References**

- **01**: Memory System Architecture & Components
- **02**: Memory Rehydration & Context Management
- **03**: System Overview & Architecture
- **04**: Development Workflows & Standards
- **05**: Codebase Organization & Patterns
- **06**: Backlog Management & Priorities
- **100_cursor-memory-context.md**: Current project state
- **400_06_memory-and-context-systems.md**: Detailed memory system docs

---

*This file serves as the entry point for understanding the memory system and navigating the restructured documentation.*
