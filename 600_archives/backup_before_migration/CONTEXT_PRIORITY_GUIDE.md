# AI Development Stack Context Priority Guide

## Overview
This document provides a prioritized list of files in the `ai-dev-tasks` project, organized by importance from macro to micro view of the AI stack. This guide is designed for:
- **Memory rehydration** for AI assistants
- **Context sharing** with other models
- **Quick onboarding** of new team members
- **Understanding the complete AI development ecosystem**

## 🧠 Memory Scaffolding System

### **Context Sharing Protocol**
When sharing context with other AI models, use this structured approach:

#### **Level 1: Essential Context (5 files)**
```
1. 400_project-overview.md - Project overview and workflow
2. 400_system-overview_advanced_features.md - Technical architecture
3. 00_backlog.md - Current priorities and status
4. dspy-rag-system/400_project-overview.md - Core system status
5. docs/400_project-overview.md - Three-lens documentation guide
```

#### **Level 2: Implementation Context (10 files)**
Add these for implementation tasks:
```
6. 104_dspy-development-context.md - Deep technical context
7. 202_setup-requirements.md - Environment setup
8. 201_model-configuration.md - AI model configuration
9. 100_backlog-automation.md - Automation patterns
10. dspy-rag-system/docs/CURRENT_STATUS.md - Real-time status
```

#### **Level 3: Domain Context (15 files)**
Add these for domain-specific tasks:
```
11-15. Tier 3 files (Core modules & agent logic)
16-20. Tier 4 files (Config & environment)
21-25. Tier 5 files (Domain assets)
```

### **Cross-Reference System**
Use these reference patterns in other documents:

#### **In PRDs and Task Lists:**
```markdown
<!-- CONTEXT_REFERENCE: CONTEXT_PRIORITY_GUIDE.md -->
<!-- ESSENTIAL_FILES: 400_project-overview.md, 400_system-overview_advanced_features.md, 00_backlog.md -->
<!-- IMPLEMENTATION_FILES: 104_dspy-development-context.md, 202_setup-requirements.md -->
<!-- DOMAIN_FILES: 100_backlog-guide.md, 103_yi-coder-integration.md -->
<!-- MODULE_REFERENCE: 102_memory-context-state.md -->
<!-- MODULE_REFERENCE: 103_memory-context-workflow.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide_additional_resources.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide_environment_setup.md -->
<!-- MODULE_REFERENCE: 100_ai-development-ecosystem_advanced_lens_technical_implementation.md -->
<!-- MODULE_REFERENCE: 400_system-overview_advanced_features.md -->
<!-- MODULE_REFERENCE: 400_system-overview_system_architecture_macro_view.md -->
<!-- MODULE_REFERENCE: 400_system-overview_development_workflow_high_level_process.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_system-overview.md -->
```

#### **In Code Comments:**
```python
# CONTEXT: See CONTEXT_PRIORITY_GUIDE.md for file organization
# ESSENTIAL: 400_project-overview.md, 400_system-overview_advanced_features.md, 00_backlog.md
# IMPLEMENTATION: 104_dspy-development-context.md, 202_setup-requirements.md
```

#### **In Documentation:**
```markdown
> **Context Reference**: See `CONTEXT_PRIORITY_GUIDE.md` for complete file organization
> **Essential Files**: `400_project-overview.md`, `400_system-overview_advanced_features.md`, `00_backlog.md`
> **Implementation Files**: `104_dspy-development-context.md`, `202_setup-requirements.md`
```

## Priority Tiers (Macro → Micro)

### **Tier 1: Top-level Architecture & Purpose**
*Files that give a 5-second mental map of the whole stack*

