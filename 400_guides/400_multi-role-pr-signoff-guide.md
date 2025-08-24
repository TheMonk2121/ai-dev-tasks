

<!-- ESSENTIAL_FILES: 400_guides/400_system-overview.md, 400_guides/400_project-overview.md -->
<!-- DSPY_ROLE: documentation -->
<!-- DSPY_AUTHORITY: documentation_standards -->
<!-- DSPY_FILES: scripts/pr_signoff.py, scripts/worklog_summarizer.py -->
<!-- DSPY_CONTEXT: Multi-role PR sign-off system documentation for comprehensive review and cleanup -->
<!-- DSPY_VALIDATION: documentation_standards, content_organization, cross_reference_accuracy -->
<!-- DSPY_RESPONSIBILITIES: documentation_standards, content_organization, cross_reference_management -->
<!-- ANCHOR_KEY: multi-role-pr-signoff -->
<!-- ANCHOR_PRIORITY: 30 -->
<!-- ROLE_PINS: ["implementer", "coder", "planner"] -->
# Multi-Role PR Sign-Off System Guide

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Comprehensive guide to the multi-role PR sign-off system for comprehensive review and cleanup | Implementing PR closure workflow or setting up role-based approvals | Use `scripts/pr_signoff.py` to manage PR sign-offs and automated cleanup |

## 📋 Overview

The Multi-Role PR Sign-Off System ensures comprehensive review and proper cleanup before closing Pull Requests. It requires approval from all DSPy roles (Planner, Implementer, Coder, Researcher) and performs automated cleanup tasks including worklog summarization, file archiving, and status updates.

### Core Capabilities

- **🔐 Role-Based Approval**: Requires sign-off from all four DSPy roles
- **✅ Automated Validation**: Runs role-specific validation checks
- **🧹 Automated Cleanup**: Archives files, generates summaries, updates status
- **📊 Status Tracking**: Real-time visibility into approval progress
- **🔗 Integration**: Works with existing Scribe and worklog systems

## 🚀 Quick Start {#quick-start}

### Check PR Sign-Off Status

```bash
# Check current status for a PR
python scripts/pr_signoff.py 123 --status

# Check status with backlog ID
python scripts/pr_signoff.py 123 --backlog-id B-097 --status
```

### Perform Role Sign-Off

```bash
# Approve as planner role
python scripts/pr_signoff.py 123 --role planner --approve --notes "Strategic alignment confirmed"

# Approve as coder role
python scripts/pr_signoff.py 123 --role coder --approve --notes "Code quality standards met"

# Approve as implementer role
python scripts/pr_signoff.py 123 --role implementer --approve --notes "Architecture validated"

# Approve as researcher role
python scripts/pr_signoff.py 123 --role researcher --approve --notes "Knowledge extracted"
```

### Perform Cleanup After Approval

```bash
# Perform automated cleanup (only works when all roles have approved)
python scripts/pr_signoff.py 123 --cleanup
```

## 🏗️ System Architecture {#system-architecture}

### Role Responsibilities

| Role | Primary Focus | Key Responsibilities |
|------|---------------|---------------------|
| **Planner** | Strategic alignment | Backlog validation, priority assessment, roadmap impact |
| **Implementer** | Technical architecture | System integration, workflow automation, Scribe health |
| **Coder** | Code quality | Linting, testing, security, documentation standards |
| **Researcher** | Knowledge extraction | Worklog analysis, pattern recognition, lessons learned |

### Workflow Process

```
PR Ready for Closure
        ↓
┌─────────────────┐
│ Role Sign-Offs  │ ← Each role must approve
│                 │
│ Planner ✅      │
│ Implementer ✅  │
│ Coder ✅        │
│ Researcher ✅   │
└─────────────────┘
        ↓
┌─────────────────┐
│ Validation      │ ← Automated checks run
│ Checks          │
│                 │
│ Strategic ✅    │
│ Technical ✅    │
│ Quality ✅      │
│ Knowledge ✅    │
└─────────────────┘
        ↓
┌─────────────────┐
│ Automated       │ ← Cleanup tasks execute
│ Cleanup         │
│                 │
│ Worklog Summary │
│ File Archiving  │
│ Status Updates  │
│ Sign-off Cleanup│
└─────────────────┘
        ↓
PR Closed Successfully
```

