# 🧠 Memory System Overview & Getting Started

<!-- ANCHOR_KEY: memory-system-overview -->
<!-- ANCHOR_PRIORITY: 1 -->
<!-- ROLE_PINS: ["researcher", "implementer"] -->

## 🔍 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Master overview of the memory system and entry point for understanding the project's current state | Starting work on the project, need to understand current state, or want to navigate the documentation | Read 01 (Memory System Architecture) then 02 (Memory Rehydration) |

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
- **Cursor Memory Context** - IDE-specific context managemen
- **DSPy Role System** - AI agent role managemen
- **Backlog Integration** - Task and priority managemen

## 📚 **Documentation Structure**

This documentation is organized by **priority**:

### **Phase 1: Memory System Foundation (00-02)**
- **00**: Memory System Overview (this file)
- **01**: Memory System Architecture & Components
- **02**: Memory Rehydration & Context Managemen

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

## 📚 **Complete Guide Navigation**

### **Core Guides (00–12)**
- `400_guides/400_00_memory-system-overview.md` - This file (entry point)
- `400_guides/400_01_memory-system-architecture.md` - Memory system architecture
- `400_guides/400_02_memory-rehydration-context-management.md` - Context management
- `400_guides/400_03_system-overview-and-architecture.md` - System architecture
- `400_guides/400_04_development-workflow-and-standards.md` - Development workflows
- `400_guides/400_05_codebase-organization-patterns.md` - Code organization
- `400_guides/400_06_backlog-management-priorities.md` - Backlog management
- `400_guides/400_07_project-planning-roadmap.md` - Project planning
- `400_guides/400_08_task-management-workflows.md` - Task management
- `400_guides/400_09_ai-frameworks-dspy.md` - AI frameworks
- `400_guides/400_10_integrations-models.md` - Integrations & models
- `400_guides/400_11_performance-optimization.md` - Performance optimization
- `400_guides/400_12_advanced-configurations.md` - Advanced configurations

### **Evaluation Systems**
- **Code-as-SSOT System**: `evals_300/` - Standardized evaluation system with auto-generated documentation
- **Generated Docs**: `evals_300/_generated/300_core.md` - Human-readable evaluation documentation
- **Legacy SOP**: `000_core/000_evaluation-system-entry-point.md`
- **Legacy Runner**: `scripts/ragchecker_official_evaluation.py`

### **Agent Entry Points**
- **Discovery ➜ Execution Path**: `000_core/000_agent-entry-point.md`
- **Memory Rehydration**: `scripts/shell/utilities/memory_up.sh`
- **Unified Memory Orchestrator**: `scripts/unified_memory_orchestrator.py`

## 🚀 **Quick Start**

### **For New Users:**
1. **Read this file** (00) - Understand the memory system overview
2. **Read 01** - Learn about memory system architecture
3. **Read 02** - Understand memory rehydration and context managemen
4. **Use memory rehydration** - Run `./scripts/shell/utilities/memory_up.sh` to get current context

### **For Returning Users:**
1. **Rehydrate memory** - Run `./scripts/shell/utilities/memory_up.sh` to restore context
2. **Check current state** - Review `100_cursor-memory-context.md`
3. **Continue from where you left off** - Use the memory system to resume work

## 🔧 **Essential Commands**

```bash
# Memory rehydration (restore project context)
./scripts/shell/utilities/memory_up.sh

# DSPy memory orchestrator (advanced context)
export POSTGRES_DSN="mock://test" && uv run python scripts/unified_memory_orchestrator.py --systems cursor --role planner "current project status"

# Check memory system health
uv run python 300_evals/scripts/evaluation/memory_healthcheck.py

# System health check
uv run python 300_evals/scripts/evaluation/system_health_check.py
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

## 🧠 **Memory & Context Systems**

### **🚨 CRITICAL: Memory & Context Systems are Essential**

**Why This Matters**: Memory and context systems provide the foundation for AI agents to understand project state, maintain continuity across sessions, and make informed decisions. Without proper memory integration, AI agents cannot provide accurate guidance or understand the current development context.

### **Memory System Architecture**

#### **Core Memory Components**
```python
class MemorySystemArchitecture:
    """Core memory system architecture components."""

    def __init__(self):
        self.memory_layers = {
            "ltst": "Long-Term Short-Term memory system with vector search",
            "cursor": "Cursor IDE memory context and session continuity",
            "go_cli": "Go CLI memory rehydration for system operations",
            "prime": "Prime Cursor integration for complex analysis",
            "unified_orchestrator": "Unified memory orchestrator coordinating all systems"
        }
        self.context_stores = {}
        self.memory_orchestrator = None

    def initialize_memory_system(self):
        """Initialize the complete memory system."""

        # Initialize LTST memory system
        self.context_stores["ltst"] = LTSTMemorySystem()

        # Initialize Cursor memory context
        self.context_stores["cursor"] = CursorMemoryContext()

        # Initialize Go CLI memory
        self.context_stores["go_cli"] = GoCLIMemory()

        # Initialize Prime Cursor
        self.context_stores["prime"] = PrimeCursorMemory()

        # Initialize unified orchestrator
        self.memory_orchestrator = UnifiedMemoryOrchestrator(self.context_stores)

    def get_memory_context(self, query: str, role: str = "planner") -> dict:
        """Get memory context for a specific query and role."""

        return self.memory_orchestrator.get_context(query, role)
