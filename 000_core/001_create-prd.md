<!-- ANCHOR_KEY: create-prd -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["planner", "implementer"] -->

# 📝 Create PRD

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Simple, clear Product Requirements Document creation | Starting new feature development | Run workflow to generate PRD for selected backlog item |

## 🎯 **Current Status**
- **Status**: ✅ **ACTIVE** - Simple PRD creation workflow
- **Priority**: 🔥 Critical - Essential for project planning
- **Points**: 4 - Moderate complexity, high importance
- **Dependencies**: 000_core/000_backlog.md
- **Next Steps**: Keep it simple, focus on what matters

## When to use {#when-to-use}

- Use for high-risk or 5+ point items, or when score_total < 3.0
- Optional for smaller items where acceptance criteria are obvious

### PRD Skip Rule (canonical) {#prd-skip-rule}

- Skip PRD when: points < 5 AND score_total ≥ 3.0 (backlog metadata `<!--score_total: X.X-->`)
- Otherwise, create a PRD with machine-verifiable acceptance criteria

### Backlog Integration {#backlog-integration}

- **Input**: Backlog item ID (e.g., B-1007) or PRD file
- **Output**: PRD file following template structure
- **Cross-reference**: `000_core/000_backlog.md` for item details and metadata

## Template {#template}

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
```

## **Special Instructions**

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

## Acceptance Criteria {#acceptance-criteria}

This simple approach ensures every PRD focuses on what actually matters: clear problems, simple solutions, realistic plans, and honest assessment of risks and challenges.

## Handoff to task generation {#handoff-to-002}

- Next step: Use `000_core/002_generate-tasks.md` with this PRD (or a Backlog ID)
- Input → PRD file; Output → 2–4 hour tasks with dependencies and gates
