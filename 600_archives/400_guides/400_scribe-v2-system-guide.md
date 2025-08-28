

<!-- ESSENTIAL_FILES: 400_guides/400_system-overview.md, 400_guides/400_getting-started.md -->
<!-- DSPY_ROLE: documentation -->
<!-- DSPY_AUTHORITY: documentation_standards -->
<!-- DSPY_FILES: scripts/single_doorway.py, scripts/worklog_summarizer.py, scripts/worklog_pre_commit.py -->
<!-- DSPY_CONTEXT: Core Scribe system documentation for automatic context capture and summarization -->
<!-- DSPY_VALIDATION: documentation_standards, content_organization, cross_reference_accuracy -->
<!-- DSPY_RESPONSIBILITIES: documentation_standards, content_organization, cross_reference_management -->

<!-- ANCHOR_KEY: scribe-system -->
<!-- ANCHOR_PRIORITY: 35 -->
<!-- ROLE_PINS: ["implementer", "coder"] -->
# Scribe v2 System Guide

> DEPRECATED: Content integrated into core guides — see `400_00_getting-started-and-index.md` (index), `400_04_development-workflow-and-standards.md` (workflow and hooks), `400_06_memory-and-context-systems.md` (memory rehydration integration), `400_08_integrations-editor-and-models.md` (editor/model integrations and dashboards), `400_09_automation-and-pipelines.md` (automation/CI and scripts), and `400_11_deployments-ops-and-observability.md` (monitoring/metrics/operations). Implementation scripts live under `scripts/` and artifacts under `artifacts/`.

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Comprehensive guide to the Scribe automatic context capture and summarization system | Setting up Scribe, troubleshooting sessions, or implementing new features | Start Scribe with `single_doorway.py scribe start`, review worklogs in `artifacts/worklogs/` |

## 📋 Overview {#overview}

Scribe is an intelligent context capture and summarization system that automatically records development sessions, extracts insights, and generates actionable summaries. It preserves valuable context during brainstorming, debugging, and implementation sessions.

### Core Capabilities

- **🔄 Automatic Context Capture**: Records diffs, shell commands, and decisions
- **🧠 Intelligent Summarization**: Extracts ideas, decisions, and next steps
- **📊 Progress Tracking**: Visualizes implementation status and progress
- **🔗 Integration**: Works with Git hooks, PR workflows, and manual commands
- **📈 Knowledge Mining**: Discovers patterns and reusable insights
- **🏷️ Session Registry**: Centralized tracking of active sessions with context tagging
- **🎯 Context Discovery**: Rich context tags for session discovery and management

## 🚀 Quick Start {#quick-start}

### Start a Scribe Session

```bash
# Start Scribe for current backlog item (auto-detected)
python scripts/single_doorway.py scribe start

# Start Scribe for specific backlog item
python scripts/single_doorway.py scribe start --backlog-id B-093

# Start Scribe with custom idle timeout (default: 30 minutes)
python scripts/single_doorway.py scribe start --idle-timeout 60
```

### Manual Interaction

```bash
# Add a note to current worklog
python scripts/single_doorway.py scribe append "New idea: Enhanced error handling"

# Check Scribe status
python scripts/single_doorway.py scribe status

# Check detailed status with verbose output
python scripts/single_doorway.py scribe status --verbose

# Stop Scribe manually
python scripts/single_doorway.py scribe stop
```

### Session Registry Management

```bash
# List all sessions with context tags
python scripts/single_doorway.py scribe list

# List sessions without context tags
python scripts/single_doorway.py scribe list --no-context

# Filter sessions by status
python scripts/single_doorway.py scribe list --status-filter active

# Add context tags to a session
python scripts/single_doorway.py scribe tag --backlog-id B-093 --tags brainstorming implementation

# Remove context tags from a session
python scripts/single_doorway.py scribe untag --backlog-id B-093 --tags brainstorming

# Get detailed session information
python scripts/single_doorway.py scribe info --backlog-id B-093

# Clean up old completed sessions
python scripts/single_doorway.py scribe cleanup

# Validate that registered processes are still running
python scripts/single_doorway.py scribe validate
```

### Generate Summaries

```bash
# Generate summary for any backlog item
python scripts/worklog_summarizer.py --backlog-id B-093

# Generate summary with custom output
python scripts/worklog_summarizer.py --backlog-id B-093 --output custom-summary.md --format json

# Generate summaries for ALL active worklogs
python scripts/generate_all_summaries.py

# Force regeneration of all summaries
python scripts/generate_all_summaries.py --force

# Generate summary for specific backlog item
python scripts/generate_all_summaries.py --backlog-id B-100

# Check memory rehydration integration
python scripts/generate_all_summaries.py --check-integration

# Generate graph integration report
python scripts/generate_all_summaries.py --graph-report
```

