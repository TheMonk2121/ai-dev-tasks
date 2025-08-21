<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: scripts/pr_signoff_v2.py -->
<!-- MEMORY_CONTEXT: HIGH - Core workflow automation system -->
<!-- ESSENTIAL_FILES: 400_guides/400_system-overview.md, 400_guides/400_project-overview.md -->
<!-- DSPY_ROLE: documentation -->
<!-- DSPY_AUTHORITY: documentation_standards -->
<!-- DSPY_FILES: scripts/pr_signoff_v2.py, scripts/worklog_summarizer.py -->
<!-- DSPY_CONTEXT: Enhanced multi-role PR sign-off system v2.0 with 5-step strategic alignment -->
<!-- DSPY_VALIDATION: documentation_standards, content_organization, cross_reference_accuracy -->
<!-- DSPY_RESPONSIBILITIES: documentation_standards, content_organization, cross_reference_management -->

# Multi-Role PR Sign-Off System v2.0 Guide

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Enhanced PR sign-off system with 5-step strategic alignment, stakeholder involvement, milestone tracking, and lessons learned generation | Implementing comprehensive PR review workflows or setting up stakeholder approval processes | Follow the Quick Start section and implement the strategic alignment process |

## 📋 Overview

The **Multi-Role PR Sign-Off System v2.0** is an enhanced comprehensive review and cleanup workflow that integrates the **5-step strategic alignment process** with stakeholder involvement, milestone tracking, and automated lessons learned generation. This system ensures all stakeholders (including you!) are aligned on strategy and creates a learning loop for continuous improvement.

### **🎯 Key Enhancements in v2.0**

- **5-Step Strategic Alignment Process**: Based on your documentation placement logic
- **Stakeholder Role**: You as the primary stakeholder with strategic approval authority
- **Milestone Tracking**: Specific check-in points where roles must agree on path forward
- **Lessons Learned Generation**: Automated artifact creation for learning loops
- **Enhanced Validation**: Role-specific checks with strategic alignment verification

## 🚀 Quick Start

### **1. Initialize Strategic Alignment**

```bash
# Start the 5-step strategic alignment process
python scripts/pr_signoff_v2.py 123 --strategic-align step1_assess_scope \
  --step-answers '{"scope": "system-wide", "impact": "high", "stakeholders": ["user", "team"]}' \
  --step-notes "This PR affects core workflow automation"
```

### **2. Complete All Strategic Steps**

```bash
# Step 2: Choose implementation path
python scripts/pr_signoff_v2.py 123 --strategic-align step2_choose_path \
  --step-answers '{"approach": "enhanced_workflow", "trade_offs": "complexity_vs_benefit"}' \
  --step-notes "Enhanced approach provides better stakeholder involvement"

# Step 3: Define milestones
python scripts/pr_signoff_v2.py 123 --strategic-align step3_define_milestones \
  --step-answers '{"milestones": ["design", "implementation", "testing"], "check_ins": "weekly"}' \
  --step-notes "Weekly check-ins ensure alignment"

# Step 4: Set validation order
python scripts/pr_signoff_v2.py 123 --strategic-align step4_set_validation \
  --step-answers '{"sequence": ["stakeholder", "planner", "implementer", "coder", "researcher"]}' \
  --step-notes "Stakeholder approval required first"

# Step 5: Add cross-references
python scripts/pr_signoff_v2.py 123 --strategic-align step5_add_references \
  --step-answers '{"links": ["400_guides/400_system-overview.md"], "discovery": "enhanced"}' \
  --step-notes "Links to system overview for context"
```

### **3. Create Milestones**

```bash
# Create a design milestone
python scripts/pr_signoff_v2.py 123 --create-milestone "Design Review" \
  --milestone-description "Review architectural design and implementation approach" \
  --required-roles stakeholder planner implementer \
  --due-date "2025-01-20"
```

### **4. Stakeholder Sign-Off**

```bash
# You (stakeholder) sign off after strategic alignment
python scripts/pr_signoff_v2.py 123 --role stakeholder --approve \
  --notes "Strategic alignment complete. Business impact acceptable. Resources allocated appropriately."
```

### **5. Role-Based Sign-Offs**

```bash
# Planner sign-off
python scripts/pr_signoff_v2.py 123 --role planner --approve \
  --notes "Strategic goals aligned. Dependencies resolved."

# Implementer sign-off
python scripts/pr_signoff_v2.py 123 --role implementer --approve \
  --notes "Architecture patterns followed. Integration validated."

# Coder sign-off
python scripts/pr_signoff_v2.py 123 --role coder --approve \
  --notes "Code quality standards met. Tests passing."

# Researcher sign-off
python scripts/pr_signoff_v2.py 123 --role researcher --approve \
  --notes "Research insights captured. Patterns documented."
```