| File | Purpose | Why First? | Cross-Reference |
|------|---------|-------------|-----------------|
| `400_project-overview.md` | Main project entry point with high-level overview, quick start, and core AI development workflow | Gives immediate understanding of the project's purpose and workflow | `<!-- CONTEXT_REFERENCE: 400_project-overview.md -->` |
| `400_system-overview_advanced_features.md` | Comprehensive technical overview of the entire AI development ecosystem | Provides the "system-of-systems" context | `<!-- CONTEXT_REFERENCE: 400_system-overview_advanced_features.md -->` |
| `dspy-rag-system/400_project-overview.md` | DSPy RAG system overview with current status and features | Shows the core AI system's capabilities | `<!-- CONTEXT_REFERENCE: dspy-rag-system/400_project-overview.md -->` |
| `dspy-rag-system/docs/CURRENT_STATUS.md` | Real-time status of all system components and features | Current operational state of the entire stack | `<!-- CONTEXT_REFERENCE: dspy-rag-system/docs/CURRENT_STATUS.md -->` |

### **Tier 2: Data-flow & Orchestration Specs**
*Files showing how components talk to each other*

| File | Purpose | Why Critical? | Cross-Reference |
|------|---------|---------------|-----------------|
| `00_backlog.md` | Central product backlog with prioritization, dependencies, and roadmap | Shows the project's direction and current priorities | `<!-- CONTEXT_REFERENCE: 00_backlog.md -->` |
| `100_backlog-automation.md` | AI-BACKLOG-META system and n8n workflow orchestration | Demonstrates automated project management | `<!-- CONTEXT_REFERENCE: 100_backlog-automation.md -->` |
| `01_create-prd.md` | Process for creating Product Requirement Documents | Defines scope → implementation flow | `<!-- CONTEXT_REFERENCE: 01_create-prd.md -->` |
| `02_generate-tasks.md` | Rules for breaking PRDs into executable task lists | Shows how high-level requirements become actionable | `<!-- CONTEXT_REFERENCE: 02_generate-tasks.md -->` |
| `03_process-task-list.md` | AI agent execution loop, state management, and error recovery | Core orchestration of AI-driven development | `<!-- CONTEXT_REFERENCE: 03_process-task-list.md -->` |
| `dspy-rag-system/src/dashboard.py` | Main dashboard orchestration and API endpoints | Central coordination point | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/dashboard.py -->` |
| `dspy-rag-system/src/mission_dashboard/mission_dashboard.py` | Real-time mission tracking orchestration | Live AI task monitoring | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/mission_dashboard/mission_dashboard.py -->` |
| `dspy-rag-system/src/n8n_workflows/backlog_webhook.py` | n8n integration webhook server | External system integration | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/n8n_workflows/backlog_webhook.py -->` |

### **Tier 3: Core Modules & Agent Logic**
*Files explaining the brains of the operation*

| File | Purpose | Why Essential? | Cross-Reference |
|------|---------|----------------|-----------------|
| `104_dspy-development-context.md` | Deep research analysis of DSPy implementation | Explains the AI reasoning system | `<!-- CONTEXT_REFERENCE: 104_dspy-development-context.md -->` |
| `docs/ARCHITECTURE.md` | DSPy Router architecture (v0.3.1) with signatures, modules, chains | Core AI system architecture | `<!-- CONTEXT_REFERENCE: docs/ARCHITECTURE.md -->` |
| `dspy-rag-system/src/dspy_modules/` | Core DSPy agent implementations | The actual AI agents | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/dspy_modules/ -->` |
| `dspy-rag-system/src/mission_dashboard/mission_tracker.py` | Mission tracking core logic | AI task lifecycle management | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/mission_dashboard/mission_tracker.py -->` |
| `dspy-rag-system/src/monitoring/production_monitor.py` | Production monitoring core | System observability | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/monitoring/production_monitor.py -->` |
| `dspy-rag-system/src/monitoring/health_endpoints.py` | Health check and readiness logic | System reliability | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/monitoring/health_endpoints.py -->` |
| `dspy-rag-system/src/n8n_workflows/backlog_scrubber.py` | Backlog scoring and automation logic | Automated prioritization | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/n8n_workflows/backlog_scrubber.py -->` |
| `dspy-rag-system/src/watch_folder.py` | Document processing and RAG pipeline | Core RAG functionality | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/watch_folder.py -->` |

### **Tier 4: Config & Environment**
*Files for reproducing or mutating the system*

| File | Purpose | Why Important? | Cross-Reference |
|------|---------|----------------|-----------------|
| `202_setup-requirements.md` | Manual setup items (n8n, PostgreSQL, Ollama, LM Studio) | Environment reproduction | `<!-- CONTEXT_REFERENCE: 202_setup-requirements.md -->` |
| `201_model-configuration.md` | AI model configuration (Mistral, Yi-Coder) | AI model setup | `<!-- CONTEXT_REFERENCE: 201_model-configuration.md -->` |
| `docs/CONFIG_REFERENCE.md` | Comprehensive configuration reference | System configuration | `<!-- CONTEXT_REFERENCE: docs/CONFIG_REFERENCE.md -->` |
| `dspy-rag-system/requirements.txt` | Python dependencies | Dependency management | `<!-- CONTEXT_REFERENCE: dspy-rag-system/requirements.txt -->` |
| `dspy-rag-system/start_mission_dashboard.sh` | Dashboard startup script | System startup | `<!-- CONTEXT_REFERENCE: dspy-rag-system/start_mission_dashboard.sh -->` |
| `dspy-rag-system/quick_start.sh` | Quick start script | Rapid deployment | `<!-- CONTEXT_REFERENCE: dspy-rag-system/quick_start.sh -->` |
| `.gitignore` | Version control exclusions | Repository management | `<!-- CONTEXT_REFERENCE: .gitignore -->` |
| `.markdownlint.jsonc` | Documentation formatting rules | Code quality | `<!-- CONTEXT_REFERENCE: .markdownlint.jsonc -->` |

### **Tier 5: Domain Assets**
*Files needed for high-quality generation after architecture is understood*

| File | Purpose | Why Valuable? | Cross-Reference |
|------|---------|---------------|-----------------|
| `100_backlog-guide.md` | Backlog system usage guide and prioritization rules | Domain knowledge | `<!-- CONTEXT_REFERENCE: 100_backlog-guide.md -->` |
| `103_yi-coder-integration.md` | Yi-Coder integration with Cursor IDE | Tool integration | `<!-- CONTEXT_REFERENCE: 103_yi-coder-integration.md -->` |
| `TIMESTAMP_UPDATE_GUIDE.md` | Timestamp update rules and process | Process knowledge | `<!-- CONTEXT_REFERENCE: TIMESTAMP_UPDATE_GUIDE.md -->` |
| `200_naming-conventions.md` | File naming conventions | Organization standards | `<!-- CONTEXT_REFERENCE: 200_naming-conventions.md -->` |
| `dspy-rag-system/docs/MISSION_DASHBOARD_GUIDE.md` | Mission dashboard usage guide | Feature documentation | `<!-- CONTEXT_REFERENCE: dspy-rag-system/docs/MISSION_DASHBOARD_GUIDE.md -->` |
| `dspy-rag-system/docs/N8N_BACKLOG_SCRUBBER_GUIDE.md` | n8n integration guide | Integration documentation | `<!-- CONTEXT_REFERENCE: dspy-rag-system/docs/N8N_BACKLOG_SCRUBBER_GUIDE.md -->` |
| `dspy-rag-system/docs/DSPY_INTEGRATION_GUIDE.md` | DSPy integration guide | Core system documentation | `<!-- CONTEXT_REFERENCE: dspy-rag-system/docs/DSPY_INTEGRATION_GUIDE.md -->` |
| `dspy-rag-system/src/mission_dashboard/templates/mission_dashboard.html` | Dashboard UI template | User interface | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/mission_dashboard/templates/mission_dashboard.html -->` |

