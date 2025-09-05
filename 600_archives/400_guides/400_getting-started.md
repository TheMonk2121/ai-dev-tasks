<!-- ANCHOR_KEY: getting-started -->
<!-- ANCHOR_PRIORITY: 10 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher", "coder"] -->

# 🚀 Getting Started Guide

> DEPRECATED: Use `400_00_getting-started-and-index.md` as the canonical entry. For workflow and memory context, see `400_04_development-workflow-and-standards.md` and `400_06_memory-and-context-systems.md`.

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Entry point and project overview for new users | First time working with the project or need to understand the big picture | Follow the quick start steps and explore the project structure |

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Getting started guide maintained
- **Priority**: 🔥 Critical - Essential for onboarding and orientation
- **Points**: 3 - Low complexity, high importance
- **Dependencies**: 400_guides/400_guide-index.md, 100_memory/100_cursor-memory-context.md
- **Next Steps**: Follow the quick start steps to get oriented

## ⚡ Quick Start

### **5-Minute Overview**

1. **Understand the Project**: AI-powered development ecosystem that transforms ideas into working software
2. **Check Current State**: Review backlog priorities and system status
3. **Choose Your Path**: Use the guide index to find the right guide for your task
4. **Start Working**: Follow the development workflow for your specific task

### **Essential Commands**

```bash
# 1. Check environment
python3 scripts/venv_manager.py --check

# 2. Get context for your task
./scripts/memory_up.sh -q "your specific task description"

# 3. Start development workflow
python3 scripts/single_doorway.py generate "feature description"
```

### **For New Users**

```bash
# Complete setup
python3 -m venv venv
source .venv/bin/activate
pip install -r requirements.txt

# Verify installation
python3 scripts/venv_manager.py --check
./scripts/memory_up.sh -q "project overview and current status"
```

## 🏗️ **Project Overview**

### **What This Project Is**

An **AI-powered development ecosystem** that transforms ideas into working software using:

- **AI Agents**: Cursor Native AI + Specialized DSPy agents
- **Structured Workflows**: PRD → Tasks → Implementation → Testing
- **Intelligent Automation**: Context capture, task generation, error recovery
- **Local-First Architecture**: PostgreSQL + PGVector, local model inference

### **Core Components**

| Component | Purpose | Location |
|-----------|---------|----------|
| **Planning Layer** | PRD creation, task generation | `000_core/` |
| **AI Execution Layer** | Cursor AI + DSPy agents | `dspy-rag-system/` |
| **Workflow Engine** | Automated task processing | `scripts/` |
| **Memory System** | Context management | `100_memory/` |
| **Documentation** | Guides and references | `400_guides/` |

### **Key Workflows**

#### **Feature Development**
```bash
# 1. Create PRD
python3 scripts/run_workflow.py generate "feature description"

# 2. Generate tasks
python3 scripts/run_workflow.py tasks "PRD-XXX"

# 3. Execute tasks
python3 scripts/run_workflow.py execute "Task-List-XXX"
```

#### **Context Management**
```bash
# Get context for any task
./scripts/memory_up.sh -q "implement authentication system"

# Start context capture
python3 scripts/single_doorway.py scribe start

# Generate summaries
python scripts/worklog_summarizer.py --backlog-id B-XXX
```

## 📋 **Project Structure**

### **Core Directories**

```
ai-dev-tasks/
├── 000_core/                    # Core workflows and backlog
│   ├── 000_backlog.md          # Prioritized backlog
│   ├── 001_create-prd.md       # PRD creation workflow
│   ├── 002_generate-tasks.md   # Task generation workflow
│   └── 003_process-task-list.md # Task execution workflow
├── 100_memory/                  # Memory and context management
│   ├── 100_cursor-memory-context.md # Memory scaffold
│   └── 104_dspy-development-context.md # DSPy context
├── 200_setup/                   # Environment setup
│   ├── 200_naming-conventions.md
│   ├── 201_database-config.py
│   └── 202_setup-requirements.md
├── 400_guides/                  # Task-based guides
│   ├── 400_guide-index.md      # Navigation hub
│   ├── 400_getting-started.md  # This guide
│   ├── 400_development-workflow.md # Development process
│   └── ...                     # Other task-specific guides
├── dspy-rag-system/            # AI system implementation
│   ├── src/dspy_modules/       # DSPy modules
│   ├── src/utils/              # Utilities
│   └── tests/                  # Test suite
└── scripts/                    # Automation scripts
    ├── venv_manager.py         # Environment management
    ├── run_workflow.py         # Workflow orchestration
    └── memory_up.sh            # Memory rehydration
```

### **Key Files**

| File | Purpose | When to Read |
|------|---------|--------------|
| `000_core/000_backlog.md` | Current priorities | Planning next work |
| `100_memory/100_cursor-memory-context.md` | Current state | Starting any session |
| `400_guides/400_guide-index.md` | Navigation | Finding the right guide |
| `400_guides/400_development-workflow.md` | Development process | Implementing features |
| `dspy-rag-system/README.md` | AI system details | Working with AI components |