```

#### **Memory System Integration Points**
- **Memory Rehydration**: Automatic context restoration across sessions
- **Context Building**: Role-aware context construction for different AI roles
- **Memory Persistence**: Long-term storage of project decisions and context
- **Cross-Session Continuity**: Seamless workflow across development sessions

### **Context Management Patterns**

#### **Context Flow Pipeline**
```python
class ContextFlowPipeline:
    """Manages context flow through the memory system."""

    def __init__(self):
        self.context_stages = [
            "memory_rehydration",
            "context_building",
            "role_awareness",
            "context_validation",
            "context_delivery"
        ]

    async def process_context_flow(self, query: str, role: str) -> dict:
        """Process context through the complete flow pipeline."""

        context_data = {}

        for stage in self.context_stages:
            if stage == "memory_rehydration":
                context_data[stage] = await self._rehydrate_memory(query)
            elif stage == "context_building":
                context_data[stage] = await self._build_context(query, context_data)
            elif stage == "role_awareness":
                context_data[stage] = await self._apply_role_awareness(role, context_data)
            elif stage == "context_validation":
                context_data[stage] = await self._validate_context(context_data)
            elif stage == "context_delivery":
                context_data[stage] = await self._deliver_context(context_data)

        return context_data
```

#### **Context Priority System**
- **High Priority (0-10)**: Core memory context, system overview, backlog
- **Medium Priority (15-20)**: Important guides, code quality, security
- **Low Priority (25-30)**: Implementation guides, deployment, testing

### **Memory System Commands**

#### **Core Memory Operations**
```bash
# Memory rehydration (restore project context)
./scripts/shell/utilities/memory_up.sh

# DSPy memory orchestrator (advanced context)
export POSTGRES_DSN="mock://test" && uv run python scripts/unified_memory_orchestrator.py --systems cursor --role planner "current project status"

# Check memory system health
uv run python 300_evals/scripts/evaluation/memory_healthcheck.py

# System health check
uv run python 300_evals/scripts/evaluation/system_health_check.py
```

#### **Role-Specific Memory Access**
```bash
# Strategic planning context
./scripts/shell/utilities/memory_up.sh -r planner "strategic analysis context"

# Technical implementation context
./scripts/shell/utilities/memory_up.sh -r implementer "technical implementation context"

# Research methodology context
./scripts/shell/utilities/memory_up.sh -r researcher "research methodology context"

# Code implementation context
./scripts/shell/utilities/memory_up.sh -r coder "code implementation context"
```

### **Memory System Health Monitoring**

#### **Health Check Commands**
```bash
# Check memory system health
uv run python 300_evals/scripts/evaluation/memory_healthcheck.py

# System health check
uv run python 300_evals/scripts/evaluation/system_health_check.py

# Monitor system performance
uv run python scripts/monitoring/system_monitor.py