### **Tier 6: Reference & Edge Cases**
*Files valuable for fine-tuning or debugging*

| File | Purpose | Why Useful? | Cross-Reference |
|------|---------|-------------|-----------------|
| `C9_COMPLETION_SUMMARY.md` | B-003 completion reference | Historical context | `<!-- CONTEXT_REFERENCE: C9_COMPLETION_SUMMARY.md -->` |
| `C10_COMPLETION_SUMMARY.md` | B-010 completion reference | Historical context | `<!-- CONTEXT_REFERENCE: C10_COMPLETION_SUMMARY.md -->` |
| `dspy-rag-system/demo_mission_dashboard.py` | Mission dashboard demonstration | Feature examples | `<!-- CONTEXT_REFERENCE: dspy-rag-system/demo_mission_dashboard.py -->` |
| `dspy-rag-system/demo_backlog_scrubber.py` | Backlog scrubber demonstration | Feature examples | `<!-- CONTEXT_REFERENCE: dspy-rag-system/demo_backlog_scrubber.py -->` |
| `dspy-rag-system/demo_production_monitoring.py` | Production monitoring demonstration | Feature examples | `<!-- CONTEXT_REFERENCE: dspy-rag-system/demo_production_monitoring.py -->` |
| `dspy-rag-system/demo_database_resilience.py` | Database resilience demonstration | Feature examples | `<!-- CONTEXT_REFERENCE: dspy-rag-system/demo_database_resilience.py -->` |
| `dspy-rag-system/tests/` | Test suites for all components | Quality assurance | `<!-- CONTEXT_REFERENCE: dspy-rag-system/tests/ -->` |
| `dspy-rag-system/watch_folder.log` | System logs | Debugging | `<!-- CONTEXT_REFERENCE: dspy-rag-system/watch_folder.log -->` |
| `dspy-rag-system/watch_folder_error.log` | Error logs | Debugging | `<!-- CONTEXT_REFERENCE: dspy-rag-system/watch_folder_error.log -->` |

