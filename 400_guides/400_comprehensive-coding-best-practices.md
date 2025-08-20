<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_contributing-guidelines.md -->
<!-- MODULE_REFERENCE: 400_guides/400_file-analysis-guide.md -->
<!-- MEMORY_CONTEXT: HIGH - Comprehensive coding standards and conflict prevention -->
<!-- DATABASE_SYNC: REQUIRED -->

# 🛡️ Comprehensive Coding Best Practices

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Complete guide to coding standards and best practices | Writing new code or reviewing existing code | Apply practices
to current development work |



## TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Complete guide to coding standards and best practices | Writing new code or reviewing existing code | Apply practices
to current development work |



## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Comprehensive standards maintained
- **Priority**: 🔥 Critical - Essential for code quality and conflict prevention
- **Points**: 8 - High complexity, strategic importance
- **Dependencies**: 400_guides/400_contributing-guidelines.md, 400_guides/400_file-analysis-guide.md
- **Next Steps**: Regular review and integration with CI/CD pipeline

## 🚀 Quick Start

### **For Immediate Issues (10-minute triage):**

1. Run `python scripts/quick_conflict_check.py` for fast conflict detection
2. Check merge markers: `git grep -nE '^(<<<<<<<|=======|>>>>>>>)'`
3. Validate dependencies: `python -m pip check` (Python) or `npm ls --all` (Node.js)

### **For Systematic Problems (Deep audit):**

1. Run comprehensive health check: `python scripts/system_health_check.py --deep`
2. Execute conflict audit: `python scripts/conflict_audit.py --full`
3. Review results and implement fixes

### **For Prevention (Long-term stability):**

1. Set up CI gates using the guardrails in this document
2. Implement automated conflict detection
3. Regular maintenance using the prevention checklist

### **AI Development Ecosystem Quick Start:**

```bash
# Start the complete AI development ecosystem
cd dspy-rag-system
./quick_start.sh

# Start mission dashboard for real-time monitoring
./start_mission_dashboard.sh

# Run comprehensive system tests
./run_comprehensive_tests.sh

# Check system health and status
./check_status.sh

# Start production monitoring
python src/monitoring/production_monitor.py &

# Test Cursor AI integration
python test_cursor_context_engineering.py

# Core execution engine commands
python3.12 scripts/single_doorway.py generate "description"  # Start automated workflow
python3.12 scripts/single_doorway.py continue B-XXX  # Continue interrupted workflow
python3.12 scripts/single_doorway.py archive B-XXX  # Archive completed work
python scripts/process_tasks.py --status  # Check task status
python scripts/process_tasks.py --execute-all  # Execute all available tasks
python scripts/error_handler.py --test  # Test error handling
python scripts/state_manager.py --status  # Check state management

# Documentation and validation
python scripts/doc_coherence_validator.py --check-all  # Validate documentation
python scripts/documentation_retrieval_cli.py --help  # Documentation CLI
python scripts/documentation_indexer.py --help  # Index documentation

# Memory and context management
python scripts/update_cursor_memory.py  # Update memory context
python scripts/show_memory_hierarchy.py  # Show memory structure
python scripts/constitution_compliance_checker.py  # Check AI constitution

# Repository maintenance
python scripts/repo_maintenance.py  # Automated maintenance
python scripts/system_health_check.py  # System health check
python scripts/conflict_audit.py --full  # Deep conflict audit
python scripts/quick_conflict_check.py  # Quick conflict check

# Research and analysis
python scripts/research_dispersal_automation.py  # Research automation
python scripts/memory_benchmark.py  # Memory performance testing
```

## ⚠️ **Implementation Status & Limitations**

### **✅ Production-Ready Systems**

Your AI development ecosystem includes these fully implemented systems:

| System | Location | Status | Key Features |
|--------|----------|--------|--------------|
| **DSPy RAG System** | `dspy-rag-system/src/dspy_modules/` | ✅ Production Ready | Document processing, vector store, AI integration |
| **Mission Dashboard** | `dspy-rag-system/src/mission_dashboard/` | ✅ Production Ready | Real-time AI task monitoring with WebSocket |
| **N8N Workflows** | `dspy-rag-system/src/n8n_workflows/` | ✅ Production Ready | Automated backlog management and event processing |
| **Production Monitoring** | `dspy-rag-system/src/monitoring/` | ✅ Production Ready | Health checks, metrics, OpenTelemetry integration |
| **Error Recovery** | `dspy-rag-system/src/utils/` | ✅ Production Ready | 15+ error patterns, hotfix templates, retry logic |
| **Database Resilience** | `dspy-rag-system/src/utils/` | ✅ Production Ready | Connection pooling, health monitoring, graceful degradation |
| **Cursor AI Integration** | `dspy-rag-system/src/cursor_integration/` | ✅ Production Ready | Native AI with specialized agents |
| **Task Execution Engine** | `scripts/process_tasks.py` | ✅ Production Ready | Core CLI for backlog execution |
| **Error Handler** | `scripts/error_handler.py` | ✅ Production Ready | Comprehensive error handling and recovery |
| **State Manager** | `scripts/state_manager.py` | ✅ Production Ready | Task execution state tracking |
| **System Health Check** | `scripts/system_health_check.py` | ✅ Production Ready | Comprehensive system validation |
| **Documentation Validation** | `scripts/doc_coherence_validator.py` | ✅ Production Ready | Cross-reference and coherence checking |
| **Conflict Detection** | `scripts/conflict_audit.py` | ✅ Production Ready | Deep conflict analysis and resolution |

### **⚠️ Still To Be Implemented**

**Documentation Integration Enhancements:**

- Cross-reference updates to point to actual implemented systems
- Real implementation examples replacing theoretical ones
- Comprehensive integration guides

**CI/CD Pipeline Enhancements:**

- Automated performance testing with production monitoring
- Enhanced security scanning with alert integration
- Automated deployment validation using system health checks

**Advanced Performance Optimizations:**

- Query result caching for frequently accessed data
- Performance profiling tools for bottleneck detection
- Advanced memory and CPU optimization strategies

**Integration Testing Enhancements:**

- End-to-end testing of complete AI development ecosystem
- Cross-system integration tests
- Load testing under realistic workloads

## 📦 Tool Versions & Dependencies

### **Required Python Packages**

```bash
# Core conflict detection tools
pip install pycycle>=0.1.0          # Circular dependency detection
pip install bandit>=1.7.0           # Security scanning
pip install safety>=2.0.0           # Dependency vulnerability scanning
pip install psutil>=5.9.0           # System resource monitoring

# Optional but recommended
pip install pipdeptree>=2.0.0       # Dependency tree visualization
pip install black>=23.0.0           # Code formatting
pip install isort>=5.12.0           # Import sorting
pip install ruff>=0.1.0             # Fast Python linter
```

## **Required Node.js Packages**

```bash
# Core conflict detection tools
npm install -g madge@^6.0.0         # Circular dependency detection
npm install -g @redocly/cli@^1.0.0  # OpenAPI schema validation
npm install -g graphql-schema-linter@^1.0.0  # GraphQL schema validation

# Optional but recommended
npm install -g typescript@^5.0.0    # TypeScript compilation
npm install -g eslint@^8.0.0        # JavaScript/TypeScript linting
```

## **System Requirements**

```bash
# Minimum versions
Python: >= 3.12
Node.js: >= 18.0.0
Git: >= 2.30.0

# Operating systems
- macOS: 12.0+ (Monterey)
- Linux: Ubuntu 20.04+, CentOS 8+, or equivalent
- Windows: Windows 10/11 with WSL2 recommended
```

## **Installation Script**

```bash
#!/bin/bash
# install_conflict_detection_tools.sh

echo "🔧 Installing Conflict Detection Tools..."

# Check Python version
python_version=$(python3.12 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
if [[ $(echo "$python_version >= 3.12" | bc -l) -eq 0 ]]; then
    echo "❌ Python 3.12+ required, found $python_version"
    exit 1
fi

# Check Node.js version
node_version=$(node --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
if [[ $(echo "$node_version >= 18.0" | bc -l) -eq 0 ]]; then
    echo "❌ Node.js 18.0+ required, found $node_version"
    exit 1
fi

# Install Python packages
echo "📦 Installing Python packages..."
pip install pycycle>=0.1.0 bandit>=1.7.0 safety>=2.0.0 psutil>=5.9.0 pipdeptree>=2.0.0

# Install Node.js packages
echo "📦 Installing Node.js packages..."
npm install -g madge@^6.0.0 @redocly/cli@^1.0.0 graphql-schema-linter@^1.0.0

echo "✅ Installation complete!"
```

## **Version Compatibility Matrix**

| Tool | Python | Node.js | Git | Notes |
|------|--------|---------|-----|-------|
| `quick_conflict_check.py` | 3.11+ | - | 2.30+ | Core conflict detection |
| `conflict_audit.py` | 3.11+ | 18.0+ | 2.30+ | Deep audit capabilities |
| `pycycle` | 3.11+ | - | - | Circular dependency detection |
| `madge` | - | 18.0+ | - | Node.js circular dependencies |
| `bandit` | 3.11+ | - | - | Security scanning |
| `safety` | 3.11+ | - | - | Dependency vulnerabilities |

