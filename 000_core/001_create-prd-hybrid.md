<!-- ANCHOR_KEY: create-prd-hybrid -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["planner", "implementer"] -->

# 📝 Create PRD (Hybrid Template)

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Enhanced PRD creation with both planning structure and implementation guidance | Starting new feature development | Run workflow to generate PRD for selected backlog item |

## 🎯 **Current Status**
- **Status**: 🔄 **PROTOTYPE** - Hybrid planning + implementation template
- **Priority**: 🔥 Critical - Essential for project planning and execution
- **Points**: 6 - Enhanced complexity, high importance
- **Dependencies**: 000_core/000_backlog.md, project context analysis
- **Next Steps**: Validate with real projects, refine implementation guidance

## When to use {#when-to-use}

- Use for high-risk or 5+ point items, or when score_total < 3.0
- Optional for smaller items where acceptance criteria are obvious
- **Enhanced**: Now includes implementation guidance for faster execution

### PRD Skip Rule (canonical) {#prd-skip-rule}

- Skip PRD when: points < 5 AND score_total ≥ 3.0 (backlog metadata `<!--score_total: X.X-->`)
- Otherwise, create a PRD with machine-verifiable acceptance criteria

### Backlog Integration {#backlog-integration}

- **Input**: Backlog item ID (e.g., B-1007) or PRD file
- **Output**: PRD file following template structure + implementation guidance
- **Cross-reference**: `000_core/000_backlog.md` for item details and metadata

## Template {#template}

### **0. Project Context & Implementation Guide**
- **Current Tech Stack** - What technologies are we using? (versions, frameworks, tools)
- **Repository Layout** - How is the code organized? (key directories, file patterns)
- **Development Patterns** - Where do different types of code go? (routing, models, views, etc.)
- **Local Development** - How do we run and test locally? (setup commands, quality gates)
- **Common Tasks** - Cheat sheet for typical changes (add page, add API, add model, etc.)

### **1. Problem Statement**
- **What's broken?** - Clear description of the current problem
- **Why does it matter?** - Impact on users, business, or system
- **What's the opportunity?** - What we can gain by fixing it

### **2. Solution Overview**
- **What are we building?** - Simple description of the solution
- **How does it work?** - Basic approach and key components
- **What are the key features?** - Main capabilities that solve the problem

### **3. Acceptance Criteria**
- **How do we know it's done?** - Clear, testable criteria
- **What does success look like?** - Measurable outcomes
- **What are the quality gates?** - Must-pass requirements

### **4. Technical Approach**
- **What technology?** - Stack and key components
- **How does it integrate?** - Connections to existing systems
- **What are the constraints?** - Technical limitations and requirements

### **5. Risks and Mitigation**
- **What could go wrong?** - Real risks and challenges
- **How do we handle it?** - Mitigation strategies
- **What are the unknowns?** - Areas of uncertainty

### **6. Testing Strategy**
- **What needs testing?** - Critical components and scenarios
- **How do we test it?** - Testing approach and tools
- **What's the coverage target?** - Minimum testing requirements

### **7. Implementation Plan**
- **What are the phases?** - High-level implementation steps
- **What are the dependencies?** - What needs to happen first
- **What's the timeline?** - Realistic time estimates

## **PRD Output Format**

```markdown
# Product Requirements Document: [Project Name]

> ⚠️**Auto-Skip Note**> This PRD was generated because either `points≥5` or `score_total<3.0`.
> Remove this banner if you manually forced PRD creation.

## 0. Project Context & Implementation Guide

### Current Tech Stack
- **Backend**: [e.g., Python 3.12, FastAPI, PostgreSQL]
- **Frontend**: [e.g., React 18, TypeScript, Tailwind CSS]
- **Infrastructure**: [e.g., Docker, AWS, Redis]
- **Development**: [e.g., Poetry, pytest, pre-commit]

### Repository Layout
```
project/
├── src/                    # Main application code
│   ├── api/               # API endpoints and routes
│   ├── models/            # Data models and business logic
│   ├── services/          # Business services and utilities
│   └── utils/             # Shared utilities and helpers
├── tests/                 # Test files (unit, integration)
├── docs/                  # Documentation
├── scripts/               # Development and deployment scripts
└── config/                # Configuration files
```

### Development Patterns
- **Add API endpoint**: `src/api/` → add route → add controller → add tests
- **Add data model**: `src/models/` → add model → add migration → add tests
- **Add business logic**: `src/services/` → add service → add tests
- **Add utility function**: `src/utils/` → add function → add tests

### Local Development
```bash
# Setup
poetry install
poetry run pre-commit install

# Run locally
poetry run uvicorn src.main:app --reload

# Quality gates
poetry run pytest              # Run tests
poetry run black .             # Format code
poetry run ruff check .        # Lint code
poetry run mypy .              # Type check
```

### Common Tasks Cheat Sheet
- **Add new feature**: API endpoint → Model → Service → Tests → Docs
- **Fix bug**: Reproduce → Test → Fix → Test → Document
- **Refactor**: Identify scope → Tests → Refactor → Tests → Validate
- **Add configuration**: Config file → Environment variables → Validation

## 1. Problem Statement
`[What's broken, why it matters, what's the opportunity]`

## 2. Solution Overview
`[What we're building, how it works, key features]`

## 3. Acceptance Criteria
`[How we know it's done, success criteria, quality gates]`

## 4. Technical Approach
`[Technology stack, integration points, constraints]`

## 5. Risks and Mitigation
`[What could go wrong, mitigation strategies, unknowns]`

## 6. Testing Strategy
`[What needs testing, testing approach, coverage targets]`

## 7. Implementation Plan
`[Phases, dependencies, timeline]`
```

## **Special Instructions**

### Planning Focus (Original)
1. **Keep it simple** - Focus on what actually matters
2. **Be honest** - Call out real problems and risks
3. **Be specific** - Clear, testable acceptance criteria
4. **Be realistic** - Honest timeline and effort estimates
5. **Consider dependencies** - What needs to happen first
6. **Think about testing** - How do we know it works?
7. **Identify risks** - What could go wrong?
8. **Align with backlog** - Use backlog priorities and scoring
9. **Parse backlog format** - Extract relevant metadata
10. **Use points for effort** - Scale tasks to point estimates

### Implementation Focus (New)
11. **Capture project context** - Document current tech stack and patterns
12. **Map repository layout** - Understand where code should go
13. **Define development patterns** - Establish conventions for common tasks
14. **Document local setup** - How to run and test the project
15. **Create task cheat sheets** - Quick reference for typical changes
16. **Identify quality gates** - Specific commands and tools for validation
17. **Consider edge cases** - Domain-specific problems to watch for
18. **Map integration points** - How new code connects to existing systems

## Acceptance Criteria {#acceptance-criteria}

This hybrid approach ensures every PRD provides both strategic planning guidance and tactical implementation direction, enabling faster and more accurate development execution.

## Handoff to task generation {#handoff-to-002}

- Next step: Use `000_core/002_generate-tasks.md` with this PRD (or a Backlog ID)
- Input → PRD file; Output → 2–4 hour tasks with dependencies and gates
- **Enhanced**: Task generation now has implementation context for better task breakdown
