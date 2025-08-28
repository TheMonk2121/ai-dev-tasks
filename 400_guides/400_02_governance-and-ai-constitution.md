\n+## ⚖️ Constitution (Condensed)
\n+- File safety first: analyze before edits; protect critical files; preserve cross‑refs.
- Context hierarchy: hydrate via `./scripts/memory_up.sh`; read `100_memory/100_cursor-memory-context.md` → `000_core/000_backlog.md` → `400_03_system-overview-and-architecture.md`.
- Workflow chain: `000_backlog.md → 001_create-prd.md → 002_generate-tasks.md → 003_process-task-list.md`.
- Error prevention: enforce testing, rollback plans, and DSPy assertions.
- Documentation: tiered guides, explicit links, single index.
- Integration: constitution hooks in prompts, CI checks, and runtime validators.
- Security: threat model linkage and minimum scans on risky changes.
- Monitoring: track context loss, safety violations, and doc integrity in ops.
# Governance and AI Constitution

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Governance policies and AI constitution for the development ecosystem | Setting up governance or need to understand AI safety policies | Review specific policies and constitution sections |

## 🎯 Purpose

This guide covers governance and AI constitution including:
- **AI constitution and safety policies**
- **Governance structure and decision-making**
- **Policy enforcement and compliance**
- **AI agent behavior guidelines**
- **Safety and validation frameworks**
- **Core constitution rules for file safety and analysis**
- **Context preservation and memory management**
- **Error prevention and recovery patterns**

## 📋 When to Use This Guide

- **Setting up governance structures**
- **Defining AI safety policies**
- **Establishing decision-making processes**
- **Implementing compliance frameworks**
- **Creating AI agent guidelines**
- **Before any file operations**
- **When writing code or implementing security measures**
- **Managing context and memory systems**

## 🎯 Expected Outcomes

- **Clear governance structure** and decision-making processes
- **Comprehensive AI safety policies** and constitution
- **Effective policy enforcement** and compliance monitoring
- **Consistent AI agent behavior** across the system
- **Robust safety and validation** frameworks
- **Protected file operations** through constitution rules
- **Preserved context and memory** management
- **Prevented errors** through systematic recovery patterns

## 📋 Policies

### AI Constitution
- **Safety-first approach** to all AI interactions
- **Transparency and explainability** in AI decisions
- **Human oversight and control** over AI systems
- **Ethical considerations** in all AI development
- **Continuous monitoring** and improvement

### Governance Structure
- **Clear decision-making hierarchy** and responsibilities
- **Policy enforcement mechanisms** and compliance monitoring
- **Regular review and updates** of governance policies
- **Stakeholder involvement** in policy development
- **Documentation and communication** of policy changes

### Core Constitution Rules
- **File Safety & Analysis**: Mandatory analysis before any file operations
- **Context Preservation**: Memory management and context hierarchy enforcement
- **Error Prevention**: Multi-turn process enforcement and recovery patterns
- **Documentation Coherence**: Cross-reference integrity and naming conventions

## 🔧 How-To

### Setting Up Governance
1. **Define governance structure** and decision-making processes
2. **Establish AI constitution** and safety policies
3. **Create enforcement mechanisms** and compliance monitoring
4. **Implement regular review** and update processes
5. **Document and communicate** policies to all stakeholders

### Implementing AI Safety
1. **Define AI constitution** and behavior guidelines
2. **Establish safety protocols** and validation frameworks
3. **Create monitoring systems** for AI behavior
4. **Implement oversight mechanisms** and human control
5. **Regular safety audits** and policy reviews

### Following Constitution Rules
1. **Complete file analysis** before any file operations
2. **Preserve critical files** and maintain dependencies
3. **Maintain context hierarchy** and memory management
4. **Implement error prevention** and recovery patterns
5. **Ensure documentation coherence** and cross-reference integrity

## 📜 CORE CONSTITUTION RULES

### Article I: File Safety & Analysis

**MANDATORY BEFORE ANY FILE OPERATIONS**

#### 1. File Analysis Requirement
- **ALWAYS read** `400_guides/400_file-analysis-guide.md` completely (463 lines)
- **Complete 6-step mandatory analysis** for any file operations
- **Show all cross-references** before proceeding
- **Get explicit user approval** for any file deletion, deprecation, or major changes

