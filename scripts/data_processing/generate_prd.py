from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any
import os
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Template Integration - Auto-populate PRDs with backlog context

Usage:
  python3 scripts/template_integrator.py B-0001 --generate-prd
  python3 scripts/template_integrator.py B-0001 --preview

Behavior:
  - Extracts context bundle from backlog ID
  - Auto-populates PRD Section 0 (Project Context & Implementation Guide)
  - Fills in problem statement, solution overview from backlog
  - Generates tech stack, dependencies, and implementation patterns
"""

def extract_backlog_context(backlog_id: str) -> dict[str, Any]:
    """Extract full context bundle from backlog ID using handoff script."""
    try:
        # Use the handoff script directly
        result = subprocess.run(
            [sys.executable, "scripts/extract_context.py", backlog_id, "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )

        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error extracting context for {backlog_id}: {e.stderr}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"Error parsing context JSON: {e}", file=sys.stderr)
        sys.exit(3)

def detect_tech_stack(context: dict[str, Any]) -> list[str]:
    """Auto-detect tech stack from backlog context."""
    base_stack = ["Python 3.12"]  # Project default

    description = context.get("what", "").lower()
    context.get("context", {})

    # Database-related
    if any(word in description for word in ["database", "postgresql", "sql"]):
        base_stack.extend(["PostgreSQL", "SQLAlchemy"])

    # Memory/embedding-related
    if any(word in description for word in ["memory", "embedding", "vector"]):
        base_stack.extend(["pgvector", "LTST Memory System"])

    # UI-related
    if any(word in description for word in ["dashboard", "ui", "interface"]):
        base_stack.append("NiceGUI")

    # Evaluation-related
    if any(word in description for word in ["evaluation", "ragchecker"]):
        base_stack.extend(["RAGChecker", "spaCy"])

    return list(set(base_stack))  # Remove duplicates

def generate_prd_section_0(context: dict[str, Any]) -> str:
    """Generate PRD Section 0 from backlog context."""
    tech_stack = detect_tech_stack(context)
    backlog_id = context["backlog_id"]

    return f"""## 0. Project Context & Implementation Guide

### Current Tech Stack
- {chr(10).join([f"**{tech}**: {'Core framework' if tech == 'Python 3.12' else 'Supporting technology'}" for tech in tech_stack])}

### Repository Layout
```
ai-dev-tasks/
├── scripts/                    # Automation and utility scripts
│   ├── handoff_context.py     # Context bundle extraction
│   ├── capture_idea.py        # Idea capture and backlog insertion
│   └── template_integrator.py # Template integration (this script)
├── 000_core/                  # Core workflow templates and backlog
│   ├── 000_backlog.md         # Project backlog with {backlog_id}
│   └── 001-003 workflow templates
├── src/schemas/               # Pydantic validation models
└── 400_guides/               # Documentation and guides
```

### Development Patterns
- **Context Extraction**: Use `python3 scripts/extract_context.py {backlog_id}` for clean pickup
- **Template Integration**: Auto-populate from backlog context
- **Validation**: Optional Pydantic schemas for data flow validation
- **Workflow Orchestration**: Complete A-Z automation with minimal context switching

### Local Development
```bash
# Get context bundle for any backlog item
uv run python scripts/extract_context.py {backlog_id}

# Auto-generate PRD from backlog context
uv run python scripts/generate_prd.py {backlog_id} --generate-prd

# Create new backlog items with auto-ID
echo "your idea" | uv run python scripts/create_backlog_item.py

# Complete workflow orchestration
uv run python scripts/workflow_orchestrator.py {backlog_id} --execute
```

### Common Tasks
- **Context Pickup**: `uv run python scripts/extract_context.py <B-ID>`
- **Idea Capture**: `echo "idea" | uv run python scripts/create_backlog_item.py`
- **PRD Generation**: `uv run python scripts/generate_prd.py <B-ID> --generate-prd`
- **Workflow Setup**: `uv run python scripts/workflow_orchestrator.py <B-ID> --execute`
"""

def generate_prd_problem_statement(context: dict[str, Any]) -> str:
    """Generate problem statement from backlog context."""
    context_data = context.get("context", {})
    problem = context_data.get("problem", "")
    description = context.get("what", "")

    return f"""## 1. Problem Statement

### What's broken?
{problem or f"Current challenge with {description}"}

### Why does it matter?
{context.get("priority", "").replace("🔥 **HIGH** - ", "")}

### What's the opportunity?
Implementing {description} will improve system reliability and user experience.
"""

def generate_prd_solution_overview(context: dict[str, Any]) -> str:
    """Generate solution overview from backlog context."""
    context_data = context.get("context", {})
    solution = context_data.get("solution", "")
    description = context.get("what", "")

    return f"""## 2. Solution Overview

### What are we building?
{description}

### How does it work?
{solution or f"Implementation approach for {description}"}

### What are the key features?
- **Core Implementation**: {description}
- **Context Integration**: Seamless handoff and pickup
- **Validation**: Structured data flow with error handling
- **Documentation**: Complete implementation guide
"""

def generate_full_prd(backlog_id: str, context: dict[str, Any]) -> str:
    """Generate complete PRD from backlog context."""
    title = context.get("title", backlog_id)

    prd = f"""# Product Requirements Document: {title}