## 🎯 **Getting Oriented**

### **I'm New Here - What Should I Do?**

1. **Read this guide** (you're here!)
2. **Check the backlog**: `000_core/000_backlog.md`
3. **Get current context**: `./scripts/memory_up.sh -q "project overview"`
4. **Find your guide**: `400_guides/400_guide-index.md`

### **I Want to...**

#### **Implement a Feature**
→ Read `400_guides/400_development-workflow.md`

#### **Debug an Issue**
→ Read `400_guides/400_testing-debugging.md`

#### **Deploy Changes**
→ Read `400_guides/400_deployment-operations.md`

#### **Plan Architecture**
→ Read `400_guides/400_planning-strategy.md`

#### **Integrate Components**
→ Read `400_guides/400_integration-security.md`

### **I'm an AI Assistant**
→ Use `./scripts/memory_up.sh -q "your specific task"` to get context

## 🔧 **Environment Setup**

### **Required Dependencies**

```bash
# Core dependencies
psycopg2-binary==2.9.9  # Database connectivity
dspy==3.0.1            # Core AI framework
pytest==8.0.0          # Testing framework
ruff==0.3.0            # Code quality and formatting
pyright==1.1.350       # Type checking

# Development tools
pre-commit==3.6.0      # Git hooks
```

### **Environment Configuration**

```bash
# Create virtual environment
python3 -m venv venv

# Activate environment
source .venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Setup pre-commit hooks
pre-commit install

# Verify setup
python3 scripts/venv_manager.py --check
```

### **Database Setup**

```bash
# Check database connection
python3 scripts/database_sync_check.py

# Setup database (if needed)
python3 dspy-rag-system/scripts/apply_clean_slate_schema.py
```

## 🚀 **First Steps**

### **1. Verify Your Environment**

```bash
# Check everything is working
python3 scripts/venv_manager.py --check
./scripts/memory_up.sh -q "verify environment setup"
```

### **2. Understand Current State**

```bash
# Get current project status
./scripts/memory_up.sh -q "current project status and priorities"

# Check backlog
cat 000_core/000_backlog.md | head -50
```

### **3. Choose Your First Task**

```bash
# Start with a simple task
python3 scripts/single_doorway.py generate "simple feature description"

# Or continue existing work
python3 scripts/single_doorway.py continue B-XXX
```

## 📚 **Learning Path**

### **For Developers**
1. **This guide** - Understand the project
2. **Development Workflow** - Learn the development process
3. **Testing & Debugging** - Understand quality assurance
4. **Deployment Operations** - Learn deployment procedures

### **For AI Assistants**
1. **Memory Context** - Understand the memory system
2. **Guide Index** - Find the right guide for any task
3. **Development Workflow** - Follow development best practices
4. **Integration Security** - Understand system integration

### **For Planners**
1. **This guide** - Understand the project scope
2. **Planning Strategy** - Learn planning approaches
3. **Backlog** - Understand current priorities
4. **System Overview** - Understand architecture

## 🔄 **Workflow Integration**

### **With AI Development Ecosystem**

```bash
# Start AI-assisted development
python3 scripts/single_doorway.py generate "feature description"

# Continue interrupted workflow
python3 scripts/single_doorway.py continue B-XXX

# Archive completed work
python3 scripts/single_doorway.py archive B-XXX
```

### **With Context Management**

```bash
# Start context capture
python3 scripts/single_doorway.py scribe start

# Add manual notes
python3 scripts/single_doorway.py scribe append "implementation note"

# Generate work summaries
python scripts/worklog_summarizer.py --backlog-id B-XXX
```

## 🚨 **Troubleshooting**

### **Common Issues**

**Environment Problems:**
```bash
# Check venv status
python3 scripts/venv_manager.py --check

# Recreate venv if needed
rm -rf venv && python3 -m venv venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Database Issues:**
```bash
# Check database connection
python3 scripts/database_sync_check.py

# Reset database if needed
python3 dspy-rag-system/scripts/apply_clean_slate_schema.py
```

**Memory System Issues:**
```bash
# Test memory rehydration
./scripts/memory_up.sh -q "test memory system"

# Check system status
python3 scripts/system_health_check.py
```

## 📚 **Related Guides**

- **Guide Index**: `400_guides/400_guide-index.md`
- **Development Workflow**: `400_guides/400_development-workflow.md`
- **Testing & Debugging**: `400_guides/400_testing-debugging.md`
- **Deployment Operations**: `400_guides/400_deployment-operations.md`
- **Integration & Security**: `400_guides/400_integration-security.md`

## 🎯 **Next Steps**

1. **Choose your path** from the guide index
2. **Get context** for your specific task
3. **Follow the workflow** for your chosen path
4. **Ask for help** if you get stuck

---

**This guide provides the entry point to the AI development ecosystem. Use the guide index to find the right guide for your specific task.**
