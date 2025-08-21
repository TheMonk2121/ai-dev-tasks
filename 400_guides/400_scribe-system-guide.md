<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: scripts/single_doorway.py -->
<!-- MEMORY_CONTEXT: HIGH - Core workflow automation system -->
<!-- ESSENTIAL_FILES: 400_guides/400_system-overview.md, 400_guides/400_project-overview.md -->
<!-- DSPY_ROLE: documentation -->
<!-- DSPY_AUTHORITY: documentation_standards -->
<!-- DSPY_FILES: scripts/single_doorway.py, scripts/worklog_summarizer.py, scripts/worklog_pre_commit.py -->
<!-- DSPY_CONTEXT: Core Scribe system documentation for automatic context capture and summarization -->
<!-- DSPY_VALIDATION: documentation_standards, content_organization, cross_reference_accuracy -->
<!-- DSPY_RESPONSIBILITIES: documentation_standards, content_organization, cross_reference_management -->

# Scribe System Guide

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Comprehensive guide to the Scribe automatic context capture and summarization system | Setting up Scribe, troubleshooting sessions, or implementing new features | Start Scribe with `single_doorway.py scribe start`, review worklogs in `artifacts/worklogs/` |

## 📋 Overview

Scribe is an intelligent context capture and summarization system that automatically records development sessions, extracts insights, and generates actionable summaries. It preserves valuable context during brainstorming, debugging, and implementation sessions.

### Core Capabilities

- **🔄 Automatic Context Capture**: Records diffs, shell commands, and decisions
- **🧠 Intelligent Summarization**: Extracts ideas, decisions, and next steps
- **📊 Progress Tracking**: Visualizes implementation status and progress
- **🔗 Integration**: Works with Git hooks, PR workflows, and manual commands
- **📈 Knowledge Mining**: Discovers patterns and reusable insights

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

### Generate Summaries

```bash
# Generate summary for any backlog item
python scripts/worklog_summarizer.py --backlog-id B-093

# Generate summary with custom output
python scripts/worklog_summarizer.py --backlog-id B-093 --output custom-summary.md --format json
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
│   └── Instance management (max 3 sessions)
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

### Pre-Commit Integration

Automatic summary generation during commits:

```bash
# Pre-commit hook automatically:
# 1. Checks for active Scribe session
# 2. Generates summary if session exists
# 3. Adds summary to commit
# 4. Shows statistics
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

## 📚 Related Documentation

- **[System Overview](../400_guides/400_system-overview.md)**: Technical architecture
- **[Project Overview](../400_guides/400_project-overview.md)**: High-level project structure
- **[Context Priority Guide](../400_guides/400_context-priority-guide.md)**: Documentation hierarchy
- **[Naming Conventions](../200_setup/200_naming-conventions.md)**: File organization standards
- **[Single Doorway Workflow](../000_core/001_create-prd.md)**: Core workflow integration

## 🔗 Quick Links {#quick-links}

- **[Quick Start](#quick-start)**: Get started with Scribe
- **[System Architecture](#system-architecture)**: Technical overview
- **[Configuration](#configuration)**: Setup and customization
- **[Troubleshooting](#troubleshooting)**: Common issues and solutions
- **[Advanced Features](#advanced-features)**: Power user capabilities