#### 2. Critical File Protection
- **Never delete files** with `<!-- CRITICAL_FILE: true -->` metadata
- **Never delete files** with `<!-- ARCHIVE_PROTECTED: true -->` metadata
- **Preserve all dependencies** up and down the chain
- **Maintain workflow chain integrity** at all costs

#### 3. Context Hierarchy Enforcement
- **HIGH Priority**: Memory context, system overview, backlog
- **MEDIUM Priority**: Workflows, core components
- **LOW Priority**: Domain-specific guides and utilities

#### 4. Multi-Turn Process Enforcement
- **Mandatory checklist** for high-risk operations
- **Validation steps** at each stage
- **Explicit confirmation** before proceeding

### Article II: Context Preservation & Memory Management

#### 1. Memory System Integrity
- **Preserve context hierarchy** (HIGH/MEDIUM/LOW priority system)
- **Maintain workflow chain** (`000_backlog.md → 001_create-prd.md → 002_generate-tasks.md → 003_process-task-list.md`)
- **Protect technology stack integrity** (Cursor Native AI + Specialized Agents + DSPy + PostgreSQL + n8n)

#### 2. RAG System Requirements
- **Span-level grounding** for precise citation retrieval
- **Hybrid search** (dense + sparse) for comprehensive results
- **Semantic chunking boundaries** for optimal context assembly

#### 3. Context Assembly Standards
- **Role-aware context assembly** for different AI roles
- **Stable anchors** for consistent retrieval
- **Role-based pinning** for specialized contexts
- **Token budgeting** for efficient context management

### Article III: Error Prevention & Recovery

#### 1. Systematic Approach
- **Quick Triage**: Immediate assessment and classification
- **Deep Audit**: Comprehensive analysis of root causes
- **Prevention & Guardrails**: Systematic prevention measures

#### 2. Recovery Patterns
- **Database connection recovery** with fallback strategies
- **File validation recovery** with safety checks
- **Error pattern recognition** for automated recovery
- **HotFix generation** for immediate resolution

#### 3. Quality Gates
- **Pre-operation validation** with 6-point checklist
- **During-operation monitoring** with real-time checks
- **Post-operation verification** with success metrics

### Article IV: Documentation & Knowledge Management

#### 1. MECE Patterns
- **Mutually Exclusive, Collectively Exhaustive** documentation
- **No content duplication** across guides
- **Cross-references** instead of content replication

#### 2. Documentation Coherence
- **File naming conventions** for consistency
- **Cross-reference integrity** across all guides
- **Structure validation** for maintainability

#### 3. Knowledge Preservation
- **"Don't lose signal"** principle for all content
- **Evidence-first generation** with explicit citations
- **Traceable reasoning** for all decisions

### Article V: System Integration & Workflow

#### 1. Workflow Chain Preservation
- **Exact sequence** of core workflow files
- **Dependency mapping** for all components
- **Integration points** for seamless operation

#### 2. Technology Stack Integrity
- **Cursor Native AI** for primary development
- **Specialized Agents** for domain-specific tasks
- **DSPy** for advanced RAG applications
- **PostgreSQL + PGVector** for data persistence
- **n8n** for workflow automation

#### 3. Constitution Integration
- **System prompt integration** patterns
- **State persistence** via `.ai_state.json`
- **Compliance tracking** with metrics and monitoring

### Article VI: Compliance & Enforcement

#### 1. Compliance Metrics
- **Zero critical context losses** - mandatory requirement
- **100% safety compliance** - non-negotiable
- **Maintained system integrity** - continuous monitoring
- **Enhanced AI reliability** - measurable improvement

#### 2. Validation Criteria (6-Point Checklist)
1. **File Safety**: All critical files protected and dependencies preserved
2. **Context Preservation**: Memory hierarchy maintained and workflow chain intact
3. **Error Prevention**: Multi-turn processes enforced with validation steps
4. **Documentation Coherence**: Cross-references valid and naming conventions followed
5. **System Integration**: Technology stack integrity maintained
6. **Compliance Monitoring**: Real-time metrics and success indicators tracked

#### 3. Success Metrics
- **Zero critical context losses** across all operations
- **100% safety compliance** in all AI interactions
- **Maintained system integrity** with no degradation
- **Enhanced AI reliability** with measurable improvements

### Article VII: Implementation & Deployment

#### 1. Implementation Phases
- **Phase 1 (Immediate)**: Core constitution rules and file safety
- **Phase 2 (Enhanced)**: Context preservation and memory management
- **Phase 3 (Advanced)**: Error prevention and recovery automation

