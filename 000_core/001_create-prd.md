<!-- ANCHOR_KEY: create-prd -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["planner", "implementer"] -->

# 📝 Create PRD

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Enhanced Product Requirements Document creation with industry standards and solo developer optimizations | Starting new feature development | Run workflow to generate PRD for selected backlog item |

## 🎯 **Current Status**
- **Status**: ✅ **ACTIVE** - Enhanced PRD creation workflow with industry standards
- **Priority**: 🔥 Critical - Essential for project planning
- **Points**: 4 - Moderate complexity, high importance
- **Dependencies**: 000_core/000_backlog.md
- **Next Steps**: Enhanced template with MoSCoW prioritization and solo optimizations

## When to use {#when-to-use}

- Use for high-risk or 5+ point items, or when score_total < 3.0
- Optional for smaller items where acceptance criteria are obvious
- **B-1009**: AsyncIO Scribe Enhancement (6 points, score_total: 6.5) - PRD required
- **B-1010**: NiceGUI Scribe Dashboard (8 points, score_total: 7.0) - PRD required

### PRD Skip Rule (canonical) {#prd-skip-rule}

- Skip PRD when: points < 5 AND score_total ≥ 3.0 (backlog metadata `<!--score_total: X.X-->`)
- Otherwise, create a PRD with machine-verifiable acceptance criteria

### Backlog Integration {#backlog-integration}

- **Input**: Backlog item ID (e.g., B-1007) or PRD file
- **Output**: PRD file following enhanced template structure
- **Cross-reference**: `000_core/000_backlog.md` for item details and metadata

## Enhanced Template {#template}

### **0. Project Context & Implementation Guide**
- **Current Tech Stack** - Document existing technology and patterns
- **Repository Layout** - Key directories and file organization
- **Development Patterns** - Common workflows and conventions
- **Local Development** - Setup and quality gate commands
- **Common Tasks** - Quick reference for typical operations

### **1. Problem Statement**
- **What's broken?** - Clear description of the current problem
- **Why does it matter?** - Impact on users, business, or system
- **What's the opportunity?** - What we can gain by fixing i

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
- **What are the dependencies?** - What needs to happen firs
- **What's the timeline?** - Realistic time estimates

### **8. Task Breakdown**
- **Phase 1**: [Phase description and tasks]
- **Phase 2**: [Phase description and tasks]
- **Phase 3**: [Phase description and tasks]
- **Phase 4**: [Phase description and tasks]

## **Enhanced PRD Output Format**

```markdown
# Product Requirements Document: [Project Name]

> ⚠️**Auto-Skip Note**> This PRD was generated because either `points≥5` or `score_total<3.0`.
> Remove this banner if you manually forced PRD creation.

## 0. Project Context & Implementation Guide
### Current Tech Stack
- **Backend**: [e.g., Python 3.12, FastAPI, PostgreSQL]
- **AI/ML**: [e.g., Cursor Native AI, DSPy, LTST Memory]
- **Infrastructure**: [e.g., Docker, Redis, n8n workflows]
- **Development**: [e.g., Poetry, pytest, pre-commit, Ruff]

### Repository Layout
```
project/
├── 000_core/              # Core workflow files (001-003)
├── 100_memory/            # Memory and context systems
├── 200_setup/             # Setup and configuration
├── 400_guides/            # Documentation and guides
├── 500_research/          # Research and analysis
├── 600_archives/          # Completed work and artifacts
├── scripts/               # Development and automation scripts
└── tests/                 # Test files
```

### Development Patterns
- **Add backlog item**: `scripts/backlog_intake.py` → update `000_core/000_backlog.md`
- **Generate PRD**: `scripts/prd_generator.py` → create `PRD-B-XXX.md`
- **Execute workflow**: `scripts/solo_workflow.py` → automated 001-003 flow
- **Update memory**: `scripts/update_cursor_memory.py` → maintain context

### Local Developmen
```bash
# Setup
poetry install
poetry run pre-commit install

# Quality gates
poetry run pytest              # Run tests
poetry run black .             # Format code
poetry run ruff check .        # Lint code
poetry run mypy .              # Type check

# Backlog operations
python3 scripts/backlog_cli.py add "description"  # Add item
python3 scripts/backlog_cli.py update B-XXX       # Update item
python3 scripts/backlog_cli.py close B-XXX        # Close item
```

### Common Tasks Cheat Shee
- **Add new feature**: Backlog intake → PRD → Tasks → Execute → Archive
- **Fix bug**: Identify → Backlog item → Quick PRD → Execute → Close
- **Refactor system**: Analysis → Backlog item → Comprehensive PRD → Phased execution
- **Update documentation**: Direct edit → Update memory → Validate coherence

## 1. Problem Statement
[What's broken, why it matters, what's the opportunity]

## 2. Solution Overview
[What we're building, how it works, key features]

## 3. Acceptance Criteria
[How we know it's done, success criteria, quality gates]

## 4. Technical Approach
[Technology stack, integration points, constraints]

## 5. Risks and Mitigation
[What could go wrong, mitigation strategies, unknowns]

## 6. Testing Strategy
[What needs testing, testing approach, coverage targets]

## 7. Implementation Plan
[Phases, dependencies, timeline]

## 8. Task Breakdown
### Phase 1: [Phase Name]
- [ ] Task 1.1: [Task description]
- [ ] Task 1.2: [Task description]
- [ ] Task 1.3: [Task description]

### Phase 2: [Phase Name]
- [ ] Task 2.1: [Task description]
- [ ] Task 2.2: [Task description]
- [ ] Task 2.3: [Task description]

### Phase 3: [Phase Name]
- [ ] Task 3.1: [Task description]
- [ ] Task 3.2: [Task description]
- [ ] Task 3.3: [Task description]

### Phase 4: [Phase Name]
- [ ] Task 4.1: [Task description]
- [ ] Task 4.2: [Task description]
- [ ] Task 4.3: [Task description]
```

## **Special Instructions**

### Implementation Focus (Enhanced)
1. **Keep it simple** - Focus on what actually matters
2. **Be honest** - Call out real problems and risks
3. **Be specific** - Clear, testable acceptance criteria
4. **Be realistic** - Honest timeline and effort estimates
5. **Consider dependencies** - What needs to happen firs
6. **Think about testing** - How do we know it works?
7. **Identify risks** - What could go wrong?
8. **Align with backlog** - Use backlog priorities and scoring
9. **Parse backlog format** - Extract relevant metadata
10. **Use points for effort** - Scale tasks to point estimates
11. **Capture project context** - Document current tech stack and patterns
12. **Include MoSCoW prioritization** - Must/Should/Could/Won't categorization
13. **Optimize for solo developer** - One-command workflows and auto-advance
14. **Consider industry standards** - Best practices for maintainability
15. **Plan for knowledge mining** - How completed work informs future planning
16. **Design for visual interface** - Consider dashboard and Kanban integration
17. **Account for dynamic reprioritization** - AI-driven priority adjustments
18. **Include context preservation** - LTST memory integration
19. **Plan for archive system** - Systematic organization with insights
20. **Consider performance implications** - Scalability and optimization needs

## Acceptance Criteria {#acceptance-criteria}

This enhanced approach ensures every PRD focuses on what actually matters: clear problems, simple solutions, realistic plans, honest assessment of risks and challenges, industry best practices, and solo developer optimizations.

## Handoff to task generation {#handoff-to-002}

- Next step: Use `000_core/002_generate-tasks.md` with this PRD (or a Backlog ID)
- Input → PRD file with embedded tasks; Output → Execution-ready configuration
- **Streamlined approach**: PRD contains tasks, 003 contains execution configuration
