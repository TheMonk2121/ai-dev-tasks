<!-- ANCHOR_KEY: create-prd-hybrid -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["planner", "implementer"] -->

# 📝 Create PRD (Hybrid Template)

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Enhanced PRD creation with both planning structure and implementation guidance | Starting new feature development | Run workflow to generate PRD for selected backlog item |

## 🎯 **Current Status**
- **Status**: ✅ **ACTIVE** - Enhanced PRD creation workflow with industry standards
- **Priority**: 🔥 Critical - Essential for project planning
- **Points**: 4 - Moderate complexity, high importance
- **Dependencies**: 000_core/000_backlog.md
- **Next Steps**: Enhanced template with MoSCoW prioritization and solo optimizations
- **Performance Monitoring**: ✅ **ENABLED** - Automatic performance collection and analysis

## When to use {#when-to-use}

- Use for high-risk or 5+ point items, or when score_total < 3.0
- Optional for smaller items where acceptance criteria are obvious
- **Enhanced**: Now includes implementation guidance for faster execution
- **Performance**: Automatic performance monitoring with real-time analysis

### PRD Skip Rule (canonical) {#prd-skip-rule}

- Skip PRD when: points < 5 AND score_total ≥ 3.0 (backlog metadata `<!--score_total: X.X-->`)
- Otherwise, create a PRD with machine-verifiable acceptance criteria

### Backlog Integration {#backlog-integration}

- **Input**: Backlog item ID (e.g., B-1007) or PRD file
- **Output**: PRD file following template structure + implementation guidance
- **Cross-reference**: `000_core/000_backlog.md` for item details and metadata

### Performance Integration {#performance-integration}

- **Collection Points**: 7 strategic points for performance monitoring
- **Real-time Analysis**: Automatic bottleneck detection and recommendations
- **Database Storage**: PostgreSQL with partitioning and retention policies
- **Dashboard Integration**: NiceGUI dashboard for performance visualization

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

## **Performance Collection Hooks**

### **Workflow Start Hook**
```python
# PERFORMANCE_HOOK: WORKFLOW_START
from src.monitoring.performance_collector import start_workflow_tracking

workflow_data = start_workflow_tracking(
    backlog_item_id="B-XXXX",
    prd_file_path="artifacts/prds/PRD-B-XXXX.md",
    task_count=0  # Will be updated during task generation
)
```

### **Section Analysis Hook**
```python
# PERFORMANCE_HOOK: SECTION_ANALYSIS
from src.monitoring.performance_collector import performance_context, CollectionPoint

with performance_context(
    CollectionPoint.SECTION_ANALYSIS,
    metadata={
        "section_name": "Problem Statement",
        "content_size": len(section_content),
        "complexity_score": calculate_complexity(section_content)
    }
):
    # Process section content
    processed_section = process_section_content(section_content)
```

### **Template Processing Hook**
```python
# PERFORMANCE_HOOK: TEMPLATE_PROCESSING
from src.monitoring.performance_collector import performance_context, CollectionPoint

with performance_context(
    CollectionPoint.TEMPLATE_PROCESSING,
    metadata={
        "template_type": "hybrid",
        "complexity_score": template_complexity,
        "sections_count": len(sections)
    }
):
    # Generate PRD from template
    prd_content = generate_prd_from_template(template_data)
```

### **Context Integration Hook**
```python
# PERFORMANCE_HOOK: CONTEXT_INTEGRATION
from src.monitoring.performance_collector import performance_context, CollectionPoint

with performance_context(
    CollectionPoint.CONTEXT_INTEGRATION,
    metadata={
        "context_source": "backlog",
        "context_size": len(backlog_context),
        "integration_complexity": calculate_integration_complexity()
    }
):
    # Integrate context from backlog and memory
    integrated_context = integrate_context(backlog_context, memory_context)
```

### **Validation Check Hook**
```python
# PERFORMANCE_HOOK: VALIDATION_CHECK
from src.monitoring.performance_collector import performance_context, CollectionPoint

with performance_context(
    CollectionPoint.VALIDATION_CHECK,
    metadata={
        "validation_rules": ["acceptance_criteria", "quality_gates"],
        "quality_gates": len(quality_gates),
        "validation_score": validation_score
    }
):
    # Perform validation checks
    validation_result = perform_validation_checks(prd_content)
```