#### 2. Research Foundation
- **Compliance required** with `500_research-analysis-summary.md`
- **Safety critical** flags for all high-risk operations
- **Evidence-based** decision making for all policies

#### 3. Version Tracking
- **Constitution Version**: 1.0
- **Implementation Date**: 2024-08-07
- **Integration Status**: Active
- **Last Updated**: 2025-08-28

### Article VIII: Cross-References & Dependencies

#### 1. Mandatory Reading
- **File Analysis**: `400_guides/400_file-analysis-guide.md` (463 lines) - mandatory reading
- **Context Priority**: `400_guides/400_context-priority-guide.md` - validation reference
- **Memory Context**: `100_memory/100_cursor-memory-context.md` - primary memory scaffold
- **System Overview**: `400_guides/400_system-overview.md` - technical architecture
- **Backlog**: `000_core/000_backlog.md` - current priorities

#### 2. Workflow Files
- **PRD Creation**: `000_core/001_create-prd.md`
- **Task Generation**: `000_core/002_generate-tasks.md`
- **Task Execution**: `000_core/003_process-task-list.md`

#### 3. Supporting Guides
- **Coding Standards**: `400_guides/400_comprehensive-coding-best-practices.md` - error handling
- **Security**: `400_guides/400_security-best-practices-guide.md` - security requirements
- **Performance**: `400_performance-optimization-guide_additional_resources.md` - performance requirements

#### 4. Research Foundation
- **Research Basis**: `500_research-analysis-summary.md` - research foundation
- **Documentation Research**: `500_research/500_documentation-coherence-research.md` - documentation patterns
- **Safety Research**: `500_research/500_maintenance-safety-research.md` - safety findings
- **Never delete files** with `<!-- CRITICAL_FILE: true -->` metadata
- **Never archive files** with `<!-- ARCHIVE_PROTECTED: true -->` metadata
- **Always check dependencies** before file operations
- **Preserve file naming conventions** and cross-references
- **Tier 1 Critical Files**: `scripts/venv_manager.py`, `scripts/single_doorway.py`, `scripts/process_tasks.py` - NEVER break without a plan

#### 3. Documentation Coherence
- **Maintain cross-reference integrity** across all documentation
- **Preserve file naming convention patterns** (400_, 500_, etc.)
- **Ensure documentation coherence** before any changes
- **Validate against** `400_guides/400_context-priority-guide.md` before operations

### Article II: Context Preservation & Memory Management

#### 1. Memory Context Priority
- **ALWAYS read** `100_memory/100_cursor-memory-context.md` first in any new session
- **Check** `000_core/000_backlog.md` for current priorities and dependencies
- **Review** `400_guides/400_system-overview.md` for technical context
- **Use existing workflows** (`000_core/001_create-prd.md`, `000_core/002_generate-tasks.md`, `000_core/003_process-task-list.md`)

#### 2. Context Hierarchy Enforcement
- **HIGH Priority**: `100_memory/100_cursor-memory-context.md`, `400_guides/400_system-overview.md`, `000_core/000_backlog.md`
- **MEDIUM Priority**: `000_core/001_create-prd.md`, `000_core/002_generate-tasks.md`, `000_core/003_process-task-list.md`
- **LOW Priority**: Domain-specific files and implementation details

#### 3. Development Environment Requirements
- **Virtual Environment**: ALWAYS check `scripts/venv_manager.py --check` before DSPy development
- **Memory Rehydration**: Use `scripts/memory_up.sh` for context assembly
- **Workflow Execution**: Use `scripts/run_workflow.py` for automatic venv management

#### 4. Context Loss Prevention
- **Reinforce critical rules** at the beginning of each operation
- **Use quick reference sections** for rapid context scanning
- **Maintain state persistence** through `.ai_state.json`
- **Preserve cross-references** and metadata patterns

### Article III: Error Prevention & Recovery

#### 1. Multi-Turn Process Enforcement
- **Use mandatory checklist enforcement** for high-risk operations
- **Implement multi-turn prompts** with validation steps
- **Require explicit confirmation** for critical changes
- **Use guardrails and constraint frameworks**

#### 2. Error Recovery Patterns
- **Follow comprehensive coding best practices** for all error handling
- **Use automated recovery scripts** when available
- **Implement systematic workflows** for common issues
- **Maintain emergency procedures** for critical failures