### File Structure

```
artifacts/
├── pr_signoffs/
│   ├── PR-123-signoff.json    # Sign-off state
│   └── PR-124-signoff.json    # Another PR
├── worklogs/
│   └── B-097.md               # Session data
└── summaries/
    └── B-097-summary.md       # Generated summaries
```

## 🔧 Role-Specific Validation {#role-validation}

### Planner Role Checks

- **Strategic Alignment**: Verifies PR aligns with backlog priorities
- **Backlog Validation**: Ensures backlog item exists and is properly formatted
- **Priority Assessment**: Confirms priority level is appropriate
- **Roadmap Impact**: Analyzes impact on project roadmap

### Implementer Role Checks

- **Technical Architecture**: Reviews architectural patterns in changed files
- **System Integration**: Validates integration points are maintained
- **Workflow Automation**: Ensures automation workflows remain intact
- **Scribe System Health**: Verifies Scribe system is operational

### Coder Role Checks

- **Code Quality**: Runs linting checks (Ruff, Black, Pyright)
- **Testing Coverage**: Executes smoke tests and validates coverage
- **Security Compliance**: Checks for security best practices
- **Documentation Standards**: Ensures documentation is updated

### Researcher Role Checks

- **Knowledge Extraction**: Analyzes worklog content for insights
- **Pattern Analysis**: Identifies recurring patterns and themes
- **Lessons Learned**: Extracts actionable lessons from the work
- **Research Impact**: Assesses impact on research findings

## 📊 Status Tracking {#status-tracking}

### Status Response Format

```json
{
  "pr_number": "123",
  "backlog_id": "B-097",
  "overall_status": "pending",
  "signoffs": {
    "planner": {
      "approved": true,
      "timestamp": "2025-08-21T11:30:00Z",
      "validation_status": "passed"
    },
    "implementer": {
      "approved": false,
      "timestamp": "2025-08-21T11:35:00Z",
      "validation_status": "failed"
    }
  },
  "missing_roles": ["coder", "researcher"],
  "can_close": false
}
```

### Status States

- **`pending`**: PR awaiting sign-offs
- **`approved`**: All roles have approved, ready for cleanup
- **`failed`**: One or more roles rejected the PR

## 🧹 Automated Cleanup {#automated-cleanup}

### Cleanup Actions

1. **Worklog Summarization**: Generates summary from session worklog
2. **File Archiving**: Archives PRD, tasks, and run files to `600_archives`
3. **Deprecation Headers**: Adds deprecation headers to archived files
4. **Status Updates**: Updates backlog item status
5. **Sign-off Cleanup**: Removes temporary sign-off files

### Archive Process

```bash
# Files are automatically archived with deprecation headers
600_archives/artifacts/000_core_temp_files/
├── PRD-B-097-*.md    # Archived with deprecation header
├── TASKS-B-097-*.md  # Archived with deprecation header
└── RUN-B-097-*.md    # Archived with deprecation header
```

### Deprecation Header Format

```markdown
<!-- ARCHIVED/DEPRECATED - do not edit -->
<!-- Archived on: 2025-08-21T11:45:00Z -->
<!-- PR: 123 -->
<!-- Backlog: B-097 -->

> **ARCHIVED**: This file has been automatically archived after PR closure.
> Do not edit this file as it is no longer actively maintained.

[Original content follows...]
```

## 🔄 Integration Workflows {#integration-workflows}

### Pre-PR Closure Integration

```bash
# Before closing a PR, check sign-off status
python scripts/pr_signoff.py 123 --status

# If all roles have approved, perform cleanup
python scripts/pr_signoff.py 123 --cleanup

# Then close the PR
gh pr close 123
```

### Scribe Integration

The system integrates with Scribe for knowledge extraction:

- **Worklog Analysis**: Analyzes Scribe worklogs for insights
- **Content Validation**: Ensures worklog contains substantial content
- **Summary Generation**: Creates summaries from session data
- **Pattern Recognition**: Identifies recurring themes and decisions

### GitHub Integration

Uses GitHub CLI for PR information:

- **PR Details**: Retrieves PR title, body, and changed files
- **Backlog Extraction**: Automatically extracts backlog ID from PR content
- **File Analysis**: Reviews changed files for architectural patterns