# Comprehensive system monitoring
uv run python scripts/monitoring/comprehensive_system_monitor.py
```

#### **Memory Quality Gates**
- **Context Integrity**: All memory context must be valid and accessible
- **Performance**: Memory operations must complete within acceptable time limits
- **Coverage**: Memory system must cover all critical project information
- **Freshness**: Memory context must be updated within acceptable timeframes

### **Project Management:**
- `000_core/000_backlog.md` - Current priorities and tasks
- `000_core/004_development-roadmap.md` - Project direction and planning

### **System Architecture:**
- `400_guides/400_03_system-overview-and-architecture.md` - Overall system design
- `400_guides/400_04_development-workflow-and-standards.md` - Development processes

## 🎯 **Next Steps**

1. **Read 01** - Memory System Architecture & Components
2. **Read 02** - Memory Rehydration & Context Managemen
3. **Run memory rehydration** to get current context
4. **Continue with Phase 2** (Codebase) or Phase 3 (Backlog) based on your needs

## 📚 **Core Terminology Glossary**

### **Memory System Terms**
- **Memory Rehydration**: Process of restoring project context and state across development sessions
- **LTST Memory System**: Long-term storage and retrieval system for project knowledge
- **Cursor Memory Context**: IDE-specific context management for Cursor AI
- **Context Bundle**: Collection of project state, decisions, and knowledge for session continuity
- **Anchor Keys**: Unique identifiers for documentation sections and concepts
- **Role Pins**: Metadata indicating which AI roles are most relevant to specific contain

### **DSPy & AI Framework Terms**
- **DSPy**: Declarative Self-improving Python framework for programming with language models
- **RAG Pipeline**: Retrieval-Augmented Generation pipeline for context-aware AI responses
- **Teleprompter Optimization**: DSPy optimization technique for improving AI model performance
- **Few-Shot Scaffolding**: Technique for providing AI models with examples to improve responses
- **Governance Aids**: Tools and frameworks for ensuring AI system safety and compliance
- **Signature Validation**: DSPy mechanism for ensuring type safety and runtime correctness

### **Development Workflow Terms**
- **Backlog Item**: Individual task or feature with priority scoring and dependencies
- **Sprint Planning**: Time-boxed development planning with capacity and goal setting
- **Quality Gates**: Automated checks and validations for code quality and system health
- **Context Preservation**: Maintaining project state and knowledge across development phases
- **Auto-Advance Workflow**: Automated progression through development stages

### **System Architecture Terms**
- **Vector-Based System Mapping**: Using embeddings to map relationships between system components
- **Hybrid Memory System**: Combination of different memory storage and retrieval mechanisms
- **Entity Expansion**: Process of enriching context with related entities and relationships
- **Multi-Hop Dependency Reasoning**: Analyzing dependencies across multiple system layers
- **Decision Intelligence**: AI-powered analysis of past decisions and their outcomes

### **Performance & Optimization Terms**
- **Multi-Level Caching**: Hierarchical caching strategy for different types of data
- **APM Monitoring**: Application Performance Monitoring for system health tracking
- **Resource Optimization**: CPU, memory, and network optimization strategies
- **Database Performance Tuning**: Optimization of database queries and schema design
- **AI Model Performance**: Monitoring and optimization of AI model inference and training

## 🔄 **Cross-References**

- **01**: Memory System Architecture & Components
- **02**: Memory Rehydration & Context Managemen
- **03**: System Overview & Architecture
- **04**: Development Workflows & Standards
- **05**: Codebase Organization & Patterns
- **06**: Backlog Management & Priorities
- **100_cursor-memory-context.md**: Current project state
- **400_06_memory-and-context-systems.md**: Detailed memory system docs

## 🔄 **Memory Operations & Workflows**

### **🚨 CRITICAL: Memory Operations & Workflows are Essential**

**Why This Matters**: Memory operations and workflows provide the systematic processes for managing memory system operations, ensuring data consistency, and maintaining system performance. Without proper operations management, memory systems become unreliable, inefficient, and difficult to maintain.

### **Memory Operations Framework**

#### **Memory Lifecycle Management**
```python
class MemoryLifecycleManager:
    """Manages the complete memory lifecycle from creation to archival."""

    def __init__(self):
        self.lifecycle_stages = {
            "creation": "Memory item creation and initialization",
            "active": "Active memory usage and access",
            "maintenance": "Memory maintenance and optimization",
            "archival": "Memory archival and cleanup"
        }
        self.lifecycle_policies = {}

    def manage_memory_lifecycle(self, memory_item: dict) -> dict:
        """Manage the complete lifecycle of a memory item."""

        # Validate memory item
        if not self._validate_memory_item(memory_item):
            raise ValueError("Invalid memory item")

        # Create memory item
        creation_result = self._create_memory_item(memory_item)

        # Activate memory item
        activation_result = self._activate_memory_item(creation_result)

        # Monitor memory item
        monitoring_result = self._monitor_memory_item(activation_result)

        return {
            "lifecycle_managed": True,
            "creation_result": creation_result,
            "activation_result": activation_result,
            "monitoring_result": monitoring_resul
        }

    def _validate_memory_item(self, memory_item: dict) -> bool:
        """Validate memory item specification."""

        required_fields = ["content", "metadata", "type", "priority"]

        for field in required_fields:
            if field not in memory_item:
                return False

        return True

    def _create_memory_item(self, memory_item: dict) -> dict:
        """Create a new memory item."""

        # Implementation for memory item creation
        return {
            "id": self._generate_memory_id(),
            "content": memory_item["content"],
            "metadata": memory_item["metadata"],
            "type": memory_item["type"],
            "priority": memory_item["priority"],
            "created_at": time.time(),
            "status": "created"
        }