### **Workflow Complete Hook**
```python
# PERFORMANCE_HOOK: WORKFLOW_COMPLETE
from src.monitoring.performance_collector import end_workflow_tracking, get_workflow_analysis

# End workflow tracking
workflow_result = end_workflow_tracking(success=True)

# Get performance analysis
analysis = get_workflow_analysis()
if analysis:
    print(f"Performance Score: {analysis['performance_score']:.1f}")
    print(f"Total Duration: {analysis['total_duration_ms']:.1f}ms")
    if analysis['bottlenecks']:
        print(f"Bottlenecks: {len(analysis['bottlenecks'])}")
    if analysis['recommendations']:
        print(f"Recommendations: {len(analysis['recommendations'])}")
```

### **Error Handling Hook**
```python
# PERFORMANCE_HOOK: ERROR_OCCURRED
from src.monitoring.performance_collector import performance_context, CollectionPoint

try:
    # Workflow operations
    pass
except Exception as e:
    with performance_context(
        CollectionPoint.ERROR_OCCURRED,
        metadata={
            "error_type": type(e).__name__,
            "error_location": "template_processing",
            "error_severity": "high"
        }
    ):
        # Handle error and recovery
        handle_error_and_recovery(e)
```

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
├── tests/                  # Test files
├── docs/                   # Documentation
├── config/                 # Configuration files
└── scripts/                # Utility scripts
```

### Development Patterns
- **Models**: `src/models/` - Data models and business logic
- **Views**: `src/views/` - UI components and templates
- **Controllers**: `src/controllers/` - Request handling and routing
- **Services**: `src/services/` - External integrations and utilities

### Local Development
```bash
# Setup
poetry install
poetry run pre-commit install

# Run tests
poetry run pytest

# Start development server
poetry run uvicorn src.main:app --reload
```

### Common Tasks
- **Add new page**: Create view in `src/views/`, add route in `src/controllers/`
- **Add new API**: Create endpoint in `src/controllers/`, add model in `src/models/`
- **Add new model**: Create file in `src/models/`, add migration in `config/migrations/`

## 1. Problem Statement

### What's broken?
[Clear description of the current problem]

### Why does it matter?
[Impact on users, business, or system]

### What's the opportunity?
[What we can gain by fixing it]

## 2. Solution Overview

### What are we building?
[Simple description of the solution]

### How does it work?
[Basic approach and key components]

### What are the key features?
[Main capabilities that solve the problem]

## 3. Acceptance Criteria

### How do we know it's done?
- [ ] [Clear, testable criteria 1]
- [ ] [Clear, testable criteria 2]
- [ ] [Clear, testable criteria 3]

### What does success look like?
[Measurable outcomes]

### What are the quality gates?
- [ ] [Must-pass requirement 1]
- [ ] [Must-pass requirement 2]
- [ ] [Must-pass requirement 3]

## 4. Technical Approach

### What technology?
[Stack and key components]

### How does it integrate?
[Connections to existing systems]

### What are the constraints?
[Technical limitations and requirements]

## 5. Risks and Mitigation

### What could go wrong?
- **Risk 1**: [Description]
- **Risk 2**: [Description]
- **Risk 3**: [Description]

### How do we handle it?
- **Mitigation 1**: [Strategy]
- **Mitigation 2**: [Strategy]
- **Mitigation 3**: [Strategy]

### What are the unknowns?
[Areas of uncertainty]

## 6. Testing Strategy

### What needs testing?
[Critical components and scenarios]

### How do we test it?
[Testing approach and tools]

### What's the coverage target?
[Minimum testing requirements]

## 7. Implementation Plan

### What are the phases?
1. **Phase 1**: [Description] (X hours)
2. **Phase 2**: [Description] (X hours)
3. **Phase 3**: [Description] (X hours)

### What are the dependencies?
[What needs to happen first]

### What's the timeline?
[Realistic time estimates]

---

## **Performance Metrics Summary**

> 📊 **Workflow Performance Data**
> - **Workflow ID**: `{workflow_id}`
> - **Total Duration**: `{total_duration_ms:.1f}ms`
> - **Performance Score**: `{performance_score:.1f}/100`
> - **Success**: `{success}`
> - **Error Count**: `{error_count}`

> 🔍 **Performance Analysis**
> - **Bottlenecks**: `{bottlenecks_count}`
> - **Warnings**: `{warnings_count}`
> - **Recommendations**: `{recommendations_count}`

> 📈 **Collection Points**
> - **Workflow Start**: `{workflow_start_duration:.1f}ms`
> - **Section Analysis**: `{section_analysis_duration:.1f}ms`
> - **Template Processing**: `{template_processing_duration:.1f}ms`
> - **Context Integration**: `{context_integration_duration:.1f}ms`
> - **Validation Check**: `{validation_check_duration:.1f}ms`
> - **Workflow Complete**: `{workflow_complete_duration:.1f}ms`