### **6. Generate Lessons Learned**

```bash
# Generate lessons learned artifact
python scripts/pr_signoff_v2.py 123 --generate-lessons
```

### **7. Complete Cleanup**

```bash
# Perform automated cleanup
python scripts/pr_signoff_v2.py 123 --cleanup
```

## 🏗️ System Architecture

### **Enhanced Role Definitions**

| Role | Responsibilities | Approval Criteria |
|------|------------------|-------------------|
| **Stakeholder** | Strategic vision approval, business impact assessment, resource allocation, timeline approval | Strategic vision aligned, business impact acceptable, resources allocated, timeline realistic |
| **Planner** | Strategic alignment check, backlog validation, priority assessment, roadmap impact | Backlog updated, goals aligned, dependencies resolved, next steps identified |
| **Implementer** | Technical architecture review, system integration, workflow automation, Scribe health | Architecture patterns followed, integration validated, workflows intact, system healthy |
| **Coder** | Code quality assessment, testing coverage, security compliance, documentation standards | Linting standards met, test coverage adequate, security practices followed, documentation updated |
| **Researcher** | Research impact assessment, knowledge extraction, pattern analysis, lessons learned | Research insights captured, patterns documented, lessons extracted, knowledge base updated |

### **5-Step Strategic Alignment Process**

The system integrates your **5-step documentation placement logic** as a strategic alignment framework:

#### **Step 1: Assess Content Type and Scope**
- **Purpose**: Determine if this is system-wide, workflow-specific, or setup-related
- **Questions**: Scope, impact, stakeholders, strategic importance
- **Outputs**: Scope assessment, impact analysis, stakeholder list

#### **Step 2: Choose Implementation Path**
- **Purpose**: Select appropriate implementation approach based on scope
- **Questions**: Best approach, multiple paths, trade-offs, strategic alignment
- **Outputs**: Implementation path, trade-off analysis, strategic alignment

#### **Step 3: Define Milestones and Check-ins**
- **Purpose**: Create specific milestones where each role must agree on path forward
- **Questions**: Key milestones, stakeholder approval points, check-in requirements, disagreement handling
- **Outputs**: Milestone list, check-in schedule, approval process

#### **Step 4: Set Reading and Validation Order**
- **Purpose**: Define sequence for role reviews and validations
- **Questions**: Optimal review order, validation dependencies, role dependencies, coverage
- **Outputs**: Validation sequence, dependency map, coverage plan

#### **Step 5: Add Cross-References and Discovery**
- **Purpose**: Ensure proper linking and discoverability for future reference
- **Questions**: Existing documentation links, discovery methods, cross-references, learning loop
- **Outputs**: Cross-references, discovery plan, learning loop integration

### **Workflow Process**

```
PR Creation
    ↓
┌─────────────────────────────────┐
│ PHASE 1: Strategic Alignment    │ ← NEW: 5-Step Process
│ (Stakeholder leads)             │
│                                 │
│ 1. Assess scope & impact        │
│ 2. Choose implementation path   │
│ 3. Define milestones & checkins │
│ 4. Set reading/validation order │
│ 5. Add cross-references         │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ PHASE 2: Milestone Tracking     │ ← NEW: Check-in Points
│ (Role-specific approvals)       │
│                                 │
│ • Design Review                 │
│ • Implementation Review         │
│ • Testing Review                │
│ • Final Approval                │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ PHASE 3: Role-Based Sign-Offs  │ ← Enhanced workflow
│ (All roles + stakeholder)       │
│                                 │
│ • Stakeholder (you!)            │
│ • Planner                       │
│ • Implementer                   │
│ • Coder                         │
│ • Researcher                    │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ PHASE 4: Lessons Learned        │ ← NEW: Learning Loop
│ (Generate artifacts)            │
│                                 │
│ • Strategic alignment insights  │
│ • Role insights                 │
│ • Milestone insights            │
│ • Recommendations               │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ PHASE 5: Automated Cleanup      │ ← Enhanced cleanup
│ (Archive + summarize)           │
│                                 │
│ • Worklog summarization         │
│ • File archiving                │
│ • Backlog updates               │
│ • Sign-off cleanup              │
└─────────────────────────────────┘
```

### **File Structure**