## **Essential Context Files for Model Rehydration**

When rehydrating an AI model's memory or sharing context with other models, start with these **top 10 files** for maximum context efficiency:

### **1. `400_project-overview.md`** 
- **Purpose**: 5-second mental map of the entire project
- **Key Info**: AI development workflow, quick start, core concepts
- **When to Use**: First file to read for any new context
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: 400_project-overview.md -->`

### **2. `400_system-overview_advanced_features.md`**
- **Purpose**: Technical architecture overview
- **Key Info**: System components, security features, reliability measures
- **When to Use**: Understanding the complete technical stack
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: 400_system-overview_advanced_features.md -->`

### **3. `00_backlog.md`**
- **Purpose**: Current priorities and roadmap
- **Key Info**: Active tasks, completed items, dependencies
- **When to Use**: Understanding what's being built and what's done
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: 00_backlog.md -->`

### **4. `dspy-rag-system/400_project-overview.md`**
- **Purpose**: Core system status and features
- **Key Info**: DSPy RAG system capabilities, current features
- **When to Use**: Understanding the main AI system
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: dspy-rag-system/400_project-overview.md -->`

### **5. `docs/ARCHITECTURE.md`**
- **Purpose**: DSPy implementation details
- **Key Info**: Router architecture, modules, chains, agent catalog
- **When to Use**: Deep technical understanding of AI system
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: docs/ARCHITECTURE.md -->`

### **6. `104_dspy-development-context.md`**
- **Purpose**: Deep technical context
- **Key Info**: Research analysis, current architecture, critical fixes
- **When to Use**: Understanding the AI reasoning system
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: 104_dspy-development-context.md -->`

### **7. `202_setup-requirements.md`**
- **Purpose**: Environment setup requirements
- **Key Info**: Manual setup items, dependencies, configuration
- **When to Use**: Reproducing or modifying the system
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: 202_setup-requirements.md -->`

### **8. `201_model-configuration.md`**
- **Purpose**: AI model configuration
- **Key Info**: Mistral, Yi-Coder setup, model parameters
- **When to Use**: Understanding AI model setup and capabilities
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: 201_model-configuration.md -->`

### **9. `100_backlog-automation.md`**
- **Purpose**: Orchestration patterns
- **Key Info**: AI-BACKLOG-META system, n8n workflows
- **When to Use**: Understanding automated processes
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: 100_backlog-automation.md -->`

### **10. `dspy-rag-system/docs/CURRENT_STATUS.md`**
- **Purpose**: Real-time system state
- **Key Info**: Working features, operational status
- **When to Use**: Understanding current system capabilities
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: dspy-rag-system/docs/CURRENT_STATUS.md -->`