### Instance Management

Scribe automatically manages running instances to prevent resource overload:

```bash
# Check current instances
python scripts/single_doorway.py scribe status

# Start new session (auto-manages instances)
python scripts/single_doorway.py scribe start --backlog-id B-XXX
```

**Instance Limits:**
- **Maximum**: 3 concurrent sessions
- **Warning**: At 2 instances
- **Auto-cleanup**: Stops oldest instance when limit reached
- **Graceful termination**: Proper process cleanup with timeout

## 🏗️ System Architecture {#system-architecture}

### Core Components

```
Scribe System
├── Session Manager (single_doorway.py)
│   ├── Start/Stop sessions
│   ├── State management (.ai_state.json)
│   ├── Instance management (max 3 sessions)
│   └── Session registry integration
├── Session Registry (session_registry.py)
│   ├── Active session tracking
│   ├── Context tagging system
│   ├── Process validation
│   └── Session discovery
├── Context Capture
│   ├── File change monitoring
│   ├── Shell command recording
│   └── Manual note capture
├── Worklog Storage
│   ├── Timestamped entries
│   ├── Session metadata
│   └── Branch tracking
└── Summarization Engine
    ├── Content analysis
    ├── Pattern extraction
    ├── Priority scoring
    └── Actionable insights
```

### File Structure

```
artifacts/
├── worklogs/
│   ├── B-093.md          # Raw session data
│   └── B-100.md          # Another session
├── summaries/
│   ├── B-093-summary.md  # Generated summaries
│   └── B-100-summary.md
├── session_registry.json # Active session registry
└── insights/             # Mined knowledge (future)
.ai_state.json            # Session state
```

### Integration Points

- **Pre-commit hooks**: Automatic summary generation
- **Git workflows**: Auto-stop on branch switch or push
- **PR management**: Summary generation on PR close
- **Memory rehydration**: Context for AI sessions

## 📝 Session Types {#session-types}

| Type | Purpose | Duration | Output | Auto-stop |
|------|---------|----------|--------|-----------|
| **Brainstorming** | Idea generation and exploration | 30-120 min | Ideas, concepts, potential features | After idle timeout or manual stop |
| **Implementation** | Active development and coding | 60-240 min | Code changes, decisions, progress | On successful Git push or branch switch |
| **Debug** | Problem solving and troubleshooting | 15-60 min | Issues, solutions, workarounds | When issue is resolved |
| **Planning** | Architecture and design decisions | 30-90 min | Decisions, trade-offs, requirements | When planning is complete |

## 🏷️ Session Registry {#session-registry}

The Session Registry provides centralized tracking and discovery of active Scribe sessions with rich context tagging capabilities.

### Registry Features

- **📊 Active Session Tracking**: Real-time monitoring of all active sessions
- **🏷️ Context Tagging**: Rich metadata for session discovery and categorization
- **🔍 Session Discovery**: Find sessions by context tags, type, or priority
- **⚡ Process Validation**: Automatic detection of orphaned sessions
- **🧹 Auto-Cleanup**: Automatic cleanup of old completed sessions

### Context Tagging System

Sessions can be tagged with rich context metadata:

```bash
# Session context tags
session_type: brainstorming, implementation, debug, planning
priority: high, medium, low
tags: ["dspy", "testing", "documentation", "performance"]
description: "Optional session description"
related_sessions: ["B-093", "B-100"]
```

### Registry Data Structure

```json
{
  "last_updated": "2025-08-21T20:30:00Z",
  "total_sessions": 3,
  "active_sessions": 2,
  "sessions": {
    "B-093": {
      "backlog_id": "B-093",
      "pid": 12345,
      "start_time": "2025-08-21T20:00:00Z",
      "worklog_path": "artifacts/worklogs/B-093.md",
      "status": "active",
      "context": {
        "tags": ["brainstorming", "dspy", "testing"],
        "session_type": "brainstorming",
        "priority": "high",
        "description": "DSPy integration testing session"
      },
      "last_activity": null,
      "idle_timeout": 1800
    }
  }
}
```

### Session Discovery

Find sessions by various criteria:

```bash
# Find sessions by context tags
python scripts/session_context_integration.py context --tags dspy testing

# Get active sessions summary
python scripts/session_context_integration.py summary

# Integrate with memory rehydration
python scripts/session_context_integration.py integrate
```

### Memory Rehydration Integration

Session registry data is automatically integrated into memory rehydration:

```python
# Enhanced memory context includes session data
{
  "session_registry": {
    "active_sessions": [...],
    "session_count": 2,
    "last_updated": "2025-08-21T20:30:00Z"
  },
  "session_summary": "📊 Active Scribe Sessions (2)\n  • B-093 (brainstorming, high)\n  • B-100 (implementation, medium)"
}
```

## 🔧 Configuration {#configuration}

### Environment Variables

```bash
# Scribe configuration
SCRIBE_IDLE_TIMEOUT=1800        # 30 minutes (default)
SCRIBE_MAX_INSTANCES=3          # Maximum concurrent sessions
SCRIBE_AUTO_SUMMARY=true        # Generate summaries automatically
SCRIBE_BRANCH_TRACKING=true     # Track branch changes
```

### Session Metadata

```json
{
  "backlog_id": "B-093",
  "branch": "feat/B-093-Doorway-Scribe-Auto-Rehydrate",
  "scribe": {
    "pid": 12345,
    "start_time": "2025-08-21T05:30:00Z",
    "session_type": "brainstorm",
    "idle_timeout": 1800
  },
  "worklog_path": "artifacts/worklogs/B-093.md"
}
```

### Worklog Format

```markdown
# B-093 Worklog

## Session started: 2025-08-21 05:30:00
Branch: feat/B-093-Doorway-Scribe-Auto-Rehydrate

- 2025-08-21 05:30:15 - Session started
- 2025-08-21 05:31:22 - New idea: Enhanced worklog summarization
- 2025-08-21 05:32:45 - Decision: Use pre-commit hooks for automation
- 2025-08-21 05:35:12 - Changes: 3 file(s)
  - scripts/worklog_summarizer.py
  - scripts/worklog_pre_commit.py
  - .git/hooks/pre-commit
```

## 🧠 Content Analysis {#content-analysis}

### Pattern Recognition

Scribe automatically identifies and extracts:

- **Ideas**: "new idea:", "enhanced:", "proposed:", "suggestion:"
- **Decisions**: "decision:", "decided:", "chose:", "implemented:"
- **Progress**: "completed:", "in progress:", "planned:", "todo:"

### Progress Tracking

Implementation progress is categorized automatically:

```python
# Progress categories
categories = {
    "completed": ["implemented:", "added", "updated", "created"],
    "in_progress": ["planning", "designing", "analyzing"],
    "planned": ["planned", "todo", "next:", "future:"]
}
```

## 📊 Summarization Features {#summarization-features}

### Executive Summary

High-level overview of the session:

```markdown
# B-093 Session Summary

**Generated**: 2025-08-21 06:03:15
**Sessions**: 4
**Branch**: feat/B-093-Doorway-Scribe-Auto-Rehydrate
**Last Activity**: 2025-08-21 06:02:08

## Key Ideas Generated
- Enhanced worklog summarization system
- Pre-commit hook integration
- Intelligent content analysis

## Decisions Made
- Use pre-commit hooks for automation
- Implement hybrid approach for summarization

## Implementation Progress
### Completed
- ✅ Created worklog summarizer script
- ✅ Enhanced pre-commit hook

## Next Steps
- Implement intelligent content analysis
- Add knowledge mining capabilities
```

### Detailed Analysis

Comprehensive breakdown with metadata:

```json
{
  "backlog_id": "B-093",
  "ideas": [
    "Enhanced worklog summarization system",
    "Pre-commit hook integration"
  ],
  "decisions": [
    "Use pre-commit hooks for automation"
  ],
  "files_modified": [
    "scripts/worklog_summarizer.py",
    "scripts/worklog_pre_commit.py"
  ],
  "implementation_progress": {
    "completed": ["Created worklog summarizer script"],
    "in_progress": ["Testing integration"],
    "planned": ["Add knowledge mining"]
  },
  "metadata": {
    "session_count": 4,
    "branch": "feat/B-093-Doorway-Scribe-Auto-Rehydrate",
    "last_activity": "2025-08-21 06:02:08"
  }
}
```

## 🔄 Integration Workflows {#integration-workflows}

### Memory Rehydration Integration

Scribe summaries are automatically integrated into the memory rehydration system:

```bash
# Summaries accessible via implementer role
./scripts/memory_up.sh -r implementer "scribe session insights"

# All summaries include comprehensive DSPy tags:
# - CONTEXT_REFERENCE: Cross-reference linking
# - DSPY_ROLE: Role-based context assignment
# - DSPY_AUTHORITY: Authority designation
# - GRAPH_NODE_TYPE: Graph visualization metadata
# - CREATED_AT/UPDATED_AT: Timestamp tracking
```

**Integration Features:**
- **Automatic Tagging**: All summaries include memory rehydration tags
- **Role Assignment**: Dynamic role assignment based on content type
- **Cross-References**: Proper linking to related documentation
- **Timestamp Tracking**: Creation and update timestamps
- **Graph Metadata**: Ready for visualization integration

### Graph Visualization Integration

Scribe summaries appear in the NiceGUI Network Graph:

```bash
# Start graph visualization
./dspy-rag-system/start_graph_visualization.sh

# View Scribe summaries in graph
# Navigate to: http://localhost:8080
# Filter by: scribe_summary nodes
```

**Graph Features:**
- **Node Type**: `scribe_summary`
- **Category**: `session_insights`
- **Weight**: Dynamic based on content richness (ideas + decisions)
- **Connections**: Links to backlog items and branch nodes
- **Visualization**: Color-coded session insights nodes

### Pre-commit Integration

Automatic summary generation during commits:

```bash
# Pre-commit hook automatically:
# 1. Detects active Scribe sessions
# 2. Generates summaries for updated worklogs
# 3. Adds summaries to commit
# 4. Validates memory rehydration integration
```

### PR Close Integration

Summary generation when PRs are closed:

```bash
# PR close webhook:
# 1. Identifies related backlog item
# 2. Generates final summary
# 3. Archives worklog with metadata
# 4. Updates backlog item status
```

### Manual Commands

On-demand summarization and management:

```bash
# Generate summary for any backlog item
python scripts/worklog_summarizer.py --backlog-id B-093

# Check active sessions
python scripts/single_doorway.py scribe status

# Add manual notes
python scripts/single_doorway.py scribe append "Manual note"
```

## 🛠️ Troubleshooting {#troubleshooting}

### Common Issues

#### Scribe Won't Start
```bash
# Check if another instance is running
python scripts/single_doorway.py scribe status

# Kill existing processes
python scripts/single_doorway.py scribe stop

# Check for state file conflicts
rm .ai_state.json  # Only if safe to do so
```

#### Missing Worklog
```bash
# Check if worklog exists
ls artifacts/worklogs/B-093.md

# Regenerate from state
python scripts/worklog_pre_commit.py

# Check state file
cat .ai_state.json
```

#### Instance Management Issues
```bash
# Check current instances
python scripts/single_doorway.py scribe status

# If too many instances, stop manually
python scripts/single_doorway.py scribe stop --backlog-id B-XXX

# Force stop all instances (emergency)
pkill -f "single_doorway.py scribe _daemon"
```

#### Summary Generation Fails
```bash
# Check worklog content
cat artifacts/worklogs/B-093.md

# Run summarizer with verbose output
python scripts/worklog_summarizer.py --backlog-id B-093

# Check for syntax errors in worklog
python scripts/worklog_summarizer.py --backlog-id B-093 --format json
```

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Set debug environment variable
export SCRIBE_DEBUG=true

# Start Scribe with debug output
python scripts/single_doorway.py scribe start --debug

# Check debug logs
tail -f artifacts/scribe-debug.log
```

## 🚀 Advanced Features {#advanced-features}

### Custom Pattern Recognition

Add custom patterns for idea extraction:

```python
# In scripts/worklog_summarizer.py
CUSTOM_PATTERNS = [
    r"custom_idea[:\s]+(.+)",
    r"project_specific[:\s]+(.+)",
    r"team_convention[:\s]+(.+)"
]
```

### Session Type Detection

Automatic session type classification:

```python
# Session type indicators
SESSION_PATTERNS = {
    "brainstorm": ["brainstorm", "ideas", "explore"],
    "implementation": ["implement", "code", "build"],
    "debug": ["debug", "fix", "error", "issue"],
    "planning": ["plan", "design", "architecture"]
}
```

### Priority Scoring

Intelligent priority assessment:

```python
# Priority factors
PRIORITY_FACTORS = {
    "urgency": ["urgent", "critical", "blocking"],
    "impact": ["major", "significant", "core"],
    "effort": ["simple", "quick", "complex"],
    "dependencies": ["depends on", "requires", "blocked by"]
}
```

## 📈 Performance Optimization {#performance-optimization}

### File Monitoring

Efficient file change detection:

```python
# Optimized file watching
WATCH_PATTERNS = [
    "*.py", "*.md", "*.yml", "*.yaml",
    "*.json", "*.toml", "*.sh"
]

