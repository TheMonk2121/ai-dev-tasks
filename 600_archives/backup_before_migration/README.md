# 🚀 AI Dev Tasks 🤖

Welcome to **AI Dev Tasks**! This repository provides a collection of markdown files designed to supercharge your feature development workflow with AI-powered IDEs and CLIs. Originally built for [Cursor](https://cursor.sh/), these tools work with any AI coding assistant including Claude Code, Windsurf, and others. By leveraging these structured prompts, you can systematically approach building features, from ideation to implementation, with built-in checkpoints for verification.

Stop wrestling with monolithic AI requests and start guiding your AI collaborator step-by-step!

<!-- CONTEXT_REFERENCE: CONTEXT_PRIORITY_GUIDE.md -->
<!-- ESSENTIAL_FILES: README.md, SYSTEM_OVERVIEW.md, 00_backlog.md -->
<!-- IMPLEMENTATION_FILES: 104_dspy-development-context.md, SETUP_REQUIREMENTS.md -->
<!-- MEMORY_CONTEXT: HIGH - Project overview and workflow guide for AI context -->

<!-- MODULE_REFERENCE: 103_memory-context-workflow.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide_additional_resources.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide_environment_setup.md -->
<!-- MODULE_REFERENCE: 100_ai-development-ecosystem_advanced_lens_technical_implementation.md -->
<!-- MODULE_REFERENCE: 400_system-overview_development_workflow_high_level_process.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide.md -->
## 🚀 Quick Start

### Quick Start Box
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r dspy-rag-system/requirements.txt

# One-liner to get started
make run-local

# Or with custom configuration
DEEP_REASONING=0 CLARIFIER=0 make run-local
```

**Virtual Environment Setup:**
The project uses a virtual environment to prevent dependency conflicts. Always activate it before running:
```bash
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

**Large LLMs Note:**
Large LLMs (Mixtral) require `LLM_TIMEOUT_SEC>=90` for optimal performance.

**Environment Variables to Configure:**
- `DEEP_REASONING=0` - Disable ReasoningAgent + Mixtral (default)
- `CLARIFIER=0` - Disable ClarifierAgent (default)
- `POOL_MIN=1` - Minimum database connections
- `POOL_MAX=10` - Maximum database connections
- `MODEL_IDLE_EVICT_SECS=600` - Idle model eviction time
- `MAX_RAM_PRESSURE=85` - Maximum RAM usage percentage
- `ENABLED_AGENTS=IntentRouter,RetrievalAgent,CodeAgent` - Comma-separated agent list
- `METRICS_PORT=9100` - Prometheus metrics endpoint port
- `REDIS_URL=redis://localhost:6379` - Redis for rate limiting persistence
- `HEALTH_CHECK_TIMEOUT=30` - Health check timeout in seconds
- `READY_CHECK_TIMEOUT=10` - Readiness check timeout in seconds

**Timeout Configuration:**
- `DB_CONNECT_TIMEOUT=10` - Database connection timeout (seconds)
- `DB_READ_TIMEOUT=30` - Database read timeout (seconds)
- `DB_WRITE_TIMEOUT=60` - Database write timeout (seconds)
- `DB_POOL_TIMEOUT=20` - Database pool timeout (seconds)
- `HTTP_CONNECT_TIMEOUT=10` - HTTP connection timeout (seconds)
- `HTTP_READ_TIMEOUT=30` - HTTP read timeout (seconds)
- `HTTP_TOTAL_TIMEOUT=120` - HTTP total timeout (seconds)
- `PDF_PROCESSING_TIMEOUT=300` - PDF processing timeout (seconds)
- `FILE_UPLOAD_TIMEOUT=600` - File upload timeout (seconds)
- `CHUNK_PROCESSING_TIMEOUT=120` - Chunk processing timeout (seconds)
- `LLM_REQUEST_TIMEOUT=120` - LLM request timeout (seconds)
- `LLM_STREAM_TIMEOUT=300` - LLM stream timeout (seconds)
- `STARTUP_TIMEOUT=60` - System startup timeout (seconds)

**Security Configuration:**
- `SECURITY_ENABLED=true` - Enable security scanning
- `SECURITY_SCAN_ON_STARTUP=true` - Run security scan on startup
- `SECURITY_VULNERABILITY_THRESHOLD=medium` - Vulnerability threshold
- `SECURITY_AUTO_FIX=false` - Auto-fix security issues
- `SECURITY_REPORT_FILE=security-report.json` - Security report file
- `SECURITY_MAX_FILE_SIZE=104857600` - Maximum file size (100MB)
- `SECURITY_TOKEN_LENGTH=32` - Security token length
- `LLM_TIMEOUT_SEC=90` - Overrides agent timeouts (the execution engine)
- `SECURITY_MAX_FILE_MB=100` - Raise default 50 MB cap (the execution engine)

**Production Monitoring Configuration:**
- `ENVIRONMENT=production` - Set environment (development, staging, production)
- `OTLP_ENDPOINT=http://localhost:4317` - OpenTelemetry endpoint (the execution engine)
- `MONITORING_INTERVAL=30` - Monitoring cycle interval in seconds
- `HEALTH_CHECK_TIMEOUT=5` - Health check timeout in seconds

**Database Resilience Configuration:**
- `POSTGRES_DSN=postgresql://user:pass@host:port/db` - Database connection string
- `DB_MIN_CONNECTIONS=1` - Minimum database connections in pool
- `DB_MAX_CONNECTIONS=10` - Maximum database connections in pool
- `DB_CONNECTION_TIMEOUT=30` - Database connection timeout in seconds
- `DB_HEALTH_CHECK_INTERVAL=60` - Database health check interval in seconds

**Config hot-reload:**
```bash
curl -X POST http://localhost:5000/admin/reload-config
```

**Override enabled agents:**
```bash
ENABLED_AGENTS=IntentRouter,RetrievalAgent make run-local
```

**Health & Metrics:**
```bash
# Health check
curl http://localhost:5000/health

# Metrics endpoint
curl http://localhost:9100/metrics

# Readiness check
curl http://localhost:5000/ready

# Production monitoring data
curl http://localhost:5000/api/monitoring

# Dependencies health check
curl http://localhost:5000/api/health/dependencies

# Database health status
curl http://localhost:5000/api/database/health
```

**Configuration Validation:**
```bash
# Validate system configuration
python3 scripts/validate_config.py

# Check configuration syntax
python3 -c "import json; json.load(open('config/system.json'))"
```

**Security Scanning:**
```bash
# Run comprehensive security scan
python3 scripts/security_scan.py

# Run security scan with failure on vulnerabilities
python3 scripts/security_scan.py --fail-on-vulnerabilities

# Run security scan with verbose output
python3 scripts/security_scan.py --verbose

# Run individual security tools
python3 -m bandit -r src/
python3 -m safety check
python3 -m pip_audit
```

## ✨ The Core Idea

Building complex features with AI can sometimes feel like a black box. This workflow aims to bring structure, clarity, and control to the process by:

1. **Defining Scope:** Clearly outlining what needs to be built with a Product Requirement Document (PRD).
2. **Detailed Planning:** Breaking down the PRD into a granular, actionable task list optimized for AI execution.
3. **AI-Optimized Implementation:** Guiding AI agents to tackle tasks efficiently with strategic human checkpoints.

This structured approach helps ensure the AI stays on track, makes it easier to debug issues, and gives you confidence in the generated code.

## Workflow: From Idea to Implemented Feature 💡➡️💻

Here's the step-by-step process using the `.md` files in this repository:

### 0️⃣ Select from Backlog (the execution engine)

For systematic development, start by selecting a high-impact feature from the backlog:

1. Ensure you have the `00_backlog.md` file from this repository accessible.
2. Review the prioritized table and select a feature based on:
   - **Points**: Lower numbers (1-3) for quick wins, higher (5-13) for complex features
   - **Priority**: 🔥 Critical, ⭐ High, 📈 Medium, 🔧 Low
   - **Status**: Choose "todo" items for new work
   - **Dependencies**: Check if prerequisites are completed
   - **Scores**: Higher scores (5.0+) indicate higher priority items

3. Use the backlog item ID (e.g., B-001) as input for PRD creation in the next step.
4. The AI can automatically parse the table format and generate PRDs using the AI-BACKLOG-META command.

*💡 **Pro Tip**: Check `200_naming-conventions.md` to understand the file organization and naming patterns used in this project.*

*📋 **For detailed backlog usage instructions and scoring system, see `100_backlog-guide.md`*

### 1️⃣ Create a Product Requirement Document (PRD)

First, lay out the blueprint for your feature. A PRD clarifies what you're building, for whom, and why.

You can create a lightweight PRD directly within your AI tool of choice:

1. Ensure you have the `01_create-prd.md` file from this repository accessible.
2. In your AI tool, initiate PRD creation:

    ```text
    Use @01_create-prd.md
    Here's the feature I want to build: [Describe your feature in detail]
    Backlog ID: [e.g., B-001 for Real-time Mission Dashboard]
    Reference these files to help you: [Optional: @file1.py @file2.ts @00_backlog.md]
    ```
    *(Pro Tip: For Cursor users, MAX mode is recommended for complex PRDs if your budget allows for more comprehensive generation.)*

    ![Example of initiating PRD creation](https://pbs.twimg.com/media/Go6DDlyX0AAS7JE?format=jpg&name=large)

### 2️⃣ Generate Your Task List from the PRD

With your PRD drafted (e.g., `MyFeature-PRD.md`), the next step is to generate a detailed, step-by-step implementation plan optimized for AI execution.

1. Ensure you have `02_generate-tasks.md` accessible.
2. In your AI tool, use the PRD to create tasks:

    ```text
    Now take @MyFeature-PRD.md and create tasks using @02_generate-tasks.md
    ```
    *(Note: Replace `@MyFeature-PRD.md` with the actual filename of the PRD you generated in step 1.)*

    ![Example of generating tasks from PRD](https://pbs.twimg.com/media/Go6FITbWkAA-RCT?format=jpg&name=medium)

### 3️⃣ Examine Your Task List

You'll now have a well-structured task list optimized for AI execution, with clear dependencies, priorities, and strategic human checkpoints. This provides a clear roadmap for implementation.

![Example of a generated task list](https://pbs.twimg.com/media/Go6GNuOWsAEcSDm?format=jpg&name=medium)

### 4️⃣ Execute Tasks with AI-Optimized Processing

To ensure methodical progress and allow for verification, we'll use `03_process-task-list.md`. This system is designed for AI agents using the v0.3.1 Ultra-Minimal Router architecture (Mistral 7B Instruct + Yi-Coder-9B-Chat-Q6_K) with strategic human oversight.

1. Create or ensure you have the `03_process-task-list.md` file accessible.
2. In your AI tool, tell the AI to start with the first task:

    ```text
    Please start on task T-1 and use @03_process-task-list.md
    ```
    *(Important: You only need to reference `@03_process-task-list.md` for the *first* task. The instructions within it guide the AI for subsequent tasks.)*

    The AI will attempt the task and then pause only when necessary for human review.

    ![Example of starting on a task with process-task-list.md](https://pbs.twimg.com/media/Go6I41KWcAAAlHc?format=jpg&name=medium)

### 5️⃣ AI-Optimized Execution with Strategic Checkpoints ✅

The AI system will automatically:
- **Execute tasks efficiently** with state caching and auto-advance
- **Handle errors gracefully** with automatic HotFix task generation
- **Pause strategically** only for high-risk operations (deployments, database changes)
- **Track progress** with clear status indicators (`[ ]`, `[x]`, `[!]`)
- **Prioritize by scores** when available for optimal task selection

You'll see a satisfying list of completed items grow, providing a clear visual of your feature coming to life!

![Example of a progressing task list with completed items](https://pbs.twimg.com/media/Go6KrXZWkAA_UuX?format=jpg&name=medium)

While it's not always perfect, this method has proven to be a very reliable way to build out larger features with AI assistance.

### Video Demonstration 🎥

If you'd like to see this in action, I demonstrated it on [Claire Vo's "How I AI" podcast](https://www.youtube.com/watch?v=fD4ktSkNCw4).

![Demonstration of AI Dev Tasks on How I AI Podcast](https://img.youtube.com/vi/fD4ktSkNCw4/maxresdefault.jpg)

## 🗂️ Files in this Repository

### **Core Workflow Files:**
* **`00_backlog.md`**: Prioritized list of future enhancements and features for systematic development planning with AI scoring system.
* **`01_create-prd.md`**: Guides the AI in generating a Product Requirement Document for your feature.
* **`02_generate-tasks.md`**: Takes the PRD markdown file as input and helps the AI break it down into a detailed, AI-optimized implementation task list.
* **`03_process-task-list.md`**: Instructs AI agents on how to process the generated task list with state management, auto-advance, and HotFix generation.

### **Automation & Tools:**
* **`100_backlog-automation.md`**: Documents the AI-BACKLOG-META system for automated backlog management and scoring.

### **Configuration & Setup:**
* **`200_naming-conventions.md`**: Explains the file naming conventions and organization structure.
* **`201_model-configuration.md`**: Documents the specific AI model setup (Mistral 7B Instruct + Yi-Coder-9B-Chat-Q6_K).

### **System Documentation:**
* **`README.md`**: This file - comprehensive guide to the AI Dev Tasks workflow.
* **`SYSTEM_OVERVIEW.md`**: Detailed technical overview of the entire AI development ecosystem.

## 🎯 Quick Reference

### **Score Ranges for Prioritization:**
- **5.0+**: Critical priority (🔥) - Foundation features, security, core functionality
- **3.0-4.9**: High priority (⭐) - UX improvements, productivity enhancements
- **1.5-2.9**: Medium priority (📈) - Integration features, automation
- **<1.5**: Low priority (🔧) - Technical debt, research, advanced capabilities

### **Effort Points:**
- **1-3 points**: Quick wins, low complexity
- **5 points**: Moderate complexity, significant value
- **8-13 points**: Complex features, high effort

### **AI Agent Instructions:**
- Parse `<!--score_total: X.X-->` comments for prioritization
- Use scores when available, fall back to human priority tags
- Consider dependencies before starting any item

## 🌟 Benefits

### Systematic Development
- **Prioritized Backlog** - Structured roadmap for feature development
- **Impact-Based Selection** - Choose features based on user value and effort
- **Consistent Workflow** - Standardized PRD → Tasks → Execution process
- **Progress Tracking** - Clear visibility into development priorities
- **Data-Driven Decisions** - AI scoring system for objective prioritization

### AI-Optimized Efficiency
- **State Caching** - AI maintains context across tasks without reloading
- **Auto-Advance** - Minimal human intervention for routine tasks
- **HotFix Generation** - Automatic error recovery with structured fix tasks
- **Strategic Pausing** - Human oversight only when necessary
- **Score-Based Prioritization** - AI agents use scoring data for optimal task selection

### Quality Assurance
- **Machine-Verifiable** - All completion criteria are automated
- **Regression Testing** - HotFixes include tests to prevent recurrence
- **Progress Tracking** - Clear status indicators for oversight
- **Error Recovery** - Structured approach to handling failures

### Safety & Control
- **Strategic Checkpoints** - Human review for high-risk operations
- **Safety Rules** - Clear guidelines for when to pause
- **Error Limits** - Stop execution after consecutive failures
- **State Persistence** - Maintain context across execution sessions