## **Usage Guidelines**

### **For Memory Rehydration**
1. Start with Tier 1 files (README, SYSTEM_OVERVIEW)
2. Move to Tier 2 for data flow understanding
3. Reference Tier 3 for specific implementation questions
4. Use Tier 4-6 as needed for detailed context

### **For Context Sharing**
1. Share the top 10 essential files first
2. Add specific files based on the task at hand
3. Include relevant Tier 5-6 files for domain-specific questions

### **For Problem Solving**
1. Check `00_backlog.md` for current priorities
2. Review relevant Tier 3 files for implementation details
3. Reference Tier 6 files for debugging context
4. Use Tier 4 files for environment setup issues

## **File Categories by Use Case**

### **Architecture Understanding**
- Tier 1 files
- `docs/ARCHITECTURE.md`
- `104_dspy-development-context.md`

### **Current Development Status**
- `00_backlog.md`
- `dspy-rag-system/docs/CURRENT_STATUS.md`
- `dspy-rag-system/400_project-overview.md`

### **Implementation Details**
- Tier 3 files
- `dspy-rag-system/src/` directory
- `tests/` directory

### **Environment Setup**
- `202_setup-requirements.md`
- `201_model-configuration.md`
- `docs/CONFIG_REFERENCE.md`

### **Process Understanding**
- `100_backlog-automation.md`
- `01_create-prd.md`
- `02_generate-tasks.md`
- `03_process-task-list.md`

## **Memory Scaffolding Integration**

### **Cross-Reference Implementation**
To integrate this guide with other documents, add these references:

#### **In 400_project-overview.md:**
```markdown
<!-- CONTEXT_REFERENCE: CONTEXT_PRIORITY_GUIDE.md -->
<!-- ESSENTIAL_FILES: 400_project-overview.md, 400_system-overview_advanced_features.md, 00_backlog.md -->
```

#### **In 400_system-overview_advanced_features.md:**
```markdown
<!-- CONTEXT_REFERENCE: CONTEXT_PRIORITY_GUIDE.md -->
<!-- ARCHITECTURE_FILES: docs/ARCHITECTURE.md, 104_dspy-development-context.md -->
```

#### **In 00_backlog.md:**
```markdown
<!-- CONTEXT_REFERENCE: CONTEXT_PRIORITY_GUIDE.md -->
<!-- WORKFLOW_FILES: 01_create-prd.md, 02_generate-tasks.md, 03_process-task-list.md -->
```

### **AI Model Context Sharing**
When sharing context with other AI models, use this structured approach:

#### **Quick Context (5 files):**
```
CONTEXT_PRIORITY_GUIDE.md
400_project-overview.md
400_system-overview_advanced_features.md
00_backlog.md
dspy-rag-system/400_project-overview.md
```

#### **Full Context (15 files):**
Add these to the quick context:
```
docs/ARCHITECTURE.md
104_dspy-development-context.md
202_setup-requirements.md
201_model-configuration.md
100_backlog-automation.md
dspy-rag-system/docs/CURRENT_STATUS.md
01_create-prd.md
02_generate-tasks.md
03_process-task-list.md
100_backlog-guide.md
```

#### **Domain-Specific Context (20+ files):**
Add relevant Tier 3-6 files based on the specific task or domain.

## **Maintenance Notes**

- **Last Updated**: 2024-08-06
- **Priority Structure**: Follows "macro → micro" rule
- **Context Efficiency**: Optimized for AI model memory rehydration
- **File Count**: 45 prioritized files across 6 tiers
- **Essential Files**: 10 files provide 80% of context needed
- **Cross-Reference System**: Integrated with all major documents
- **Memory Scaffolding**: Structured for AI model context sharing

This guide ensures that any AI model can quickly understand the complete AI development stack from the highest level down to implementation details, making it perfect for memory rehydration and context sharing. 