## 🛠️ Troubleshooting {#troubleshooting}

### Common Issues

#### Sign-Off Fails Validation
```bash
# Check validation results
python scripts/pr_signoff.py 123 --role coder --approve --notes "Test"

# Review validation output for specific failures
# Fix issues and retry sign-off
```

#### Cleanup Fails
```bash
# Check if all roles have approved
python scripts/pr_signoff.py 123 --status

# Ensure all required roles have signed off
# Then retry cleanup
python scripts/pr_signoff.py 123 --cleanup
```

#### Missing Backlog ID
```bash
# Provide backlog ID explicitly
python scripts/pr_signoff.py 123 --backlog-id B-097 --status

# Or ensure PR title/body contains B-XXX reference
```

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Set debug environment variable
export PR_SIGNOFF_DEBUG=true

# Run with verbose output
python scripts/pr_signoff.py 123 --status
```

## 🚀 Advanced Features {#advanced-features}

### Custom Validation Rules

Add custom validation checks:

```python
# In scripts/pr_signoff.py
def _run_custom_check(self, role: str, responsibility: str) -> Dict[str, Any]:
    """Add custom validation logic here."""
    # Custom validation implementation
    pass
```

### Role-Specific Notes

Include detailed notes for each sign-off:

```bash
# Comprehensive notes example
python scripts/pr_signoff.py 123 --role planner --approve \
  --notes "Strategic alignment confirmed. PR addresses B-097 requirements.
  No impact on roadmap. Dependencies resolved."
```

### Batch Processing

Process multiple PRs:

```bash
# Script to process multiple PRs
for pr in 123 124 125; do
  python scripts/pr_signoff.py $pr --status
done
```

## 📈 Performance Optimization {#performance-optimization}

### Validation Caching

- **Result Caching**: Cache validation results to avoid re-running checks
- **Incremental Updates**: Only re-validate changed components
- **Parallel Processing**: Run independent checks in parallel

### File System Optimization

- **Efficient Archiving**: Batch archive operations
- **Compression**: Compress archived files to save space
- **Cleanup Scheduling**: Schedule cleanup during low-usage periods

## 🎯 Current Version: v1.0 {#current-version}

### ✅ v1.0 Features (Implemented)
- **Role-Based Approval**: All four DSPy roles must approve
- **Automated Validation**: Role-specific validation checks
- **Status Tracking**: Real-time status visibility
- **Automated Cleanup**: File archiving and summarization
- **GitHub Integration**: PR information retrieval
- **Scribe Integration**: Worklog analysis and summarization

## 🔮 Future Enhancements {#future-enhancements}

### v1.1 Features
- **Web Interface**: Web-based sign-off dashboard
- **Notification System**: Email/Slack notifications for sign-offs
- **Advanced Analytics**: Sign-off metrics and trends
- **Custom Roles**: Configurable role definitions

### v1.2 Features
- **Approval Templates**: Pre-defined approval templates
- **Conditional Approval**: Role-specific approval conditions
- **Integration APIs**: REST API for external tool integration
- **Advanced Reporting**: Detailed approval reports

### v1.3 Features
- **Machine Learning**: AI-powered approval recommendations
- **Predictive Analytics**: Predict approval likelihood
- **Advanced Workflows**: Custom approval workflows
- **Mobile Support**: Mobile app for sign-offs

## 📚 Related Documentation

- **[System Overview](../400_guides/400_system-overview.md)**: Technical architecture
- **[Project Overview](../400_guides/400_project-overview.md)**: High-level project structure
- **[Scribe System Guide](../400_guides/400_scribe-v2-system-guide.md)**: Context capture system
- **[Context Priority Guide](../400_guides/400_context-priority-guide.md)**: Documentation hierarchy
- **[Single Doorway Workflow](../000_core/001_create-prd.md)**: Core workflow integration

## 🔗 Quick Links {#quick-links}

- **[Quick Start](#quick-start)**: Get started with PR sign-offs
- **[System Architecture](#system-architecture)**: Technical overview
- **[Role Validation](#role-validation)**: Role-specific checks
- **[Automated Cleanup](#automated-cleanup)**: Cleanup process
- **[Troubleshooting](#troubleshooting)**: Common issues and solutions
