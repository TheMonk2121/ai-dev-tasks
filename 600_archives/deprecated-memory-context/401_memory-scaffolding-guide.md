---
context: HIGH
tags: [memory, scaffolding]
---

# Memory Scaffolding Documentation Guidelines (Deprecated)

> This guidance is merged into `400_context-priority-guide.md`. For rehydration, use `100_cursor-memory-context.md`.

<!-- MEMORY_CONTEXT: HIGH - Memory scaffolding patterns and guidelines for AI context -->

<!-- MODULE_REFERENCE: 400_few-shot-context-examples_memory_context_examples.md -->
<!-- MODULE_REFERENCE: 400_system-overview.md -->
<!-- MODULE_REFERENCE: 400_few-shot-context-examples.md -->
<!-- MODULE_REFERENCE: 400_system-overview.md -->
## 🧠 Memory Scaffolding Documentation Guidelines

### Content Structure
Each file should include:
1. **Memory Context Comment**: `<!-- MEMORY_CONTEXT: [HIGH|MEDIUM|LOW] - [description] -->`
2. **Context Reference**: `<!-- CONTEXT_REFERENCE: [related-file].md -->`
3. **Clear Purpose**: What this file is for and when to read it
4. **Related Files**: Links to other relevant documentation

### Memory Context Levels
- **HIGH**: Read first for instant context (core workflow, system overview)
- **MEDIUM**: Read when working on specific workflows (PRD creation, task generation)
- **LOW**: Read for detailed implementation (specific integrations, configurations)

### Quality Checklist
- [ ] Clear, descriptive filename
- [ ] Memory context comment included
- [ ] Purpose and usage explained
- [ ] Related files referenced
- [ ] Content is current and accurate
- [ ] Follows established patterns

### Cross-Reference System
Use these reference patterns in other documents:

#### **In PRDs and Task Lists:**
```markdown
<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- ESSENTIAL_FILES: 400_project-overview.md, 400_system-overview_advanced_features.md, 000_backlog.md -->
<!-- IMPLEMENTATION_FILES: 104_dspy-development-context.md, 202_setup-requirements.md -->
<!-- DOMAIN_FILES: 100_backlog-guide.md, 103_yi-coder-integration.md -->
```

#### **In Code Comments:**
```python
# CONTEXT: See 400_context-priority-guide.md for file organization
# ESSENTIAL: 400_project-overview.md, 400_system-overview_advanced_features.md, 000_backlog.md
# IMPLEMENTATION: 104_dspy-development-context.md, 202_setup-requirements.md
```

#### **In Documentation:**
```markdown
> **Context Reference**: See `400_context-priority-guide.md` for complete file organization
> **Essential Files**: `400_project-overview.md`, `400_system-overview_advanced_features.md`, `000_backlog.md`
> **Implementation Files**: `104_dspy-development-context.md`, `202_setup-requirements.md`
```

### Memory Context Integration

#### **For AI Agents**
- **Structured Data**: Easy to parse and understand
- **Consistent Format**: Predictable metadata structure
- **Automated Updates**: Reduce manual intervention
- **Dependency Management**: Clear prerequisite tracking

#### **For Developers**
- **Reduced Overhead**: Less manual memory maintenance
- **Better Prioritization**: Data-driven decision making
- **Consistent Workflow**: Standardized process across projects
- **Progress Tracking**: Clear visibility into development status

### Implementation Notes

#### **Parsing Rules**
- Use regex to extract table rows
- Parse HTML comments for metadata
- Handle missing or malformed data gracefully
- Validate dependencies before processing

#### **Command Execution**
- Execute memory context commands in order
- Rollback changes if any step fails
- Log all operations for audit trail
- Handle errors gracefully

#### **Error Handling**
- Skip invalid entries
- Use fallback values when metadata is missing
- Report parsing errors clearly
- Maintain backward compatibility

### Best Practices

#### **File Organization**
- **Essential**: `400_project-overview.md`, `400_system-overview_advanced_features.md`, `000_backlog.md`
- **Implementation**: `104_dspy-development-context.md`, `202_setup-requirements.md`
- **Domain**: `100_backlog-guide.md`, `103_yi-coder-integration.md`

#### **Memory State Updates**
- **When to update**: After completing backlog items, changing focus, adding features
- **How to update**: Run `python scripts/update_cursor_memory.py`
- **What gets updated**: Priorities, completed items, system status, timestamps

#### **Quality Standards**
- **Clear Purpose**: Every file should have a clear, single purpose
- **Consistent Format**: Follow established patterns for metadata
- **Current Content**: Keep information up-to-date and accurate
- **Cross-References**: Maintain proper links between related files 