```

#### **Memory Workflow Orchestration**
```python
class MemoryWorkflowOrchestrator:
    """Orchestrates memory system workflows and operations."""

    def __init__(self):
        self.workflow_types = {
            "memory_retrieval": "Memory retrieval and search workflows",
            "memory_storage": "Memory storage and organization workflows",
            "memory_optimization": "Memory optimization and cleanup workflows",
            "memory_synchronization": "Memory synchronization and consistency workflows"
        }
        self.active_workflows = {}

    def orchestrate_workflow(self, workflow_type: str, workflow_config: dict) -> dict:
        """Orchestrate a specific memory workflow."""

        if workflow_type not in self.workflow_types:
            raise ValueError(f"Unknown workflow type: {workflow_type}")

        # Validate workflow configuration
        if not self._validate_workflow_config(workflow_config):
            raise ValueError("Invalid workflow configuration")

        # Create workflow instance
        workflow_instance = self._create_workflow_instance(workflow_type, workflow_config)

        # Execute workflow
        execution_result = self._execute_workflow(workflow_instance)

        # Monitor workflow progress
        monitoring_result = self._monitor_workflow(workflow_instance)

        return {
            "workflow_orchestrated": True,
            "workflow_type": workflow_type,
            "workflow_instance": workflow_instance,
            "execution_result": execution_result,
            "monitoring_result": monitoring_resul
        }
```

### **Memory Operations Commands**

#### **Lifecycle Management Commands**
```bash
# Memory system health check
uv run python 300_evals/scripts/evaluation/memory_healthcheck.py

# System health monitoring
uv run python scripts/monitoring/system_monitor.py

# Memory system maintenance
uv run python scripts/maintenance/maintenance.py

# Comprehensive system monitoring
uv run python scripts/monitoring/comprehensive_system_monitor.py
```

#### **Workflow Orchestration Commands**
```bash
# Unified memory orchestrator
uv run python scripts/unified_memory_orchestrator.py --systems ltst cursor --role planner "query"

# Memory system integration
uv run python scripts/utilities/mcp_memory_server.py

# Agent memory training
uv run python scripts/utilities/agent_memory_trainer.py

# Memory system verification
uv run python scripts/utilities/run_memory_verification.py
```

### **Memory Operations Quality Gates**

#### **Lifecycle Management Standards**
- **Creation Quality**: All memory items must be properly created and validated
- **Activation Reliability**: Memory activation must be reliable and consistent
- **Monitoring Coverage**: Comprehensive monitoring must be in place for all memory items
- **Maintenance Efficiency**: Memory maintenance must be efficient and non-disruptive

#### **Workflow Requirements**
- **Workflow Validation**: All workflows must be validated before execution
- **Execution Monitoring**: Workflow execution must be monitored and controlled
- **Error Handling**: Proper error handling and recovery mechanisms must be in place
- **Performance Optimization**: Workflows must be optimized for performance and efficiency

## 🧪 **Evaluation System Structure**

The evaluation system (`300_evals/`) has been streamlined for **stateless agents** with a simple, clear structure:

### **📁 Streamlined Directory Structure**
```
300_evals/
├── test_results/           # All test outputs, baselines, and artifacts
├── stable_build/          # Production-ready evaluation components
│   ├── modules/           # Evaluation modules and tools
│   ├── harnesses/         # Test harnesses and compiled configs
│   └── config/            # Active configuration files
└── experiments/           # Experimental work
    ├── active/            # Current experiments and research
    └── legacy/            # Archived experiments (gitignored, excluded from DB)
```

### **🎯 Key Design Principles**
- **Simple & Clear**: 3 main folders instead of 15+ nested directories
- **Stateless-Friendly**: Easy for agents to understand and navigate
- **Consolidated**: All test results in one place
- **Organized**: Stable build components by function
- **Isolated**: Legacy experiments properly archived

### **🔒 Database Exclusion**
- `experiments/legacy/` is automatically excluded from database ingestion
- Contains `.gitignore` to exclude from git tracking

---

*This file serves as the entry point for understanding the memory system and navigating the restructured documentation.*