### **AI Development Ecosystem Tools**

| Tool | Location | Status | Notes |
|------|----------|--------|-------|
| **DSPy RAG System** | `dspy-rag-system/src/dspy_modules/` | ✅ Production Ready | Document processing, vector store, AI integration |
| **Mission Dashboard** | `dspy-rag-system/src/mission_dashboard/` | ✅ Production Ready | Real-time AI task monitoring with WebSocket |
| **N8N Workflows** | `dspy-rag-system/src/n8n_workflows/` | ✅ Production Ready | Automated backlog management and event processing |
| **Production Monitoring** | `dspy-rag-system/src/monitoring/` | ✅ Production Ready | Health checks, metrics, OpenTelemetry integration |
| **Error Recovery** | `dspy-rag-system/src/utils/` | ✅ Production Ready | 15+ error patterns, hotfix templates, retry logic |
| **Database Resilience** | `dspy-rag-system/src/utils/` | ✅ Production Ready | Connection pooling, health monitoring, graceful degradation |
| **Cursor AI Integration** | `dspy-rag-system/src/cursor_integration/` | ✅ Production Ready | Native AI with specialized agents |
| **Task Execution Engine** | `scripts/process_tasks.py` | ✅ Production Ready | Core CLI for backlog execution |
| **Error Handler** | `scripts/error_handler.py` | ✅ Production Ready | Comprehensive error handling and recovery |
| **State Manager** | `scripts/state_manager.py` | ✅ Production Ready | Task execution state tracking |
| **System Health Check** | `scripts/system_health_check.py` | ✅ Production Ready | Comprehensive system validation |
| **Documentation Validation** | `scripts/doc_coherence_validator.py` | ✅ Production Ready | Cross-reference and coherence checking |
| **Conflict Detection** | `scripts/conflict_audit.py` | ✅ Production Ready | Deep conflict analysis and resolution |

### **Core Execution Engine Scripts**

| Script | Location | Purpose | Key Features |
|--------|----------|---------|--------------|
| **Single Doorway System** | `scripts/single_doorway.py` | Core CLI for automated workflow | Backlog → PRD → tasks → execution → archive automation |
| **Task Execution Engine** | `scripts/process_tasks.py` | Core CLI for backlog execution | Automated task processing, state management, error handling |
| **Error Handler** | `scripts/error_handler.py` | Comprehensive error handling | Retry logic, graceful degradation, error reporting |
| **State Manager** | `scripts/state_manager.py` | Task execution state tracking | Progress tracking, execution history, metadata management |

### **Complete Script Index**

#### **Core Execution & Quality Assurance**

- **Single Doorway System**: `scripts/single_doorway.py` - Automated workflow from backlog → PRD → tasks → execution → archive
- **Task Execution**: `scripts/process_tasks.py` - Core CLI for backlog execution
- **Error Handling**: `scripts/error_handler.py` - Comprehensive error recovery
- **State Management**: `scripts/state_manager.py` - Execution state tracking
- **Conflict Detection**: `scripts/conflict_audit.py` - Deep conflict analysis
- **Quick Conflict Check**: `scripts/quick_conflict_check.py` - Fast conflict detection
- **System Health**: `scripts/system_health_check.py` - System validation

#### **Documentation & Validation** (See [`400_guides/400_documentation-retrieval-guide.md`](400_documentation-retrieval-guide.md))

- **Documentation Validation**: `scripts/doc_coherence_validator.py` - Cross-reference checking
- **Documentation Retrieval**: `scripts/documentation_retrieval_cli.py` - CLI for context retrieval
- **Documentation Indexing**: `scripts/documentation_indexer.py` - Automatic indexing
- **Documentation Navigator**: `scripts/documentation_navigator.py` - File discovery and navigation

#### **Memory & Context Management** (See [`100_memory/100_cursor-memory-context.md`](../100_memory/100_cursor-memory-context.md))

- **Memory Updates**: `scripts/update_cursor_memory.py` - Memory context updates
- **Constitution Compliance**: `scripts/constitution_compliance_checker.py` - AI constitution validation
- **Context Index**: `scripts/context_index_validator.py` - Context validation
- **Memory Benchmark**: `scripts/memory_benchmark.py` - Memory performance testing
- **Memory Hierarchy**: `scripts/show_memory_hierarchy.py` - Memory structure visualization

#### **Repository Maintenance** (See [`400_contributing-guidelines.md`](400_contributing-guidelines.md))

- **Repository Maintenance**: `scripts/repo_maintenance.py` - Automated maintenance
- **Database Recovery**: `scripts/auto_recover_database.py` - Database recovery
- **File Analysis**: `scripts/file_analysis_checklist.py` - File operation analysis
- **Backlog Parser**: `scripts/backlog_parser.py` - Backlog parsing and analysis
- **Conflict Audit**: `scripts/conflict_audit.py` - Deep conflict analysis
- **Quick Conflict Check**: `scripts/quick_conflict_check.py` - Fast conflict detection
- **Conflict Check**: `scripts/check-number-unique.sh` - Unique identifier validation

#### **Markdown & Documentation Tools** (VS Code Handles Basic Formatting)