IGNORE_PATTERNS = [
    "__pycache__", ".git", "venv",
    "node_modules", "*.tmp", "*.log"
]
```

### Memory Management

Optimized memory usage for long sessions:

```python
# Memory optimization strategies
- Buffer writes to reduce I/O
- Compress old worklog entries
- Clean up temporary files
- Limit concurrent file watchers
```

### Caching

Intelligent caching for repeated operations:

```python
# Cache strategies
- Summary generation cache
- Pattern matching cache
- File change cache
- Session metadata cache
```

## 🎯 Current Version: v1.0 {#current-version}

### ✅ v1.0 Features (Implemented)
- **Status Command**: `scribe status` with verbose output
- **Instance Management**: Max 3 sessions with auto-cleanup
- **Worklog Summarization**: Pre-commit integration
- **Enhanced Documentation**: Comprehensive guide with DSPy integration
- **Error Handling**: Robust process management
- **User Experience**: Clear warnings and feedback
- **Memory Rehydration Integration**: Automatic tagging and role assignment
- **Graph Visualization**: Ready for NiceGUI Network Graph display
- **Batch Summary Generation**: `generate_all_summaries.py` script
- **Timestamp Tracking**: Creation and update timestamps
- **Cross-Reference Linking**: Proper documentation linking
- **Session Registry**: Centralized session tracking with context tagging
- **Context Discovery**: Rich metadata for session discovery and management
- **Process Validation**: Automatic detection of orphaned sessions
- **Session Management CLI**: Complete CLI for session registry operations

## 🔮 Future Enhancements {#future-enhancements}

### v1.1 Features
- **Knowledge Mining**: Extract reusable patterns across sessions
- **Cross-Reference Linking**: Connect related ideas and decisions
- **Progress Visualization**: Charts and graphs for implementation status
- **Team Collaboration**: Multi-user session support

### v1.2 Features
- **AI-Powered Analysis**: LLM integration for deeper insights
- **Predictive Suggestions**: Recommend next steps based on patterns
- **Integration APIs**: REST API for external tool integration
- **Advanced Filtering**: Search and filter across all sessions

### v1.3 Features
- **Real-time Collaboration**: Live session sharing
- **Advanced Analytics**: Session productivity metrics
- **Custom Workflows**: Configurable automation rules
- **Mobile Support**: Mobile app for session management

## 📚 Related Documentation {#related-documentation}

- **[System Overview](./400_system-overview.md)**: Technical architecture
- **[Project Overview](./400_getting-started.md)**: High-level project structure
- **[Context Priority Guide](./400_context-priority-guide.md)**: Documentation hierarchy
- **[Comprehensive Coding Best Practices](400_comprehensive-coding-best-practices.md)**: Coding standards and development workflow
- **[Naming Conventions](../200_setup/200_naming-conventions.md)**: File organization standards
- **[Single Doorway Workflow](../000_core/001_create-prd.md)**: Core workflow integration
- **[Graph Visualization Guide](./400_graph-visualization-guide.md)**: Graph integration details
- **[Memory Rehydration System](../100_memory/100_cursor-memory-context.md)**: Context retrieval system

## 🔧 Related Scripts {#related-scripts}

- **[single_doorway.py](../scripts/single_doorway.py)**: Main Scribe session management
- **[session_registry.py](../scripts/session_registry.py)**: Session registry and context tagging
- **[session_context_integration.py](../scripts/session_context_integration.py)**: Memory rehydration integration
- **[worklog_summarizer.py](../scripts/worklog_summarizer.py)**: Individual summary generation
- **[generate_all_summaries.py](../scripts/generate_all_summaries.py)**: Batch summary generation
- **[worklog_pre_commit.py](../scripts/worklog_pre_commit.py)**: Pre-commit integration

## 🛡️ Quality Assurance Integration {#quality-assurance-integration}

Scribe integrates with the comprehensive coding best practices through:

- **Pre-commit Hooks**: Automatic summary generation during commits
- **Code Quality Gates**: Scribe data feeds into quality assessment
- **Development Workflow**: Context capture supports coding standards compliance
- **Memory Rehydration**: Scribe insights enhance AI development context
- **Documentation Standards**: Scribe summaries follow documentation best practices