```
artifacts/
├── pr_signoffs/
│   └── PR-123-signoff-v2.json          # Enhanced sign-off state
├── lessons_learned/
│   └── PR-123-lessons.md               # Lessons learned artifact
└── summaries/
    └── B-XXX-summary.md                # Worklog summaries
```

## 🎯 Role-Specific Validation

### **Stakeholder Validation**

The stakeholder role (you!) has enhanced validation requirements:

- **Strategic Vision Approval**: Verifies 5-step strategic alignment is complete
- **Business Impact Assessment**: Confirms business impact has been assessed
- **Resource Allocation Approval**: Validates appropriate resource allocation
- **Timeline Approval**: Ensures timeline is realistic and achievable

### **Enhanced Role Checks**

Each role now includes strategic alignment verification:

- **Planner**: Must verify strategic alignment is complete before signing off
- **Implementer**: Reviews technical architecture with strategic context
- **Coder**: Ensures code quality aligns with strategic goals
- **Researcher**: Extracts knowledge with strategic alignment insights

## 📊 Status Tracking

### **Enhanced Status Information**

```bash
python scripts/pr_signoff_v2.py 123 --status
```

Returns comprehensive status including:

```json
{
  "pr_number": "123",
  "backlog_id": "B-097",
  "version": "2.0",
  "overall_status": "strategic_alignment_complete",
  "strategic_alignment": {
    "completed_steps": 5,
    "total_steps": 5,
    "is_complete": true
  },
  "signoffs": {
    "stakeholder": {
      "approved": true,
      "timestamp": "2025-01-19T10:30:00",
      "validation_status": "passed"
    }
  },
  "milestones": {
    "Design Review": {
      "status": "approved",
      "approvals": {
        "stakeholder": {"approved": true},
        "planner": {"approved": true},
        "implementer": {"approved": true}
      }
    }
  },
  "missing_roles": ["planner", "implementer", "coder", "researcher"],
  "can_close": false
}
```

## 🔄 Automated Cleanup

### **Enhanced Cleanup Process**

The v2.0 system includes comprehensive cleanup:

1. **Generate Lessons Learned**: Creates structured lessons learned artifact
2. **Worklog Summarization**: Generates worklog summaries
3. **File Archiving**: Archives temporary files with v2.0 deprecation headers
4. **Backlog Updates**: Updates backlog item status
5. **Sign-off Cleanup**: Removes temporary sign-off files

### **Lessons Learned Artifact**

Automatically generates `artifacts/lessons_learned/PR-XXX-lessons.md` containing:

- **Strategic Alignment Insights**: Key decisions from each step
- **Role Insights**: Validation results and notes from each role
- **Milestone Insights**: Approval patterns and coordination insights
- **Recommendations**: Actionable improvements for future PRs
- **Patterns Identified**: Recurring themes and successful approaches

## 🔧 Integration Workflows

### **With Scribe System**

The v2.0 system integrates seamlessly with Scribe:

```bash
# Start Scribe for strategic alignment session
python scripts/single_doorway.py scribe start --backlog-id B-097

# Complete strategic alignment steps
python scripts/pr_signoff_v2.py 123 --strategic-align step1_assess_scope \
  --step-answers '{"scope": "system-wide"}' \
  --step-notes "Captured in Scribe session"

# Stop Scribe after alignment
python scripts/single_doorway.py scribe stop
```

### **With Memory Rehydration**

Strategic alignment data is preserved for future reference:

```bash
# Rehydrate with strategic alignment context
python scripts/cursor_memory_rehydrate.py stakeholder "PR-123 strategic alignment decisions"
```

### **With Backlog Management**

Enhanced backlog integration:

```bash
# Update backlog with strategic alignment insights
python scripts/backlog_parser.py --update B-097 --strategic-insights PR-123
```

## 🛠️ Troubleshooting

### **Common Issues**

#### **Strategic Alignment Incomplete**
```
❌ Stakeholder must complete strategic alignment before signing off
```
**Solution**: Complete all 5 strategic alignment steps before stakeholder sign-off

#### **Milestone Approval Missing**
```
❌ Milestone Design Review not approved by required roles
```
**Solution**: Ensure all required roles approve the milestone

#### **Role Validation Failed**
```
❌ Planner validation failed: Strategic alignment not complete
```
**Solution**: Wait for stakeholder to complete strategic alignment

### **Validation Errors**

#### **Invalid Strategic Alignment Step**
```
❌ Invalid step: step6_invalid
```
**Solution**: Use only valid steps: `step1_assess_scope`, `step2_choose_path`, `step3_define_milestones`, `step4_set_validation`, `step5_add_references`

