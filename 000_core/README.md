<!-- ANCHOR_KEY: core-readme -->
<!-- ANCHOR_PRIORITY: 10 -->

<!-- ROLE_PINS: ["planner", "implementer"] -->

# 🚀 AI Development Ecosystem

{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
|  |  |  |

- **what this file is**: Quick summary of 🚀 AI Development Ecosystem.

- **read when**: When you need a fast orientation or before using this file in a workflow.

- **do next**: Scan the headings below and follow any 'Quick Start' or 'Usage' sections.

> **Welcome to the AI Development Ecosystem!** This repository contains a comprehensive AI-powered development system
with sophisticated documentation, automated workflows, and intelligent task management.

## 🎯 **Start Here** New to this project? Follow this quick path

1. **Read the 5‑minute overview** → [../400_guides/400_project-overview.md](../400_guides/400_project-overview.md) ← **START HERE**
2. **Check current state** → [../100_memory/100_cursor-memory-context.md](../100_memory/100_cursor-memory-context.md)
3. **See priorities/roadmap** → [000_backlog.md](000_backlog.md)
4. **Understand architecture** → [../400_guides/400_03_system-overview-and-architecture.md](../400_guides/400_03_system-overview-and-architecture.md)
5. **Learn navigation rules** → [../400_guides/400_context-priority-guide.md](../400_guides/400_context-priority-guide.md)

**Want to understand what this is?** → **[../400_guides/400_project-overview.md](../400_guides/400_project-overview.md)** - 5-minute overview of the entire system
**Want to see the current state?** → **[../100_memory/100_cursor-memory-context.md](../100_memory/100_cursor-memory-context.md)** - Instant project state
**Want to see what's being built?** → **[000_backlog.md](000_backlog.md)** - Current priorities and roadmap

## 📚 **What This Project Is**

This is a sophisticated AI development ecosystem that transforms ideas into working
software using AI agents (Cursor Native AI + Specialized Agents). It provides:

- **Structured Workflows**: From ideation to implementation with built-in checkpoints
- **Automated Task Processing**: AI-driven task execution with intelligent error recovery
- **Comprehensive Documentation**: Cognitive scaffolding system for AI context preservation
- **Metadata Collection**: Sophisticated analytics and data-driven decision making
- **Quality Assurance**: Testing, security, and performance frameworks

## 🚨 **CRITICAL OPERATIONAL PRINCIPLE: RED LINE BASELINE**

### **🏁 ONCE ACHIEVED: NEVER GO BELOW**

**Status**: 🔴 **ABSOLUTE PERFORMANCE FLOOR** - Never Violate
**Rule**: **NO NEW FEATURES** until metrics are restored above baseline
**Purpose**: Prevents over-engineering and tech debt accumulation

#### **🎯 Core Principle**
> **"We don't innovate until we firm things up"**

Once your system achieves production-ready baseline metrics, **these become your absolute performance floor**. You are **FORBIDDEN** from building new features or making changes that would degrade performance below these thresholds.

#### **🚫 BUILD FREEZE TRIGGERS**
When **ANY** baseline metric falls below target:
- **Recall@20** < 0.65 → **BUILD FREEZE**
- **Precision@k** < 0.20 → **BUILD FREEZE**
- **Faithfulness** < 0.60 → **BUILD FREEZE**
- **P50 E2E** > 2.0s → **BUILD FREEZE**
- **P95 E2E** > 4.0s → **BUILD FREEZE**

#### **✅ BUILD RESUME CONDITIONS**
**ALL** baseline metrics must be restored above targets before:
- New feature development resumes
- Major system changes proceed
- Performance-impacting updates deploy
- Production deployments continue

**This rule prevents over-engineering and ensures sustainable, quality-first development.**

## 🚀 **Quick Start**

### **Single Doorway System (Recommended)**
```bash
# Generate a new backlog item and start the full workflow
python3.12 scripts/single_doorway.py generate "I want to work on fixing a feature"

# Continue an interrupted workflow
python3.12 scripts/single_doorway.py continue B-XXX

# Archive completed work
python3.12 scripts/single_doorway.py archive B-XXX

# Open files for a backlog item
python3.12 scripts/single_doorway.py open B-XXX
```

**Note**: This system requires Python 3.12. If you're using Python 3.9, the system will automatically detect and use Python 3.12 if available via Homebrew. All tests run in the Python 3.12 virtual environment.

### **Traditional Setup**
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r dspy-rag-system/requirements.txt

# Start the system
./dspy-rag-system/quick_start.sh
```

## 📖 **Documentation Navigation**

### **Core Documentation**
- **[README.md](README.md)** - Start here navigation
- **[../400_guides/400_project-overview.md](../400_guides/400_project-overview.md)** - Main project overview
- **[../400_guides/400_system-overview.md](../400_guides/400_system-overview.md)** - Technical architecture
- **[000_backlog.md](000_backlog.md)** - Current priorities and roadmap
- **[../400_guides/400_documentation-retrieval-guide.md](../400_guides/400_documentation-retrieval-guide.md)** - Documentation search/index + validator quick start

### **Development Workflow**
- **[Single Doorway System](../scripts/single_doorway.py)** - Automated workflow from backlog → PRD → tasks → execution → archive
- **[001_create-prd.md](001_create-prd.md)** - Create Product Requirements Documents (manual)
- **[002_generate-tasks.md](002_generate-tasks.md)** - Generate executable tasks (manual)
- **[003_process-task-list.md](003_process-task-list.md)** - Execute tasks with AI (manual)
- **[004_development-roadmap.md](004_development-roadmap.md)** - Strategic roadmap and sprint planning
- **[005_rag-tuning-protocol.md](005_rag-tuning-protocol.md)** - Industry-grade RAG performance optimization methodology
- **[scripts/backlog_status_tracking.py](../scripts/backlog_status_tracking.py)** - Status tracking with timestamps

### **Setup & Configuration**
- **[../200_setup/202_setup-requirements.md](../200_setup/202_setup-requirements.md)** - Environment setup
- **[../400_guides/400_11_deployments-ops-and-observability.md](../400_guides/400_11_deployments-ops-and-observability.md)** - Deployments & Ops

### **Quality & Standards**
- **[../400_guides/400_contributing-guidelines.md](../400_guides/400_contributing-guidelines.md)** - Development standards
- **[../400_guides/400_05_coding-and-prompting-standards.md](../400_guides/400_05_coding-and-prompting-standards.md)** - Coding & testing
- **[../400_guides/400_10_security-compliance-and-access.md](../400_guides/400_10_security-compliance-and-access.md)** - Security guidelines
- **[../400_guides/400_11_deployments-ops-and-observability.md](../400_guides/400_11_deployments-ops-and-observability.md)** - Performance & observability

## 🤖 **AI System Components**

### **Core AI System**
- **DSPy RAG System**: Enhanced retrieval-augmented generation
- **Cursor Native AI**: Foundation AI model integration
- **Specialized Agents**: Task-specific AI agents
- **Metadata Collection**: Comprehensive analytics and state management

### **Automation & Workflows**
- **Single Doorway System**: Automated workflow from backlog → PRD → tasks → execution → archive
- **n8n Integration**: Automated backlog management
- **Mission Dashboard**: Real-time task monitoring
- **Error Recovery**: Intelligent error handling and retry logic
- **State Management**: Persistent execution state tracking
- **Enhanced Backlog Tracking**: Timestamp tracking and stale item detection

### **Quality Assurance**
- **Testing Framework**: Comprehensive test suites
- **Security Scanning**: Automated security validation
- **Performance Monitoring**: Real-time system health tracking
- **Documentation Validation**: Automated documentation coherence checking

## 🔧 **Key Commands**

### **Single Doorway System**
```bash
# Generate new backlog item and start workflow
python3 scripts/single_doorway.py generate "description"

# Continue interrupted workflow
python3 scripts/single_doorway.py continue B-XXX

# Archive completed work
python3 scripts/single_doorway.py archive B-XXX

# Open files for backlog item
python3 scripts/single_doorway.py open B-XXX
```

### **Traditional Commands**
```bash
# List all tasks
python3 ../scripts/process_tasks.py list

# Execute a specific task
python3 ../scripts/process_tasks.py execute B-049

# Check system status
python3 ../scripts/process_tasks.py status

# Start mission dashboard
../dspy-rag-system/start_mission_dashboard.sh

# Run tests
../dspy-rag-system/run_tests.sh
```

## 📊 **System Status**

- **Current Focus**: B-011 Cursor Native AI + Specialized Agents Integration
- **Infrastructure**: v0.3.1-rc3 Core Hardening ✅ completed
- **Documentation**: Comprehensive cognitive scaffolding system ✅ completed
- **Metadata System**: Advanced analytics and state management ✅ completed

## 🎯 **Getting Help**

1. **Use this README (Start Here)** for navigation guidance
2. **Check [000_backlog.md](000_backlog.md)** for current priorities
3. **Review [../400_guides/400_system-overview.md](../400_guides/400_system-overview.md)** for technical context
4. See [metadata guide](../400_guides/400_metadata-collection-guide.md) for quick reference
5. Use [../400_guides/400_metadata-collection-guide.md](../400_guides/400_metadata-collection-guide.md#) for detailed commands

---

- **Last Updated**: 2025-08-24
- **Documentation**: Comprehensive cognitive scaffolding system
- **Status**: Active development with AI-powered workflows
# Test
# Test
# Test hook fix
# Test hook fix 2
# Test pre-push fix