> **Auto-Generated from {backlog_id}** using template integration system.
> Source context: `python3 scripts/handoff_context.py {backlog_id}`

{generate_prd_section_0(context)}

{generate_prd_problem_statement(context)}

{generate_prd_solution_overview(context)}

## 3. Acceptance Criteria

### How do we know it's done?
- [ ] **Core Implementation**: {context.get("what", "")} is fully implemented
- [ ] **Context Handoff**: Clean pickup with `handoff_context.py {backlog_id}`
- [ ] **Documentation**: Implementation approach documented
- [ ] **Validation**: Error-free execution with expected outputs

### What does success look like?
- **Functional Success**: {context.get("next", "")}
- **Quality Success**: Clean, maintainable implementation
- **Integration Success**: Seamless workflow handoff

### What are the quality gates?
- [ ] **Handoff Test**: `python3 scripts/handoff_context.py {backlog_id}` returns valid context
- [ ] **Implementation Test**: Core functionality works as expected
- [ ] **Integration Test**: Fits into existing workflow seamlessly

## 4. Technical Approach

### What technology?
{chr(10).join([f"- **{tech}**: Implementation component" for tech in detect_tech_stack(context)])}

### How does it integrate?
- **Handoff System**: Uses existing context bundle extraction
- **Template System**: Integrates with 001-003 workflow templates
- **Validation System**: Optional Pydantic schema validation

### What are the constraints?
- **Dependencies**: {context.get("context", {}).get("dependencies", "None identified")}
- **Scope**: Minimal viable implementation, avoid over-engineering
- **Compatibility**: Must work with existing handoff system

## 5. Risks and Mitigation

### What could go wrong?
- **Risk 1**: Context extraction fails or returns invalid data
- **Risk 2**: Template integration breaks existing workflows
- **Risk 3**: Implementation doesn't meet acceptance criteria

### How do we handle it?
- **Mitigation 1**: Validate context bundle before proceeding
- **Mitigation 2**: Test template integration with existing items
- **Mitigation 3**: Use iterative development with validation checkpoints

### What are the unknowns?
- Integration points with existing systems
- Performance impact of template generation
- Long-term maintenance requirements

## 6. Testing Strategy

### What needs testing?
- **Context Extraction**: Backlog parsing and bundle generation
- **Template Generation**: PRD creation from context
- **Integration**: End-to-end workflow validation

### How do we test it?
- **Unit Testing**: Individual component validation
- **Integration Testing**: Full workflow testing
- **Acceptance Testing**: User scenario validation

### What's the coverage target?
- **Core Functions**: 100% - Critical path coverage
- **Integration Points**: 100% - Handoff validation
- **Error Scenarios**: 90% - Exception handling

## 7. Implementation Plan

### What are the phases?
1. **Phase 1 - Context Integration** (2 hours): Template system integration with handoff context
2. **Phase 2 - PRD Generation** (3 hours): Automated PRD creation from backlog context
3. **Phase 3 - Validation** (2 hours): Testing and quality assurance
4. **Phase 4 - Documentation** (1 hour): Usage guide and integration examples

### What are the dependencies?
- **Handoff System**: `scripts/handoff_context.py` must be functional
- **Template System**: 001-003 workflow templates must be accessible
- **Validation System**: Optional Pydantic schemas for data validation

### What's the timeline?
- **Total Implementation Time**: 8 hours
- **Phase 1**: 2 hours (Context Integration)
- **Phase 2**: 3 hours (PRD Generation)
- **Phase 3**: 2 hours (Validation)
- **Phase 4**: 1 hour (Documentation)

---

## **Auto-Generated Context Bundle**

```json
{json.dumps(context, indent=2)}
```

> 🎯 **Next Steps**: Use this PRD to generate tasks with `002_generate-tasks-TEMPLATE.md`
> 📝 **Pickup Command**: `python3 scripts/handoff_context.py {backlog_id}`
"""

    return prd

def main() -> None:
    ap = argparse.ArgumentParser(description="Auto-populate PRD templates from backlog context")
    ap.add_argument("backlog_id", help="Backlog ID, e.g., B-0001")
    ap.add_argument("--generate-prd", action="store_true", help="Generate complete PRD")
    ap.add_argument("--preview", action="store_true", help="Preview PRD without writing")
    ap.add_argument("--output", help="Output file path (default: PRD-{backlog_id}.md)")
    args = ap.parse_args()

    # Extract context from backlog
    context = extract_backlog_context(args.backlog_id)

    if args.generate_prd or args.preview:
        prd_content = generate_full_prd(args.backlog_id, context)

        if args.preview:
            print(prd_content)
            return

        # Write PRD file
        output_path = args.output or f"PRD-{args.backlog_id}.md"
        Path(output_path).write_text(prd_content, encoding="utf-8")
        print(f"Generated PRD: {output_path}")
    else:
        # Just show context
        print(json.dumps(context, indent=2))

if __name__ == "__main__":  # pragma: no cover
    main()