#### 3. Safety Validation
- **Validate all changes** against safety requirements
- **Use regression testing** for critical operations
- **Implement rollback procedures** for major changes
- **Maintain backup and recovery systems**

### Article IV: Documentation & Knowledge Management

#### 1. Documentation Architecture
- **Follow modular, MECE-aligned** documentation patterns
- **Use self-contained chunks** with explicit links
- **Maintain cross-reference integrity** across all documentation
- **Preserve file naming conventions** and organizational patterns

#### 2. Knowledge Preservation
- **Maintain comprehensive documentation** of all system components
- **Preserve implementation details** and technical decisions
- **Document architectural patterns** and design decisions
- **Maintain historical context** for system evolution

## 📋 Checklists

### Governance Setup Checklist
- [ ] **Governance structure defined** and documented
- [ ] **Decision-making processes established**
- [ ] **Policy enforcement mechanisms in place**
- [ ] **Compliance monitoring systems implemented**
- [ ] **Regular review processes scheduled**

### AI Safety Implementation Checklist
- [ ] **AI constitution defined** and documented
- [ ] **Safety policies established** and communicated
- [ ] **Validation frameworks implemented**
- [ ] **Monitoring systems operational**
- [ ] **Oversight mechanisms in place**

### Constitution Compliance Checklist
- [ ] **File analysis completed** before any operations
- [ ] **Critical files protected** and dependencies checked
- [ ] **Context hierarchy maintained** and memory preserved
- [ ] **Error prevention measures** implemented
- [ ] **Documentation coherence validated**

## 🔗 Interfaces

### Governance Structure
- **Policy Definition**: Clear policy statements and guidelines
- **Enforcement Mechanisms**: Automated and manual compliance checks
- **Review Processes**: Regular policy review and update cycles
- **Communication Channels**: Policy communication and training

### AI Constitution
- **Behavior Guidelines**: Clear rules for AI agent behavior
- **Safety Protocols**: Safety measures and validation processes
- **Oversight Mechanisms**: Human oversight and control systems
- **Monitoring Systems**: Continuous monitoring and alerting

### Constitution Rules
- **File Analysis**: Systematic analysis procedures and tools
- **Context Management**: Memory hierarchy and preservation systems
- **Error Prevention**: Multi-turn processes and validation frameworks
- **Documentation**: Coherence validation and cross-reference management

## 📚 Examples

### AI Constitution Example
```markdown
## AI Constitution

### Core Principles
1. **Safety First**: All AI interactions prioritize safety and security
2. **Transparency**: AI decisions are explainable and auditable
3. **Human Control**: Humans maintain ultimate control over AI systems
4. **Ethical Behavior**: AI systems follow ethical guidelines and principles
5. **Continuous Improvement**: AI systems learn and improve over time

### Behavior Guidelines
- **Respect human autonomy** and decision-making
- **Provide clear explanations** for all decisions and actions
- **Maintain confidentiality** and data privacy
- **Follow established protocols** and safety measures
- **Report potential issues** or concerns immediately
```

### File Analysis Example
```bash
# Complete 6-step file analysis
1. Read core memory context
2. Understand file organization system
3. Apply tier-based decisions
4. Check dependencies and relationships
5. Validate against safety requirements
6. Get explicit user approval for changes
```

### Context Preservation Example
```bash
# Memory rehydration sequence
./scripts/memory_up.sh -q "current project status"
# Read 100_memory/100_cursor-memory-context.md
# Check 000_core/000_backlog.md for priorities
# Review 400_guides/400_system-overview.md for context
```

## 🔗 Related Guides

- **Getting Started**: `400_00_getting-started-and-index.md`
- **System Overview**: `400_03_system-overview-and-architecture.md`
- **Security**: `400_10_security-compliance-and-access.md`
- **Documentation Playbook**: `400_01_documentation-playbook.md`
- **File Analysis**: `400_guides/400_file-analysis-guide.md`

## 📚 References

- **Migration Map**: `migration_map.csv`
- **PRD**: `artifacts/prd/PRD-B-1035-400_guides-Consolidation.md`
- **Original Governance**: Various governance-related files (now stubs)
- **Comprehensive Coding Best Practices**: `400_05_coding-and-prompting-standards.md`

## 📋 Changelog

- **2025-08-28**: Created as part of B-1035 consolidation
- **2025-08-28**: Consolidated governance and AI constitution guides
- **2025-08-28**: Merged content from:
  - `400_ai-constitution-governance.md`
  - `400_ai-constitution.md`