- **Markdown Fixes**: `scripts/fix_markdown_blanks.py` - Comprehensive markdown normalization
- **Bare URL Fixes**: `scripts/fix_md034_bare_urls.py` - Bare URL formatting (VS Code doesn't handle)
- **Code Language Fixes**: `scripts/fix_md040_code_languages.py` - Code block language detection (VS Code doesn't handle)
- **HTML Anchor Fixes**: `scripts/fix_md033_html_anchors.py` - HTML anchor formatting (VS Code doesn't handle)

#### **Research & Analysis**

- **Research Dispersal**: `scripts/research_dispersal_automation.py` - Research automation
- **Research Integration**: `scripts/research_integration_helper.py` - Research helpers
- **Research Execution**: `scripts/run_research_dispersal.py` - Research dispersal execution

#### **Security & Validation**

- **Security Scanning**: `dspy-rag-system/scripts/security_scan.py` - Security vulnerability scanning
- **Configuration Validation**: `scripts/validate_config.py` - Configuration validation
- **Pre-commit Validation**: `scripts/pre_commit_doc_validation.sh` - Pre-commit documentation validation

#### **Setup & Configuration**

- **AI Model Setup**: `scripts/setup_ai_models.py` - AI model configuration
- **PRD Decision Helper**: `scripts/prd_decision_helper.py` - PRD creation assistance

#### **Note on Obsolete Scripts**

The following scripts have been **removed from this index** as they are obsolete:

**Redundant Markdown Fix Scripts (VS Code handles automatically):**

- ~~`fix_md012_multiple_blanks.py`~~ - VS Code `"files.trimFinalNewlines": true` handles this
- ~~`fix_md047_trailing_newlines.py`~~ - VS Code `"files.insertFinalNewline": true` handles this

**Problem-Specific Scripts (targets never implemented):**

- ~~`split_giant_guides.py`~~ - Giant guide splitting was never executed
- ~~`migrate_giant_guide_references.py`~~ - No split files exist to migrate references for
- ~~`migrate_memory_context.py`~~ - Modular memory context system was never implemented
- ~~`normalize_metadata_headers.py`~~ - Metadata normalization already completed

The remaining markdown fix scripts provide functionality that VS Code doesn't handle automatically, such as intelligent content analysis and bulk operations.

## 🔧 Core Execution Engine Implementation

### **1. Single Doorway System (`scripts/single_doorway.py`)**

The core CLI script that serves as the automated workflow orchestrator for the entire development process.

### **Key Features**

- **Automated Workflow**: Complete automation from backlog → PRD → tasks → execution → archive
- **Single Command Interface**: One command to start the entire development process
- **State Management**: Track workflow execution status and progress
- **Error Handling**: Comprehensive error recovery with retry logic
- **Archive Management**: Automated archiving of completed work
- **Cross-Platform Support**: Works on macOS, Linux, and Windows

### **Usage Examples**

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

**Note**: This system requires Python 3.12. The system will automatically detect and use `python3.12` if available via Homebrew.

## **2. Task Execution Engine (`scripts/process_tasks.py`)**

The core CLI script that serves as the execution engine for all backlog items in the AI development ecosystem.

#### **Key Features**

- **Automated Task Processing:** Parse and execute backlog items automatically
- **State Management**: Track task execution status and progress
- **Error Handling**: Comprehensive error recovery with retry logic
- **Dependency Resolution**: Handle task dependencies and execution order
- **Human Interaction**: Support for tasks requiring human input

#### **Usage Examples**

```bash
# Execute a specific backlog item
python scripts/process_tasks.py --backlog-id B-001

# Execute all available tasks
python scripts/process_tasks.py --execute-all

# Show task status
python scripts/process_tasks.py --status

# Execute with specific priority
python scripts/process_tasks.py --priority 🔥
```

## **Core Implementation Patterns**

```python
# Task execution with error handling
@retry_with_backoff(max_retries=3, base_delay=1)
def execute_task(task: Task) -> Dict[str, Any]:
    """Execute a single task with comprehensive error handling."""
    try:
        # Validate task requirements
        validate_task_requirements(task)

        # Execute task based on type
        if task.tech_footprint == "DSPy + PostgreSQL":
            result = execute_dspy_task(task)
        elif task.tech_footprint == "n8n + JavaScript":
            result = execute_n8n_task(task)
        else:
            result = execute_generic_task(task)

        # Update state
        state_manager.update_task_status(task.id, TaskStatus.COMPLETED)

        return {
            "success": True,
            "result": result,
            "execution_time": time.time() - start_time
        }

    except Exception as e:
        error_handler.handle_error(e, task)
        state_manager.update_task_status(task.id, TaskStatus.FAILED)
        return {
            "success": False,
            "error": str(e),
            "retry_count": task.retry_count
        }
```

## **2. Error Handler (`scripts/error_handler.py`)**

Comprehensive error handling and recovery system for task execution.

### **Key Features**

- **Error Classification**: Categorize errors by type and severity
- **Retry Logic**: Configurable retry strategies with exponential backoff
- **Graceful Degradation**: Continue operation despite non-critical errors
- **Error Reporting**: Structured error reporting and logging
- **Recovery Actions**: Automatic recovery for common error scenarios

#### **Error Categories**

```python
class ErrorCategory(Enum):
    """Error categories for classification."""
    NETWORK = "network"
    FILE_SYSTEM = "file_system"
    DATABASE = "database"
    PERMISSION = "permission"
    TIMEOUT = "timeout"
    VALIDATION = "validation"
    EXECUTION = "execution"
    UNKNOWN = "unknown"

class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

#### **Recovery Strategies**

```python
def handle_database_error(error: Exception, context: str) -> RecoveryAction:
    """Handle database-related errors with recovery strategies."""
    if "connection" in str(error).lower():
        return RecoveryAction(
            name="database_reconnection",
            description="Reconnect to database with exponential backoff",
            action_type="retry_with_backoff",
            parameters={"max_retries": 5, "base_delay": 2.0},
            success_criteria="Database connection established",
            estimated_time=30.0
        )
    elif "timeout" in str(error).lower():
        return RecoveryAction(
            name="query_optimization",
            description="Optimize query or increase timeout",
            action_type="query_optimization",
            parameters={"timeout": 60.0},
            success_criteria="Query completes within timeout",
            estimated_time=10.0
        )
```

### **3. State Manager (`scripts/state_manager.py`)**

State management system for tracking task execution progress and history.

#### **Key Features**

- **Execution Tracking**: Track task execution status and progress
- **Metadata Management**: Store and retrieve task metadata
- **Execution History**: Maintain complete execution history
- **Progress Monitoring**: Real-time progress tracking
- **State Persistence**: Persistent state storage in SQLite

#### **State Management Patterns**

```python
class StateManager:
    """Comprehensive state management system for task execution."""

    def update_task_status(self, task_id: str, status: TaskStatus,
                          progress: float = 0.0, error_message: str = None):
        """Update task execution status with progress tracking."""
        try:
            self.conn.execute("""
                UPDATE task_executions
                SET status = ?, progress = ?, error_message = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE task_id = ?
            """, (status.value, progress, error_message, task_id))

            self.conn.commit()
            logger.info(f"Updated task {task_id} status to {status.value}")

        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
            raise

    def get_execution_history(self, task_id: str) -> List[ExecutionRecord]:
        """Get complete execution history for a task."""
        cursor = self.conn.execute("""
            SELECT * FROM task_executions
            WHERE task_id = ?
            ORDER BY created_at DESC
        """, (task_id,))

        records = []
        for row in cursor.fetchall():
            records.append(ExecutionRecord(
                task_id=row[0],
                status=TaskStatus(row[1]),
                started_at=datetime.fromisoformat(row[2]),
                completed_at=datetime.fromisoformat(row[3]) if row[3] else None,
                error_message=row[4],
                retry_count=row[5],
                progress=row[6],
                execution_time=row[7]
            ))

        return records
```

### **Quick Setup Commands**

```bash
# One-liner setup (Unix/macOS)
curl -sSL https://raw.githubusercontent.com/your-repo/install_conflict_detection_tools.sh | bash

# Manual setup
git clone <your-repo>
cd <your-repo>
pip install -r requirements.txt
npm install -g madge @redocly/cli graphql-schema-linter

# Verify installation
python scripts/quick_conflict_check.py --help
python scripts/conflict_audit.py --help
python scripts/process_tasks.py --help

# Core execution engine verification
python scripts/process_tasks.py --status
python scripts/error_handler.py --test
python scripts/state_manager.py --status

# System health verification
python scripts/system_health_check.py
python scripts/doc_coherence_validator.py --check-all
```

## **Environment-Specific Setup**

### **Docker Environment**

```dockerfile
# Dockerfile for conflict detection environment
FROM python:3.12-slim

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

# Install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Node.js packages
RUN npm install -g madge@^6.0.0 @redocly/cli@^1.0.0 graphql-schema-linter@^1.0.0

# Copy scripts
COPY scripts/ /app/scripts/
WORKDIR /app
```

## **GitHub Actions Environment**

```yaml
# .github/workflows/conflict-detection.yml
name: Conflict Detection

on: [push, pull_request]

jobs:
  conflict-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python 3.12
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Set up Node.js 18
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install Python dependencies
        run: |
          pip install pycycle>=0.1.0 bandit>=1.7.0 safety>=2.0.0 psutil>=5.9.0

      - name: Install Node.js dependencies
        run: |
          npm install -g madge@^6.0.0 @redocly/cli@^1.0.0 graphql-schema-linter@^1.0.0

      - name: Run conflict detection
        run: |
          python scripts/quick_conflict_check.py
          python scripts/conflict_audit.py --full
```

## **Troubleshooting Common Issues**

### **Python Issues**

```bash
# If pycycle installation fails
pip install --upgrade pip setuptools wheel
pip install pycycle --no-cache-dir

# If bandit fails to run
pip install bandit[pyyaml]  # Include YAML support

# If safety check fails
pip install safety --upgrade
```

## **Node.js Issues**

```bash
# If madge fails to install
npm cache clean --force
npm install -g madge@^6.0.0

# If TypeScript compilation fails
npm install -g typescript@^5.0.0
npx tsc --version
```

```bash
# If git grep fails
git --version  # Should be >= 2.30.0
git config --global core.pager cat  # Disable pager for scripts
```

## **Performance Optimization**

### **For Large Repositories**

```bash
# Use faster alternatives for large repos
pip install ruff>=0.1.0  # Faster than flake8
npm install -g eslint@^8.0.0  # Faster than tslint

# Parallel execution
python scripts/quick_conflict_check.py --parallel
python scripts/conflict_audit.py --workers 4
```

## **Caching Strategies**

```bash
# Cache dependency checks
python scripts/quick_conflict_check.py --cache
python scripts/conflict_audit.py --cache-dir .cache

# Skip expensive checks when not needed
python scripts/conflict_audit.py --skip-circular-deps
python scripts/conflict_audit.py --skip-build-checks
```

## 📋 Systematic Approach

### **Phase 1: Quick Triage (10-minute wins)**

#### **1. Merge Marker Detection**

```bash
# Check for leftover merge markers
git grep -nE '^(<<<<<<<|=======|>>>>>>>)'

# Check for backup files
git ls-files -z | xargs -0 -n1 basename | grep -E '\.orig$|\.rej$'
```

## **2. Package Manager Conflicts**

```bash
# Python: Check for mixed package managers
find . -maxdepth 2 -name "requirements.txt" -o -name "pyproject.toml" -o -name "Pipfile" -o -name "poetry.lock"

# Node.js: Check for mixed lockfiles
find . -maxdepth 2 -name "package-lock.json" -o -name "yarn.lock" -o -name "pnpm-lock.yaml"
```

## **3. Dual Configuration Detection**

```bash
# Python: Check for multiple config files
find . -name ".flake8" -o -name ".ruff.toml" -o -name "pyproject.toml" -o -name "setup.cfg"

# TypeScript: Check for multiple config files
find . -name "tsconfig*.json" -o -name ".eslintrc*" -o -name "eslint.config.*"
```

## **4. Module Shadowing (Python)**

```bash
# Check for local modules shadowing stdlib
find . -maxdepth 3 -type f -name '*.py' | grep -E '/(email|json|jwt|requests|string|typing|dataclasses)\.py$'
```

## **5. Case-Sensitive Name Collisions**

```bash
# Check for case-sensitive collisions
git ls-files | awk '{print tolower($0)}' | sort | uniq -d
```

## **Phase 2: Deep Audit by Conflict Vector**

### **1. Dependency Graph Analysis**

**Python:**
```bash
# Check for dependency conflicts
python -m pip check
pipdeptree --warn fail

# Check for circular imports
pip install pycycle
pycycle path/to/pkg
```

**Node.js:**
```bash
# Check for peer dependency issues
npm ls --all

# Check for circular dependencies
npx madge --circular src
```

## **2. Build Toolchain & Module Resolution**

**TypeScript/JavaScript:**
```bash
# Check for path alias drift
npx tsc --noEmit

# Verify module resolution
npx tsc --listFiles | grep -E "(alias|path)"
```

**Python:**
```bash
# Check for namespace package issues
find . -name "__init__.py" -exec grep -l "namespace" {} \;
```

## **3. Interface/Contract Drift**

**API Contracts:**
```bash
# OpenAPI schema validation
npx @redocly/cli lint openapi.yaml

# GraphQL schema validation
npx graphql-schema-linter schema.graphql
```

## **4. Data Model & Migrations**

**Database Migrations:**
```bash
# Check for migration conflicts
alembic heads
alembic branches

# Prisma migration status
npx prisma migrate status
```

## **5. Test Configuration Drift**

**Test Environment Validation:**
```bash
# Python: Check test environment
python -c "import sys; print(sys.version); print(sys.path)"

# Node.js: Check test environment
node -e "console.log(process.version); console.log(process.env.NODE_ENV)"
```

## **Phase 3: Prevention & Guardrails**

### **CI/CD Environment Parity**

```yaml
# GitHub Actions example
- name: Environment Parity Check
  run: |
    echo "Node: $(node --version)"
    echo "Python: $(python --version)"
    echo "OS: $(uname -s)"
    echo "Arch: $(uname -m)"
```

## **Automated Conflict Detection**

```yaml
# Pre-commit hooks
- repo: local
  hooks:
    - id: conflict-check
      name: Check for merge conflicts
      entry: git grep -nE '^(<<<<<<<|=======|>>>>>>>)'
      language: system
      pass_filenames: false
```

## 💻 Code Standards (Enhanced)

### **1. Python Code Standards**

#### **Enhanced Style Guidelines**

```python
# Python Code Style Standards (Enhanced)

PYTHON_STANDARDS = {
    "style_guide": "PEP 8 with Black formatting",
    "line_length": 88,  # Black default
    "docstrings": "Google style docstrings",
    "type_hints": "Required for all functions",
    "naming": "snake_case for variables and functions",
    "classes": "PascalCase for class names",
    "constants": "UPPER_SNAKE_CASE for constants",

    # Conflict Prevention Additions
    "imports": {
        "order": "stdlib, third_party, local",
        "grouping": "Use isort for consistent import ordering",
        "avoid_shadowing": "Never create local modules that shadow stdlib"
    },
    "dependencies": {
        "pinning": "Pin major versions for critical dependencies",
        "peer_deps": "Explicitly handle peer dependencies",
        "conflict_resolution": "Use dependency resolution tools"
    },
    "error_handling": {
        "specific_exceptions": "Catch specific exceptions, not generic Exception",
        "logging": "Use structured logging for all errors",
        "recovery": "Implement graceful degradation"
    }
}

# Example of conflict-aware code
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ConflictAwareConfig:
    """Configuration with conflict prevention built-in.

    Attributes:
        environment: Current environment (dev/staging/prod)
        debug: Whether debug mode is enabled
        database_url: Database connection URL
        conflict_checks: Whether to run conflict detection
    """
    environment: str
    debug: bool
    database_url: str
    conflict_checks: bool = True

    def __post_init__(self):
        """Validate configuration and check for conflicts."""
        self._validate_environment()
        if self.conflict_checks:
            self._check_conflicts()

    def _validate_environment(self) -> None:
        """Validate environment configuration."""
        if self.environment not in ['dev', 'staging', 'prod']:
            raise ValueError(f"Invalid environment: {self.environment}")

        if self.environment == 'prod' and self.debug:
            logger.warning("DEBUG should be False in production")

    def _check_conflicts(self) -> None:
        """Check for common configuration conflicts."""
        # Check for conflicting environment variables
        # Check for duplicate configuration files
        # Check for dependency conflicts
        pass
```

## **2. Linter Configuration & Standards**

### **Unified Linter Setup**

This repository uses a **single, unified linter configuration** to prevent conflicts and ensure consistent code quality across all tools.

#### **Markdown Linting**

**Configuration File**: `.markdownlint.jsonc`

```jsonc
{
  // https://github.com/markdownlint/markdownlint/blob/main/docs/RULES.md
  "default": true,
  // Trailing spaces
  "MD009": false,
  // Line length (default: 80)
  "MD013": false,
  // Duplicate headings (e.g., nested headings)
  "MD024": false,
  // Ordered list item prefix
  "MD029": {
    "style": "ordered"
  },
  // Fenced code blocks should be surrounded by blank lines
  "MD031": false,
  // Emphasis as heading (e.g., table of contents)
  "MD036": false,
  // Bare URLs (enforce proper link formatting)
  "MD034": true,
  // Fenced code block language (require language specification)
  "MD040": true,
  // Code block style (allow fenced code blocks)
  "MD046": {
    "style": "fenced"
  }
}
```

**VS Code Integration**:

- VS Code references the external config file via `"markdownlint.configFile": ".markdownlint.jsonc"`
- Ensures consistent linting behavior across all tools

**Usage Commands**:
```bash
# Run markdown linting
markdownlint ./*.md

# Fix specific issues
markdownlint --fix ./*.md

# Check specific file
markdownlint README.md
```

## **Python Linting**

**Configuration File**: `pyproject.toml`

```toml
[tool.black]
line-length = 120
target-version = ["py39"]

[tool.ruff]
line-length = 120
target-version = "py39"
exclude = [
  "venv",
  "600_archives",
  "docs/legacy",
  "**/__pycache__"
]

[tool.ruff.lint]
select = ["E", "F", "I"]
ignore = ["E501"]  # Line too long - handled by black
# Note: F841 removed from ignore list to catch unused variables
```

**Usage Commands**:
```bash
# Format code with Black
black .

# Lint with Ruff
ruff check .

# Fix issues automatically
ruff check --fix .

# Sort imports
ruff check --select I --fix .
```

## **Import Resolution & Static Analysis**

### **Pyright Configuration Best Practices**

#### **"One Source Per Scope" Policy**
- **Root scope** (repo open in Cursor): `pyrightconfig.json` handles repo-wide analysis
- **Subproject scope** (dspy-rag-system/ opened directly): `dspy-rag-system/pyrightconfig.json` handles local development
- **No conflicts**: Avoid `[tool.pyright]` in pyproject.toml files
- **VS Code alignment**: `.vscode/settings.json` mirrors root pyrightconfig.json

#### **Common Import Resolution Issues**
```bash
# Check Pyright configuration
pyright --version
pyright --project dspy-rag-system/

# Troubleshoot import issues
pyright --verbose dspy-rag-system/src/
```

#### **"Undefined Name" Errors (Ruff/Pyright)**

**What these errors mean:**
- **"Undefined name `os`"**: The code uses `os.environ` but `import os` is missing
- **"Undefined name `sys`"**: The code uses `sys.path` but `import sys` is missing
- **Static analysis tools**: Both Ruff and Pyright catch these before runtime to prevent `NameError` exceptions

**Common causes and solutions:**

1. **Missing imports** (most common):
   ```python
   # ❌ Error: os is not defined
   os.environ['VAR'] = 'value'

   # ✅ Solution: Add import
   import os
   os.environ['VAR'] = 'value'
   ```

2. **Typo in variable name**:
   ```python
   # ❌ Error: variable_name is not defined
   print(variable_name)  # typo in variable name

   # ✅ Solution: Fix the typo
   print(variable_name)  # correct spelling
   ```

3. **Scope issues**:
   ```python
   # ❌ Error: variable not defined in current scope
   def function():
       print(global_var)  # global_var not in scope

   # ✅ Solution: Use global or pass as parameter
   def function():
       global global_var
       print(global_var)
   ```

4. **Database query results** (common in scripts):
   ```python
   # ❌ Error: Object of type None is not subscriptable
   cursor.execute("SELECT id FROM documents WHERE filename = %s", (filename,))
   document_id = cursor.fetchone()[0]  # fetchone() can return None

   # ✅ Solution: Check for None before accessing
   cursor.execute("SELECT id FROM documents WHERE filename = %s", (filename,))
   result = cursor.fetchone()
   if result is None:
       print(f"Document not found: {filename}")
       continue
   document_id = result[0]
   ```

**Quick fix workflow:**
```bash
# 1. Identify the error
ruff check tests/test_secrets_manager.py
# Output: "Undefined name `os`" at line 333

# 2. Add missing import
# Add: import os at the top of the file

# 3. Verify the fix
ruff check tests/test_secrets_manager.py
# Output: "All checks passed!"

# 4. Run isort to ensure proper import ordering
isort tests/test_secrets_manager.py
```

**Best practices to avoid these errors:**
1. **Use linting tools**: Run Ruff/Pyright regularly to catch these early
2. **IDE integration**: Most IDEs (like Cursor) show these errors in real-time
3. **Import organization**: Use `isort` to keep imports organized and catch missing ones
4. **Type hints**: Use type hints to help static analyzers catch more issues

**Systematic fixes for test files:**
```bash
# Find all undefined name errors in tests
ruff check dspy-rag-system/tests/ --select F821

# Common missing imports in test files:
# - import os (for file operations, environment variables)
# - import sys (for sys.exit(), sys.path)
# - import tempfile (for temporary file operations)

# Quick fix pattern for test files:
# 1. Add missing imports at the top
# 2. Run isort to organize imports
# 3. Verify with ruff check
```

**Common patterns in test files:**
- **File operations**: `os.path.join()`, `os.path.exists()`, `os.unlink()` → need `import os`
- **Environment variables**: `os.getenv()`, `os.environ` → need `import os`
- **Process operations**: `os.getpid()` → need `import os`
- **System operations**: `sys.exit()`, `sys.path` → need `import sys`
- **Temporary files**: `tempfile.mkdtemp()` → need `import tempfile`

**Common patterns in database scripts:**
- **Database queries**: `cursor.fetchone()[0]` → can return `None`, need null check
- **Query results**: `result = cursor.fetchone(); result[0]` → check `if result is not None`
- **Aggregate queries**: `SUM()` can return `None` for empty tables → use `or 0` default

#### **Configuration Files**
```json
// pyrightconfig.json (root)
{
  "pythonVersion": "3.12",
  "typeCheckingMode": "basic",
  "extraPaths": ["dspy-rag-system/src"],
  "exclude": ["**/.venv/**", "**/__pycache__/**", "**/.pytest_cache/**"]
}
```

### **Test Import Management**
> **📖 For detailed test import guidance, see `dspy-rag-system/tests/README-dev.md`**

- **Centralized setup**: Use `conftest.py` for import path management
- **Static analysis compatibility**: `tests/__init__.py` handles sys.path for tools
- **No manual sys.path**: Remove per-file path manipulation
- **Dynamic imports**: Keep for legitimate use cases (database mocking, model switching)

### **Database Operations & Static Analysis**
> **📖 For database utilities, see `dspy-rag-system/scripts/database_utils.py`**

#### **Context-Aware Database Utilities**
- **Operational scripts**: Use `context="operational"` for fast development (assumes data exists)
- **Production code**: Use `context="production"` for robust error handling
- **No more Pyright errors**: Eliminates "Object of type None is not subscriptable" issues

#### **Usage Patterns**
```python
# Operational scripts (fast development)
from database_utils import get_database_stats
stats = get_database_stats("operational")  # Assumes data exists
print(f"Total: {stats['total_documents']}")

# Production code (robust error handling)
try:
    stats = get_database_stats("production")  # Raises RuntimeError if no data
    print(f"Total: {stats['total_documents']}")
except RuntimeError as e:
    print(f"Database error: {e}")
```

#### **Available Functions**
- `get_database_stats(context)` - Database statistics
- `get_chunk_size_analysis(context)` - Chunk size analysis
- `get_cross_reference_analysis(context)` - Cross-reference analysis
- `get_duplicate_chunk_count(context)` - Duplicate chunk count
- `get_storage_analysis(context)` - Storage analysis
- `execute_query(query, context)` - Execute queries with context-aware handling

### **Quality Standards for Critical Files**
> **📖 For detailed quality standards, see `400_guides/400_code-criticality-guide.md`**

- **Tier 1/2 files**: Zero F841 errors allowed
- **Pre-commit gates**: All linter checks must pass
- **CI/CD integration**: F841 errors treated as failures
- **Code review**: Unused variable patterns reviewed

## **Unused Variable Handling (F841)**

### **When to Fix vs. Ignore F841 Errors**

**✅ Fix These Cases:**
- Variable overwriting in tests (e.g., `error_message = "x"; error_message = "y"`)
- Unused return values from function calls
- Dead code assignments
- Unused test setup variables
- Variables assigned but never referenced

**⚠️ Consider Ignoring These Cases:**
- Debug variables during development (use `_debug_var` naming)
- Callback parameters that may not always be used
- Test variables that are intentionally unused
- Temporary variables during refactoring

### **Best Practices:**

#### **1. Use Unique Variable Names**
```python
# ❌ Bad: Variable overwriting
def test_severity_scores():
    error_message = "Security violation"
    error_message = "File not found"  # Overwrites previous!

# ✅ Good: Unique variable names
def test_severity_scores():
    critical_error = "Security violation"
    medium_error = "File not found"
```

#### **2. Remove Unused Variables**
```python
# ❌ Bad: Unused variable
def process_data(data):
    result = transform(data)
    unused_var = calculate_extra(data)  # Never used
    return result

# ✅ Good: Remove unused variable
def process_data(data):
    result = transform(data)
    return result
```

#### **3. Use Descriptive Names for Test Data**
```python
# ❌ Bad: Generic names
def test_multiple_patterns():
    error = "Database timeout"
    error = "Authentication failed"  # Overwrites

# ✅ Good: Descriptive names
def test_multiple_patterns():
    timeout_error = "Database timeout"
    auth_error = "Authentication failed"
```

#### **4. Handle Intentionally Unused Variables**
```python
# ✅ Good: Use underscore prefix
def callback_function(event, _unused_context):
    process_event(event)

# ✅ Good: Use noqa comment for specific cases
def test_with_unused_setup():
    setup_data = create_test_data()  # noqa: F841
    # setup_data used implicitly by test framework
```

### **Test-Specific Guidelines:**
> **📖 For comprehensive test variable management, see `dspy-rag-system/tests/README-dev.md`**

- **Avoid variable overwriting** in test functions
- **Use descriptive variable names** for test data
- **Remove unused test setup variables**
- **Keep dynamic imports** for legitimate use cases (database mocking, model switching)

#### **Common Test Patterns**
```python
# ✅ Good: Test with unique variables
def test_error_patterns():
    # Test critical severity
    critical_error = "Security violation: blocked pattern detected"
    critical_analysis = analyze_error_pattern(critical_error, "SecurityError")
    assert critical_analysis.severity_score == 1.0

    # Test medium severity
    medium_error = "File not found: /path/to/file"
    medium_analysis = analyze_error_pattern(medium_error, "FileNotFoundError")
    assert medium_analysis.severity_score == 0.5
```

### **Configuration Guidelines:**

#### **Current Ruff Configuration**
```toml
[tool.ruff.lint]
select = ["E", "F", "I"]
ignore = ["E501"]  # Line too long - handled by black
# Note: F841 removed from ignore list to catch unused variables
```

#### **When to Use Per-File Ignores**
```toml
[tool.ruff.lint.per-file-ignores]
# Only for specific, justified cases
"legacy_file.py" = ["F841"]  # Legacy code that can't be easily fixed
"generated_file.py" = ["F841"]  # Auto-generated code
```

### **Quality Gates Integration:**

#### **Pre-commit Checks**
```bash
# Check for unused variables
ruff check --select F841 .

# Fix automatically fixable issues
ruff check --select F841 --fix .
```

#### **CI/CD Integration**
```bash
# Fail on unused variables in critical files
ruff check --select F841 dspy-rag-system/src/ scripts/

# Allow warnings in test files (with review)
ruff check --select F841 dspy-rag-system/tests/ || echo "Review F841 warnings in tests"
```

### **Migration Strategy:**

#### **For Existing Code**
1. **Identify F841 errors**: `ruff check --select F841 .`
2. **Fix variable overwriting**: Use unique variable names
3. **Remove unused variables**: Clean up dead code
4. **Add noqa comments**: Only for justified cases
5. **Update tests**: Apply test-specific guidelines

#### **For New Code**
1. **Follow best practices** from the start
2. **Use descriptive variable names**
3. **Avoid variable overwriting**
4. **Remove unused variables immediately**

## **SQL Linting**

**Configuration File**: `.sqlfluff`

```ini
[sqlfluff]
dialect = postgres
templater = jinja
exclude_rules = L009
verbose = 0

[rules]
max_line_length = 120

[sqlfluff:rules:L016]
ignore_comment_lines = true

[sqlfluff:indentation]
indented_joins = true

[sqlfluff:rules:capitalisation.keywords]
capitalisation_policy = upper

[tool:paths]
ignore = [
  "600_archives/**",
  "docs/legacy/**"
]
```

**Usage Commands**:
```bash
# Lint SQL files
sqlfluff lint .

# Fix SQL issues
sqlfluff fix .

# Check specific file
sqlfluff lint path/to/file.sql
```

## **JavaScript/TypeScript Linting**

**Configuration**: ESLint (referenced in installation)

```bash
# Install ESLint
npm install -g eslint@^8.0.0

# Run ESLint
eslint src/

# Fix issues
eslint src/ --fix
```

## **Linter Integration in Quality Gates**

| Linter | Quality Gate | Command | Purpose |
|--------|-------------|---------|---------|
| **Markdown** | Documentation Quality | `markdownlint ./*.md` | Ensure markdown standards |
| **Python** | Code Quality | `ruff check . && black --check .` | Ensure Python standards |
| **SQL** | Database Quality | `sqlfluff lint .` | Ensure SQL standards |
| **JavaScript** | Frontend Quality | `eslint src/` | Ensure JS/TS standards |

### **Linter Benefits**

- ✅ **Single Source of Truth**: One config file per language for all linter rules
- ✅ **Consistent Behavior**: Same rules applied in VS Code and command line
- ✅ **Easier Maintenance**: One config file to update for each language
- ✅ **Better Documentation**: All rules documented in config files

#### **Linter Usage in Development Workflow**

```bash
# Pre-commit linting check
markdownlint ./*.md && ruff check . && sqlfluff lint .

# Auto-fix common issues
markdownlint --fix ./*.md && ruff check --fix . && sqlfluff fix .

# CI/CD integration
python scripts/quick_conflict_check.py  # Includes linter config validation
```

## **Conflict-Aware Function Standards**

```python
# Conflict-Aware Function Standards

def process_ai_request_with_conflict_prevention(
    prompt: str,
    model_name: str = "cursor-native-ai",
    max_tokens: int = 1000,
    temperature: float = 0.7,
    conflict_check: bool = True
) -> Dict[str, Any]:
    """Process AI model request with conflict prevention.

    Args:
        prompt: Input prompt for AI model
        model_name: Name of the AI model to use
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0.0 to 1.0)
        conflict_check: Whether to run conflict detection

    Returns:
        Dict containing response data and metadata

    Raises:
        ValueError: If prompt is empty or invalid
        ModelNotFoundError: If specified model is not available
        RateLimitError: If rate limit is exceeded
        ConflictError: If configuration conflicts detected
    """
    # Input validation with conflict awareness
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    if temperature < 0.0 or temperature > 1.0:
        raise ValueError("Temperature must be between 0.0 and 1.0")

    # Conflict detection
    if conflict_check:
        check_model_conflicts(model_name)
        check_environment_conflicts()

    # Process request with error handling
    try:
        response = ai_client.generate(
            prompt=prompt,
            model=model_name,
            max_tokens=max_tokens,
            temperature=temperature
        )

        return {
            "success": True,
            "content": response.content,
            "tokens_used": response.tokens_used,
            "model": model_name,
            "timestamp": datetime.utcnow().isoformat(),
            "conflict_checked": conflict_check
        }

    except Exception as e:
        logger.error(f"AI request failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "model": model_name,
            "conflict_checked": conflict_check
        }

def check_model_conflicts(model_name: str) -> None:
    """Check for model-specific conflicts."""
    # Check for model availability
    # Check for version conflicts
    # Check for resource conflicts
    pass

def check_environment_conflicts() -> None:
    """Check for environment-specific conflicts."""
    # Check for conflicting environment variables
    # Check for conflicting configuration files
    # Check for conflicting dependencies
    pass
```

## **3. Enhanced Error Handling Standards**

### **Conflict-Aware Exception Hierarchy**

```python
# Enhanced Error Handling Standards

class AIEcosystemError(Exception):
    """Base exception for AI ecosystem errors."""
    pass

class ConflictError(AIEcosystemError):
    """Raised when configuration or dependency conflicts are detected."""
    pass

class ValidationError(AIEcosystemError):
    """Raised when input validation fails."""
    pass

class ModelNotFoundError(AIEcosystemError):
    """Raised when AI model is not available."""
    pass

class RateLimitError(AIEcosystemError):
    """Raised when rate limit is exceeded."""
    pass

class DependencyConflictError(ConflictError):
    """Raised when dependency conflicts are detected."""
    pass

class ConfigurationConflictError(ConflictError):
    """Raised when configuration conflicts are detected."""
    pass

def safe_execute_with_conflict_detection(
    func: Callable,
    *args,
    conflict_check: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """Execute function with comprehensive error handling and conflict detection.

    Args:
        func: Function to execute
        *args: Positional arguments
        conflict_check: Whether to run conflict detection
        **kwargs: Keyword arguments

    Returns:
        Dict with result or error information
    """
    # Pre-execution conflict check
    if conflict_check:
        try:
            check_execution_conflicts(func, *args, **kwargs)
        except ConflictError as e:
            return {
                "success": False,
                "error_type": "conflict",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    # Execute function with error handling
    try:
        result = func(*args, **kwargs)
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
            "conflict_checked": conflict_check
        }

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return {
            "success": False,
            "error_type": "validation",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

    except ModelNotFoundError as e:
        logger.error(f"Model not found: {e}")
        return {
            "success": False,
            "error_type": "model_not_found",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded: {e}")
        return {
            "success": False,
            "error_type": "rate_limit",
            "error": str(e),
            "retry_after": getattr(e, 'retry_after', 60),
            "timestamp": datetime.utcnow().isoformat()
        }

    except ConflictError as e:
        logger.error(f"Conflict detected: {e}")
        return {
            "success": False,
            "error_type": "conflict",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "success": False,
            "error_type": "unexpected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

def check_execution_conflicts(func: Callable, *args, **kwargs) -> None:
    """Check for conflicts before function execution."""
    # Check for dependency conflicts
    # Check for configuration conflicts
    # Check for resource conflicts
    pass
```

## **4. Enhanced Logging Standards**

### **Conflict-Aware Structured Logging**

```python
# Enhanced Logging Standards

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

class ConflictAwareLogger:
    """Structured logger with conflict detection capabilities."""

    def __init__(self, name: str, level: str = "INFO", conflict_detection: bool = True):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.conflict_detection = conflict_detection

        # Configure JSON formatter
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s"}'
        )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_event_with_conflict_check(
        self,
        event_type: str,
        data: Dict[str, Any],
        level: str = "INFO",
        check_conflicts: bool = True
    ) -> None:
        """Log structured event data with optional conflict detection."""
        log_data = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "conflict_checked": check_conflicts and self.conflict_detection
        }

        # Conflict detection
        if check_conflicts and self.conflict_detection:
            conflicts = self._detect_event_conflicts(event_type, data)
            if conflicts:
                log_data["conflicts"] = conflicts
                level = "WARNING"

        getattr(self.logger, level.lower())(
            f"Event: {json.dumps(log_data)}"
        )

    def log_ai_request_with_conflict_check(
        self,
        prompt: str,
        model: str,
        response_time: float,
        check_conflicts: bool = True
    ) -> None:
        """Log AI request with performance metrics and conflict detection."""
        self.log_event_with_conflict_check("ai_request", {
            "prompt_length": len(prompt),
            "model": model,
            "response_time": response_time,
            "tokens_used": getattr(response_time, 'tokens_used', 0)
        }, check_conflicts=check_conflicts)

    def log_conflict_detected(
        self,
        conflict_type: str,
        details: Dict[str, Any],
        severity: str = "WARNING"
    ) -> None:
        """Log detected conflicts."""
        self.log_event_with_conflict_check("conflict_detected", {
            "conflict_type": conflict_type,
            "details": details,
            "severity": severity
        }, level=severity, check_conflicts=False)

    def _detect_event_conflicts(self, event_type: str, data: Dict[str, Any]) -> List[str]:
        """Detect conflicts in event data."""
        conflicts = []

        # Check for common conflict patterns
        if event_type == "ai_request":
            if data.get("model") and data.get("model") not in self._get_available_models():
                conflicts.append(f"Model {data['model']} not available")

        return conflicts

    def _get_available_models(self) -> List[str]:
        """Get list of available AI models."""
        # Implementation to get available models
        return ["cursor-native-ai", "gpt-4", "claude-3"]
```

## 🎯 **Real-World Implementation Examples**

### **Production-Ready AI Development Ecosystem**

The coding standards above are implemented in your actual AI development ecosystem:

**Core Systems:**

- **DSPy RAG System** (`dspy-rag-system/src/dspy_modules/`) - Document processing, vector store, AI integration
- **Mission Dashboard** (`dspy-rag-system/src/mission_dashboard/`) - Real-time AI task monitoring with WebSocket
- **N8N Workflows** (`dspy-rag-system/src/n8n_workflows/`) - Automated backlog management and event processing
- **Production Monitoring** (`dspy-rag-system/src/monitoring/`) - Health checks, metrics, OpenTelemetry integration
- **Error Recovery** (`dspy-rag-system/src/utils/`) - 15+ error patterns, hotfix templates, retry logic
- **Database Resilience** (`dspy-rag-system/src/utils/`) - Connection pooling, health monitoring, graceful degradation
- **Cursor AI Integration** (`dspy-rag-system/src/cursor_integration/`) - Native AI with specialized agents

**Quick Start Commands**:
```bash
# Start the complete AI development ecosystem
cd dspy-rag-system
./quick_start.sh

# Start mission dashboard for real-time monitoring
./start_mission_dashboard.sh

# Run comprehensive system tests
./run_comprehensive_tests.sh

# Check system health and status
./check_status.sh
```

## 🛡️ Quality Gates (Enhanced)

### **Enhanced Quality Gates for Solo Development**

| Gate | Purpose | Criteria | Tools | Conflict Prevention |
|------|---------|----------|-------|-------------------|
| **Conflict Check** | Prevent configuration conflicts | No merge markers, no package conflicts, no dual configs | `python scripts/quick_conflict_check.py` | Automated detection |
| **Task Execution** | Validate task execution engine | Task processing, state management, error handling | `python scripts/process_tasks.py --test` | Core execution validation |
| **Error Handling** | Validate error recovery system | Error classification, retry logic, recovery actions | `python scripts/error_handler.py --test` | Error handling validation |
| **State Management** | Validate state tracking system | Progress tracking, execution history, metadata management | `python scripts/state_manager.py --test` | State management validation |
| **System Health Check** | Validate system integrity | All components operational, database connectivity, AI services | `python scripts/system_health_check.py` | Comprehensive validation |
| **Documentation Validation** | Ensure documentation coherence | Cross-references valid, naming conventions, backlog alignment | `python scripts/doc_coherence_validator.py` | Automated coherence checking |
| **Memory Context** | Validate memory scaffolding | Memory updates, context validation, hierarchy integrity | `python scripts/update_cursor_memory.py` | Memory context validation |
| **Repository Maintenance** | Validate repository health | Automated maintenance, file analysis, backlog parsing | `python scripts/repo_maintenance.py` | Repository health validation |
| **Code Review** | Ensure code quality | Standards compliance, logic correctness, conflict awareness | Self-review + conflict detection | Manual + automated |
| **Testing** | Verify functionality | Unit tests, integration tests, conflict tests | `python -m pytest -v` (preferred) · `./dspy-rag-system/run_tests.sh --tiers 1 --kinds smoke` (shim) | Test environment validation |
| **Documentation** | Maintain clarity | Documentation completeness, conflict documentation | Manual review + conflict docs | Conflict resolution docs |
| **Security** | Prevent vulnerabilities | Security validation, conflict-aware security | `python dspy-rag-system/src/monitoring/production_monitor.py` | Conflict security analysis |
| **Performance** | Ensure efficiency | Performance checks, conflict performance impact | Mission dashboard monitoring | Conflict performance analysis |
| **Deployment** | Safe deployment | Environment parity, conflict-free deployment | `./dspy-rag-system/check_status.sh` | Conflict deployment validation |

### **Enhanced Quality Checklist**

```python
# Enhanced Quality Checklist with Conflict Prevention

ENHANCED_QUALITY_CHECKLIST = {
    "conflict_prevention": [
        "No merge markers in code",
        "No package manager conflicts",
        "No dual configuration files",
        "No module shadowing issues",
        "No case-sensitive name collisions",
        "No circular dependencies",
        "No path alias drift",
        "No interface/contract drift"
    ],
    "code_standards": [
        "Code follows PEP 8 style guidelines",
        "Black formatting applied",
        "Type hints added to functions",
        "Docstrings added to functions and classes",
        "Import ordering follows standards",
        "No stdlib module shadowing"
    ],
    "testing": [
        "Unit tests added for new functionality",
        "Tests pass successfully",
        "Test coverage is adequate",
        "Edge cases are tested",
        "Conflict scenarios are tested",
        "Test environment is validated"
    ],
    "documentation": [
        "Code is self-documenting",
        "Docstrings are clear and complete",
        "README is updated if needed",
        "API documentation is current",
        "Conflict resolution is documented",
        "Configuration conflicts are documented"
    ],
    "security": [
        "Input validation is implemented",
        "Error handling is secure",
        "No sensitive data is exposed",
        "Security best practices are followed",
        "Conflict-related security issues are addressed",
        "Configuration conflicts don't create security holes"
    ],
    "performance": [
        "No obvious performance issues",
        "Memory usage is reasonable",
        "Response times are acceptable",
        "Resource usage is optimized",
        "Conflict detection doesn't impact performance",
        "Conflict resolution is efficient"
    ],
    "deployment": [
        "All tests pass in deployment environment",
        "Configuration is correct",
        "Dependencies are properly specified",
        "Deployment process is documented",
        "Environment parity is validated",
        "Conflict-free deployment is ensured"
    ]
}

def run_quality_check() -> Dict[str, Any]:
    """Run enhanced quality check with conflict prevention."""
    results = {
        "conflict_prevention": check_conflict_prevention(),
        "code_standards": check_code_standards(),
        "testing": check_testing(),
        "documentation": check_documentation(),
        "security": check_security(),
        "performance": check_performance(),
        "deployment": check_deployment()
    }

    all_passed = all(results.values())

    return {
        "quality_check_passed": all_passed,
        "results": results,
        "failed_checks": [k for k, v in results.items() if not v],
        "conflict_issues": results.get("conflict_prevention", {}).get("issues", [])
    }

def check_conflict_prevention() -> Dict[str, Any]:
    """Check for common conflict issues."""
    issues = []

    # Check for merge markers
    if has_merge_markers():
        issues.append("Merge markers detected")

    # Check for package conflicts
    if has_package_conflicts():
        issues.append("Package conflicts detected")

    # Check for dual configs
    if has_dual_configs():
        issues.append("Dual configuration files detected")

    return {
        "passed": len(issues) == 0,
        "issues": issues
    }
```

## 🔧 Implementation Tools

### **Quick Conflict Check Script**

```python
#!/usr/bin/env python3
"""
Quick Conflict Check Script

Runs the 10-minute triage checks for immediate conflict detection.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any

class QuickConflictChecker:
    def __init__(self):
        self.issues = []
        self.warnings = []

    def check_merge_markers(self) -> bool:
        """Check for leftover merge markers."""
        try:
            result = subprocess.run(
                ['git', 'grep', '-nE', '^(<<<<<<<|=======|>>>>>>>)'],
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                self.issues.append(f"Merge markers found:\n{result.stdout}")
                return False
            return True
        except Exception as e:
            self.warnings.append(f"Could not check merge markers: {e}")
            return True

    def check_package_conflicts(self) -> bool:
        """Check for package manager conflicts."""
        conflicts = []

        # Check Python package managers
        python_configs = list(Path('.').glob('requirements.txt')) + \
                        list(Path('.').glob('pyproject.toml')) + \
                        list(Path('.').glob('Pipfile'))

        if len(python_configs) > 1:
            conflicts.append(f"Multiple Python package managers: {python_configs}")

        # Check Node.js package managers
        node_configs = list(Path('.').glob('package-lock.json')) + \
                      list(Path('.').glob('yarn.lock')) + \
                      list(Path('.').glob('pnpm-lock.yaml'))

        if len(node_configs) > 1:
            conflicts.append(f"Multiple Node.js package managers: {node_configs}")

        if conflicts:
            self.issues.extend(conflicts)
            return False
        return True

    def check_dual_configs(self) -> bool:
        """Check for dual configuration files."""
        conflicts = []

        # Check Python configs
        python_configs = list(Path('.').glob('.flake8')) + \
                        list(Path('.').glob('.ruff.toml')) + \
                        list(Path('.').glob('pyproject.toml'))

        if len(python_configs) > 1:
            conflicts.append(f"Multiple Python config files: {python_configs}")

        # Check TypeScript configs
        ts_configs = list(Path('.').glob('tsconfig*.json')) + \
                    list(Path('.').glob('.eslintrc*')) + \
                    list(Path('.').glob('eslint.config.*'))

        if len(ts_configs) > 1:
            conflicts.append(f"Multiple TypeScript config files: {ts_configs}")

        if conflicts:
            self.issues.extend(conflicts)
            return False
        return True

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all quick conflict checks."""
        checks = [
            ("merge_markers", self.check_merge_markers),
            ("package_conflicts", self.check_package_conflicts),
            ("dual_configs", self.check_dual_configs)
        ]

        results = {}
        for name, check_func in checks:
            results[name] = check_func()

        return {
            "all_passed": all(results.values()),
            "results": results,
            "issues": self.issues,
            "warnings": self.warnings
        }

def main():
    checker = QuickConflictChecker()
    results = checker.run_all_checks()

    if results["all_passed"]:
        print("✅ All conflict checks passed")
        sys.exit(0)
    else:
        print("❌ Conflict issues detected:")
        for issue in results["issues"]:
            print(f"  - {issue}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### **Comprehensive Conflict Audit Script**

```python
#!/usr/bin/env python3
"""
Comprehensive Conflict Audit Script

Runs deep audit checks for systematic conflict detection.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any

class ConflictAuditor:
    def __init__(self, full_audit: bool = False):
        self.full_audit = full_audit
        self.issues = []
        self.warnings = []

    def check_dependency_conflicts(self) -> Dict[str, Any]:
        """Check for dependency conflicts."""
        results = {}

        # Python dependency conflicts
        try:
            result = subprocess.run(
                ['python', '-m', 'pip', 'check'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                results["python"] = result.stdout
                self.issues.append(f"Python dependency conflicts: {result.stdout}")
            else:
                results["python"] = "No conflicts"
        except Exception as e:
            self.warnings.append(f"Could not check Python dependencies: {e}")

        # Node.js dependency conflicts
        try:
            result = subprocess.run(
                ['npm', 'ls', '--all'],
                capture_output=True,
                text=True
            )
            if "invalid" in result.stdout or "unmet" in result.stdout:
                results["nodejs"] = result.stdout
                self.issues.append(f"Node.js dependency conflicts: {result.stdout}")
            else:
                results["nodejs"] = "No conflicts"
        except Exception as e:
            self.warnings.append(f"Could not check Node.js dependencies: {e}")

        return results

    def check_circular_dependencies(self) -> Dict[str, Any]:
        """Check for circular dependencies."""
        results = {}

        # Python circular imports
        try:
            result = subprocess.run(
                ['python', '-c', 'import pycycle; pycycle.check(".")'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                results["python"] = result.stdout
                self.issues.append(f"Python circular dependencies: {result.stdout}")
            else:
                results["python"] = "No circular dependencies"
        except Exception as e:
            self.warnings.append(f"Could not check Python circular dependencies: {e}")

        # Node.js circular dependencies
        try:
            result = subprocess.run(
                ['npx', 'madge', '--circular', 'src'],
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                results["nodejs"] = result.stdout
                self.issues.append(f"Node.js circular dependencies: {result.stdout}")
            else:
                results["nodejs"] = "No circular dependencies"
        except Exception as e:
            self.warnings.append(f"Could not check Node.js circular dependencies: {e}")

        return results

    def run_full_audit(self) -> Dict[str, Any]:
        """Run comprehensive conflict audit."""
        audit_results = {
            "dependency_conflicts": self.check_dependency_conflicts(),
            "circular_dependencies": self.check_circular_dependencies(),
        }

        if self.full_audit:
            # Add more comprehensive checks
            pass

        return {
            "audit_complete": True,
            "results": audit_results,
            "issues": self.issues,
            "warnings": self.warnings,
            "total_issues": len(self.issues),
            "total_warnings": len(self.warnings)
        }

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run comprehensive conflict audit")
    parser.add_argument("--full", action="store_true", help="Run full audit")
    args = parser.parse_args()

    auditor = ConflictAuditor(full_audit=args.full)
    results = auditor.run_full_audit()

    print("🔍 Conflict Audit Results")
    print("=" * 50)

    if results["total_issues"] == 0:
        print("✅ No critical conflicts detected")
    else:
        print(f"❌ {results['total_issues']} critical issues detected:")
        for issue in results["issues"]:
            print(f"  - {issue}")

    if results["total_warnings"] > 0:
        print(f"⚠️ {results['total_warnings']} warnings:")
        for warning in results["warnings"]:
            print(f"  - {warning}")

    sys.exit(0 if results["total_issues"] == 0 else 1)

if __name__ == "__main__":
    main()
```

## 🚀 CI/CD Integration

### **GitHub Actions Workflow**

```yaml
name: Conflict Prevention CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  conflict-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Quick Conflict Check
        run: python scripts/quick_conflict_check.py

      - name: Comprehensive Conflict Audit
        run: python scripts/conflict_audit.py --full

      - name: Environment Parity Check
        run: |
          echo "Python: $(python --version)"
          echo "Node: $(node --version)"
          echo "OS: $(uname -s)"
          echo "Arch: $(uname -m)"

      - name: Dependency Conflict Check
        run: |
          python -m pip check
          npm ls --all || true

      - name: Circular Dependency Check
        run: |
          pip install pycycle
          pycycle . || true
          npx madge --circular src || true

  quality-gates:
    needs: conflict-check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Quality Gates


      - name: Security Scan
        run: |
          bandit -r src/
          safety check

      - name: Performance Check

```

## 📚 Additional Resources

### **Specialized Development Guides**

> **📖 For comprehensive guidance on specific development areas, see these specialized guides:**

- **Test Development**: `dspy-rag-system/tests/README-dev.md` - Import management, variable handling, configuration policy
- **Code Criticality**: `400_guides/400_code-criticality-guide.md` - Quality standards, tier-based requirements, quality gates
- **File Analysis**: `400_guides/400_file-analysis-guide.md` - Mandatory 6-step analysis process
- **Testing Strategy**: `400_guides/400_testing-strategy-guide.md` - Comprehensive testing approaches and frameworks

### **Development Resources**

- **Python Style Guide**: PEP 8 and Black formatting
- **Testing Best Practices**: pytest and coverage tools
- **Security Guidelines**: OWASP Top 10 and security best practices
- **Performance Optimization**: Profiling and benchmarking tools
- **Conflict Prevention**: This document and related scripts

### **Quality Assurance Resources**

- **Code Review Guidelines**: Effective code review practices
- **Testing Strategies**: Comprehensive testing approaches
- **Documentation Standards**: Clear and maintainable documentation
- **Deployment Best Practices**: Safe and reliable deployment procedures
- **Conflict Resolution**: Systematic conflict detection and resolution

### **Solo Development Resources**

- **Git Workflow**: Simple version control practices
- **Self-Review Process**: Effective self-review techniques
- **Quality Standards**: Maintaining code quality as a solo developer
- **Continuous Improvement**: Learning and improving over time
- **Conflict Prevention**: Proactive conflict detection and prevention

## 🔄 Integration with Existing Workflows

### **Integration with File Analysis Guide**

This comprehensive approach integrates with our existing `400_guides/400_file-analysis-guide.md` by:

- Adding conflict detection to the 6-step analysis process
- Including conflict prevention in file operations
- Enhancing cross-reference analysis with conflict awareness

### **Integration with Contributing Guidelines**

This document enhances our existing `400_guides/400_contributing-guidelines.md` by:

- Adding systematic conflict prevention to code standards
- Enhancing error handling with conflict awareness
- Expanding quality gates with conflict detection

### **Integration with Development Workflow**

This approach integrates with our development workflow by:

- Adding conflict checks to the PRD creation process
- Including conflict prevention in task generation
- Enhancing AI execution with conflict awareness

### **Integration with AI Development Ecosystem**

This document integrates with your implemented AI development ecosystem by:

- Referencing actual production-ready systems in examples
- Using real file paths and commands from your codebase
- Providing practical workflows that work with your existing tools

## 📈 Monitoring and Improvement

### **Key Metrics**

- **Conflict Detection Rate**: How many conflicts are caught before they cause issues
- **Conflict Resolution Time**: How quickly conflicts are resolved
- **False Positive Rate**: How often conflict detection flags non-issues
- **Prevention Effectiveness**: How well conflict prevention reduces issues

### **Continuous Improvement**

- Regular review of conflict patterns
- Updates to detection rules based on new conflict types
- Enhancement of prevention strategies
- Integration of new tools and techniques

---

- **Last Updated**: 2024-12-19
- **Next Review**: Monthly
- **Development Standards Level**: Production Ready with Conflict Prevention
- **Optimized for**: Solo Development Workflow with Systematic Conflict Prevention

## **Automated Database Synchronization**

### **Git Hooks for Database Management**

The repository now includes automated database synchronization through Git hooks:

#### **Pre-commit Hook** (`.git/hooks/pre-commit`)
- **Purpose**: Validates markdown files before commit
- **Action**: Runs `doc_coherence_validator.py --dry-run`
- **Behavior**: Blocks commit if validation fails

#### **Post-commit Hook** (`.git/hooks/post-commit`)
- **Purpose**: Automatically updates database after core documentation changes
- **Trigger**: Changes to core files (`100_cursor-memory-context.md`, `000_backlog.md`, `400_comprehensive-coding-best-practices.md`, `400_code-criticality-guide.md`, `400_ai-constitution.md`, `400_file-analysis-guide.md`, `400_testing-strategy-guide.md`, `400_deployment-environment-guide.md`, `400_cursor-context-engineering-guide.md`)
- **Actions**:
  1. Runs `update_cursor_memory.py` to update memory context
  2. Runs `database_sync_check.py --auto-update` to sync files with `DATABASE_SYNC: REQUIRED` tags

#### **Pre-push Hook** (`.git/hooks/pre-push`)
- **Purpose**: Ensures database is synchronized before pushing
- **Action**: Runs `database_sync_check.py` and warns if updates are needed
- **Behavior**: Allows user to continue or abort push

### **DATABASE_SYNC Tags**

Files that should be automatically synchronized with the database should include:
```markdown
<!-- DATABASE_SYNC: REQUIRED -->
```

**Current files with DATABASE_SYNC tags:**
- `100_memory/100_cursor-memory-context.md`
- `000_core/000_backlog.md`
- `400_guides/400_comprehensive-coding-best-practices.md`
- `400_guides/400_code-criticality-guide.md`
- `400_guides/400_ai-constitution.md`
- `400_guides/400_file-analysis-guide.md`
- `400_guides/400_testing-strategy-guide.md`
- `400_guides/400_deployment-environment-guide.md`
- `400_guides/400_cursor-context-engineering-guide.md`
- `scripts/database_sync_check.py`

### **Manual Database Management**

```bash
# Check database synchronization status
python3.12 scripts/database_sync_check.py

# Update all files with DATABASE_SYNC tags
python3.12 scripts/database_sync_check.py --auto-update

# Update memory context only
python3.12 scripts/update_cursor_memory.py

# Check database consistency (dspy-rag-system)
cd dspy-rag-system && python3.12 scripts/database_maintenance.py
```