#### **Missing Required Parameters**
```
❌ --step-answers required for strategic alignment
```
**Solution**: Provide JSON-formatted answers for the strategic alignment step

## 🚀 Advanced Features

### **Milestone Management**

Create complex milestone workflows:

```bash
# Create multi-phase milestone
python scripts/pr_signoff_v2.py 123 --create-milestone "Phase 1: Foundation" \
  --milestone-description "Establish core infrastructure and patterns" \
  --required-roles stakeholder planner implementer \
  --due-date "2025-01-25"

# Approve milestone
python scripts/pr_signoff_v2.py 123 --approve-milestone "Phase 1: Foundation" \
  --milestone-role stakeholder \
  --milestone-notes "Foundation approach approved"
```

### **Strategic Alignment Templates**

Pre-defined strategic alignment templates for common scenarios:

```bash
# System-wide enhancement template
python scripts/pr_signoff_v2.py 123 --strategic-align step1_assess_scope \
  --step-answers '{"scope": "system-wide", "impact": "high", "stakeholders": ["user", "team", "stakeholders"]}' \
  --step-notes "Using system-wide enhancement template"
```

### **Lessons Learned Mining**

Extract patterns from lessons learned:

```bash
# Generate lessons learned
python scripts/pr_signoff_v2.py 123 --generate-lessons

# Analyze patterns across multiple PRs
python scripts/lessons_analyzer.py --pattern-extraction
```

## ⚡ Performance Optimization

### **Efficient Strategic Alignment**

- **Batch Processing**: Complete multiple strategic steps in sequence
- **Template Usage**: Use pre-defined templates for common scenarios
- **Parallel Milestones**: Create milestones that can be approved in parallel

### **Validation Optimization**

- **Cached Results**: Validation results are cached to avoid redundant checks
- **Incremental Updates**: Only re-run validation when dependencies change
- **Parallel Validation**: Role validations can run in parallel where possible

## 📈 Current Version: v2.0

### **Version History**

- **v1.0**: Basic multi-role sign-off system
- **v2.0**: Enhanced with 5-step strategic alignment, stakeholder role, milestone tracking, and lessons learned generation

### **Breaking Changes in v2.0**

- **New Required Role**: Stakeholder role must complete strategic alignment
- **Enhanced CLI**: New commands for strategic alignment and milestone management
- **New File Formats**: Enhanced sign-off state and lessons learned artifacts
- **Validation Changes**: Strategic alignment verification required for all roles

## 🔮 Future Enhancements

### **Planned Features**

- **AI-Powered Strategic Alignment**: Automated suggestions for strategic alignment steps
- **Advanced Milestone Templates**: Pre-defined milestone workflows for common scenarios
- **Cross-PR Pattern Analysis**: Identify patterns across multiple PRs
- **Integration with CI/CD**: Automated strategic alignment in CI/CD pipelines
- **Real-time Collaboration**: Live collaboration features for strategic alignment sessions

### **Learning Loop Enhancements**

- **Pattern Recognition**: Automatically identify successful patterns
- **Recommendation Engine**: Suggest improvements based on historical data
- **Knowledge Graph**: Build knowledge graph from lessons learned
- **Predictive Analytics**: Predict PR success based on strategic alignment quality

## 📚 Related Documentation

- **[System Overview](../400_guides/400_system-overview.md)**: Technical architecture
- **[Project Overview](../400_guides/400_project-overview.md)**: Project context and workflow
- **[Scribe System Guide](../400_guides/400_scribe-system-guide.md)**: Context capture system
- **[Context Priority Guide](../400_guides/400_context-priority-guide.md)**: Documentation hierarchy
- **[Naming Conventions](../200_setup/200_naming-conventions.md)**: File organization standards

## 🔗 Quick Links

- **[Quick Start](#-quick-start)**: Get started immediately
- **[System Architecture](#️-system-architecture)**: Understand the system design
- **[Role-Specific Validation](#-role-specific-validation)**: Role requirements and checks
- **[Status Tracking](#-status-tracking)**: Monitor progress and status
- **[Troubleshooting](#️-troubleshooting)**: Common issues and solutions
- **[Advanced Features](#-advanced-features)**: Advanced usage patterns
- **[Integration Workflows](#-integration-workflows)**: Work with other systems

---

**Version**: 2.0
**Last Updated**: 2025-01-19
**Next Review**: When strategic alignment process changes
